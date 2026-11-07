## Ciclo 20261107-205440 (workflow_dispatch)
- data_version: `dv-20261024-622a2671`, 6141 dia(s) novo(s), dados até 2026-10-24
- features eleitas (8): tmed, dia_ano_cos, tmin, radiacao, vento_dir_cos, tmax, pressao_delta, rajada

| modelo | algoritmo | MAE validação |
|---|---|---|
| A | ridge | 1.929 |
| B | hist_gradient_boosting | 1.887 |
| persistência | amanhã = hoje | 2.569 |

- vencedor: **B**; decisão: **promovido** (primeiro ciclo: ainda não havia modelo vigente)
- MAE do vigente no teste (últimos 30 dias): 2.209 °C (persistência: 2.977 °C)
- previsão para 2026-10-25: **25.2 °C**
- monitoramento: sem alerta
