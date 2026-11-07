"""Entrada de dados: busca no Open-Meteo só os dias que ainda não temos e grava como um lote novo."""
import hashlib
import os
import time
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd
import requests

from src.ciclo import RAW


def carregar_bruto():
    """Junta todos os lotes de data/raw. Se uma data aparecer em dois lotes, vale a do lote mais novo."""
    arquivos = sorted(RAW.glob("lote_*.csv"))
    if not arquivos:
        return pd.DataFrame(columns=["data", "lote"])
    df = pd.concat([pd.read_csv(a, parse_dates=["data"]).assign(lote=a.stem) for a in arquivos])
    return df.drop_duplicates("data", keep="last").sort_values("data").reset_index(drop=True)


def buscar_api(cfg, inicio, fim):
    d = cfg["dados"]
    params = {"latitude": d["latitude"], "longitude": d["longitude"], "start_date": str(inicio),
              "end_date": str(fim), "daily": ",".join(d["variaveis"]), "timezone": d["fuso"],
              "models": d["modelo"]}
    for tentativa in range(3):
        try:
            resposta = requests.get(d["url"], params=params, timeout=120)
            resposta.raise_for_status()
            break
        except requests.RequestException:
            if tentativa == 2:
                raise
            time.sleep(20)
    df = pd.DataFrame(resposta.json()["daily"]).rename(columns={"time": "data", **d["variaveis"]})
    df["data"] = pd.to_datetime(df["data"])
    # O ERA5 chega com uns 7 dias de atraso e a API devolve esses dias vazios.
    # Só entram dias completos, e só até o primeiro buraco, para o calendário não pular datas.
    incompleto = df.drop(columns="data").isna().any(axis=1)
    return df[~incompleto.cummax()]


def atualizar(cfg):
    """Busca os dias depois do último que já temos e grava em data/raw/lote_<inicio>_<fim>.csv."""
    atual = carregar_bruto()
    inicio = (atual["data"].max() + timedelta(days=1)).date() if len(atual) else date.fromisoformat(cfg["dados"]["inicio"])
    fim = datetime.now(ZoneInfo(cfg["dados"]["fuso"])).date()
    if os.environ.get("DATA_LIMITE"):  # usado só para demonstrar a chegada de um lote (workflow_dispatch)
        fim = min(fim, date.fromisoformat(os.environ["DATA_LIMITE"]))
    novos = buscar_api(cfg, inicio, fim) if inicio <= fim else pd.DataFrame()
    if novos.empty:
        return {"n_novos": 0, "consultado": [str(inicio), str(fim)]}
    RAW.mkdir(parents=True, exist_ok=True)
    arquivo = RAW / f"lote_{novos['data'].min():%Y%m%d}_{novos['data'].max():%Y%m%d}.csv"
    novos.to_csv(arquivo, index=False)
    return {"n_novos": len(novos), "arquivo": arquivo.name, "inicio": str(novos["data"].min().date()),
            "fim": str(novos["data"].max().date()), "consultado": [str(inicio), str(fim)]}


def versao_dados(bruto):
    """data_version = último dia + sha256 dos arquivos de data/raw. Mesmo dado, mesma versão."""
    conteudo = b"".join(a.read_bytes() for a in sorted(RAW.glob("lote_*.csv")))
    return f"dv-{bruto['data'].max():%Y%m%d}-{hashlib.sha256(conteudo).hexdigest()[:8]}"
