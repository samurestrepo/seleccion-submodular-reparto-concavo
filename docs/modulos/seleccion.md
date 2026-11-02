# Ficha: `red/seleccion.py`

## Para qué existe
Resuelve la **Parte 2** de la ronda: elige k nodos que maximicen la cobertura f(S). Como el problema es NP-difícil, usa el voraz aproximado del informe (sección 6.3).

## Funciones públicas
| Función | Recibe | Devuelve | Complejidad (tiempo · espacio) |
|---|---|---|---|
| `seleccionar_nodos(oraculo, V, k, traza=None)` | oráculo de cobertura, ids en orden creciente, k, traza opcional | `(S, valorS)`: S en el orden en que se eligió, valorS = f(S) | k·N − k(k−1)/2 llamadas a Δ = Θ(N·k) en todos los casos; O(k·M) en tiempo con cobertura · O(k + \|U\|) adicional |

## Cómo funciona
1. **Línea 1:** S vacío, `cubiertos` vacío y valorS ← f(∅) = 0.
2. **Línea 2:** se repite k veces (un paso por cada nodo que entra).
3. **Líneas 3 a 7:** se recorre V en orden creciente y se salta lo que ya está en S. Por cada candidato v se pide Δ(v | S) al oráculo (**línea 5**, una llamada) y se guarda el mejor.
4. **Línea 8:** el mejor entra a S, sus elementos pasan a `cubiertos` y valorS sube en Δ.
5. **Línea 9:** si hay traza, se anotan los Δ de ese paso, el elegido y f(S).

## Por qué así
- **Δ sin recalcular la unión:** `cubiertos` guarda cub(S), así que Δ(v | S) = \|C_v ∖ cub(S)\| se calcula recorriendo solo C_v (informe 6.3).
- **Empates por el menor índice** (decisión 6): como se recorre en orden creciente y se usa `>` estricto, un candidato con el mismo Δ no reemplaza al que ya estaba.
- `en_S` es un `set` para que preguntar "¿v ya está en S?" sea O(1).
- El ciclo de la línea 4 recorre todo V aunque salte a los de S: eso cuesta O(N) por paso, pero no son llamadas a f.

## Cómo modificarlo
- **Desempatar por el mayor índice:** cambiar `>` por `>=` en la línea 34 (`if delta > mejor_delta`). La complejidad no cambia.
- **Variante (a), costos por nodo:** elegir por Δ/costo y dejar de agregar cuando se acaba el presupuesto. Cambia la cota (ya no es 1 − 1/e). Pendiente de diseño.
- Cualquier cambio aquí: correr `pruebas/test_seleccion.py`.

## Pruebas
`pruebas/test_seleccion.py`:
- Ejemplo del informe: elige [1, 3] con 5 y los Δ de cada paso son 3, 2, 2 y 1, 2.
- Contraejemplo: {1,2,3,4}, {1,2,5}, {3,4,6} con k = 2 da 5; la fuerza bruta da 6 (el voraz **no** es exacto).
- Desempate por el menor índice.
- Conteo exacto: las llamadas son k·N − k(k−1)/2 en 4 tamaños.
- 200 instancias al azar: siempre f(S) ≥ (1 − 1/e)·OPT.

## Preguntas probables en la sustentación
- **¿Por qué Θ(N·k) y no solo O(N·k)?** Porque se hacen exactamente k·N − k(k−1)/2 llamadas, y como k < N eso está entre kN/2 y kN (encierro). No hay salida anticipada, así que mejor, peor y promedio coinciden.
- **¿El voraz da el óptimo?** No; el contraejemplo da 5 contra 6. Garantiza al menos 63 % del óptimo (Nemhauser, Wolsey y Fisher, 1978), porque la cobertura es monótona, submodular y f(∅) = 0.
- **¿Dónde se usa la submodularidad?** En la garantía de aproximación, no en el funcionamiento del código.

_Última actualización: 2026-11-02 · creación_
