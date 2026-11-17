# Ficha: `scripts/tabla_cota_variante_c.py`

## Para qué existe
Genera `resultados/variantes/c_tabla_cota.csv`: los dos modelos de la variante (c) contra el exacto por enumeración, en una batería aleatoria de influencia (decisión 46). Muestra que en c1 el voraz coincide con el óptimo y mide en c2 la razón U/OPT contra la cota 1 − (1 − 1/B)^B.

## Funciones públicas
| Función | Recibe | Devuelve | Complejidad |
|---|---|---|---|
| `fila_de_una_instancia(inst, nombre, beta)` | instancia ya leída (con grafo), su nombre y β | dict con las columnas del CSV | selección base O(k·(N + A)) + dos voraces O(B·(k + A_S)) + dos enumeraciones de R_B repartos a O(k + A_S) cada uno |
| `bateria(tamanos, densidades, semillas, betas, presupuestos)` | por omisión N ∈ {8, 10, 12}, densidad ∈ {0.3, 0.6, 1.0}, semillas 1, 2, 3, β ∈ {0.2, 0.5, 1.0, 2.0}, B ∈ {3, 6, 10} | 324 filas en memoria | 324 × lo anterior (unos 2 s) |
| `escribir_csv(ruta, columnas, filas)` | ruta, columnas, filas | escribe el CSV | O(filas) |
| `main()` | nada | escribe el CSV e imprime cuántas coinciden en c1 y la razón mínima de c2; 0 si todas cumplen | lo anterior |

Columnas: caso, N, k, densidad, semilla, beta, B, S, aristas_en_S, repartos, U_c1_voraz, U_c1_exacto, c1_coincide, x_c2_voraz, x_c2_exacto, U_c2_voraz, U_c2_exacto, razon_c2, cota_c2, cumple.

## Cómo funciona
Por cada (N, densidad, semilla, B) crea la instancia con `generar_instancia_influencia(N, 4, B, densidad, semilla)` (tope de cada nodo = B, que no limita) y la pasa por `instancia_desde_diccionario`; S es el del voraz de la Parte 2 base (k = 4). Por cada β corre `repartir_c1`, `repartir_c2` y `repartir_exacto` con la U de cada modelo. `c1_coincide` = |U_voraz − OPT| ≤ 1e-9 relativo; `razon_c2` = U/OPT (1 si OPT = 0); `cumple` = c1 coincide y cota ≤ razon_c2 ≤ 1 (tolerancia 1e-9).

## Resultados (2026-11-17)
324 filas: c1 coincide con la enumeración en las 324. En c2, 7 filas con razón < 1 (0 con β = 0,2; 3 con 0,5; 2 con 1,0; 2 con 2,0); la mínima es **0,986703184** (`aleatorio_N8_d0.3_s1_B3`, β = 2, S = N03, N06, N07, N04 con 2 aristas; voraz x = 1, 0, 0, 2 y U = 20,756976; óptimo x = 1, 1, 0, 1 y U = 21,036697; cota 0,7037). Todas cumplen.

## Por qué así
k = 4 y B ≤ 10 mantienen la enumeración en C(14, 4) = 1001 repartos como máximo: el script tarda unos 2 s. B pequeño hace que la cota sea más exigente (0,7037 con B = 3, 0,6513 con B = 10). β = 2 se agrega para forzar un acople fuerte: con β = 0,2 el voraz no perdió nunca. Las semillas son fijas (regla del repositorio).

## Cómo modificarlo
Otros tamaños, β o B: las constantes `TAMANOS`, `DENSIDADES`, `SEMILLAS`, `BETAS`, `PRESUPUESTOS` y `K`. Con k o B grandes la enumeración crece como C(B + k, k); `repartir_exacto` se niega por encima de 200000. Si cambian, actualizar `test_bateria_c1_coincide_con_el_exacto_y_c2_respeta_la_cota` (mínimo y número de filas < 1) y regenerar el CSV.

## Pruebas
`pruebas/test_variante_vecinos.py`: la batería completa (324 filas, c1 siempre coincide, c2 ≥ cota y ≤ 1, mínimo 0,986703184, 7 filas < 1) y el CSV del repositorio igual al que genera el script (columnas, casos, x del voraz de c2 y razones).

## Preguntas probables en la sustentación
- **¿Qué muestra la tabla?** Que c1 es exacto (como dice §7.1.1) y que c2, aunque no es exacto, queda muy por encima de su cota: la peor razón fue 0,9867 contra una cota de 0,7037.

_Última actualización: 2026-11-17 · archivo nuevo (P-4 fase 3)_
