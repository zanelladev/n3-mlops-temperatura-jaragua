# 🌡️ Máxima prevista para 22/11/2026: 24,4 °C

📌 **Modelo vigente mantido** · 🟢 **Sem alerta de drift** · 1 dia novo no ERA5 (15/11/2026)

Previsão feita com os dados até 21/11/2026: ERA5 até 15/11/2026 e, depois, dado provisório da API de previsão do Open-Meteo.

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
| `tmax_media3` | ● |  |  | 1 |
| `chuva` |  | ● |  | 1 |
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

### 🏁 Competição A × B: erro médio na validação, de 16/10/2025 a 15/10/2026

| Modelo | MAE (°C) | Erra menos que a persistência |
|:--|--:|--:|
| 🥇 **B · HistGradientBoosting** | 1,889 | 27,3% |
| A · Ridge | 1,941 | 25,3% |
| Persistência (amanhã = hoje) | 2,599 | referência |

### 📌 Promoção: modelo mantido

| | MAE na mesma janela (°C) |
|:--|--:|
| Modelo vigente | 1,903 |
| Vencedor desta execução (B · HistGradientBoosting) | 1,889 |
| **Melhora** (o limiar é 2%) | **0,7%** |

_Melhora de 0,7% sobre o vigente, abaixo do limiar de 2%._

### 🔮 Previsões do modelo vigente

| Dia | Previsto | Real | Erro |
|:--|--:|--:|--:|
| **22/11/2026** | **24,4 °C** | aguardando | |
| 15/11/2026 | 26,0 °C | 25,9 °C | +0,1 °C |
| 14/11/2026 | 27,0 °C | 24,7 °C | +2,3 °C |
| 13/11/2026 | 25,5 °C | 26,5 °C | −1,0 °C |

O valor real chega com uns 7 dias de atraso. No teste (últimos 30 dias) o vigente errou 1,97 °C em média, contra 2,34 °C da persistência.

### 🟢 Drift: sem alerta

| Sinal | Valor | Alarme acima de |
|:--|--:|--:|
| Maior PSI sazonal (`tmed`) | 0,14 | 1,0 |
| Erro do último mês ÷ mesmas datas do ano anterior | 0,98 | 1,5 |

<details><summary>🔎 Rastreabilidade</summary>

- **Versão dos dados:** `dv-20261115-4a4d32b5` (6.163 dias, de 01/01/2010 a 15/11/2026)
- **Dado provisório:** de 16/11/2026 a 21/11/2026, da API de previsão do Open-Meteo, só na linha da previsão (`evidencias/ciclos/20261122-183427/provisorio.csv`)
- **Janelas:** treino de 07/01/2010 a 15/10/2025 · validação de 16/10/2025 a 15/10/2026 · teste de 16/10/2026 a 14/11/2026
- **Runs no MLflow:** votação `b3fee6d7` · A `de5beff4` · B `d6f8857b` · decisão `89bf4326` · previsões `9bdec83e` · monitoramento `be6114fa`
- **Evidências:** [`evidencias/ciclos/20261122-183427/`](https://github.com/zanelladev/n3-mlops-temperatura-jaragua/tree/main/evidencias/ciclos/20261122-183427/)

</details>

<sub>Execução agendada de 22/11/2026 às 15:34 (horário de Brasília) · identificador `20261122-183427`</sub>
