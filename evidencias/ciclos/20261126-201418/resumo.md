# 🌡️ Máxima prevista para 26/11/2026: 28,6 °C

📌 **Modelo vigente mantido** · 🟢 **Sem alerta de drift** · 1 dia novo no ERA5 (19/11/2026)

Previsão feita com os dados até 25/11/2026: ERA5 até 19/11/2026 e, depois, dado provisório da API de previsão do Open-Meteo.

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

### 🏁 Competição A × B: erro médio na validação, de 20/10/2025 a 19/10/2026

| Modelo | MAE (°C) | Erra menos que a persistência |
|:--|--:|--:|
| 🥇 **B · HistGradientBoosting** | 1,901 | 26,7% |
| A · Ridge | 1,946 | 25,0% |
| Persistência (amanhã = hoje) | 2,594 | referência |

### 📌 Promoção: modelo mantido

| | MAE na mesma janela (°C) |
|:--|--:|
| Modelo vigente | 1,910 |
| Vencedor desta execução (B · HistGradientBoosting) | 1,901 |
| **Melhora** (o limiar é 2%) | **0,4%** |

_Melhora de 0,4% sobre o vigente, abaixo do limiar de 2%._

### 🔮 Previsões do modelo vigente

| Dia | Previsto | Real | Erro |
|:--|--:|--:|--:|
| **26/11/2026** | **28,6 °C** | aguardando | |
| 19/11/2026 | 27,3 °C | 29,1 °C | −1,8 °C |
| 18/11/2026 | 26,4 °C | 28,3 °C | −1,9 °C |
| 17/11/2026 | 25,8 °C | 26,4 °C | −0,6 °C |

O valor real chega com uns 7 dias de atraso. No teste (últimos 30 dias) o vigente errou 1,84 °C em média, contra 2,17 °C da persistência.

### 🟢 Drift: sem alerta

| Sinal | Valor | Alarme acima de |
|:--|--:|--:|
| Maior PSI sazonal (`radiacao`) | 0,27 | 1,0 |
| Erro do último mês ÷ mesmas datas do ano anterior | 0,80 | 1,5 |

<details><summary>🔎 Rastreabilidade</summary>

- **Versão dos dados:** `dv-20261119-0aa68191` (6.167 dias, de 01/01/2010 a 19/11/2026)
- **Dado provisório:** de 20/11/2026 a 25/11/2026, da API de previsão do Open-Meteo, só na linha da previsão (`evidencias/ciclos/20261126-201418/provisorio.csv`)
- **Janelas:** treino de 07/01/2010 a 19/10/2025 · validação de 20/10/2025 a 19/10/2026 · teste de 20/10/2026 a 18/11/2026
- **Runs no MLflow:** votação `cf77c878` · A `7a5bebf4` · B `c3564d4f` · decisão `b098d6f5` · previsões `4c939cbc` · monitoramento `a2e92d6a`
- **Evidências:** [`evidencias/ciclos/20261126-201418/`](https://github.com/zanelladev/n3-mlops-temperatura-jaragua/tree/main/evidencias/ciclos/20261126-201418/)

</details>

<sub>Execução agendada de 26/11/2026 às 17:14 (horário de Brasília) · identificador `20261126-201418`</sub>
