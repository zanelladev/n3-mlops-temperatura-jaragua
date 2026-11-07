"""Critério 10: monitoramento de drift com referência sazonal e alerta."""
import numpy as np
import pandas as pd


def psi(referencia, janela, bins):
    """Population Stability Index com faixas nos quantis da referência. Soma 0,5 em cada faixa
    para que uma faixa vazia na janela curta (30 dias) não faça o log explodir."""
    ref, jan = referencia.dropna().to_numpy(), janela.dropna().to_numpy()
    cortes = np.unique(np.quantile(ref, np.linspace(0, 1, bins + 1))[1:-1])
    p = np.bincount(np.searchsorted(cortes, ref, side="right"), minlength=len(cortes) + 1) + 0.5
    q = np.bincount(np.searchsorted(cortes, jan, side="right"), minlength=len(cortes) + 1) + 0.5
    p, q = p / p.sum(), q / q.sum()
    return float(np.sum((q - p) * np.log(q / p)))


def mesma_epoca(datas, janela, margem):
    """Máscara das datas que caem na mesma época do ano da janela, com margem em dias."""
    dias = {(d - 1 + m) % 366 + 1 for d in janela.day_of_year for m in range(-margem, margem + 1)}
    return datas.day_of_year.isin(list(dias))


def comparar(referencia, janela, features, cfg_mon):
    """PSI de cada feature contra duas referências: o ano todo e só a mesma época dos outros anos."""
    ref = referencia.drop(janela.index, errors="ignore")
    sazonal = ref[mesma_epoca(ref.index, janela.index, cfg_mon["margem_sazonal_dias"])]
    return pd.DataFrame({
        "psi_anual": {f: psi(ref[f], janela[f], cfg_mon["bins"]) for f in features},
        "psi_sazonal": {f: psi(sazonal[f], janela[f], cfg_mon["bins"]) for f in features},
    })


def backtest(referencia, features, cfg_mon):
    """A mesma checagem em janelas antigas (uma por mês) do período de treino do vigente:
    mostra quantas vezes cada referência teria disparado alerta em meses normais."""
    n = cfg_mon["janela_dias"]
    maximos = {}
    for inicio in range(0, len(referencia) - n + 1, n):
        janela = referencia.iloc[inicio: inicio + n]
        maximos[janela.index[0]] = comparar(referencia, janela, features, cfg_mon).max()
    return pd.DataFrame(maximos).T


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    base = pd.Series(rng.normal(20, 3, 3000))
    assert psi(base, pd.Series(rng.normal(20, 3, 30)), 5) < 0.5      # mesma distribuição: baixo
    assert psi(base, pd.Series(rng.normal(26, 3, 30)), 5) > 1.0      # deslocou 2 desvios: alto
    datas = pd.date_range("2020-01-01", "2023-12-31")
    marcadas = datas[mesma_epoca(datas, pd.date_range("2024-01-01", "2024-01-10"), 5)]
    assert set(marcadas.month) == {12, 1} and marcadas.min() == pd.Timestamp("2020-01-01")
    print("monitoramento ok")
