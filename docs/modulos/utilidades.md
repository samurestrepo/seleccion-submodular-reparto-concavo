# Ficha: `red/utilidades.py`

## Para qué existe
Define las funciones de utilidad u_i de la Parte 1 y su ganancia marginal Δ_i(x) = u_i(x + 1) − u_i(x), siempre en O(1).

## Funciones públicas
| Función | Recibe | Devuelve | Complejidad (tiempo · espacio) |
|---|---|---|---|
| `UtilidadLog(a)` | a > 0 | u(x) = a·ln(1 + x) | O(1) · O(1) |
| `UtilidadRaiz(a)` | a > 0 | u(x) = a·√x | O(1) · O(1) |
| `UtilidadTabla(ganancias)` | lista Δ(0), Δ(1), … | u acumulada | construir O(L) · O(L); consultar O(1) |
| `.valor(x)`, `.ganancia(x)` | entero x ≥ 0 | u(x), Δ(x) | O(1) |
| `crear_utilidad(descripcion)` | `{"tipo": ..., ...}` | el objeto | O(1) (O(L) para tabla) |

## Cómo funciona
- **log** y **raiz** son las familias del formato provisional (informe 6.5). Ambas son crecientes y cóncavas si a > 0.
- **tabla** recibe directamente la lista de ganancias de cada unidad, como en los ejemplos del informe (P: 9, 5, 2, 1). Guarda las sumas acumuladas para que u(x) salga en O(1). Después de la última unidad de la lista, cada unidad extra aporta 0.

## Por qué así
- La familia **tabla** no está en el informe 6.5: se agregó para poder probar los ejemplos del informe tal cual y el contraejemplo convexo (decisión 10). No exige concavidad; la revisa `verificacion.py`.
- Todas las familias tienen los mismos métodos, así que `reparto.py` no sabe cuál está usando.

## Cómo modificarlo
- **Nueva familia** (por ejemplo, a·x/(1 + x)): una clase con `valor`, `ganancia` y `describir`, y un `if` más en `crear_utilidad`. Si Δ sigue siendo O(1), la complejidad no cambia. Agregar una prueba de que es creciente y cóncava.
- **Utilidad convexa para mostrar que el voraz falla:** usar `tabla` con ganancias que suben (ver `test_contraejemplo_convexo`).

## Pruebas
`pruebas/test_utilidades.py`: valores y ganancias de log y raíz; que las dos sean crecientes y cóncavas en 50 unidades; sumas acumuladas de tabla; error con un tipo desconocido.

## Preguntas probables en la sustentación
- **¿Por qué Δ es O(1)?** Son dos evaluaciones de una fórmula cerrada (o dos consultas a una lista).
- **¿Qué pasa si una u_i no es cóncava?** El voraz deja de ser óptimo; la verificación de entrada lo reporta como FALLA.

_Última actualización: 2026-11-02 · creación_
