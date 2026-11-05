# Ficha: `red/ronda.py`

## Para qué existe
Orquesta una ronda completa (informe 6.1): verificar la entrada, Parte 2, Parte 1 sobre los k elegidos, verificar la salida y medir tiempos.

## Funciones públicas
| Función | Recibe | Devuelve | Complejidad |
|---|---|---|---|
| `ejecutar_ronda(instancia, repeticiones=REPETICIONES)` | `Instancia` y R ≥ 1 (por omisión, 21); con R < 1 lanza `ValueError` | diccionario con entrada, selección, reparto, tiempos, verificaciones, traza, `todas_cumplen` y, solo en el formato de la profesora, `informativo` | algoritmos, por repetición: O(k·(N + M) + B(1 + lg k)) con cobertura, O(k·(N + A) + B(1 + lg k)) con influencia; más la verificación O(N + M + Σ min(L_i, B)) con cobertura, O(N + A) con influencia |
| `resultado_de_error(nombre, mensaje)` | nombre del caso y mensaje | resultado rechazado de un archivo que no se pudo leer; N, k y B en `None` | O(1) |

## Cómo funciona
1. Verifica la entrada. Si algo falla, **no corre** los algoritmos: `_resultado_rechazado` devuelve la entrada, sus verificaciones, `todas_cumplen = False` y una traza vacía con `motivo_rechazo`.
2. **Ejecución medida** (`_ejecucion_medida`): R veces corre la Parte 2 y luego la Parte 1 **sin traza**, con `time.perf_counter()` alrededor de cada una y un oráculo nuevo, creado fuera del reloj. La Parte 1 recibe los topes de la instancia. `_resumen_tiempos` calcula la mediana, el mínimo y el máximo de cada parte.
3. **Ejecución con traza:** las corre otra vez anotando todo.
4. Verifica las salidas de la **primera** repetición, el conteo de llamadas de la primera, que **todas las repeticiones** dieron el mismo S y el mismo reparto (`_verificar_repeticiones`), y que la ejecución con traza dio lo mismo.
5. Si el caso es del formato de la profesora, agrega la sección `informativo` (`_informativo`).

Cada ejecución usa su propio oráculo, pedido con `instancia.crear_oraculo()`: `ronda.py` no sabe si es de cobertura o de influencia, y los contadores no se mezclan.

## Por qué así
- El tiempo se mide solo alrededor de cada algoritmo (decisión 8) y sin traza (decisión 11), para que corresponda a la T(n) deducida.
- **Mediana de R repeticiones (decisión 29):** con N = 15, cada parte dura microsegundos, y una sola medición la domina el ruido del sistema. La mediana no se deja arrastrar por una repetición lenta: de 1, 2 y 1000, reporta 2. Con R par, promedia los dos del centro. No resiste una ráfaga lenta que cubra más de la mitad de las repeticiones: ahí el mínimo es más estable (medido en la decisión 29). **Por eso para T(n) se usa el mínimo** (decisión 30): el ruido del sistema solo suma tiempo. La mediana queda como dato reportado.
- **El tiempo que se reporta sigue siendo el de una ejecución:** es la mediana de R, no la suma, así que sigue correspondiendo a la T(n) deducida. Lo que se multiplica por R es lo que tarda la corrida completa. Guardar las corridas cuesta O(R·k) de memoria, fuera del reloj.
- Los algoritmos son deterministas (empates por el menor índice), así que todas las ejecuciones deben coincidir; si no, falla "todas las repeticiones dan el mismo S y el mismo reparto" o "ejecución con traza = ejecución medida".
- La Parte 1 recibe S de la Parte 2: su tamaño es (k, B), no (N, B).
- **Costo de los algoritmos:** O(k·(N + M)) de la selección (decisión 16) más O(k + B(1 + lg k)) del reparto (decisión 15). El término k queda absorbido por k·(N + M).
- **Un caso rechazado también lleva traza** (decisión 22), para que siempre quede escrito el motivo.
- **`informativo` no es una verificación** (decisión 26): trae la Σ de `costo_participacion` de S frente a `presupuesto_costos_participacion_por_ronda` (variante a) y `numero_rondas` (variante b), con el texto "no se aplica en la solución base". Queda fuera de `verificaciones`, así que `todas_cumplen` no lo mira: aunque los costos superen el presupuesto, el caso cumple. Se calcula al final, fuera de los tiempos medidos, en O(N). Un caso rechazado no lo lleva, porque no hay S.

## Cómo modificarlo
- **Cambiar R:** la constante `REPETICIONES` o la opción `--repeticiones`. Ya está hecho (decisión 29).
- **Reportar otra medida:** `salida.json` trae mediana, mínimo y máximo, y `resumen.csv` trae mediana y mínimo. `traza.txt` muestra la mediana (`a_texto`).
- **Variante (b), T rondas:** llamar `ejecutar_ronda` T veces quitando los nodos que fallan entre rondas. Pendiente de diseño.

## Pruebas
`pruebas/test_ronda.py`: la ronda del ejemplo del informe; una entrada con k = N no corre los algoritmos y deja el motivo en la traza; una utilidad no cóncava se reporta; una tabla mala fuera del presupuesto sí corre y es óptima; el generador produce rondas válidas; `ejecutar.py` escribe las evidencias. `pruebas/test_traza.py` revisa el reporte de `resultado_de_error`. También en `test_ronda.py`: el contenido de `informativo`; que no decide `todas_cumplen` aunque los costos superen el presupuesto; que no aparece en el formato propio ni en un caso rechazado; que `presupuesto_total_nodo` es el tope y sobrar presupuesto no es una falla; que los oráculos no comparten contadores. **Repeticiones:** mediana, mínimo, máximo y R; 21 por omisión; una repetición lenta no arrastra la mediana; cada repetición usa un oráculo nuevo; una repetición con otro S o con otro reparto se detecta; lo reportado es la primera; R = 1 funciona y R < 1 es un error.

## Preguntas probables en la sustentación
- **¿Qué incluye el tiempo reportado?** Solo el algoritmo; no la lectura, la escritura, la traza ni las verificaciones. Es la mediana de 21 repeticiones.
- **¿Por qué la mediana y no el promedio?** Porque una repetición lenta, por ejemplo si el sistema interrumpe, sube el promedio y casi no mueve la mediana.
- **¿La mediana cambia la complejidad?** No: cada repetición cuesta lo mismo, y se reporta una duración, no la suma.
- **¿Cuánto cuesta la ronda?** O(k·(N + M)) de la selección más O(k + B(1 + lg k)) del reparto. Si ningún C_v es vacío, N ≤ M y la selección es O(k·M). Con influencia, la selección es O(k·(N + A)).
- **¿Se pasó del presupuesto de costos?** En el caso de la profesora, la Σ de costos de S es 23 frente a 24. Es informativo: la solución base no aplica esa restricción.

_Última actualización: 2026-11-04 · mediana de R repeticiones, topes, `crear_oraculo` y sección `informativo`_
