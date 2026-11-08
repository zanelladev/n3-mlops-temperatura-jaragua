## Ciclo 20261108-170654 (schedule)
- data_version: `dv-20261101-158b26fd`, 1 dia(s) novo(s), dados até 2026-11-01
- features eleitas (8): tmed, dia_ano_cos, tmin, radiacao, vento_dir_cos, tmax, pressao_delta, rajada

| modelo | algoritmo | MAE validação |
|---|---|---|
| A | ridge | 1.945 |
| B | hist_gradient_boosting | 1.897 |
| persistência | amanhã = hoje | 2.610 |

- vencedor: **B**; decisão: **mantido** (melhora de 0,0% sobre o vigente, abaixo do limiar de 2%)
- MAE do vigente no teste (últimos 30 dias): 2.263 °C (persistência: 2.440 °C)
- previsão para 2026-11-02: **26.2 °C**
- monitoramento: sem alerta
