"""Gera reports/relatorio_n3.pdf a partir das evidências que o workflow commitou.

Uso, na raiz do projeto e depois de um git pull: python reports/gerar_relatorio.py
Precisa do Google Chrome (para imprimir o PDF) e do gh autenticado (tabela de execuções).
"""
import json
import os
import re
import subprocess
import sys
import tempfile
from io import StringIO
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from src import ciclo, ingestao, preprocessamento  # noqa: E402

CHROME = os.environ.get("CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
REPO = "https://github.com/zanelladev/n3-mlops-temperatura-jaragua"
INTEGRANTES = ["André Ramos da Silva", "Artur Felippe Zanella", "Felipe Bogo",
               "Jeison Diniz de Souza Marinho", "Thierry Augusto Busnardo"]
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto",
         "setembro", "outubro", "novembro", "dezembro"]
plt.rcParams.update({"font.family": "Arial", "font.size": 9, "svg.fonttype": "path",
                     "axes.spines.top": False, "axes.spines.right": False})


def br(x, casas=2):
    return f"{x:,.{casas}f}".replace(",", "#").replace(".", ",").replace("#", ".")


def dbr(data):
    return pd.Timestamp(data).strftime("%d/%m/%Y")


def svg(fig):
    buf = StringIO()
    fig.savefig(buf, format="svg", bbox_inches="tight")
    plt.close(fig)
    texto = buf.getvalue()
    return texto[texto.index("<svg"):]


def html_tabela(df, classe=""):
    return df.to_html(index=False, border=0, classes=classe, escape=False, na_rep="")


def execucoes_github():
    try:
        saida = subprocess.run(["gh", "run", "list", "--workflow", "pipeline_mlops.yml", "--limit", "300", "--json",
                                "databaseId,event,conclusion,status,createdAt,url"],
                               cwd=RAIZ, capture_output=True, text=True, check=True).stdout
        return pd.DataFrame(json.loads(saida))
    except (OSError, subprocess.CalledProcessError):
        return pd.DataFrame()


# ---------------------------------------------------------------- dados das evidências
cfg = ciclo.carregar_config()
hist = ciclo.historico()
hist = hist[hist["monitoramento.alerta"].notna()].reset_index(drop=True)   # só ciclos completos
if hist.empty:
    sys.exit("nenhum ciclo completo em evidencias/ciclos: rode o workflow e faça git pull")
ultimo = hist.iloc[-1]
pasta = ciclo.EVIDENCIAS / "ciclos" / ultimo["cycle_id"]
votos = pd.read_csv(pasta / "votos.csv", index_col="feature")
diag = pd.read_csv(pasta / "diagnostico.csv", header=[0, 1], index_col=0)
teste = pd.read_csv(pasta / "previsoes_teste.csv", parse_dates=["data_alvo", "data_base"])
psis = pd.read_csv(pasta / "monitoramento.csv", index_col="feature")
backtest = pd.read_csv(pasta / "backtest_drift.csv", index_col=0, parse_dates=True) \
    if (pasta / "backtest_drift.csv").exists() else None
diarias = pd.read_csv(ciclo.EVIDENCIAS / "previsoes_diarias.csv", parse_dates=["data_alvo", "data_base"])
manifesto = json.loads(ciclo.MANIFESTO.read_text(encoding="utf-8"))
estado = json.loads((pasta / "ciclo.json").read_text(encoding="utf-8"))
mlflow = ciclo.configurar_mlflow(cfg)
runs_mlflow = mlflow.search_runs()
gh = execucoes_github()

av, vt, pr, mon = cfg["avaliacao"], cfg["votacao"], cfg["promocao"], cfg["monitoramento"]
jan = estado["janelas"]
comp = estado["competicao"]
n_ciclos = len(hist)
n_agendados = int((hist["evento"] == "schedule").sum())

# ---------------------------------------------------------------- figuras
serie = preprocessamento.limpar(ingestao.carregar_bruto()).set_index("data")["tmax"]
serie = serie.loc[: estado["dados"]["fim"]]
fig, ax = plt.subplots(figsize=(7.2, 2.3))
serie.iloc[-3 * 365:].plot(ax=ax, color="0.55", lw=0.7, label="máxima diária")
for nome, cor, rotulo in [("validacao", "tab:orange", "validação"), ("teste", "tab:red", "teste")]:
    ax.axvspan(pd.Timestamp(jan[nome][0]), pd.Timestamp(jan[nome][1]), color=cor, alpha=0.18, label=rotulo)
ax.set_ylabel("°C")
ax.set_xlabel("")
ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%Y"))
ax.legend(loc="lower left", bbox_to_anchor=(0, 1), ncols=3, frameon=False)
fig_janelas = svg(fig)

fig, ax = plt.subplots(figsize=(7.2, 2.4))
ax.plot(teste.data_alvo, teste.real, "k-o", ms=2.5, lw=1, label="real")
ax.plot(teste.data_alvo, teste.previsto, "-o", color="tab:blue", ms=2.5, lw=1,
        label=f"vigente (MAE {br(estado['previsoes']['mae_teste'])} °C)")
ax.plot(teste.data_alvo, teste.persistencia, "--", color="0.6", lw=0.9,
        label=f"persistência (MAE {br(estado['previsoes']['mae_persistencia_teste'])} °C)")
ax.set_ylabel("máxima (°C)")
ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=8))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
ax.legend(loc="lower left", bbox_to_anchor=(0, 1), ncols=3, frameon=False)
fig_teste = svg(fig)

fig_backtest = ""
if backtest is not None:
    fig, ax = plt.subplots(figsize=(7.2, 2.3))
    ax.plot(backtest.index, backtest.psi_anual, color="0.65", lw=0.9, label="referência: ano todo")
    ax.plot(backtest.index, backtest.psi_sazonal, color="tab:blue", lw=1.1, label="referência: mesma época")
    ax.axhline(mon["limiar_psi"], color="tab:red", ls="--", lw=0.9, label=f"limiar {br(mon['limiar_psi'], 1)}")
    ax.set_ylabel("maior PSI da janela")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1), ncols=3, frameon=False)
    fig_backtest = (f'<div class="figura">{svg(fig)}</div><p class="legenda">Figura 4. Backtest do alerta: maior PSI '
                    'de cada janela de 30 dias do treino do vigente, com as duas referências.</p>')


def diagrama():
    """Fluxo único desenhado à mão em SVG."""
    passos = ["GitHub Actions: schedule (todo dia, 08:17) ou workflow_dispatch",
              "checkout: código + estado do último ciclo (data/raw, mlflow.db, manifesto)",
              "01_etl: dias novos da API, ETL, atributos, cycle_id e data_version",
              "02_votacao_features: SelectKBest, Random Forest e RFE, votação",
              "03_treino_competicao: Ridge (A) x HistGradientBoosting (B)",
              "04_selecao_promocao: vencedor do ciclo x modelo vigente",
              "05_previsoes: teste final, dia seguinte e teste integrado",
              "06_monitoramento: drift sazonal e de desempenho",
              "commit do estado no repositório + artifact + issue se houver alerta"]
    x, w, h, passo = 150, 330, 26, 38
    partes = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 650 352" width="100%" font-family="Arial" font-size="10">',
              '<defs><marker id="seta" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">'
              '<path d="M0,0 L10,5 L0,10 z" fill="#555"/></marker></defs>']
    for i, texto in enumerate(passos):
        y = 4 + i * passo
        cor = "#eaf1fb" if 2 <= i <= 7 else "#f2f2f2"
        partes.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{cor}" stroke="#8a8a8a"/>')
        partes.append(f'<text x="{x + w / 2}" y="{y + 16.5}" text-anchor="middle">{texto}</text>')
        if i < len(passos) - 1:
            partes.append(f'<line x1="{x + w / 2}" y1="{y + h}" x2="{x + w / 2}" y2="{y + passo - 1}" stroke="#555" marker-end="url(#seta)"/>')

    def lateral(xl, y0, y1, titulo, sub):
        partes.append(f'<rect x="{xl}" y="{y0}" width="140" height="{y1 - y0}" rx="4" fill="#fff8e6" stroke="#c9a227"/>')
        partes.append(f'<text x="{xl + 70}" y="{(y0 + y1) / 2 - 2}" text-anchor="middle" font-weight="bold">{titulo}</text>')
        partes.append(f'<text x="{xl + 70}" y="{(y0 + y1) / 2 + 11}" text-anchor="middle">{sub}</text>')

    lateral(505, 4 + 2 * passo - 4, 4 + 2 * passo + h + 4, "Open-Meteo", "ERA5-Seamless")
    lateral(505, 4 + 3 * passo, 4 + 7 * passo + h, "MLflow", "mlflow.db + mlartefatos")
    lateral(0, 4 + 5 * passo - 4, 4 + 6 * passo + h + 4, "modelo_vigente.json", "manifesto")
    for i in (2,):
        partes.append(f'<line x1="505" y1="{4 + i * passo + h / 2}" x2="{x + w + 2}" y2="{4 + i * passo + h / 2}" stroke="#c9a227" marker-end="url(#seta)"/>')
    for i in range(3, 8):
        partes.append(f'<line x1="{x + w}" y1="{4 + i * passo + h / 2}" x2="503" y2="{4 + i * passo + h / 2}" stroke="#c9a227" marker-end="url(#seta)"/>')
    for i in (5, 6):
        partes.append(f'<line x1="140" y1="{4 + i * passo + h / 2}" x2="{x - 2}" y2="{4 + i * passo + h / 2}" stroke="#c9a227"/>')
    # o commit de hoje é o checkout de amanhã
    yc, yk = 4 + 8 * passo + h / 2, 4 + passo + h / 2
    partes.append(f'<path d="M{x},{yc} L{x - 128},{yc} L{x - 128},{yk} L{x - 2},{yk}" fill="none" stroke="#555" stroke-dasharray="4 3" marker-end="url(#seta)"/>')
    partes.append(f'<text x="{x - 124}" y="{yk + 16}" font-size="9">próximo ciclo</text>')
    partes.append('</svg>')
    return "".join(partes)


# ---------------------------------------------------------------- tabelas
nomes_var = {"tmax": "temperatura máxima", "tmin": "temperatura mínima", "tmed": "temperatura média",
             "umidade": "umidade relativa média", "orvalho": "ponto de orvalho médio",
             "pressao": "pressão média ao nível do mar", "nuvens": "nebulosidade média",
             "vento_max": "vento máximo", "vento_med": "vento médio", "rajada": "rajada máxima",
             "vento_dir": "direção dominante do vento", "chuva": "chuva acumulada", "radiacao": "radiação solar"}

rotulos_diag = {"ausentes": "ausentes", "fora_da_faixa": "fora da faixa", "outliers_z5": "outliers (z > 5)"}
tab_diag = diag.astype(int)
tab_diag.columns = pd.MultiIndex.from_tuples([(a, rotulos_diag[b]) for a, b in tab_diag.columns])
tab_diag.insert(0, ("", "variável"), "<code>" + tab_diag.index + "</code>")
outliers = diag[("antes", "outliers_z5")].sort_values(ascending=False)
mais_outliers = [f"<code>{c}</code> ({br(n, 0)})" for c, n in outliers.items() if n > 0][:4]

tv = votos.reset_index()
marca = {True: "•", False: ""}
tab_votos = pd.DataFrame({
    "feature": "<code>" + tv["feature"] + "</code>",
    "rank F": tv["rank_kbest"].astype(int), "rank RF": tv["rank_rf"].astype(int), "rank RFE": tv["rank_rfe"].astype(int),
    "voto F": tv["voto_kbest"].map(marca), "voto RF": tv["voto_rf"].map(marca), "voto RFE": tv["voto_rfe"].map(marca),
    "votos": tv["votos"], "ranking médio": tv["ranking_medio"].map(lambda v: br(v, 1)),
    "eleita": tv["eleita"].map({True: "<b>sim</b>", False: ""})})

linhas_comp = []
for papel in ("A", "B"):
    r = comp[papel]
    linhas_comp.append({"modelo": f"{papel}: {r['algoritmo']}", "MAE (°C)": br(r["validacao"]["mae"], 3),
                        "RMSE (°C)": br(r["validacao"]["rmse"], 3), "R²": br(r["validacao"]["r2"], 3)})
linhas_comp.append({"modelo": "persistência (amanhã = hoje)", "MAE (°C)": br(comp["persistencia"]["mae"], 3),
                    "RMSE (°C)": br(comp["persistencia"]["rmse"], 3), "R²": br(comp["persistencia"]["r2"], 3)})
tab_comp = pd.DataFrame(linhas_comp)

evento_br = {"schedule": "agendado", "workflow_dispatch": "manual", "local": "local"}
tab_hist = pd.DataFrame({
    "cycle_id": hist["cycle_id"], "gatilho": hist["evento"].map(evento_br),
    "dados até": hist["dados.fim"].map(dbr), "dias novos": hist["lote.n_novos"].map(lambda v: br(v, 0)),
    "feat.": hist["votacao.n"],
    "MAE A": hist["competicao.A.validacao.mae"].map(lambda v: br(v, 3)),
    "MAE B": hist["competicao.B.validacao.mae"].map(lambda v: br(v, 3)),
    "venc.": hist["decisao.vencedor"],
    "MAE vig.": hist["decisao.mae_vigente"].map(lambda v: "" if pd.isna(v) else br(v, 3)),
    "decisão": hist["decisao.decisao"],
    "MAE teste": hist["previsoes.mae_teste"].map(lambda v: br(v, 3)),
    "alerta": hist["monitoramento.alerta"].map({True: "sim", False: "não"})})

tab_gh = pd.DataFrame()
if not gh.empty:
    ciclo_por_run = dict(zip(hist["github_run_id"].astype(str), hist["cycle_id"]))
    decisao_por_run = dict(zip(hist["github_run_id"].astype(str), hist["decisao.decisao"]))
    gh = gh.sort_values("createdAt")
    resultado = []
    for _, r in gh.iterrows():
        rid = str(r["databaseId"])
        if r["status"] != "completed":
            resultado.append("em andamento")
        elif r["conclusion"] != "success":
            resultado.append(f"falhou ({r['conclusion']})")
        elif rid in ciclo_por_run:
            resultado.append(f"ciclo {ciclo_por_run[rid]}: {decisao_por_run[rid]}")
        else:
            resultado.append("sem dados novos, encerrado após o 01")
    tab_gh = pd.DataFrame({
        "início (Brasília)": pd.to_datetime(gh["createdAt"]).dt.tz_convert("America/Sao_Paulo").dt.strftime("%d/%m/%Y %H:%M"),
        "gatilho": gh["event"],
        "run": [f'<a href="{u}">{i}</a>' for u, i in zip(gh["url"], gh["databaseId"])],
        "resultado": resultado})
n_runs_schedule = int((gh["event"] == "schedule").sum()) if not gh.empty else 0

tab_diarias = diarias.assign(
    **{"data prevista": diarias["data_alvo"].map(dbr), "dados até": diarias["data_base"].map(dbr),
       "previsto (°C)": diarias["previsto"].map(lambda v: br(v, 1)),
       "real (°C)": diarias["real"].map(lambda v: "" if pd.isna(v) else br(v, 1)),
       "erro (°C)": diarias["erro"].map(lambda v: "aguardando" if pd.isna(v) else br(v, 1))}
)[["data prevista", "dados até", "previsto (°C)", "real (°C)", "erro (°C)", "cycle_id"]]
conferidas = diarias.dropna(subset=["real"])

tab_psi = psis.reset_index().assign(
    feature=lambda t: "<code>" + t["feature"] + "</code>",
    psi_anual=lambda t: t["psi_anual"].map(br), psi_sazonal=lambda t: t["psi_sazonal"].map(br)
).rename(columns={"psi_anual": "PSI contra o ano todo", "psi_sazonal": "PSI contra a mesma época"})

# ---------------------------------------------------------------- fatos para o texto
eleitas = estado["votacao"]["features"]
unanimes = votos.index[votos["votos"] == 3].tolist()
dois = votos.index[votos["votos"] == 2].tolist()
completou = len(eleitas) > len(unanimes) + len(dois)
lags_fora = [f for f in ("tmax_lag1", "tmax_lag2", "tmax_lag3") if f not in eleitas]
conjuntos = hist["votacao.features"].map(tuple)
mudancas_votacao = int((conjuntos != conjuntos.shift()).iloc[1:].sum())
a_mae, b_mae, p_mae = comp["A"]["validacao"]["mae"], comp["B"]["validacao"]["mae"], comp["persistencia"]["mae"]
melhor = min(a_mae, b_mae)
ganho_pers = 1 - melhor / p_mae
decisoes = hist["decisao.decisao"].value_counts()
promocoes = hist[hist["decisao.decisao"] == "promovido"]
vencedores = hist["decisao.vencedor"].value_counts()
taxa_anual, taxa_sazonal = estado["monitoramento"]["backtest_taxa_anual"], estado["monitoramento"]["backtest_taxa_sazonal"]
alertas = int(hist["monitoramento.alerta"].sum())
issues = []
try:
    saida = subprocess.run(["gh", "issue", "list", "--state", "all", "--json", "number,title,url,state,createdAt"],
                           cwd=RAIZ, capture_output=True, text=True, check=True).stdout
    issues = [i for i in json.loads(saida) if i["title"].startswith("Alerta de drift")]
except (OSError, subprocess.CalledProcessError):
    pass
runs_por_ciclo = runs_mlflow.groupby("tags.cycle_id").size()
hoje = pd.Timestamp.now(tz="America/Sao_Paulo")

if n_runs_schedule:
    agendadas = gh[gh["event"] == "schedule"]
    primeira = dbr(pd.to_datetime(agendadas["createdAt"]).min().tz_convert("America/Sao_Paulo"))  # gh lista da mais nova
    sem_dia_novo = (" As que não encontraram dia novo terminaram depois do notebook 01, como previsto."
                    if n_runs_schedule > n_agendados else "")
    if n_runs_schedule == 1:
        texto_schedule = (f"Até agora houve 1 execução disparada pelo próprio schedule, em {primeira}, e ela "
                          + ("trouxe dia novo e fechou um ciclo completo." if n_agendados else
                             "não encontrou dia novo e terminou depois do notebook 01, como previsto."))
    else:
        fechados = ("nenhuma delas trouxe dia novo" if n_agendados == 0 else
                    "1 delas trouxe dia novo e fechou um ciclo completo" if n_agendados == 1 else
                    f"{n_agendados} delas trouxeram dia novo e fecharam um ciclo completo")
        texto_schedule = (f"Até agora foram {n_runs_schedule} execuções disparadas pelo próprio schedule, a primeira em "
                          f"{primeira}, e {fechados}.{sem_dia_novo}")
else:
    texto_schedule = ("O schedule já está ativo no repositório, mas ainda não houve execução agendada até a geração "
                      "desta versão do relatório. As execuções abaixo foram disparadas manualmente.")

texto_votacao_extra = ""
if lags_fora:
    votantes = {m for m, col in (("F-score", "voto_kbest"), ("Random Forest", "voto_rf"), ("RFE", "voto_rfe"))
                if votos.loc[lags_fora, col].any()}
    texto_votacao_extra = (f" Um resultado que chamou atenção: {', '.join(f'<code>{x}</code>' for x in lags_fora)} "
                           "ficaram de fora. A informação dos dias anteriores já aparece em <code>tmed</code>, "
                           "<code>tmax</code> e <code>tmin</code> do próprio dia, e os métodos que olham os atributos "
                           "em conjunto preferem ficar com uma dessas variáveis em vez de várias quase iguais.")
    if votantes == {"F-score"}:
        texto_votacao_extra += " Só o F-score, que avalia uma variável de cada vez, chegou a votar em algum lag."

texto_mudancas = (f"nos {n_ciclos} ciclos o conjunto eleito foi sempre o mesmo" if mudancas_votacao == 0
                  else f"nos {n_ciclos} ciclos o conjunto eleito mudou {mudancas_votacao} vez(es)")
texto_vencedores = "; ".join(f"o modelo {p} venceu em {n} de {n_ciclos} ciclos" for p, n in vencedores.items())

if decisoes.get("promovido", 0) == 1 and hist["decisao.decisao"].iloc[0] == "promovido":
    texto_decisoes = (f"Nos {n_ciclos} ciclos completos houve uma promoção, no primeiro ciclo (quando ainda não existia "
                      f"modelo vigente), e o vigente foi mantido nos outros {decisoes.get('mantido', 0)}.")
else:
    texto_decisoes = (f"Nos {n_ciclos} ciclos completos houve {decisoes.get('promovido', 0)} promoção(ões) e "
                      f"{decisoes.get('mantido', 0)} manutenção(ões) do vigente.")

ultima = manifesto["ultima_decisao"]
texto_ultima = (f"No último ciclo ({ultima['cycle_id']}) o vencedor foi o modelo {ultima['vencedor']} "
                f"({ultima['algoritmo_vencedor']}), com MAE de {br(ultima['mae_vencedor'], 3)} °C na validação")
if ultima["mae_vigente"] is not None:
    melhoria = (ultima["mae_vigente"] - ultima["mae_vencedor"]) / ultima["mae_vigente"]
    texto_ultima += (f", contra {br(ultima['mae_vigente'], 3)} °C do vigente na mesma janela, uma melhora de "
                     f"{br(melhoria * 100, 1)}% para um limiar de {br(pr['limiar_melhoria'] * 100, 0)}%. "
                     f"Decisão automática: <b>{ultima['decisao']}</b>.")
else:
    texto_ultima += f". Decisão automática: <b>{ultima['decisao']}</b> ({ultima['motivo']})."

texto_diarias = ""
if len(conferidas):
    texto_diarias = (f" Das {len(diarias)} previsões registradas até aqui, {len(conferidas)} já foram conferidas com o "
                     f"dado real, com erro absoluto médio de {br(conferidas['erro'].abs().mean(), 2)} °C.")

texto_alertas = (f"Nos {n_ciclos} ciclos não houve alerta." if alertas == 0
                 else f"Nos {n_ciclos} ciclos houve {alertas} alerta(s).")
texto_issue = ""
if issues:
    itens = ", ".join(f'<a href="{i["url"]}">#{i["number"]} ({i["title"]})</a>' for i in issues)
    texto_issue = (f" O canal de alerta foi testado de ponta a ponta com o input <code>testar_alerta</code> do "
                   f"workflow_dispatch, que abriu a issue {itens} pelo próprio GitHub Actions.")

# ---------------------------------------------------------------- HTML
CSS = """
@page { size: A4; margin: 2.5cm 2cm 2.2cm 2.5cm; @bottom-right { content: counter(page); font: 10pt Arial; } }
@page :first { @bottom-right { content: none; } }
body { font-family: Arial, sans-serif; font-size: 12pt; line-height: 1.45; color: #111; hyphens: auto; text-align: justify; }
h1 { font-size: 15pt; margin: 0 0 4pt; text-align: left; }
h2 { font-size: 13pt; margin: 18pt 0 6pt; break-after: avoid; text-align: left; }
h3 { font-size: 12pt; margin: 12pt 0 4pt; break-after: avoid; }
p { margin: 0 0 8pt; }
ul { margin: 0 0 8pt; padding-left: 18pt; }
li { margin-bottom: 3pt; }
code { font-family: Arial, sans-serif; font-size: 11pt; background: #f1f1f1; padding: 0 2pt; hyphens: none; }
table { border-collapse: collapse; width: 100%; font-size: 10pt; margin: 4pt 0 4pt; text-align: left; break-inside: auto; hyphens: none; }
table.historico { font-size: 9pt; }
table.historico td { white-space: nowrap; padding: 2.5pt 3pt; }
th[colspan] { text-align: center; }
tr { break-inside: avoid; }
th { border-bottom: 1.2pt solid #333; padding: 3pt 4pt; text-align: left; vertical-align: bottom; }
td { border-bottom: 0.5pt solid #ccc; padding: 2.5pt 4pt; vertical-align: top; }
td code { font-size: 9.5pt; }
.bloco { break-inside: avoid; }
.legenda { font-size: 10pt; color: #333; margin: 2pt 0 12pt; text-align: left; }
.figura { margin: 6pt 0 0; break-inside: avoid; }
.figura svg { width: 100%; height: auto; }
.capa { height: 24cm; display: flex; flex-direction: column; justify-content: space-between; text-align: center; }
.capa .topo { font-size: 13pt; line-height: 1.6; }
.capa .titulo { font-size: 18pt; font-weight: bold; line-height: 1.35; }
.capa .sub { font-size: 13pt; margin-top: 10pt; }
.capa .nomes { font-size: 12pt; line-height: 1.7; }
.quebra { break-before: page; }
a { color: #0b4f9c; text-decoration: none; }
"""

paginas = f"""
<section class="capa">
  <div class="topo">Católica de Santa Catarina<br>Análise Preditiva<br>Prof. M. Sc. Rodrigo Hagstrom</div>
  <div>
    <div class="titulo">Trabalho Avaliativo N3<br>Pipeline MLOps para prever a temperatura máxima<br>do dia seguinte em Jaraguá do Sul</div>
    <div class="sub">Relatório técnico</div>
  </div>
  <div class="nomes">{'<br>'.join(INTEGRANTES)}</div>
  <div class="topo">Repositório: <a href="{REPO}">{REPO.replace('https://', '')}</a><br>
  Jaraguá do Sul, {MESES[hoje.month - 1]} de {hoje.year}</div>
</section>

<section class="quebra">
<h1>Visão geral</h1>
<p>Este relatório descreve o projeto que fizemos para a N3: um pipeline de MLOps que, todo dia, busca dados novos de
clima, escolhe as features por votação de três métodos, coloca dois algoritmos para competir e decide sozinho se o
modelo em produção deve ser trocado. O problema é prever a temperatura máxima do dia seguinte em Jaraguá do Sul.
Escolhemos clima porque a fonte é real, gratuita e muda todo dia, então a ingestão e o versionamento dos dados
acontecem de verdade, sem simulação. Até a geração deste relatório ({dbr(hoje)}) o workflow fechou {n_ciclos} ciclos
completos, o último com dados até {dbr(estado['dados']['fim'])}. Todos os números abaixo saem das evidências que o
próprio workflow grava no repositório, e o script <code>reports/gerar_relatorio.py</code> refaz este PDF a partir delas.</p>

<h2>Problema e dados</h2>
<p><b>Problema.</b> Regressão. A variável-alvo é a temperatura máxima do dia t+1, em °C, e a unidade de observação é
um dia em Jaraguá do Sul. Tudo o que o modelo usa é conhecido até o fim do dia t.</p>
<p><b>Fonte e licença.</b> Historical Weather API do Open-Meteo, com a reanálise ERA5-Seamless (combinação do ERA5 e do
ERA5-Land, do Copernicus/ECMWF). A API é gratuita, não pede chave, e os dados são distribuídos sob a licença CC BY 4.0,
que permite o uso com atribuição ("Weather data by Open-Meteo.com"). Usamos o ponto de grade mais próximo de Jaraguá
do Sul (-26,49; -49,07), com a série diária desde 01/01/2010 agregada no fuso de São Paulo. No último ciclo a base tinha
{br(estado['dados']['linhas'], 0)} dias, de {dbr(estado['dados']['inicio'])} a {dbr(estado['dados']['fim'])}, em
{len(estado['dados']['lotes'])} lotes.</p>
<p><b>Atributos de origem.</b> Treze variáveis diárias: {', '.join(nomes_var.values())}. Sobre elas construímos os
atributos da seção de ETL, chegando a {len(votos)} candidatas.</p>
<p><b>Limitações dos dados.</b> Reanálise não é estação meteorológica: é um modelo que assimila observações numa grade
de 9 a 25 km, então suaviza os extremos locais. O ERA5 chega com cerca de 7 dias de atraso. Para a previsão sair para o
dia da execução, buscamos os dias que ainda faltam na API de previsão do Open-Meteo, como dado provisório; eles montam só
a linha da previsão e não entram no treino, na validação, no teste nem no monitoramento. Medimos o custo disso em
09/11/2026: nos 46 dias de 16/09 a 31/10/2026, o vigente errou 2,78 °C com o dado provisório na entrada, contra 2,48 °C
com o ERA5 e 3,03 °C da persistência. É uma série de um ponto só, e os dias mais
recentes do ERA5 podem ser levemente revisados depois; guardamos o valor da primeira consulta para manter cada versão
reproduzível.</p>

<h2>Métrica e desenho da avaliação</h2>
<p><b>Métrica principal.</b> MAE em °C, a minimizar, fixada no <code>config.yaml</code> antes do primeiro treino. Ela
está na unidade do problema, não deixa poucos dias atípicos dominarem a comparação como o RMSE faria, e é fácil de
comparar com a referência ingênua da persistência (a máxima de amanhã igual à de hoje). RMSE e R² são registrados como
apoio.</p>
<p><b>Particionamento.</b> Como é série temporal, nada é embaralhado. Com os dias em ordem: treino, depois a validação
com os {av['validacao_dias']} dias seguintes e por fim o teste com os {av['teste_dias']} dias mais recentes. A validação
tem um ano inteiro para que a comparação entre modelos passe por todas as estações. No último ciclo as janelas foram:
treino de {dbr(jan['treino'][0])} a {dbr(jan['treino'][1])} ({br(jan['treino'][2], 0)} dias), validação de
{dbr(jan['validacao'][0])} a {dbr(jan['validacao'][1])} e teste de {dbr(jan['teste'][0])} a {dbr(jan['teste'][1])}.
Votação, escolha entre A e B e promoção usam só treino e validação; o teste fica reservado para a avaliação final do
modelo vigente.</p>
<p><b>Chegada de novos registros.</b> Cada execução pergunta à API pelos dias depois do último que já está em
<code>data/raw</code> e grava o que vier num arquivo novo, <code>lote_&lt;inicio&gt;_&lt;fim&gt;.csv</code>. Como as janelas
são contadas a partir do fim da série, um dia novo entra no teste e empurra um dia da validação para o treino.</p>
<p><b>Por que o vigente nunca é retreinado com validação e teste.</b> O modelo promovido é exatamente o que foi
avaliado, treinado só com a janela de treino. Assim ele nunca viu os dias de validação dos ciclos seguintes (as
janelas só andam para frente), e a comparação com cada novo desafiante é justa. O notebook 04 confere isso e para o
pipeline se não for verdade. O custo é o modelo não aprender com os últimos 13 meses, o que pesa pouco diante de
15 anos de histórico.</p>
<div class="figura">{fig_janelas}</div>
<p class="legenda">Figura 1. Máxima diária nos últimos três anos da série, com as janelas de validação e teste do último ciclo.</p>

<h2>ETL e engenharia de atributos</h2>
<p>O notebook 01 junta os lotes, faz o diagnóstico, trata, valida e monta os atributos. O diagnóstico procura ausentes,
datas duplicadas, dias faltando no calendário, valores fora de uma faixa física plausível para a região (por exemplo,
umidade fora de 0 a 100% ou pressão fora de 950 a 1050 hPa), mínima maior que a máxima e outliers por z robusto acima
de 5. A Tabela 1 mostra o diagnóstico do último ciclo, antes e depois dos tratamentos.</p>
<div class="bloco"><p class="legenda">Tabela 1. Diagnóstico por variável, antes e depois da limpeza (último ciclo).</p>
{html_tabela(tab_diag)}</div>
<p style="margin-top:8pt">Resumo geral antes da limpeza: {br(estado['diagnostico']['antes']['linhas'], 0)} linhas,
{estado['diagnostico']['antes']['datas_duplicadas']} datas duplicadas, {estado['diagnostico']['antes']['dias_faltando']}
dias faltando e {estado['diagnostico']['antes']['tmin_maior_que_tmax']} casos de mínima maior que a máxima. A reanálise
vem limpa; o que o diagnóstico mais acusa são outliers pelo z robusto, principalmente em {', '.join(mais_outliers)}.
São variáveis assimétricas (a maioria dos dias tem pouca ou nenhuma chuva), então os valores altos são dias de chuva
forte ou de vento forte de verdade, e ficam na base. Os tratamentos, todos no código e não à mão, são:</p>
<ul>
<li><b>Data repetida:</b> fica a versão do lote mais novo, então reprocessar um lote nunca duplica dias.</li>
<li><b>Dia faltando:</b> vira uma linha vazia, para os lags e as médias móveis sempre olharem para o dia anterior de verdade.</li>
<li><b>Valor fisicamente impossível ou mínima maior que a máxima:</b> vira ausente. A imputação pela mediana acontece
dentro do Pipeline, ajustada só com o treino, junto com a padronização. Nada é ajustado com validação ou teste.</li>
<li><b>Outlier:</b> só sinalizado. Em clima, uma onda de calor ou uma frente fria forte são dados reais, e são justamente
os dias difíceis de prever.</li>
</ul>
<p>Depois dos tratamentos uma validação para o pipeline se faltar coluna, se sobrar data repetida ou buraco no
calendário, ou se mais de 1% do alvo estiver ausente. Os atributos construídos olham só para trás:</p>
<ul>
<li><code>tmax_lag1</code> a <code>tmax_lag3</code>, <code>tmax_media3</code> e <code>tmax_media7</code>: a temperatura tem muita inércia.</li>
<li><code>tmax_delta</code> e <code>amplitude</code>: se esquentou ou esfriou de ontem para hoje, e a diferença entre máxima e mínima (grande em dia de céu aberto).</li>
<li><code>pressao_delta</code>, <code>umidade_delta</code> e <code>chuva_3d</code>: pressão caindo e umidade subindo costumam anunciar frente fria e chuva.</li>
<li><code>vento_dir_sin</code> e <code>vento_dir_cos</code>: direção do vento é circular (350° fica perto de 10°); vento de norte esquenta, vento de sul esfria.</li>
<li><code>dia_ano_sin</code> e <code>dia_ano_cos</code>: a época do ano, sem o salto entre 31/12 e 01/01.</li>
</ul>
<p><b>Versão dos dados.</b> O <code>data_version</code> é o último dia da série mais o início do sha256 dos arquivos de
<code>data/raw</code>, por exemplo <code>{estado['data_version']}</code>. Mesmo dado gera a mesma versão; qualquer dia novo
gera outra. Conferimos isso rodando os mesmos dois primeiros ciclos na nossa máquina e no runner do GitHub: os
<code>data_version</code> saíram idênticos. O <code>ciclo.json</code> de cada ciclo lista os lotes que existiam naquele
momento.</p>

<h2>Seleção de features por votação</h2>
<p>O notebook 02 roda os três métodos no mesmo notebook, todos ajustados só com o treino: SelectKBest com
<code>f_regression</code> (teste F de cada atributo contra o alvo, adequado para alvo contínuo), importância do Random
Forest ({vt['rf_arvores']} árvores, pega relações não lineares) e RFE com Ridge (tira o atributo de menor coeficiente até
sobrarem k, então descarta os redundantes). Não usamos validação cruzada, então não existe seleção dentro de fold: a
validação e o teste simplesmente não entram nesta etapa.</p>
<p><b>Regra de votação, fixada no config antes de rodar:</b> cada método vota nas suas k = {vt['k']} melhores; é eleita a
feature com pelo menos {vt['votos_minimos']} dos 3 votos; se a maioria eleger menos de {vt['min_features']}, o conjunto é
completado pelo menor ranking médio dos três métodos, que também desempata a ordem. Escolhemos maioria porque um
atributo forte em só um método pode ser artefato daquele método (o F-score, por exemplo, gosta de todas as variáveis
de temperatura ao mesmo tempo, mesmo sendo quase cópias umas das outras).</p>
<div class="bloco"><p class="legenda">Tabela 2. Votação do último ciclo ({ultimo['cycle_id']}). Rank 1 é o melhor de cada método; F = SelectKBest, RF = Random Forest.</p>
{html_tabela(tab_votos, "votos")}</div>
<p style="margin-top:8pt">Foram eleitas {len(eleitas)} features: {', '.join(f'<code>{x}</code>' for x in eleitas)}.
{len(unanimes)} tiveram os três votos e {len(dois)} tiveram dois{', e a regra de mínimo completou o conjunto' if completou else ', então a regra de mínimo não precisou entrar'}.{texto_votacao_extra}
A votação é refeita em todo ciclo, e {texto_mudancas}. Votos,
rankings, importâncias, parâmetros da regra e <code>cycle_id</code> ficam no run <code>votacao</code> do MLflow.</p>

<h2>Competição entre os dois modelos</h2>
<p>O notebook 03 treina dois algoritmos distintos com as mesmas features eleitas, o mesmo treino, o mesmo Pipeline de
pré-processamento (imputação pela mediana e padronização) e a mesma semente ({cfg['projeto']['semente']}), e avalia os
dois na mesma janela de validação:</p>
<ul>
<li><b>Modelo A, Ridge</b> (alpha = {cfg['modelos']['A']['params']['alpha']}): regressão linear com penalização L2, simples e estável com atributos parecidos entre si.</li>
<li><b>Modelo B, HistGradientBoosting</b> ({cfg['modelos']['B']['params']['max_iter']} iterações, taxa
{br(cfg['modelos']['B']['params']['learning_rate'])}, até {cfg['modelos']['B']['params']['max_leaf_nodes']} folhas por árvore): árvores em
sequência, cada uma corrigindo o erro das anteriores, capaz de pegar efeitos não lineares como o da frente fria.</li>
</ul>
<div class="bloco"><p class="legenda">Tabela 3. Métricas na validação ({dbr(comp['janela_validacao'][0])} a {dbr(comp['janela_validacao'][1])}), último ciclo.</p>
{html_tabela(tab_comp)}</div>
<p style="margin-top:8pt">Os dois modelos erram bem menos que a persistência: o melhor tem MAE {br(ganho_pers * 100, 0)}%
menor. Entre os dois, a diferença é pequena ({br(abs(a_mae - b_mae), 3)} °C no último ciclo): {texto_vencedores}.
Para cada modelo o MLflow guarda hiperparâmetros, semente,
lista de features, janelas, métricas e o modelo serializado (o Pipeline inteiro, no formato skops), num run
identificado pelo mesmo <code>cycle_id</code> e <code>data_version</code> da votação.</p>

<h2>Eleição do vencedor e promoção</h2>
<p>O notebook 04 elege o vencedor do ciclo pelo menor MAE na validação (empate fica com A, o mais simples). Depois
carrega o modelo vigente pelo MLflow, a partir do manifesto <code>models/modelo_vigente.json</code>, e avalia esse modelo
na mesma janela de validação, com as features dele. A regra de promoção, definida antes no config, é: o desafiante
precisa errar menos que a persistência e ter MAE pelo menos {br(pr['limiar_melhoria'] * 100, 0)}% menor que o do vigente.
No primeiro ciclo, sem vigente, basta bater a persistência. O limiar existe para não trocar de modelo por diferenças
que são só ruído de um dia a mais de dados.</p>
<p>{texto_decisoes} {texto_ultima} A decisão, o motivo e as métricas ficam no run <code>decisao</code> do MLflow e no
manifesto. Quando há promoção, o vigente antigo vai para a lista <code>anteriores</code> do manifesto, e todos os
modelos continuam guardados no MLflow.</p>
<p>O vigente atual é o {manifesto['algoritmo']} promovido no ciclo {manifesto['cycle_id']} (dados
<code>{manifesto['data_version']}</code>), treinado até {dbr(manifesto['treino_ate'])}, com MAE de
{br(manifesto['valor_validacao'], 3)} °C na validação daquele ciclo e run_id <code>{manifesto['run_id']}</code>.</p>

<h2>Arquitetura do fluxo único</h2>
<div class="figura">{diagrama()}</div>
<p class="legenda">Figura 2. O único workflow (<code>.github/workflows/pipeline_mlops.yml</code>) e onde cada etapa lê e grava.</p>
<p>Há um só workflow (<i>Previsão da máxima diária</i>) e um só job, com os passos em sequência: obter o código e o
estado, instalar o <code>requirements.txt</code>, executar os notebooks 01 a 06, um por passo, com
<code>jupyter nbconvert --execute</code>, escrever o resumo da execução na página do run, salvar o estado, abrir a issue
de alerta se for o caso e publicar as evidências como artifact. Os gatilhos são o schedule
(<code>17 11 * * *</code>, 08:17 em Brasília) e o <code>workflow_dispatch</code> para depuração. O
<code>concurrency</code> impede duas execuções ao mesmo tempo.</p>
<p><b>Persistência entre execuções.</b> Como o runner é descartado, o estado vive no próprio repositório: no fim de cada
ciclo o workflow commita <code>data/raw</code>, <code>mlflow.db</code>, <code>mlartefatos/</code>, <code>models/</code> e
<code>evidencias/</code>, e a execução seguinte começa do checkout desse commit. O manifesto e o modelo vigente são
lidos dali, sem depender de arquivos do runner anterior. O mesmo pacote também é publicado como artifact baixável.</p>
<p><b>Falhas.</b> O shell do Actions roda com <code>-e</code>: se qualquer notebook der erro, o job para antes do commit,
nada é promovido e o vigente continua o mesmo. Se a API não tiver dia novo, o workflow encerra depois do notebook 01
sem treinar.</p>
<p><b>MLflow portátil.</b> O MLflow 3.18 não aceita mais o armazenamento em pasta (<code>./mlruns</code>), então usamos
SQLite (<code>mlflow.db</code>). Ele grava o caminho absoluto dos artefatos, o que quebraria o histórico ao sair do
runner. Na criação do experimento trocamos esse caminho por um relativo (<code>mlartefatos</code>), e com isso o mesmo
<code>mlflow.db</code> funciona no runner, na nossa máquina e na de quem clonar o repositório, inclusive com
<code>mlflow ui</code>.</p>

<h2>Evidências de execução</h2>
<p>{texto_schedule} A Tabela 4 lista as execuções do workflow e o que cada uma produziu. Os logs ficam na aba Actions
do repositório; os notebooks executados de cada ciclo ficam em <code>evidencias/ciclos/&lt;cycle_id&gt;/</code>, junto
com o <code>ciclo.json</code>, as tabelas e o resumo do ciclo; e cada ciclo termina com um commit do bot que diz o
gatilho, a data e a decisão.</p>
<div class="bloco"><p class="legenda">Tabela 4. Execuções do workflow <i>Previsão da máxima diária</i> no GitHub Actions.</p>
{html_tabela(tab_gh) if not tab_gh.empty else '<p>(gh indisponível ao gerar o relatório)</p>'}</div>
<div class="bloco"><p class="legenda" style="margin-top:10pt">Tabela 5. Histórico dos ciclos completos (MAE em °C; A, B e vigente na validação do ciclo, teste para o vigente).</p>
{html_tabela(tab_hist, "historico")}</div>
<p style="margin-top:8pt">O MLflow tem {len(runs_mlflow)} runs no experimento <code>{cfg['mlflow']['experimento']}</code>,
{int(runs_por_ciclo.median()) if len(runs_por_ciclo) else 0} por ciclo (votação, A, B, decisão, previsões e
monitoramento), todos com as tags <code>cycle_id</code>, <code>data_version</code>, <code>etapa</code> e
<code>evento</code>. Para consultar: <code>mlflow ui --backend-store-uri sqlite:///mlflow.db</code> na raiz do projeto e o
filtro <code>tags.cycle_id = '...'</code> ou <code>tags.etapa = 'treino'</code>.</p>

<h2>Previsões e teste integrado</h2>
<p>O notebook 05 carrega o vigente pelo MLflow. O objeto salvo é o Pipeline inteiro (imputação, padronização e modelo) e
a lista de features vem do manifesto, então a previsão usa exatamente o pré-processamento do treino. A avaliação final
é no teste, os {av['teste_dias']} dias mais recentes com alvo conhecido, que não entraram em nenhuma escolha do ciclo.
No último ciclo o vigente teve MAE de {br(estado['previsoes']['mae_teste'])} °C no teste, contra
{br(estado['previsoes']['mae_persistencia_teste'])} °C da persistência. Como o teste cobre só um mês, o MAE dele
oscila com o tempo que fez naquele mês: um mês com muitas mudanças bruscas de temperatura é mais difícil para qualquer
modelo, inclusive para a persistência. Pelo mesmo motivo o R² perde sentido em 30 dias, já que a variação da máxima
dentro de um mês é pequena, e por isso ele fica de fora aqui.</p>
<div class="figura">{fig_teste}</div>
<p class="legenda">Figura 3. Avaliação final no teste do último ciclo: máxima real, prevista pelo vigente e persistência.</p>
<p>O notebook também prevê a máxima do dia seguinte ao último dia com dado, que na execução agendada é o próprio dia
da execução, e registra a previsão em
<code>evidencias/previsoes_diarias.csv</code>. Quando o dado real daquele dia chega, num ciclo seguinte, o erro é
preenchido.{texto_diarias}</p>
<div class="bloco"><p class="legenda">Tabela 6. Previsões do dia seguinte feitas pelo pipeline.</p>
{html_tabela(tab_diarias)}</div>
<p style="margin-top:8pt"><b>Teste integrado.</b> No fim do notebook 05, asserts consultam o MLflow e conferem que o
ciclo atual refez a votação, treinou A e B, que os dois usaram exatamente as features eleitas, que todos os runs têm
o mesmo <code>data_version</code> e que a decisão do ciclo está no manifesto. Se alguma condição falhar, o notebook dá
erro e o workflow para. O mesmo notebook mostra o que mudou em relação ao ciclo anterior (dias novos, versão dos
dados, features que entraram ou saíram, métricas e decisão).</p>

<h2>Recurso adicional (critério 10): monitoramento de drift sazonal com alerta</h2>
<p><b>Problema identificado.</b> O vigente pode ficar muitos ciclos sem ser trocado (a regra de promoção é conservadora
de propósito) e ninguém abre os notebooks todo dia. Precisávamos ser avisados quando os dados saem do normal (um mês
muito mais quente ou seco que o habitual, ou uma mudança na própria fonte) e quando o modelo começa a errar mais.</p>
<p><b>Justificativa.</b> A checagem de drift mais comum compara os dados recentes com o treino inteiro. Em clima isso
dispara quase todo mês, porque novembro sempre é diferente da média do ano. Alarme que toca sempre vira ruído e passa a
ser ignorado. O drift que interessa é o que foge do normal para a época.</p>
<p><b>Solução implementada.</b> O notebook 06 (<code>src/monitoramento.py</code>) calcula o PSI de cada feature do vigente
nos últimos {mon['janela_dias']} dias contra os dias da mesma época do ano (com {mon['margem_sazonal_dias']} dias de
margem) nos anos de treino do vigente, e também contra o ano todo, só para comparar. Também compara o MAE do vigente no
último mês com o MAE dele nas mesmas datas do ano anterior, que estão na validação e ele nunca viu. Há alerta se alguma
feature passar de PSI {br(mon['limiar_psi'], 1)} ou se o erro passar de {br(mon['limiar_razao_mae'], 1)} vez o do ano
anterior. Com só 30 dias o PSI tem um piso de ruído alto, então o limiar clássico de 0,25 dispararia demais; por isso
rodamos a mesma checagem em todos os meses antigos do treino (backtest) e calibramos o limiar.</p>
{fig_backtest}
<p><b>Resultado demonstrado.</b> No backtest, com o mesmo limiar, a referência do ano todo teria disparado alerta em
{br(taxa_anual * 100, 0)}% dos meses normais e a referência sazonal em {br(taxa_sazonal * 100, 0)}%. No último ciclo o maior
PSI sazonal foi {br(estado['monitoramento']['psi_sazonal_max'])} (contra {br(estado['monitoramento']['psi_anual_max'])}
na comparação com o ano todo) e a razão de erro foi {br(estado['monitoramento']['razao_mae'])}, então
{'houve alerta' if estado['monitoramento']['alerta'] else 'não houve alerta'}. {texto_alertas}{texto_issue}</p>
<div class="bloco"><p class="legenda">Tabela 7. PSI das features monitoradas no último ciclo.</p>
{html_tabela(tab_psi)}</div>
<p style="margin-top:8pt"><b>Ponto de integração.</b> É o último notebook do mesmo workflow, depois das previsões. As
métricas vão para o run <code>monitoramento</code> do MLflow e para o <code>ciclo.json</code>; se houver alerta, o notebook
grava <code>alerta.md</code> e o passo seguinte do YAML abre a issue "Alerta de drift" no repositório (ou comenta na que
já estiver aberta), o que manda notificação para quem acompanha o repositório.</p>

<h2>Limitações e conclusões</h2>
<p><b>Limitações.</b> Os dados são de reanálise e de um ponto só. Como o ERA5 atrasa uma semana, a linha da previsão usa dado
provisório de modelos de previsão, que erra um pouco mais que o ERA5, e cada previsão só é conferida uma semana depois. Os hiperparâmetros são fixos no config,
sem busca. O teste de 30 dias é pequeno e oscila com o tempo que fez no mês. Guardar o <code>mlflow.db</code> e os
artefatos no Git funciona bem para um trabalho, mas o repositório cresce uns 2,5 MB por ciclo (quase tudo é o modelo
B serializado); num projeto real usaríamos um servidor de tracking e um armazenamento de objetos. E o GitHub pode atrasar ou pular execuções agendadas em horários de pico.</p>
<p><b>Conclusões.</b> O pipeline roda sozinho de ponta a ponta: cada execução agendada busca dados reais novos, gera
uma versão nova dos dados, refaz a votação, treina os dois modelos com as mesmas features, compara com o vigente numa
janela que nenhum dos dois viu e decide automaticamente, deixando tudo rastreável no MLflow, no manifesto e no
histórico do Git. Os modelos erram cerca de {br(ganho_pers * 100, 0)}% menos que a persistência. A maioria dos ciclos
mantém o vigente, o que é o comportamento esperado: um dia a mais de dados quase não muda o problema, e o limiar de
promoção evita trocar de modelo por ruído. O monitoramento sazonal resolveu um problema que só apareceu quando
olhamos os dados de perto: a checagem tradicional de drift não serve para clima.</p>
</section>
"""

html = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Relatório N3</title>
<style>{CSS}</style></head><body>{paginas}</body></html>"""

# caminhos longos dentro de <code> podem quebrar depois da barra
html = re.sub(r"<code>([^<]{20,})</code>", lambda m: "<code>" + m.group(1).replace("/", "/<wbr>") + "</code>", html)
saida_html = RAIZ / "reports" / "relatorio_n3.html"
saida_pdf = RAIZ / "reports" / "relatorio_n3.pdf"
saida_html.write_text(html, encoding="utf-8")
with tempfile.TemporaryDirectory() as perfil:
    subprocess.run([CHROME, "--headless", "--no-pdf-header-footer", f"--user-data-dir={perfil}",
                    f"--print-to-pdf={saida_pdf}", saida_html.as_uri()], check=True, capture_output=True)
print(f"ok: {saida_pdf.relative_to(RAIZ)} ({n_ciclos} ciclos, {len(tab_gh)} execuções)")
