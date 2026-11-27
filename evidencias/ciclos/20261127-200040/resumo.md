# 🌡️ Máxima prevista para 27/11/2026: 24,9 °C

📌 **Modelo vigente mantido** · 🟢 **Sem alerta de drift** · 1 dia novo no ERA5 (20/11/2026)

Previsão feita com os dados até 26/11/2026: ERA5 até 20/11/2026 e, depois, dado provisório da API de previsão do Open-Meteo.

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
| `tmax_media7` | ● |  |  | 1 |
| `amplitude` |  |  | ● | 1 |
| `pressao` | ● |  |  | 1 |
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
| `vento_max` |  |  |  | 0 |
| `umidade_delta` |  |  |  | 0 |

</details>

### 🏁 Competição A × B: erro médio na validação, de 21/10/2025 a 20/10/2026

| Modelo | MAE (°C) | Erra menos que a persistência |
|:--|--:|--:|
| 🥇 **B · HistGradientBoosting** | 1,903 | 26,7% |
| A · Ridge | 1,947 | 25,0% |
| Persistência (amanhã = hoje) | 2,596 | referência |

### 📌 Promoção: modelo mantido

| | MAE na mesma janela (°C) |
|:--|--:|
| Modelo vigente | 1,907 |
| Vencedor desta execução (B · HistGradientBoosting) | 1,903 |
| **Melhora** (o limiar é 2%) | **0,2%** |

_Melhora de 0,2% sobre o vigente, abaixo do limiar de 2%._

### 🔮 Previsões do modelo vigente

| Dia | Previsto | Real | Erro |
|:--|--:|--:|--:|
| **27/11/2026** | **24,9 °C** | aguardando | |
| 20/11/2026 | 27,1 °C | 26,9 °C | +0,1 °C |
| 19/11/2026 | 27,3 °C | 29,1 °C | −1,8 °C |
| 18/11/2026 | 26,4 °C | 28,3 °C | −1,9 °C |

O valor real chega com uns 7 dias de atraso. No teste (últimos 30 dias) o vigente errou 1,89 °C em média, contra 2,15 °C da persistência.

### 🟢 Drift: sem alerta

| Sinal | Valor | Alarme acima de |
|:--|--:|--:|
| Maior PSI sazonal (`radiacao`) | 0,28 | 1,0 |
| Erro do último mês ÷ mesmas datas do ano anterior | 0,83 | 1,5 |

<details><summary>🔎 Rastreabilidade</summary>

- **Versão dos dados:** `dv-20261120-fa8a8c3c` (6.168 dias, de 01/01/2010 a 20/11/2026)
- **Dado provisório:** de 21/11/2026 a 26/11/2026, da API de previsão do Open-Meteo, só na linha da previsão (`evidencias/ciclos/20261127-200040/provisorio.csv`)
- **Janelas:** treino de 07/01/2010 a 20/10/2025 · validação de 21/10/2025 a 20/10/2026 · teste de 21/10/2026 a 19/11/2026
- **Runs no MLflow:** votação `6ef90581` · A `535b4f45` · B `1b10cdba` · decisão `eed1d85e` · previsões `d496742f` · monitoramento `c7080056`
- **Evidências:** [`evidencias/ciclos/20261127-200040/`](https://github.com/zanelladev/n3-mlops-temperatura-jaragua/tree/main/evidencias/ciclos/20261127-200040/)

</details>

<sub>Execução agendada de 27/11/2026 às 17:00 (horário de Brasília) · identificador `20261127-200040`</sub>
