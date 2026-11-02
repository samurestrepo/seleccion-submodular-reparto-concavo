# Ficha: `red/utilidades.py`

## Para qué existe
Define las funciones de utilidad u_i de la Parte 1 y su ganancia marginal Δ_i(x) = u_i(x + 1) − u_i(x), siempre en O(1). Cada familia sabe además revisar si es creciente y cóncava.

## Funciones públicas
| Función | Recibe | Devuelve | Complejidad (tiempo · espacio) |
|---|---|---|---|
| `UtilidadLog(a)` | a > 0 | u(x) = a·ln(1 + x) | O(1) · O(1) |
| `UtilidadRaiz(a)` | a > 0 | u(x) = a·√x | O(1) · O(1) |
| `UtilidadTabla(ganancias)` | lista Δ(0), Δ(1), … | u acumulada | construir O(L) · O(L); consultar O(1) |
| `.valor(x)`, `.ganancia(x)` | entero x ≥ 0 | u(x), Δ(x) | O(1) |
| `.revisar_forma(B, tolerancia)` | B y la tolerancia de los decimales | `None` si es creciente y cóncava; si no, el motivo | log y raíz O(1); tabla O(min(L, B)) |
| `.describir()` | — | los datos, como en el archivo de entrada | O(1) |
| `crear_utilidad(descripcion)` | `{"tipo": ..., ...}` | el objeto; `ValueError` o `KeyError` si los datos no sirven | O(1) (O(L) para tabla) |

Los constructores no validan, para poder crear a mano una utilidad convexa. Lo que viene de un archivo siempre pasa por `crear_utilidad`.

## Cómo funciona
- **log** y **raiz** son las familias del formato provisional (informe 6.5). Ambas son crecientes y cóncavas si a > 0.
- **tabla** recibe directamente la lista de ganancias de cada unidad, como en los ejemplos del informe (P: 9, 5, 2, 1). Guarda las sumas acumuladas para que u(x) salga en O(1). Después de la última unidad de la lista, cada unidad extra aporta 0.
- **`crear_utilidad`** exige que `a` sea un número finito > 0 y que las ganancias sean una lista de números finitos. `_es_numero_finito` rechaza `bool` (en Python `True` también es un `int`), cadenas, NaN, Infinity y enteros enormes que no caben en un float.

## Por qué así
- La familia **tabla** se agregó para poder probar los ejemplos del informe tal cual y el contraejemplo convexo (decisión 10). No exige concavidad al crearse; la revisa `revisar_forma`. **El contraejemplo convexo solo se muestra por llamada directa a `repartir_presupuesto`** (ver `test_contraejemplo_convexo`): por `ejecutar.py` esa entrada se rechaza sin correr los algoritmos (decisión 14).
- **`revisar_forma` en cada familia** (decisión 20): log y raíz no necesitan recorrer nada, porque con cálculo se sabe que su derivada es positiva y decrece: a/(1 + x) y a/(2√x). La tabla sí se recorre, pero solo una vez: después de la lista todo vale 0.
- **Solo las unidades entregables** (decisión 21): la tabla mira Δ(x) con x < B y compara con Δ(x + 1) solo si x + 1 < B. Δ(B) nunca se entrega.
- **a > 0 y no a ≥ 0** (decisión 17): con a = 0 la utilidad es constante, no creciente. Las tablas sí pueden tener Δ = 0, porque su cola vale 0 por diseño.
- Todas las familias tienen los mismos métodos, así que `reparto.py` y `verificacion.py` no saben cuál están usando.

## Cómo modificarlo
- **Nueva familia** (por ejemplo, a·x/(1 + x)): una clase con `valor`, `ganancia`, `revisar_forma` y `describir`, y un `if` más en `crear_utilidad`. Si Δ sigue siendo O(1), la complejidad no cambia. Agregar una prueba de que es creciente y cóncava.
- **Utilidad convexa para mostrar que el voraz falla:** crear `UtilidadTabla([1, 10])` y llamar directamente a `repartir_presupuesto` (ver `test_contraejemplo_convexo`). No se puede por archivo.
- **Permitir Δ negativas ("≤ B"):** quitar de `UtilidadTabla.revisar_forma` la comprobación `Δ(x) < 0`. Receta 2 de `docs/agente/GUIA_CAMBIOS.md`.

## Pruebas
- `pruebas/test_utilidades.py`: valores y ganancias de log y raíz; que las dos sean crecientes y cóncavas en 50 unidades; sumas acumuladas de tabla; error con un tipo desconocido.
- `pruebas/test_entrada.py`: `a` y `ganancias` inválidos dan `ErrorDeFormato`.
- `pruebas/test_verificacion.py`: `revisar_forma` de cada familia, sin recorrer B en log y raíz.

## Preguntas probables en la sustentación
- **¿Por qué Δ es O(1)?** Son dos evaluaciones de una fórmula cerrada (o dos consultas a una lista).
- **¿Qué pasa si una u_i no es cóncava?** El voraz deja de ser óptimo; la verificación de entrada lo reporta como FALLA y la ronda no corre.
- **¿Por qué log y raíz se revisan en O(1)?** Porque su forma depende solo del signo de a: la derivada es positiva y decreciente para todo x.

_Última actualización: 2026-11-02 · `revisar_forma`, a finito y > 0, ganancias finitas, contraejemplo solo por llamada directa_
