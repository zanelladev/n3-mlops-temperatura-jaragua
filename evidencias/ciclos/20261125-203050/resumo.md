# 🌡️ Máxima prevista para 25/11/2026: 26,5 °C

📌 **Modelo vigente mantido** · 🟢 **Sem alerta de drift** · 1 dia novo no ERA5 (18/11/2026)

Previsão feita com os dados até 24/11/2026: ERA5 até 18/11/2026 e, depois, dado provisório da API de previsão do Open-Meteo.

### 🗳️ Votação: 26 candidatas, 8 eleitas
Cada método vota nas suas 10 melhores olhando só o treino, e entra quem tiver pelo menos 2 votos.

| Feature | SelectKBest | Random Forest | RFE | Votos |
|:--|:-:|:-:|:-:|:-:|
| `tmed` | ● | ● | ● | 3 |
| `dia_ano_cos` | ● | ● | ● | 3 |
| `tmin` | ● | ● | ● | 3 |
| `radiacao` | ● | ● | ● | 3 |
| `vento_dir_cos` |  | ● | ● | 2 |
| `tmax` | ● | ● |  | 2 |
| `pressao_delta` |  | ● | ● | 2 |
| `rajada` |  | ● | ● | 2 |

<details><summary>As outras 18 candidatas</summary>

| Feature | SelectKBest | Random Forest | RFE | Votos |
|:--|:-:|:-:|:-:|:-:|
| `orvalho` | ● |  |  | 1 |
| `amplitude` |  |  | ● | 1 |
| `pressao` | ● |  |  | 1 |
| `tmax_media7` | ● |  |  | 1 |
| `tmax_media3` | ● |  |  | 1 |
| `chuva` |  | ● |  | 1 |
| `nuvens` |  |  | ● | 1 |
| `vento_dir_sin` |  | ● |  | 1 |
| `tmax_lag1` | ● |  |  | 1 |
| `umidade` |  |  | ● | 1 |
| `tmax_lag2` |  |  |  | 0 |
| `dia_ano_sin` |  |  |  | 0 |
| `tmax_lag3` |  |  |  | 0 |
| `tmax_delta` |  |  |  | 0 |
| `vento_med` |  |  |  | 0 |
| `chuva_3d` |  |  |  | 0 |
| `umidade_delta` |  |  |  | 0 |
| `vento_max` |  |  |  | 0 |

</details>

### 🏁 Competição A × B: erro médio na validação, de 19/10/2025 a 18/10/2026

| Modelo | MAE (°C) | Erra menos que a persistência |
|:--|--:|--:|
| 🥇 **B · HistGradientBoosting** | 1,886 | 27,0% |
| A · Ridge | 1,941 | 24,9% |
| Persistência (amanhã = hoje) | 2,585 | referência |

### 📌 Promoção: modelo mantido

| | MAE na mesma janela (°C) |
|:--|--:|
| Modelo vigente | 1,905 |
| Vencedor desta execução (B · HistGradientBoosting) | 1,886 |
| **Melhora** (o limiar é 2%) | **1,0%** |

_Melhora de 1,0% sobre o vigente, abaixo do limiar de 2%._

### 🔮 Previsões do modelo vigente

| Dia | Previsto | Real | Erro |
|:--|--:|--:|--:|
| **25/11/2026** | **26,5 °C** | aguardando | |
| 18/11/2026 | 26,4 °C | 28,3 °C | −1,9 °C |
| 17/11/2026 | 25,8 °C | 26,4 °C | −0,6 °C |
| 16/11/2026 | 25,6 °C | 25,3 °C | +0,3 °C |

O valor real chega com uns 7 dias de atraso. No teste (últimos 30 dias) o vigente errou 1,90 °C em média, contra 2,27 °C da persistência.

### 🟢 Drift: sem alerta

| Sinal | Valor | Alarme acima de |
|:--|--:|--:|
| Maior PSI sazonal (`radiacao`) | 0,26 | 1,0 |
| Erro do último mês ÷ mesmas datas do ano anterior | 0,87 | 1,5 |

<details><summary>🔎 Rastreabilidade</summary>

- **Versão dos dados:** `dv-20261118-5a5ee3d6` (6.166 dias, de 01/01/2010 a 18/11/2026)
- **Dado provisório:** de 19/11/2026 a 24/11/2026, da API de previsão do Open-Meteo, só na linha da previsão (`evidencias/ciclos/20261125-203050/provisorio.csv`)
- **Janelas:** treino de 07/01/2010 a 18/10/2025 · validação de 19/10/2025 a 18/10/2026 · teste de 19/10/2026 a 17/11/2026
- **Runs no MLflow:** votação `639193af` · A `9a4ccc8b` · B `d753a501` · decisão `df96b20f` · previsões `0b7744b6` · monitoramento `7f5dbec8`
- **Evidências:** [`evidencias/ciclos/20261125-203050/`](https://github.com/zanelladev/n3-mlops-temperatura-jaragua/tree/main/evidencias/ciclos/20261125-203050/)

</details>

<sub>Execução agendada de 25/11/2026 às 17:30 (horário de Brasília) · identificador `20261125-203050`</sub>
