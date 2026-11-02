# Ficha: `red/traza.py`

## Para qué existe
Guarda el paso a paso de los dos voraces y lo escribe en texto y en JSON. La guía de G2 pide la traza: selección de nodos, ganancias marginales, reparto y verificaciones.

## Funciones públicas
| Función | Recibe | Devuelve | Complejidad |
|---|---|---|---|
| `Traza()` | — | traza vacía | O(1) |
| `.paso_seleccion(paso, aportes, elegido, ganancia, valor)` | datos de un paso del voraz de selección | — | O(N) por los aportes |
| `.unidad_reparto(unidad, nodo, ganancia)` | datos de una unidad | — | O(1) |
| `.a_diccionario()` | — | dict para JSON | O(tamaño de la traza) |
| `a_texto(resultado)` | resultado completo de `ronda.py` | reporte legible | O(tamaño del resultado) |
| `escribir_json(ruta, datos)` | ruta y dict | escribe el archivo | — |

## Cómo funciona
Los algoritmos llaman a la traza solo si la reciben (línea 9 de SELECCIONAR-NODOS, línea 7 de REPARTIR-PRESUPUESTO). `a_texto` arma el reporte por secciones: entrada, Parte 2, Parte 1, verificaciones y tiempos.

## Por qué así
La traza es opcional para que la ejecución **medida** no incluya el costo de anotar (decisión 11).

## Cómo modificarlo
- **Agregar un dato a la traza** (por ejemplo, el tamaño del montículo): agregar el campo en el método correspondiente y en `a_texto`.

## Pruebas
`test_seleccion.py` y `test_reparto.py` revisan los Δ anotados en los ejemplos del informe; `test_ronda.py` revisa que se escriban los archivos.

## Preguntas probables en la sustentación
- **¿La traza afecta el tiempo medido?** No: el tiempo se mide en una ejecución sin traza.

_Última actualización: 2026-11-02 · creación_
