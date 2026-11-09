# 🌡️ Máxima prevista para 09/11/2026: 23,7 °C

📌 **Modelo vigente mantido** · 🟢 **Sem alerta de drift** · 1 dia novo no ERA5 (02/11/2026)

Previsão feita com os dados até 08/11/2026: ERA5 até 02/11/2026 e, depois, dado provisório da API de previsão do Open-Meteo.

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
| `amplitude` |  |  | ● | 1 |
| `pressao` | ● |  |  | 1 |
| `tmax_media7` | ● |  |  | 1 |
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
| `umidade_delta` |  |  |  | 0 |
| `chuva_3d` |  |  |  | 0 |
| `vento_max` |  |  |  | 0 |

</details>

### 🏁 Competição A × B: erro médio na validação, de 03/10/2025 a 02/10/2026

| Modelo | MAE (°C) | Erra menos que a persistência |
|:--|--:|--:|
| 🥇 **B · HistGradientBoosting** | 1,888 | 28,1% |
| A · Ridge | 1,941 | 26,1% |
| Persistência (amanhã = hoje) | 2,625 | referência |

### 📌 Promoção: modelo mantido

| | MAE na mesma janela (°C) |
|:--|--:|
| Modelo vigente | 1,895 |
| Vencedor desta execução (B · HistGradientBoosting) | 1,888 |
| **Melhora** (o limiar é 2%) | **0,4%** |

_Melhora de 0,4% sobre o vigente, abaixo do limiar de 2%._

### 🔮 Previsões do modelo vigente

| Dia | Previsto | Real | Erro |
|:--|--:|--:|--:|
| **09/11/2026** | **23,7 °C** | aguardando | |
| 02/11/2026 | 26,2 °C | 29,2 °C | −3,0 °C |
| 01/11/2026 | 23,6 °C | 24,9 °C | −1,3 °C |
| 25/10/2026 | 25,2 °C | 20,8 °C | +4,4 °C |

O valor real chega com uns 7 dias de atraso. No teste (últimos 30 dias) o vigente errou 2,29 °C em média, contra 2,40 °C da persistência.

### 🟢 Drift: sem alerta

| Sinal | Valor | Alarme acima de |
|:--|--:|--:|
| Maior PSI sazonal (`tmax`) | 0,37 | 1,0 |
| Erro do último mês ÷ mesmas datas do ano anterior | 1,19 | 1,5 |

<details><summary>🔎 Rastreabilidade</summary>

- **Versão dos dados:** `dv-20261102-97fa6541` (6.150 dias, de 01/01/2010 a 02/11/2026)
- **Dado provisório:** de 03/11/2026 a 08/11/2026, da API de previsão do Open-Meteo, só na linha da previsão (`evidencias/ciclos/20261109-184535/provisorio.csv`)
- **Janelas:** treino de 07/01/2010 a 02/10/2025 · validação de 03/10/2025 a 02/10/2026 · teste de 03/10/2026 a 01/11/2026
- **Runs no MLflow:** votação `3763a59e` · A `ca6d04de` · B `08af57b0` · decisão `5d0fb8e1` · previsões `0c89ba0f` · monitoramento `215488c1`
- **Evidências:** [`evidencias/ciclos/20261109-184535/`](https://github.com/zanelladev/n3-mlops-temperatura-jaragua/tree/main/evidencias/ciclos/20261109-184535/)

</details>

<sub>Execução manual de 09/11/2026 às 15:45 (horário de Brasília) · identificador `20261109-184535`</sub>
