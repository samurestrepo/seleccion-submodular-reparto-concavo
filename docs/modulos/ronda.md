# Ficha: `red/ronda.py`

## Para qué existe
Orquesta una ronda completa (informe 6.1): verificar la entrada, Parte 2, Parte 1 sobre los k elegidos, verificar la salida y medir tiempos.

## Funciones públicas
| Función | Recibe | Devuelve | Complejidad |
|---|---|---|---|
| `ejecutar_ronda(instancia)` | `Instancia` | diccionario con entrada, selección, reparto, tiempos, verificaciones, traza y `todas_cumplen` | algoritmos: O(k·(N + M) + B(1 + lg k)); más la verificación O(N + M + Σ min(L_i, B)) |
| `resultado_de_error(nombre, mensaje)` | nombre del caso y mensaje | resultado rechazado de un archivo que no se pudo leer; N, k y B en `None` | O(1) |

## Cómo funciona
1. Verifica la entrada. Si algo falla, **no corre** los algoritmos: `_resultado_rechazado` devuelve la entrada, sus verificaciones, `todas_cumplen = False` y una traza vacía con `motivo_rechazo`.
2. **Ejecución medida:** corre la Parte 2 y luego la Parte 1 **sin traza**, con `time.perf_counter()` alrededor de cada una.
3. **Ejecución con traza:** las corre otra vez anotando todo.
4. Verifica las dos salidas, el conteo de llamadas y que las dos ejecuciones dieron lo mismo.

## Por qué así
- El tiempo se mide solo alrededor de cada algoritmo (decisión 8) y sin traza (decisión 11), para que corresponda a la T(n) deducida.
- Los algoritmos son deterministas (empates por el menor índice), así que la segunda ejecución debe coincidir; si no, la verificación "ejecución con traza = ejecución medida" falla.
- La Parte 1 recibe S de la Parte 2: su tamaño es (k, B), no (N, B).
- **Costo de los algoritmos:** O(k·(N + M)) de la selección (decisión 16) más O(k + B(1 + lg k)) del reparto (decisión 15). El término k queda absorbido por k·(N + M).
- **Un caso rechazado también lleva traza** (decisión 22), para que siempre quede escrito el motivo.

## Cómo modificarlo
- **Repetir la medición r veces y quedarse con el mínimo** (útil para la validación experimental): envolver el bloque 1 en un ciclo.
- **Variante (b), T rondas:** llamar `ejecutar_ronda` T veces quitando los nodos que fallan entre rondas. Pendiente de diseño.

## Pruebas
`pruebas/test_ronda.py`: la ronda del ejemplo del informe; una entrada con k = N no corre los algoritmos y deja el motivo en la traza; una utilidad no cóncava se reporta; una tabla mala fuera del presupuesto sí corre y es óptima; el generador produce rondas válidas; `ejecutar.py` escribe las evidencias. `pruebas/test_traza.py` revisa el reporte de `resultado_de_error`.

## Preguntas probables en la sustentación
- **¿Qué incluye el tiempo reportado?** Solo el algoritmo; no la lectura, la escritura, la traza ni las verificaciones.
- **¿Cuánto cuesta la ronda?** O(k·(N + M)) de la selección más O(k + B(1 + lg k)) del reparto. Si ningún C_v es vacío, N ≤ M y la selección es O(k·M).

_Última actualización: 2026-11-02 · resultado rechazado con traza; complejidad corregida_
