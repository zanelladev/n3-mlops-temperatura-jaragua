"""Etapa 4: os dois algoritmos, treinados com as mesmas features e avaliados do mesmo jeito."""
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.pipeline import Pipeline

from src.preprocessamento import preparador

ALGORITMOS = {"ridge": Ridge, "hist_gradient_boosting": HistGradientBoostingRegressor,
              "random_forest": RandomForestRegressor}

# O MLflow salva o modelo no formato skops (mais seguro que pickle) e só aceita tipos liberados.
# Estes são os que o Pipeline com Ridge e HistGradientBoosting usa.
TIPOS_CONFIAVEIS = ["numpy.dtype", "sklearn.ensemble._hist_gradient_boosting.predictor.TreePredictor"]


def treinar(algoritmo, params, treino, features, semente):
    """Pipeline completo (imputação, escala e modelo): o pré-processamento vai junto no modelo salvo."""
    estimador = ALGORITMOS[algoritmo](**params)
    if "random_state" in estimador.get_params():
        estimador.set_params(random_state=semente)
    return Pipeline(preparador() + [("modelo", estimador)]).fit(treino[features], treino["alvo"])


def metricas(real, previsto):
    return {"mae": float(mean_absolute_error(real, previsto)),
            "rmse": float(root_mean_squared_error(real, previsto)),
            "r2": float(r2_score(real, previsto))}


def persistencia(df):
    """Referência ingênua: a máxima de amanhã repete a de hoje."""
    return metricas(df["alvo"], df["tmax"])
