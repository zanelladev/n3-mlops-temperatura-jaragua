"""Configuração, caminhos, estado do ciclo e MLflow, compartilhados por todos os notebooks."""
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import yaml

os.environ.setdefault("MLFLOW_DISABLE_AGENT_HINT", "1")
import mlflow  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
RAW = RAIZ / "data" / "raw"
PROCESSED = RAIZ / "data" / "processed"
EVIDENCIAS = RAIZ / "evidencias"
MANIFESTO = RAIZ / "models" / "modelo_vigente.json"
PONTEIRO = PROCESSED / "ciclo_atual.txt"


def carregar_config():
    # Os notebooks rodam de dentro de notebooks/, mas todos os caminhos partem da raiz do projeto.
    os.chdir(RAIZ)
    return yaml.safe_load((RAIZ / "config" / "config.yaml").read_text(encoding="utf-8"))


def novo_ciclo(data_version, **dados):
    """Abre um ciclo: cycle_id e data_version que a votação, os treinos e a decisão vão compartilhar."""
    agora = datetime.now(timezone.utc)
    estado = {
        "cycle_id": agora.strftime("%Y%m%d-%H%M%S"),
        "data_version": data_version,
        "inicio_utc": agora.isoformat(timespec="seconds"),
        "evento": os.environ.get("GITHUB_EVENT_NAME", "local"),
        "github_run_id": os.environ.get("GITHUB_RUN_ID"),
        **dados,
    }
    pasta(estado).mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    PONTEIRO.write_text(estado["cycle_id"])
    salvar(estado)
    return estado


def pasta(estado):
    return EVIDENCIAS / "ciclos" / estado["cycle_id"]


def atual():
    cycle_id = PONTEIRO.read_text().strip()
    return json.loads((EVIDENCIAS / "ciclos" / cycle_id / "ciclo.json").read_text(encoding="utf-8"))


def salvar(estado):
    texto = json.dumps(estado, indent=2, ensure_ascii=False, default=str)
    (pasta(estado) / "ciclo.json").write_text(texto, encoding="utf-8")


def historico():
    """Uma linha por ciclo, montada a partir das evidências commitadas pelo workflow."""
    import pandas as pd

    arquivos = sorted((EVIDENCIAS / "ciclos").glob("*/ciclo.json"))
    return pd.json_normalize([json.loads(a.read_text(encoding="utf-8")) for a in arquivos])


def tags(estado, etapa):
    return {"cycle_id": estado["cycle_id"], "data_version": estado["data_version"],
            "etapa": etapa, "evento": estado["evento"]}


def configurar_mlflow(cfg):
    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    nome = cfg["mlflow"]["experimento"]
    if mlflow.get_experiment_by_name(nome) is None:
        eid = mlflow.create_experiment(nome)
        # ponytail: o MLflow grava o caminho absoluto dos artefatos. Trocamos por um caminho relativo
        # à raiz para o mesmo mlflow.db funcionar no runner, na máquina do grupo e na do professor.
        with sqlite3.connect(RAIZ / "mlflow.db") as con:
            con.execute("UPDATE experiments SET artifact_location = 'mlartefatos' WHERE experiment_id = ?", (eid,))
    mlflow.set_experiment(nome)
    return mlflow


def resumo_md(estado):
    """Resumo do ciclo para o job summary do GitHub Actions."""
    d, c, v = estado["decisao"], estado["competicao"], estado["votacao"]
    p, m = estado["previsoes"], estado["monitoramento"]
    linhas = [
        f"## Ciclo {estado['cycle_id']} ({estado['evento']})",
        f"- data_version: `{estado['data_version']}`, {estado['lote']['n_novos']} dia(s) novo(s), "
        f"dados até {estado['dados']['fim']}",
        f"- features eleitas ({v['n']}): {', '.join(v['features'])}",
        "",
        "| modelo | algoritmo | MAE validação |",
        "|---|---|---|",
        *[f"| {papel} | {c[papel]['algoritmo']} | {c[papel]['validacao']['mae']:.3f} |" for papel in ("A", "B")],
        f"| persistência | amanhã = hoje | {c['persistencia']['mae']:.3f} |",
        "",
        f"- vencedor: **{d['vencedor']}**; decisão: **{d['decisao']}** ({d['motivo']})",
        f"- MAE do vigente no teste (últimos {p['dias_teste']} dias): {p['mae_teste']:.3f} °C "
        f"(persistência: {p['mae_persistencia_teste']:.3f} °C)",
        f"- previsão para {p['data_alvo']}: **{p['previsto']:.1f} °C**",
        f"- monitoramento: {'**ALERTA**: ' + '; '.join(m['motivos']) if m['alerta'] else 'sem alerta'}",
    ]
    return "\n".join(linhas) + "\n"
