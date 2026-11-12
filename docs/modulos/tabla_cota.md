# Ficha: `scripts/tabla_cota.py`

## Para qué existe
Genera `resultados/cota/tabla_cota.csv`: para cada caso, f del voraz, OPT exacto (`red/exacto.py`), su razón y las cotas 1 − (1 − 1/k)^k y 1 − 1/e. Uso, desde la raíz: `python scripts/tabla_cota.py`. También genera `resultados/cota/tabla_cota_aleatoria.csv`: una batería de 45 instancias de influencia aleatorias (decisión 34), con las columnas caso, N, k, densidad, semilla, f_voraz, OPT, razon, cota_k, cota_e, cumple.

## Funciones públicas
| Función | Recibe | Devuelve | Complejidad |
|---|---|---|---|
| `rutas_de_los_casos()` | nada | casos propios con N <= 20 y el de la profesora | O(archivos) |
| `fila_de_un_caso(ruta)` | ruta de un caso | dict con las columnas del CSV | voraz Θ(N·k) llamadas a Δ + C(N, k) evaluaciones de f |
| `fila_de_una_instancia(inst, nombre)` | instancia ya leída | dict de una fila | igual que `fila_de_un_caso` |
| `bateria_aleatoria()` | nada | 45 filas (N ∈ {12,14,16,18,20}, k = 5, densidad ∈ {0.3, 0.6, 1.0}, semillas 1, 2, 3), en memoria | 45 × (voraz + C(N, 5) evaluaciones); C(20, 5) = 15504 |
| `escribir_csv(ruta, columnas, filas)` | ruta, columnas, filas | escribe el CSV | O(filas) |
| `main()` | nada | escribe los dos CSV; devuelve 0 si todos cumplen | suma de las anteriores |

## Cómo funciona
Lee el caso, corre `seleccionar_nodos` y `seleccionar_exacto` con oráculos distintos y calcula `razon = f_voraz / OPT` (1.0 si OPT = 0). `cumple` = f_voraz <= OPT y razon >= cota_k (tolerancia 1e-9). Valores redondeados a 6 decimales.

## Por qué así
La batería aleatoria no usa archivos: `generar_instancia_influencia` da el diccionario y `instancia_desde_diccionario` (el camino de entrada del formato de la profesora) crea la instancia; el nombre del caso es `aleatorio_N<N>_d<densidad>_s<semilla>`. B = 100 no influye en f ni en la selección. Tarda unos 6 s en total. Solo escribe en `resultados/cota/`; nunca en `resultados/profesora/`. No toca la ronda. Decisión 31.

## Cómo modificarlo
Para otros casos, cambiar `rutas_de_los_casos`. Si C(N, k) > 200000 el exacto lanza excepción.

## Pruebas
`pruebas/test_exacto.py` (casos propios y profesora) y `pruebas/test_tabla_cota.py` (batería aleatoria: 45 filas, reproducible, f_voraz <= OPT, razón en (0, 1], todas cumplen y columnas del CSV).

## Preguntas probables en la sustentación
- **¿Qué muestra la tabla?** Que en todos los casos la razón supera 1 − (1 − 1/k)^k y, por tanto, 1 − 1/e; el peor es el contraejemplo (5/6).

_Última actualización: 2026-11-12 · batería aleatoria (decisión 34)_
