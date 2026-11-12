# Ficha: `red/generador.py`

## Para qué existe
Genera instancias sintéticas en el formato provisional, con semilla fija. Las piden el enunciado (instancias de tamaño creciente) y las entregas de experimentación.

## Funciones públicas
| Función | Recibe | Devuelve | Complejidad |
|---|---|---|---|
| `generar_instancia(N, k, B, tam_universo=None, max_cubre=None, semilla=0)` | parámetros | diccionario listo para JSON | O(N · max_cubre) |
| `generar_instancia_influencia(N, k, B, densidad, semilla=0)` | parámetros y densidad en [0, 1] | diccionario en el formato de la profesora (`parametros`, `grafo`, `nodos`) | O(N²): recorre todos los pares |
| `main(argumentos)` | línea de comandos (`--formato {cobertura, influencia}`, `--densidad`) | escribe el archivo | — |

Uso: `python -m red.generador --N 50 --k 5 --B 100 --semilla 1 --salida casos/propios/sintetico_N50.json`
Influencia: `python -m red.generador --N 50 --k 5 --B 100 --formato influencia --densidad 0.1 --semilla 1 --salida caso.json` (por omisión `--formato cobertura`, que no cambia nada de lo anterior; `--densidad` por omisión 0.5 y solo se usa con influencia).

## Cómo funciona
Universo e1, …, e(tam_universo) (por omisión 2N). Cada nodo cubre entre 1 y max_cubre elementos distintos (por omisión 5), y su utilidad es log o raíz con a entre 1 y 10, redondeado a 2 decimales. Usa `random.Random(semilla)`: misma semilla, misma instancia.

### Formato de influencia (P-2)
Ids "N01", "N02", … con relleno de ceros (al menos 2 dígitos, más si N lo pide: "N001" con N = 120). Cada par i < j tiene una arista con probabilidad `densidad` (`random() < densidad`: con 1 siempre, con 0 nunca) y `peso_influencia` uniforme en [0,05; 0,70] con 2 decimales. Por nodo: `coeficiente_utilidad` uniforme en [1; 10] (2 decimales), `costo_participacion` entero en [1; 5] y `presupuesto_total_nodo` = B (el tope nunca limita en una ronda). `numero_rondas` = 1 y `presupuesto_costos_participacion_por_ronda` = 5·k (alcanza para cualquier k nodos). **El grafo del formato de la profesora NO es dirigido** (`_leer_grafo` rechaza {u, v} y {v, u} como arista repetida): con densidad 1 hay N(N−1)/2 aristas, no N(N−1). Pasa todas las verificaciones de `verificar_entrada` (pesos en [0, 1], a > 0, ids únicos, k < N).

## Por qué así
- Reproducible (CLAUDE.md, regla de reproducibilidad). El generador propio no usa la familia tabla, para que todas las instancias cumplan la concavidad.
- La ayuda de `--help` escribe `1 <= k < N` y no usa el símbolo de "menor o igual": ese carácter no existe en cp1252, y en una consola Windows con esa codificación `--help` terminaba con `UnicodeEncodeError`.

## Cómo modificarlo
- **Más solapamiento entre nodos:** bajar `--universo` o subir `--max-cubre`.
- **Serie de tamaños para la experimentación:** ya la hace `scripts/experimentos.py`, que llama a los dos generadores en un ciclo sobre N (decisión 32).

## Pruebas
- `test_ronda.py::test_generador_reproducible_y_valido`: misma semilla da la misma instancia y la ronda sale en OK.
- `pruebas/test_generador.py` (influencia): misma semilla da la misma instancia; densidad 1 da N(N−1)/2 aristas; densidad 0 da 0; rangos de pesos, coeficientes y costos; ids con ceros según N; todo lo generado pasa `leer_instancia` y `verificar_entrada` (densidad 0, 0.3 y 1); parámetros malos lanzan `ValueError`.
- `pruebas/test_generador.py`: `--help` se puede imprimir en cp1252; la semilla 1 reproduce `casos/propios/sintetico_N040_k5.json` (N = 40, k = 5, B = 80); los coeficientes generados cumplen a > 0.

## Preguntas probables en la sustentación
- **¿Por qué semilla fija?** Para que cualquiera reproduzca exactamente los mismos casos y tiempos comparables.

_Última actualización: 2026-11-12 · `generar_instancia_influencia`, `--formato` y `--densidad`_
