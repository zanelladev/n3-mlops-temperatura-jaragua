"""Etapa 3: três métodos de seleção de atributos e a votação que elege as features do ciclo."""
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_selection import RFE, SelectKBest, f_regression
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline

from src.preprocessamento import preparador


def tres_metodos(treino, candidatas, cfg, semente):
    """Ranking de cada método, sempre ajustado só com o treino."""
    X = Pipeline(preparador()).fit_transform(treino[candidatas])
    y = treino["alvo"]
    k = cfg["votacao"]["k"]
    kbest = SelectKBest(f_regression, k=k).fit(X, y)
    rf = RandomForestRegressor(n_estimators=cfg["votacao"]["rf_arvores"], min_samples_leaf=5,
                               random_state=semente, n_jobs=-1).fit(X, y)
    rfe = RFE(Ridge(alpha=1.0), n_features_to_select=k).fit(X, y)

    tab = pd.DataFrame({"f_score": kbest.scores_, "rf_importancia": rf.feature_importances_,
                        "rfe_ranking": rfe.ranking_}, index=candidatas)
    tab["rank_kbest"] = tab["f_score"].rank(ascending=False, method="first")
    tab["rank_rf"] = tab["rf_importancia"].rank(ascending=False, method="first")
    # O RFE dá ranking 1 para as k que sobraram; entre elas desempata o |coeficiente| final do Ridge.
    tab["rfe_coef"] = 0.0
    tab.loc[rfe.support_, "rfe_coef"] = abs(rfe.estimator_.coef_)
    ordem = tab.sort_values(["rfe_ranking", "rfe_coef"], ascending=[True, False]).index
    tab["rank_rfe"] = pd.Series(range(1, len(ordem) + 1), index=ordem, dtype=float)
    return tab


def votar(tab, cfg):
    """Regra fixada no config antes de olhar o resultado: cada método vota nas suas k melhores,
    entra quem tiver pelo menos votos_minimos votos e, se sobrarem menos que min_features,
    completa pelo menor ranking médio (que também desempata a ordem)."""
    v = cfg["votacao"]
    tab = tab.copy()
    for metodo in ("kbest", "rf", "rfe"):
        tab[f"voto_{metodo}"] = tab[f"rank_{metodo}"] <= v["k"]
    tab["votos"] = tab[["voto_kbest", "voto_rf", "voto_rfe"]].sum(axis=1)
    tab["ranking_medio"] = tab[["rank_kbest", "rank_rf", "rank_rfe"]].mean(axis=1)
    tab = tab.sort_values(["votos", "ranking_medio"], ascending=[False, True])
    eleitas = tab.index[tab["votos"] >= v["votos_minimos"]].tolist()
    if len(eleitas) < v["min_features"]:
        eleitas = tab.index[: v["min_features"]].tolist()
    tab["eleita"] = tab.index.isin(eleitas)
    return tab, eleitas


if __name__ == "__main__":
    # Checagem rápida da regra: com k=2, a tem 3 votos, b tem 2 e c só 1. Com min_features=4,
    # a maioria elege a e b e o ranking médio completa as outras duas vagas.
    t = pd.DataFrame({"rank_kbest": [1, 2, 3, 4, 5], "rank_rf": [2, 1, 5, 3, 4], "rank_rfe": [1, 4, 2, 5, 3]},
                     index=list("abcde"), dtype=float)
    _, e = votar(t, {"votacao": {"k": 2, "votos_minimos": 2, "min_features": 2}})
    assert e == ["a", "b"], e
    _, e = votar(t, {"votacao": {"k": 2, "votos_minimos": 2, "min_features": 4}})
    assert e[:2] == ["a", "b"] and len(e) == 4, e
    print("votação ok")
