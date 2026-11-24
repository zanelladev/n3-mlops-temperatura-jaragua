# 🌡️ Máxima prevista para 24/11/2026: 26,5 °C

📌 **Modelo vigente mantido** · 🟢 **Sem alerta de drift** · 1 dia novo no ERA5 (17/11/2026)

Previsão feita com os dados até 23/11/2026: ERA5 até 17/11/2026 e, depois, dado provisório da API de previsão do Open-Meteo.

### 🗳️ Votação: 26 candidatas, 8 eleitas
Cada método vota nas suas 10 melhores olhando só o treino, e entra quem tiver pelo menos 2 votos.

| Feature | SelectKBest | Random Forest | RFE | Votos |
|:--|:-:|:-:|:-:|:-:|
| `tmed` | ● | ● | ● | 3 |
| `dia_ano_cos` | ● | ● | ● | 3 |
| `tmin` | ● | ● | ● | 3 |
| `vento_dir_cos` |  | ● | ● | 2 |
| `tmax` | ● | ● |  | 2 |
| `radiacao` | ● |  | ● | 2 |
| `pressao_delta` |  | ● | ● | 2 |
| `rajada` |  | ● | ● | 2 |

<details><summary>As outras 18 candidatas</summary>

| Feature | SelectKBest | Random Forest | RFE | Votos |
|:--|:-:|:-:|:-:|:-:|
| `orvalho` | ● |  |  | 1 |
| `tmax_media7` | ● |  |  | 1 |
| `amplitude` |  |  | ● | 1 |
| `pressao` | ● |  |  | 1 |
| `chuva` |  | ● |  | 1 |
| `tmax_media3` | ● |  |  | 1 |
| `nuvens` |  |  | ● | 1 |
| `vento_dir_sin` |  | ● |  | 1 |
| `dia_ano_sin` |  | ● |  | 1 |
| `tmax_lag1` | ● |  |  | 1 |
| `umidade` |  |  | ● | 1 |
| `tmax_lag2` |  |  |  | 0 |
| `tmax_lag3` |  |  |  | 0 |
| `tmax_delta` |  |  |  | 0 |
| `vento_med` |  |  |  | 0 |
| `chuva_3d` |  |  |  | 0 |
| `vento_max` |  |  |  | 0 |
| `umidade_delta` |  |  |  | 0 |

</details>

### 🏁 Competição A × B: erro médio na validação, de 18/10/2025 a 17/10/2026

| Modelo | MAE (°C) | Erra menos que a persistência |
|:--|--:|--:|
| 🥇 **B · HistGradientBoosting** | 1,895 | 27,1% |
| A · Ridge | 1,943 | 25,3% |
| Persistência (amanhã = hoje) | 2,601 | referência |

### 📌 Promoção: modelo mantido

| | MAE na mesma janela (°C) |
|:--|--:|
| Modelo vigente | 1,906 |
| Vencedor desta execução (B · HistGradientBoosting) | 1,895 |
| **Melhora** (o limiar é 2%) | **0,6%** |

_Melhora de 0,6% sobre o vigente, abaixo do limiar de 2%._

### 🔮 Previsões do modelo vigente

| Dia | Previsto | Real | Erro |
|:--|--:|--:|--:|
| **24/11/2026** | **26,5 °C** | aguardando | |
| 17/11/2026 | 25,8 °C | 26,4 °C | −0,6 °C |
| 16/11/2026 | 25,6 °C | 25,3 °C | +0,3 °C |
| 15/11/2026 | 26,0 °C | 25,9 °C | +0,1 °C |

O valor real chega com uns 7 dias de atraso. No teste (últimos 30 dias) o vigente errou 1,93 °C em média, contra 2,26 °C da persistência.

### 🟢 Drift: sem alerta

| Sinal | Valor | Alarme acima de |
|:--|--:|--:|
| Maior PSI sazonal (`radiacao`) | 0,16 | 1,0 |
| Erro do último mês ÷ mesmas datas do ano anterior | 0,88 | 1,5 |

<details><summary>🔎 Rastreabilidade</summary>

- **Versão dos dados:** `dv-20261117-49f165ea` (6.165 dias, de 01/01/2010 a 17/11/2026)
- **Dado provisório:** de 18/11/2026 a 23/11/2026, da API de previsão do Open-Meteo, só na linha da previsão (`evidencias/ciclos/20261124-211903/provisorio.csv`)
- **Janelas:** treino de 07/01/2010 a 17/10/2025 · validação de 18/10/2025 a 17/10/2026 · teste de 18/10/2026 a 16/11/2026
- **Runs no MLflow:** votação `38b5cea3` · A `644bff51` · B `c119b27b` · decisão `47f1e13f` · previsões `fa44d543` · monitoramento `78b8fc02`
- **Evidências:** [`evidencias/ciclos/20261124-211903/`](https://github.com/zanelladev/n3-mlops-temperatura-jaragua/tree/main/evidencias/ciclos/20261124-211903/)

</details>

<sub>Execução agendada de 24/11/2026 às 18:19 (horário de Brasília) · identificador `20261124-211903`</sub>
