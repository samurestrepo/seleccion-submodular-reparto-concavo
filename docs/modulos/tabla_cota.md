# Ficha: `scripts/tabla_cota.py`

## Para qué existe
Genera `resultados/cota/tabla_cota.csv`: para cada caso, f del voraz, OPT exacto (`red/exacto.py`), su razón y las cotas 1 − (1 − 1/k)^k y 1 − 1/e. Uso, desde la raíz: `python scripts/tabla_cota.py`.

## Funciones públicas
| Función | Recibe | Devuelve | Complejidad |
|---|---|---|---|
| `rutas_de_los_casos()` | nada | casos propios con N <= 20 y el de la profesora | O(archivos) |
| `fila_de_un_caso(ruta)` | ruta de un caso | dict con las columnas del CSV | voraz Θ(N·k) llamadas a Δ + C(N, k) evaluaciones de f |
| `main()` | nada | escribe el CSV; devuelve 0 si todos cumplen | suma de las anteriores |

## Cómo funciona
Lee el caso, corre `seleccionar_nodos` y `seleccionar_exacto` con oráculos distintos y calcula `razon = f_voraz / OPT` (1.0 si OPT = 0). `cumple` = f_voraz <= OPT y razon >= cota_k (tolerancia 1e-9). Valores redondeados a 6 decimales.

## Por qué así
Solo escribe en `resultados/cota/`; nunca en `resultados/profesora/`. No toca la ronda. Decisión 31.

## Cómo modificarlo
Para otros casos, cambiar `rutas_de_los_casos`. Si C(N, k) > 200000 el exacto lanza excepción.

## Pruebas
Las mismas comprobaciones están en `pruebas/test_exacto.py`; el script no tiene prueba propia.

## Preguntas probables en la sustentación
- **¿Qué muestra la tabla?** Que en todos los casos la razón supera 1 − (1 − 1/k)^k y, por tanto, 1 − 1/e; el peor es el contraejemplo (5/6).

_Última actualización: 2026-11-09 · archivo nuevo_
