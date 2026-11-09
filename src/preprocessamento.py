"""ETL: diagnóstico, limpeza, validação, atributos, divisão temporal e o pré-processamento ajustado no treino."""
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

from src.ciclo import PROCESSED

# Faixas fisicamente possíveis para Jaraguá do Sul. Fora disso é erro de dado, não clima extremo.
FAIXAS = {"tmax": (-10, 45), "tmin": (-15, 40), "tmed": (-12, 42), "umidade": (0, 100),
          "orvalho": (-20, 35), "pressao": (950, 1050), "nuvens": (0, 100), "vento_max": (0, 200),
          "vento_med": (0, 150), "rajada": (0, 250), "vento_dir": (0, 360), "chuva": (0, 500),
          "radiacao": (0, 40)}


def diagnostico(df):
    """Por coluna: ausentes, valores fora da faixa física e outliers (z robusto acima de 5)."""
    linhas = {}
    for col, (minimo, maximo) in FAIXAS.items():
        s = df[col]
        desvio = (s - s.median()).abs()
        escala = 1.4826 * desvio.median()   # chuva tem mediana 0 na maioria dos meses: sem escala, sem z
        z = desvio / escala if escala > 0 else desvio * 0
        linhas[col] = {"ausentes": int(s.isna().sum()), "fora_da_faixa": int((~s.between(minimo, maximo) & s.notna()).sum()),
                       "outliers_z5": int((z > 5).sum()), "min": s.min(), "max": s.max()}
    calendario = pd.date_range(df["data"].min(), df["data"].max())
    geral = {"linhas": len(df), "datas_duplicadas": int(df["data"].duplicated().sum()),
             "dias_faltando": len(calendario.difference(df["data"])),
             "tmin_maior_que_tmax": int((df["tmin"] > df["tmax"]).sum())}
    return pd.DataFrame.from_dict(linhas, orient="index"), geral


def limpar(df):
    """Sem datas repetidas, calendário diário completo e valor impossível vira ausente (imputado depois,
    no Pipeline). Outlier de clima é real (frente fria, onda de calor), então só é sinalizado."""
    df = df.drop_duplicates("data", keep="last").set_index("data").sort_index()
    # Dia faltando vira linha vazia: assim "uma linha antes" é sempre "o dia anterior" nos lags.
    df = df.reindex(pd.date_range(df.index.min(), df.index.max(), name="data"))
    for col, (minimo, maximo) in FAIXAS.items():
        df[col] = df[col].where(df[col].between(minimo, maximo))
    df.loc[df["tmin"] > df["tmax"], ["tmin", "tmax"]] = np.nan
    return df.reset_index()


def validar(df, cfg):
    """Regras que, se quebradas, param o pipeline e com ele qualquer promoção."""
    problemas = []
    faltando = set(cfg["dados"]["variaveis"].values()) - set(df.columns)
    if faltando:
        problemas.append(f"colunas faltando: {sorted(faltando)}")
    if not (df["data"].is_unique and df["data"].is_monotonic_increasing):
        problemas.append("datas repetidas ou fora de ordem")
    if not (df["data"].diff().dropna() == pd.Timedelta(days=1)).all():
        problemas.append("calendário com buracos")
    if df["tmax"].isna().mean() > 0.01:
        problemas.append("mais de 1% da variável-alvo ausente")
    if problemas:
        raise ValueError("validação dos dados falhou: " + "; ".join(problemas))


def construir_atributos(df):
    """Atributos do dia t para prever a tmax de t+1. Tudo olha só para trás, então nada vaza do futuro."""
    f = df.set_index("data")[list(FAIXAS)].copy()
    for lag in (1, 2, 3):
        f[f"tmax_lag{lag}"] = f["tmax"].shift(lag)
    f["tmax_media3"] = f["tmax"].rolling(3).mean()
    f["tmax_media7"] = f["tmax"].rolling(7).mean()
    f["tmax_delta"] = f["tmax"].diff()
    f["amplitude"] = f["tmax"] - f["tmin"]
    f["pressao_delta"] = f["pressao"].diff()       # pressão caindo costuma anunciar frente fria
    f["umidade_delta"] = f["umidade"].diff()
    f["chuva_3d"] = f["chuva"].rolling(3).sum()
    direcao = np.deg2rad(f.pop("vento_dir"))       # 350° e 10° são vizinhos: seno e cosseno
    f["vento_dir_sin"], f["vento_dir_cos"] = np.sin(direcao), np.cos(direcao)
    dia = 2 * np.pi * f.index.day_of_year / 365.25
    f["dia_ano_sin"], f["dia_ano_cos"] = np.sin(dia), np.cos(dia)
    f["alvo"] = f["tmax"].shift(-1)
    return f.iloc[6:]                               # a primeira semana não tem média de 7 dias


def dividir(dataset, cfg):
    """Divisão cronológica: treino | validação | teste. A última linha ainda não tem alvo:
    é dela que sai a previsão do dia seguinte."""
    rotulado = dataset[dataset["alvo"].notna()]
    v, t = cfg["avaliacao"]["validacao_dias"], cfg["avaliacao"]["teste_dias"]
    return {"treino": rotulado.iloc[: -(v + t)], "validacao": rotulado.iloc[-(v + t): -t],
            "teste": rotulado.iloc[-t:], "proximo": dataset.tail(1)}


def linha_da_previsao(bruto, provisorio):
    """Atributos do último dia com dado, de onde sai a previsão. Os dias provisórios (depois do último dia do ERA5)
    entram só aqui, e por isso a previsão sai para o dia atual e não para uma semana atrás."""
    serie = bruto.drop(columns="lote", errors="ignore")
    if len(provisorio):
        serie = pd.concat([serie, provisorio], ignore_index=True)
    return construir_atributos(limpar(serie)).tail(1)


def carregar(cfg):
    dataset = pd.read_csv(PROCESSED / "dataset.csv", index_col="data", parse_dates=True)
    janelas = dividir(dataset, cfg)
    if (PROCESSED / "proximo.csv").exists():  # gravado pelo notebook 01, já com os dias provisórios
        janelas["proximo"] = pd.read_csv(PROCESSED / "proximo.csv", index_col="data", parse_dates=True)
    return dataset, janelas


def preparador():
    """Imputação pela mediana e padronização, sempre dentro do Pipeline: ajustadas só com o treino."""
    return [("imputacao", SimpleImputer(strategy="median")), ("escala", StandardScaler())]
