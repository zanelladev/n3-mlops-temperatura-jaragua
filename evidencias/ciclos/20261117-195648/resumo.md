# 🌡️ Máxima prevista para 17/11/2026: 25,8 °C

📌 **Modelo vigente mantido** · 🟢 **Sem alerta de drift** · 1 dia novo no ERA5 (10/11/2026)

Previsão feita com os dados até 16/11/2026: ERA5 até 10/11/2026 e, depois, dado provisório da API de previsão do Open-Meteo.

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

### 🏁 Competição A × B: erro médio na validação, de 11/10/2025 a 10/10/2026

| Modelo | MAE (°C) | Erra menos que a persistência |
|:--|--:|--:|
| 🥇 **B · HistGradientBoosting** | 1,906 | 27,3% |
| A · Ridge | 1,953 | 25,5% |
| Persistência (amanhã = hoje) | 2,622 | referência |

### 📌 Promoção: modelo mantido

| | MAE na mesma janela (°C) |
|:--|--:|
| Modelo vigente | 1,919 |
| Vencedor desta execução (B · HistGradientBoosting) | 1,906 |
| **Melhora** (o limiar é 2%) | **0,7%** |

_Melhora de 0,7% sobre o vigente, abaixo do limiar de 2%._

### 🔮 Previsões do modelo vigente

| Dia | Previsto | Real | Erro |
|:--|--:|--:|--:|
| **17/11/2026** | **25,8 °C** | aguardando | |
| 10/11/2026 | 23,4 °C | 21,6 °C | +1,8 °C |
| 09/11/2026 | 23,7 °C | 20,2 °C | +3,5 °C |
| 02/11/2026 | 26,2 °C | 29,2 °C | −3,0 °C |

O valor real chega com uns 7 dias de atraso. No teste (últimos 30 dias) o vigente errou 2,00 °C em média, contra 2,31 °C da persistência.

### 🟢 Drift: sem alerta

| Sinal | Valor | Alarme acima de |
|:--|--:|--:|
| Maior PSI sazonal (`tmax`) | 0,29 | 1,0 |
| Erro do último mês ÷ mesmas datas do ano anterior | 0,91 | 1,5 |

<details><summary>🔎 Rastreabilidade</summary>

- **Versão dos dados:** `dv-20261110-134aafcd` (6.158 dias, de 01/01/2010 a 10/11/2026)
- **Dado provisório:** de 11/11/2026 a 16/11/2026, da API de previsão do Open-Meteo, só na linha da previsão (`evidencias/ciclos/20261117-195648/provisorio.csv`)
- **Janelas:** treino de 07/01/2010 a 10/10/2025 · validação de 11/10/2025 a 10/10/2026 · teste de 11/10/2026 a 09/11/2026
- **Runs no MLflow:** votação `85008d97` · A `4e63c1e8` · B `e9feafe0` · decisão `8c784ea9` · previsões `ed17acf8` · monitoramento `72057128`
- **Evidências:** [`evidencias/ciclos/20261117-195648/`](https://github.com/zanelladev/n3-mlops-temperatura-jaragua/tree/main/evidencias/ciclos/20261117-195648/)

</details>

<sub>Execução agendada de 17/11/2026 às 16:56 (horário de Brasília) · identificador `20261117-195648`</sub>
