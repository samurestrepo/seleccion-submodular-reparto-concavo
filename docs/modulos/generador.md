# Ficha: `red/generador.py`

## Para qué existe
Genera instancias sintéticas en el formato provisional, con semilla fija. Las piden el enunciado (instancias de tamaño creciente) y las entregas de experimentación.

## Funciones públicas
| Función | Recibe | Devuelve | Complejidad |
|---|---|---|---|
| `generar_instancia(N, k, B, tam_universo=None, max_cubre=None, semilla=0)` | parámetros | diccionario listo para JSON | O(N · max_cubre) |
| `main(argumentos)` | línea de comandos | escribe el archivo | — |

Uso: `python -m red.generador --N 50 --k 5 --B 100 --semilla 1 --salida casos/propios/sintetico_N50.json`

## Cómo funciona
Universo e1, …, e(tam_universo) (por omisión 2N). Cada nodo cubre entre 1 y max_cubre elementos distintos (por omisión 5), y su utilidad es log o raíz con a entre 1 y 10, redondeado a 2 decimales. Usa `random.Random(semilla)`: misma semilla, misma instancia.

## Por qué así
- Reproducible (CLAUDE.md, regla de reproducibilidad). El generador propio no usa la familia tabla, para que todas las instancias cumplan la concavidad.
- La ayuda de `--help` escribe `1 <= k < N` y no usa el símbolo de "menor o igual": ese carácter no existe en cp1252, y en una consola Windows con esa codificación `--help` terminaba con `UnicodeEncodeError`.

## Cómo modificarlo
- **Más solapamiento entre nodos:** bajar `--universo` o subir `--max-cubre`.
- **Serie de tamaños para la experimentación:** llamar `generar_instancia` en un ciclo sobre N (entrega posterior).

## Pruebas
- `test_ronda.py::test_generador_reproducible_y_valido`: misma semilla da la misma instancia y la ronda sale en OK.
- `pruebas/test_generador.py`: `--help` se puede imprimir en cp1252; la semilla 1 reproduce `casos/propios/sintetico_N040_k5.json` (N = 40, k = 5, B = 80); los coeficientes generados cumplen a > 0.

## Preguntas probables en la sustentación
- **¿Por qué semilla fija?** Para que cualquiera reproduzca exactamente los mismos casos y tiempos comparables.

_Última actualización: 2026-11-02 · ayuda imprimible en cp1252_
