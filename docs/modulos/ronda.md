# Ficha: `red/ronda.py`

## Para qué existe
Orquesta una ronda completa (informe 6.1): verificar la entrada, Parte 2, Parte 1 sobre los k elegidos, verificar la salida y medir tiempos.

## Funciones públicas
| Función | Recibe | Devuelve | Complejidad |
|---|---|---|---|
| `ejecutar_ronda(instancia)` | `Instancia` | diccionario con entrada, selección, reparto, tiempos, verificaciones, traza y `todas_cumplen` | algoritmos: O(k·M + B lg k); más la verificación O(N·B) |

## Cómo funciona
1. Verifica la entrada. Si algo falla, **no corre** los algoritmos y devuelve solo esas verificaciones.
2. **Ejecución medida:** corre la Parte 2 y luego la Parte 1 **sin traza**, con `time.perf_counter()` alrededor de cada una.
3. **Ejecución con traza:** las corre otra vez anotando todo.
4. Verifica las dos salidas, el conteo de llamadas y que las dos ejecuciones dieron lo mismo.

## Por qué así
- El tiempo se mide solo alrededor de cada algoritmo (decisión 8) y sin traza (decisión 11), para que corresponda a la T(n) deducida.
- Los algoritmos son deterministas (empates por el menor índice), así que la segunda ejecución debe coincidir; si no, la verificación "ejecución con traza = ejecución medida" falla.
- La Parte 1 recibe S de la Parte 2: su tamaño es (k, B), no (N, B).

## Cómo modificarlo
- **Repetir la medición r veces y quedarse con el mínimo** (útil para la validación experimental): envolver el bloque 1 en un ciclo.
- **Variante (b), T rondas:** llamar `ejecutar_ronda` T veces quitando los nodos que fallan entre rondas. Pendiente de diseño.

## Pruebas
`pruebas/test_ronda.py`: la ronda del ejemplo del informe; una entrada con k = N no corre los algoritmos; una utilidad no cóncava se reporta; el generador produce rondas válidas; `ejecutar.py` escribe las evidencias.

## Preguntas probables en la sustentación
- **¿Qué incluye el tiempo reportado?** Solo el algoritmo; no la lectura, la escritura, la traza ni las verificaciones.
- **¿Cuánto cuesta la ronda?** O(k·M) de la selección más O(k + B lg k) del reparto.

_Última actualización: 2026-11-02 · creación_
