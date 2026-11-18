# 🌡️ Máxima prevista para 18/11/2026: 26,4 °C

📌 **Modelo vigente mantido** · 🟢 **Sem alerta de drift** · 1 dia novo no ERA5 (11/11/2026)

Previsão feita com os dados até 17/11/2026: ERA5 até 11/11/2026 e, depois, dado provisório da API de previsão do Open-Meteo.

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

### 🏁 Competição A × B: erro médio na validação, de 12/10/2025 a 11/10/2026

| Modelo | MAE (°C) | Erra menos que a persistência |
|:--|--:|--:|
| 🥇 **B · HistGradientBoosting** | 1,916 | 26,9% |
| A · Ridge | 1,958 | 25,4% |
| Persistência (amanhã = hoje) | 2,622 | referência |

### 📌 Promoção: modelo mantido

| | MAE na mesma janela (°C) |
|:--|--:|
| Modelo vigente | 1,923 |
| Vencedor desta execução (B · HistGradientBoosting) | 1,916 |
| **Melhora** (o limiar é 2%) | **0,4%** |

_Melhora de 0,4% sobre o vigente, abaixo do limiar de 2%._

### 🔮 Previsões do modelo vigente

| Dia | Previsto | Real | Erro |
|:--|--:|--:|--:|
| **18/11/2026** | **26,4 °C** | aguardando | |
| 11/11/2026 | 23,7 °C | 24,8 °C | −1,1 °C |
| 10/11/2026 | 23,4 °C | 21,6 °C | +1,8 °C |
| 09/11/2026 | 23,7 °C | 20,2 °C | +3,5 °C |

O valor real chega com uns 7 dias de atraso. No teste (últimos 30 dias) o vigente errou 1,93 °C em média, contra 2,37 °C da persistência.

### 🟢 Drift: sem alerta

| Sinal | Valor | Alarme acima de |
|:--|--:|--:|
| Maior PSI sazonal (`tmax`) | 0,27 | 1,0 |
| Erro do último mês ÷ mesmas datas do ano anterior | 0,90 | 1,5 |

<details><summary>🔎 Rastreabilidade</summary>

- **Versão dos dados:** `dv-20261111-742476c5` (6.159 dias, de 01/01/2010 a 11/11/2026)
- **Dado provisório:** de 12/11/2026 a 17/11/2026, da API de previsão do Open-Meteo, só na linha da previsão (`evidencias/ciclos/20261118-192602/provisorio.csv`)
- **Janelas:** treino de 07/01/2010 a 11/10/2025 · validação de 12/10/2025 a 11/10/2026 · teste de 12/10/2026 a 10/11/2026
- **Runs no MLflow:** votação `5199153a` · A `67fbbc23` · B `f1f660cb` · decisão `e1a84aea` · previsões `8834a51c` · monitoramento `a8859bd8`
- **Evidências:** [`evidencias/ciclos/20261118-192602/`](https://github.com/zanelladev/n3-mlops-temperatura-jaragua/tree/main/evidencias/ciclos/20261118-192602/)

</details>

<sub>Execução agendada de 18/11/2026 às 16:26 (horário de Brasília) · identificador `20261118-192602`</sub>
