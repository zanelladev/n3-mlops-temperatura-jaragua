# Temperatura máxima do dia seguinte em Jaraguá do Sul, com MLOps

Trabalho N3 de Análise Preditiva, Católica de Santa Catarina, prof. Rodrigo Hagstrom.

**Integrantes:** André Ramos da Silva, Artur Felippe Zanella, Felipe Bogo, Jeison Diniz de Souza Marinho e Thierry Augusto Busnardo.

O projeto prevê a temperatura máxima do dia seguinte em Jaraguá do Sul (SC) com dados reais do Open-Meteo. Um único workflow do GitHub Actions roda todo dia: busca os dias novos, refaz o ETL, elege as features pela votação de três métodos, treina dois algoritmos com as mesmas features, escolhe o vencedor, decide se ele substitui o modelo vigente, faz as previsões e monitora drift. Tudo fica registrado no MLflow, e o estado de cada ciclo é commitado de volta neste repositório.

O relatório técnico está em [`reports/relatorio_n3.pdf`](reports/relatorio_n3.pdf).

## Fluxo de um ciclo

```
schedule (todo dia, 08:17 de Brasília) ou workflow_dispatch
  01_etl                dias novos da API -> data/raw/lote_*.csv, data_version, ETL, atributos, cycle_id
  02_votacao_features   SelectKBest + Random Forest + RFE, maioria de 2 em 3 -> features do ciclo
  03_treino_competicao  Ridge (A) x HistGradientBoosting (B), mesmas features, MAE na validação
  04_selecao_promocao   vencedor do ciclo x vigente, limiar de 2% -> promove ou mantém
  05_previsoes          avaliação final no teste, previsão do dia seguinte, teste integrado
  06_monitoramento      drift sazonal e de desempenho -> issue de alerta (critério 10)
  commit do estado (data/raw, mlflow.db, mlartefatos, models, evidencias) + artifact do ciclo
```

Todos os passos de um ciclo compartilham o mesmo `cycle_id` (data e hora UTC de início) e o mesmo `data_version` (último dia da série mais o sha256 dos arquivos de `data/raw`).

## Estrutura

```
.github/workflows/pipeline_mlops.yml   o único workflow (schedule + workflow_dispatch)
config/config.yaml                     dados, métrica, votação, algoritmos, promoção e monitoramento
data/raw/                              lotes baixados do Open-Meteo, um arquivo por chegada
notebooks/01 a 06                      o processo documentado, chamando as funções de src/
src/                                   ingestao, preprocessamento, features, modelagem, promocao, monitoramento, ciclo
models/modelo_vigente.json             manifesto do modelo vigente e da última decisão
mlflow.db + mlartefatos/               tracking do MLflow (SQLite) e artefatos, com caminhos relativos
evidencias/ciclos/<cycle_id>/          estado, tabelas e notebooks executados de cada ciclo
evidencias/previsoes_diarias.csv       previsões do dia seguinte, conferidas quando o dado real chega
reports/                               relatório em PDF e o script que o gera
```

## Como rodar localmente

Python 3.12.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
for nb in 01_etl 02_votacao_features 03_treino_competicao 04_selecao_promocao 05_previsoes 06_monitoramento; do
  jupyter nbconvert --to notebook --execute notebooks/$nb.ipynb --output-dir executados
done
```

Uma execução local abre um ciclo novo (com evento `local`) e altera `mlflow.db`, `models/` e `evidencias/`. Para não misturar com o histórico do workflow, rode num clone separado ou descarte as mudanças depois. Os testes rápidos das regras de votação, promoção e PSI rodam com `python -m src.features`, `python -m src.promocao` e `python -m src.monitoramento`.

## Execução agendada

- O cron é `17 11 * * *` (UTC). O GitHub pode atrasar execuções agendadas em alguns minutos.
- O ERA5 chega com uns 7 dias de atraso, então cada execução costuma trazer um dia novo. Se não vier nenhum, o workflow para depois do notebook 01 e não treina nada.
- Se qualquer notebook falhar, o job para antes do commit: nada é promovido e o vigente continua o mesmo.
- O estado persistente é o próprio repositório. Cada ciclo termina com um commit do bot no formato `Execução agendada de DD/MM/AAAA: modelo mantido, máxima prevista de XX,X °C para DD/MM`, e a execução seguinte começa do checkout desse commit, sem depender de arquivos do runner anterior. As evidências também são publicadas como artifact da execução (`evidencias-execucao-N`).
- A página de cada execução no Actions traz um resumo: a máxima prevista, a votação, a competição A × B, a decisão de promoção, as últimas previsões conferidas com o valor real e o drift. O mesmo texto fica em `evidencias/ciclos/<cycle_id>/resumo.md`.
- `workflow_dispatch` aceita `data_limite` (ingerir só até uma data, usado para demonstrar a chegada de um lote) e `testar_alerta` (testar a issue de alerta).
- As execuções ficam na aba Actions; o filtro `event:schedule` mostra só as agendadas.

## Consultar o MLflow

Na raiz do projeto:

```bash
mlflow ui --backend-store-uri sqlite:///mlflow.db
```

Abrir http://127.0.0.1:5000, experimento `n3-tmax-jaragua`. Cada ciclo tem os runs `votacao`, `A-ridge`, `B-hist_gradient_boosting`, `decisao`, `previsoes` e `monitoramento`, todos com as tags `cycle_id`, `data_version`, `etapa` e `evento`. Para ver um ciclo: `tags.cycle_id = '20261108-111702'`. Para comparar os treinos de todos os ciclos: `tags.etapa = 'treino'`.

## Reproduzir as previsões

```python
import json
from src import ciclo, ingestao, preprocessamento

cfg = ciclo.carregar_config()
mlflow = ciclo.configurar_mlflow(cfg)
vigente = json.load(open("models/modelo_vigente.json"))
modelo = mlflow.sklearn.load_model(vigente["model_uri"])      # Pipeline com imputação e escala

dataset = preprocessamento.construir_atributos(preprocessamento.limpar(ingestao.carregar_bruto()))
print(modelo.predict(dataset[vigente["features"]].tail(1)))   # máxima do dia seguinte ao último dado
```

Para reproduzir um ciclo antigo, o `ciclo.json` dele lista os lotes de `data/raw` que existiam naquele momento.

## Recurso adicional (critério 10): drift sazonal com alerta

O notebook 06 compara as features do vigente nos últimos 30 dias com a mesma época do ano (±15 dias) nos anos de treino, usando PSI, e compara o erro do último mês com o erro nas mesmas datas do ano anterior. A comparação comum, contra o ano todo, dispara em quase todo mês por causa da estação. No backtest dos meses antigos, com o mesmo limiar, a referência do ano todo dispararia em 72% dos meses e a sazonal em 3%. Quando há alerta, o workflow abre (ou comenta) a issue "Alerta de drift" no repositório.

## Dados e licença

Weather data by [Open-Meteo.com](https://open-meteo.com/), licença CC BY 4.0, a partir da reanálise ERA5 e ERA5-Land do Copernicus Climate Change Service. Ponto de grade em -26,49; -49,07 (Jaraguá do Sul), série diária desde 01/01/2010.
