# Ficha: `red/reparto.py`

## Para qué existe
Resuelve la **Parte 1** de la ronda: reparte B unidades entre los nodos que eligió la Parte 2 para maximizar Σ u_i(x_i). Es el voraz con montículo del informe (sección 6.4), y es **óptimo** porque cada u_i es creciente y cóncava.

## Funciones públicas
| Función | Recibe | Devuelve | Complejidad (tiempo · espacio) |
|---|---|---|---|
| `repartir_presupuesto(S, B, utilidades, traza=None)` | ids elegidos, B, diccionario id → utilidad, traza opcional | `ResultadoReparto` con `x`, `utilidad`, `extracciones` e `inserciones` | Peor caso O(N + B lg N); mejor caso Θ(N + B), con N = \|S\| · Θ(N) |

## Cómo funciona
1. **Línea 1:** x[i] ← 0 para cada nodo.
2. **Línea 2:** se arma la lista de parejas (−Δ_i(0), i) y `heapq.heapify` la vuelve montículo en O(N) (BUILD-HEAP).
3. **Línea 3:** se repite B veces.
4. **Línea 4:** `heappop` saca la raíz: el nodo cuya siguiente unidad aporta más. O(lg N).
5. **Línea 5:** ese nodo recibe la unidad.
6. **Línea 6:** se calcula Δ_i de su **siguiente** unidad y se vuelve a meter con `heappush`. O(lg N). Así el montículo siempre tiene N elementos.
7. **Línea 7:** traza (unidad, nodo, ganancia).
8. **Línea 8:** se suma la utilidad total.

## Por qué así
- **`heapq` es de mínimos** (decisión 7). Se guarda **−ganancia**: la ganancia más grande tiene el negativo más pequeño, así que queda en la raíz. **Pregunta probable de sustentación.**
- **Desempate por el menor índice** (decisión 6): si dos negativos son iguales, Python compara el segundo elemento de la pareja, el índice, y sale primero el menor.
- Las líneas 4 y 6 se podrían fusionar en `heapq.heapreplace` (el informe lo menciona). Se dejaron separadas para que el código se lea como el pseudocódigo; la complejidad es la misma.
- Los contadores `extracciones` e `inserciones` deben valer B; la verificación lo revisa.

## Cómo modificarlo
- **Desempatar por el mayor índice:** guardar `(-ganancia, -i)` en las líneas 42 y 53, y deshacer el signo del índice al sacar (línea 48).
- **Permitir gastar menos de B ("≤ B") con Δ negativas:** justo después de la línea 50 (`delta = -menos_delta`), si `delta < 0`, salir del ciclo (y quitar la verificación Σ x_i = B).
- **Tope por nodo (x_i ≤ c_i):** en la línea 53, no reinsertar al nodo si llegó a su tope (y detener el ciclo si el montículo queda vacío).
- Cualquier cambio aquí: correr `pruebas/test_reparto.py`.

## Pruebas
`pruebas/test_reparto.py`:
- Ejemplo del informe: P = 9, 5, 2, 1 y Q = 7, 6, 1, 0 con B = 4 da 27 en el orden P, Q, Q, P.
- Contraejemplo convexo: P = 1, 10 y Q = 3, 0 con B = 2 da 4; la fuerza bruta da 11 (sin concavidad, el voraz falla).
- Desempate, B = 0, error si no hay nodos, contadores = B.
- 150 instancias al azar con log y raíz: la utilidad coincide con la fuerza bruta (el voraz es óptimo).

## Preguntas probables en la sustentación
- **¿Por qué el negativo?** Porque `heapq` solo hace montículos de mínimos; con −ganancia, el mínimo es la mayor ganancia.
- **¿De dónde sale O(N + B lg N)?** heapify es O(N); el ciclo corre B veces y cada vuelta hace un pop y un push de O(lg N), porque el montículo siempre tiene N elementos (altura ⌊lg N⌋). Calcular Δ es O(1).
- **¿Por qué es óptimo?** Con concavidad, la lista de ganancias de cada nodo no aumenta; tomar siempre la mayor equivale a quedarse con las B mayores de todas las listas (argumento de intercambio, entrega posterior).

_Última actualización: 2026-11-02 · creación_
