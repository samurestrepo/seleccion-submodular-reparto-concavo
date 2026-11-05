# Ficha: `red/traza.py`

## Para qué existe
Guarda el paso a paso de los dos voraces y lo escribe en texto y en JSON. La guía de G2 pide la traza: selección de nodos, ganancias marginales, reparto y verificaciones.

## Funciones públicas
| Función | Recibe | Devuelve | Complejidad |
|---|---|---|---|
| `Traza()` | — | traza vacía | O(1) |
| `.paso_seleccion(paso, aportes, elegido, ganancia, valor)` | datos de un paso del voraz de selección | — | O(N) por los aportes |
| `.unidad_reparto(unidad, nodo, ganancia)` | datos de una unidad | — | O(1) |
| `.entrada_rechazada(motivos)` | lista de textos | — | O(1) |
| `.a_diccionario()` | — | dict para JSON; `motivo_rechazo` solo si hubo rechazo | O(1): devuelve referencias a las listas |
| `a_texto(resultado)` | resultado de `ronda.py`, válido o rechazado | reporte legible | O(tamaño del resultado) |
| `escribir_json(ruta, datos)` | ruta y dict | escribe el archivo | — |

## Cómo funciona
Los algoritmos llaman a la traza solo si la reciben (línea 9 de SELECCIONAR-NODOS, línea 7 de REPARTIR-PRESUPUESTO). `a_texto` arma el reporte por secciones: entrada, Parte 2, Parte 1, verificaciones, informativo (solo en el formato de la profesora, con `_lineas_informativo`) y tiempos. Si el caso se rechazó, el reporte trae solo la entrada, sus verificaciones y el motivo; si el archivo no se pudo leer, dice que N, k y B no se conocen.

## Por qué así
- La traza es opcional para que la ejecución **medida** no incluya el costo de anotar (decisión 11). Por eso `seleccion.py` tampoco llena `aportes` sin traza.
- `motivo_rechazo` solo aparece si hubo rechazo, para que las evidencias de los casos válidos no cambien (decisión 22).
- La sección de tiempos muestra la mediana y dice de cuántas repeticiones (decisión 29). El mínimo y el máximo solo están en `salida.json`.
- La sección "Informativo" solo aparece si el resultado la trae, y por eso las trazas del formato propio tampoco cambian. No lleva `[OK]` ni `[FALLA]`, porque no es una verificación (decisión 26).

## Cómo modificarlo
- **Agregar un dato a la traza** (por ejemplo, el tamaño del montículo): agregar el campo en el método correspondiente y en `a_texto`.

## Pruebas
`pruebas/test_traza.py`: lo que anota, cuándo aparece `motivo_rechazo`, JSON con acentos, y el reporte de un caso válido, de una entrada inválida (antes lanzaba `KeyError`) y de un archivo que no se pudo leer. `test_seleccion.py` y `test_reparto.py` revisan los Δ anotados en los ejemplos del informe; `test_ronda.py` y `test_ejecutar.py` revisan que se escriban los archivos. `test_ronda.py` y `test_bateria.py` revisan la sección "Informativo" y que no aparezca en el formato propio.

## Preguntas probables en la sustentación
- **¿La traza afecta el tiempo medido?** No: el tiempo se mide en una ejecución sin traza, y sin traza los algoritmos no anotan nada.
- **¿Qué queda en la traza si un caso se rechaza?** La entrada, sus verificaciones y el motivo.

_Última actualización: 2026-11-04 · tiempos con mediana y R; sección "Informativo" en `a_texto`_
