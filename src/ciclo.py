"""Configuração, caminhos, estado do ciclo e MLflow, compartilhados por todos os notebooks."""
import csv
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

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


NOMES = {"ridge": "Ridge", "hist_gradient_boosting": "HistGradientBoosting"}
EVENTOS = {"schedule": "agendada", "workflow_dispatch": "manual", "local": "local"}


def _num(x, casas=1):
    return f"{x:.{casas}f}".replace(".", ",").replace("-", "−")


def _int(n):
    return f"{n:,}".replace(",", ".")


def _data(iso, ano=True):
    return f"{iso[8:10]}/{iso[5:7]}" + (f"/{iso[:4]}" if ano else "")


def _ler_csv(caminho):
    if not caminho.exists():
        return []
    with open(caminho, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _execucao(estado):
    inicio = datetime.fromisoformat(estado["inicio_utc"]).astimezone(ZoneInfo("America/Sao_Paulo"))
    return f"Execução {EVENTOS.get(estado['evento'], estado['evento'])} de {inicio:%d/%m/%Y}", inicio


def titulo(estado):
    """Uma linha sobre a execução, usada como mensagem do commit do estado."""
    execucao, _ = _execucao(estado)
    if "previsoes" not in estado:
        return f"{execucao}: sem dados novos"
    p = estado["previsoes"]
    return (f"{execucao}: modelo {estado['decisao']['decisao']}, "
            f"máxima prevista de {_num(p['previsto'])} °C para {_data(p['data_alvo'], ano=False)}")


def resumo_md(estado):
    """Resumo da execução em Markdown, para a página do run no GitHub Actions e para o resumo.md do ciclo."""
    execucao, inicio = _execucao(estado)
    rodape = f"<sub>{execucao} às {inicio:%H:%M} (horário de Brasília) · identificador `{estado['cycle_id']}`</sub>"
    previsoes = _ler_csv(EVIDENCIAS / "previsoes_diarias.csv")

    if "previsoes" not in estado:  # a execução parou no notebook 01
        ultima = (f" Continua valendo a última previsão: **{_num(float(previsoes[-1]['previsto']))} °C para "
                  f"{_data(previsoes[-1]['data_alvo'])}**." if previsoes else "")
        return "\n".join([
            "# 🌡️ Sem dados novos hoje", "",
            f"O Open-Meteo ainda não publicou nenhum dia depois de {_data(estado['dados']['fim'])}, então a execução "
            f"parou depois do ETL, sem treinar e sem trocar o modelo.{ultima}", "",
            rodape, ""])

    cfg = yaml.safe_load((RAIZ / "config" / "config.yaml").read_text(encoding="utf-8"))
    c, d, p, m = estado["competicao"], estado["decisao"], estado["previsoes"], estado["monitoramento"]
    lote, dados, jan = estado["lote"], estado["dados"], estado["janelas"]
    promovido = d["decisao"] == "promovido"
    novos = (f"1 dia novo ({_data(lote['inicio'])})" if lote["n_novos"] == 1 else
             f"{_int(lote['n_novos'])} dias novos ({_data(lote['inicio'])} a {_data(lote['fim'])})")
    linhas = [
        f"# 🌡️ Máxima prevista para {_data(p['data_alvo'])}: {_num(p['previsto'])} °C",
        "",
        ("🆕 **Novo modelo promovido**" if promovido else "📌 **Modelo vigente mantido**")
        + (" · 🔴 **Alerta de drift**" if m["alerta"] else " · 🟢 **Sem alerta de drift**") + f" · {novos}",
        "",
    ]

    votos = _ler_csv(pasta(estado) / "votos.csv")
    eleitas = [r for r in votos if r["eleita"] == "True"]
    outras = [r for r in votos if r["eleita"] != "True"]
    cabecalho = ["| Feature | SelectKBest | Random Forest | RFE | Votos |", "|:--|:-:|:-:|:-:|:-:|"]

    def linha_voto(r):
        marcas = ["●" if r[col] == "True" else "" for col in ("voto_kbest", "voto_rf", "voto_rfe")]
        return f"| `{r['feature']}` | {' | '.join(marcas)} | {r['votos']} |"

    linhas += [
        f"### 🗳️ Votação: {len(votos)} candidatas, {len(eleitas)} eleitas",
        f"Cada método vota nas suas {cfg['votacao']['k']} melhores olhando só o treino, e entra quem tiver pelo menos "
        f"{cfg['votacao']['votos_minimos']} votos.",
        "", *cabecalho, *map(linha_voto, eleitas), "",
        f"<details><summary>As outras {len(outras)} candidatas</summary>", "",
        *cabecalho, *map(linha_voto, outras), "", "</details>", "",
    ]

    persistencia = c["persistencia"]["mae"]
    papeis = sorted(("A", "B"), key=lambda k: c[k]["validacao"]["mae"])

    def linha_modelo(k):
        mae = c[k]["validacao"]["mae"]
        nome = f"{k} · {NOMES.get(c[k]['algoritmo'], c[k]['algoritmo'])}"
        if k == d["vencedor"]:
            nome = f"🥇 **{nome}**"
        return f"| {nome} | {_num(mae, 3)} | {_num((1 - mae / persistencia) * 100)}% |"

    linhas += [
        f"### 🏁 Competição A × B: erro médio na validação, de {_data(c['janela_validacao'][0])} a "
        f"{_data(c['janela_validacao'][1])}",
        "",
        "| Modelo | MAE (°C) | Erra menos que a persistência |",
        "|:--|--:|--:|",
        *map(linha_modelo, papeis),
        f"| Persistência (amanhã = hoje) | {_num(persistencia, 3)} | referência |",
        "",
    ]

    motivo = f"_{d['motivo'][0].upper()}{d['motivo'][1:]}._"
    if d["mae_vigente"] is None:
        linhas += [f"### 🆕 Promoção: o {d['vencedor']} virou o primeiro modelo vigente", "", motivo, ""]
    else:
        linhas += [
            f"### {'🆕' if promovido else '📌'} Promoção: modelo {d['decisao']}",
            "",
            "| | MAE na mesma janela (°C) |",
            "|:--|--:|",
            f"| Modelo vigente | {_num(d['mae_vigente'], 3)} |",
            f"| Vencedor desta execução ({d['vencedor']} · "
            f"{NOMES.get(d['algoritmo_vencedor'], d['algoritmo_vencedor'])}) | {_num(d['mae_vencedor'], 3)} |",
            f"| **Melhora** (o limiar é {_num(d['limiar_melhoria'] * 100, 0)}%) | "
            f"**{_num((1 - d['mae_vencedor'] / d['mae_vigente']) * 100)}%** |",
            "",
            motivo,
            "",
        ]

    def linha_previsao(r, destaque):
        dia, previsto = _data(r["data_alvo"]), f"{_num(float(r['previsto']))} °C"
        if destaque:
            dia, previsto = f"**{dia}**", f"**{previsto}**"
        if not r["real"]:
            return f"| {dia} | {previsto} | aguardando | |"
        erro = float(r["erro"])
        return f"| {dia} | {previsto} | {_num(float(r['real']))} °C | {'+' if erro > 0 else ''}{_num(erro)} °C |"

    linhas += [
        "### 🔮 Previsões do modelo vigente",
        "",
        "| Dia | Previsto | Real | Erro |",
        "|:--|--:|--:|--:|",
        *[linha_previsao(r, i == 0) for i, r in enumerate(reversed(previsoes[-4:]))],
        "",
        f"O valor real chega com uns 7 dias de atraso. No teste (últimos {p['dias_teste']} dias) o vigente errou "
        f"{_num(p['mae_teste'], 2)} °C em média, contra {_num(p['mae_persistencia_teste'], 2)} °C da persistência.",
        "",
    ]

    psis = _ler_csv(pasta(estado) / "monitoramento.csv")
    pior = max(psis, key=lambda r: float(r["psi_sazonal"]))["feature"] if psis else "?"
    limites = cfg["monitoramento"]
    linhas += [
        f"### {'🔴' if m['alerta'] else '🟢'} Drift: {'alerta' if m['alerta'] else 'sem alerta'}",
        "",
        "| Sinal | Valor | Alarme acima de |",
        "|:--|--:|--:|",
        f"| Maior PSI sazonal (`{pior}`) | {_num(m['psi_sazonal_max'], 2)} | {_num(limites['limiar_psi'])} |",
        f"| Erro do último mês ÷ mesmas datas do ano anterior | {_num(m['razao_mae'], 2)} | "
        f"{_num(limites['limiar_razao_mae'])} |",
        "",
        *([*(f"- {motivo}" for motivo in m["motivos"]), "", "O workflow abre uma issue com o alerta no repositório.", ""]
          if m["alerta"] else []),
    ]

    repo = os.environ.get("GITHUB_REPOSITORY")
    caminho = f"evidencias/ciclos/{estado['cycle_id']}/"
    runs = {"votação": estado["votacao"]["run_id"], "A": c["A"]["run_id"], "B": c["B"]["run_id"],
            "decisão": d["run_id"], "previsões": p["run_id"], "monitoramento": m["run_id"]}
    linhas += [
        "<details><summary>🔎 Rastreabilidade</summary>",
        "",
        f"- **Versão dos dados:** `{estado['data_version']}` ({_int(dados['linhas'])} dias, de {_data(dados['inicio'])} "
        f"a {_data(dados['fim'])})",
        f"- **Janelas:** treino de {_data(jan['treino'][0])} a {_data(jan['treino'][1])} · validação de "
        f"{_data(jan['validacao'][0])} a {_data(jan['validacao'][1])} · teste de {_data(jan['teste'][0])} a "
        f"{_data(jan['teste'][1])}",
        "- **Runs no MLflow:** " + " · ".join(f"{nome} `{run_id[:8]}`" for nome, run_id in runs.items()),
        f"- **Evidências:** " + (f"[`{caminho}`](https://github.com/{repo}/tree/main/{caminho})" if repo else f"`{caminho}`"),
        "",
        "</details>",
        "",
        rodape,
        "",
    ]
    return "\n".join(linhas)
