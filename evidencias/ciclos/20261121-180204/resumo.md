# 🌡️ Máxima prevista para 21/11/2026: 26,4 °C

📌 **Modelo vigente mantido** · 🟢 **Sem alerta de drift** · 1 dia novo no ERA5 (14/11/2026)

Previsão feita com os dados até 20/11/2026: ERA5 até 14/11/2026 e, depois, dado provisório da API de previsão do Open-Meteo.

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
| `umidade_delta` |  |  |  | 0 |
| `vento_max` |  |  |  | 0 |

</details>

### 🏁 Competição A × B: erro médio na validação, de 15/10/2025 a 14/10/2026

| Modelo | MAE (°C) | Erra menos que a persistência |
|:--|--:|--:|
| 🥇 **B · HistGradientBoosting** | 1,904 | 26,9% |
| A · Ridge | 1,944 | 25,3% |
| Persistência (amanhã = hoje) | 2,603 | referência |

### 📌 Promoção: modelo mantido

| | MAE na mesma janela (°C) |
|:--|--:|
| Modelo vigente | 1,909 |
| Vencedor desta execução (B · HistGradientBoosting) | 1,904 |
| **Melhora** (o limiar é 2%) | **0,3%** |

_Melhora de 0,3% sobre o vigente, abaixo do limiar de 2%._

### 🔮 Previsões do modelo vigente

| Dia | Previsto | Real | Erro |
|:--|--:|--:|--:|
| **21/11/2026** | **26,4 °C** | aguardando | |
| 14/11/2026 | 27,0 °C | 24,7 °C | +2,3 °C |
| 13/11/2026 | 25,5 °C | 26,5 °C | −1,0 °C |
| 12/11/2026 | 24,9 °C | 26,6 °C | −1,6 °C |

O valor real chega com uns 7 dias de atraso. No teste (últimos 30 dias) o vigente errou 1,98 °C em média, contra 2,31 °C da persistência.

### 🟢 Drift: sem alerta

| Sinal | Valor | Alarme acima de |
|:--|--:|--:|
| Maior PSI sazonal (`tmin`) | 0,20 | 1,0 |
| Erro do último mês ÷ mesmas datas do ano anterior | 0,93 | 1,5 |

<details><summary>🔎 Rastreabilidade</summary>

- **Versão dos dados:** `dv-20261114-009f0968` (6.162 dias, de 01/01/2010 a 14/11/2026)
- **Dado provisório:** de 15/11/2026 a 20/11/2026, da API de previsão do Open-Meteo, só na linha da previsão (`evidencias/ciclos/20261121-180204/provisorio.csv`)
- **Janelas:** treino de 07/01/2010 a 14/10/2025 · validação de 15/10/2025 a 14/10/2026 · teste de 15/10/2026 a 13/11/2026
- **Runs no MLflow:** votação `4bb1eb78` · A `d5a46c17` · B `fb2aadee` · decisão `8380a8fd` · previsões `00598f8e` · monitoramento `99abb1e4`
- **Evidências:** [`evidencias/ciclos/20261121-180204/`](https://github.com/zanelladev/n3-mlops-temperatura-jaragua/tree/main/evidencias/ciclos/20261121-180204/)

</details>

<sub>Execução agendada de 21/11/2026 às 15:02 (horário de Brasília) · identificador `20261121-180204`</sub>
