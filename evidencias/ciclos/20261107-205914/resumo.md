## Ciclo 20261107-205914 (workflow_dispatch)
- data_version: `dv-20261031-5975bc1e`, 7 dia(s) novo(s), dados até 2026-10-31
- features eleitas (8): tmed, dia_ano_cos, tmin, radiacao, vento_dir_cos, tmax, pressao_delta, rajada

| modelo | algoritmo | MAE validação |
|---|---|---|
| A | ridge | 1.933 |
| B | hist_gradient_boosting | 1.867 |
| persistência | amanhã = hoje | 2.604 |

- vencedor: **B**; decisão: **mantido** (melhora de 1.2% sobre o vigente, abaixo do limiar de 2%)
- MAE do vigente no teste (últimos 30 dias): 2.366 °C (persistência: 2.533 °C)
- previsão para 2026-11-01: **23.6 °C**
- monitoramento: sem alerta
