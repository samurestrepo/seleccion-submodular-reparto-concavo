# Ficha: `red/seleccion.py`

## Para qué existe
Resuelve la **Parte 2** de la ronda: elige k nodos que maximicen la cobertura f(S). Como el problema es NP-difícil, usa el voraz aproximado del informe (sección 6.3).

## Funciones públicas
| Función | Recibe | Devuelve | Complejidad (tiempo · espacio) |
|---|---|---|---|
| `seleccionar_nodos(oraculo, V, k, traza=None)` | oráculo de cobertura, ids en orden creciente, k, traza opcional | `(S, valorS)`: S en el orden en que se eligió, valorS = f(S) | k·N − k(k−1)/2 llamadas a Δ = Θ(N·k) en todos los casos; O(k·(N + M)) en tiempo con cobertura · O(k + \|U\|) adicional sin traza; con traza, además Θ(N·k) |

M = Σ \|C_v\|, el total de elementos en los conjuntos.

**Precondición** (en el docstring; aquí no se comprueba, para seguir el pseudocódigo, decisión 19): 1 ≤ k ≤ \|V\|, con V ordenado y sin repetidos. `ronda.py` ya lo valida antes de llamar. Si no se cumple: k > \|V\| lanza `KeyError: None`; k ≤ 0 devuelve S vacío; V desordenado rompe el desempate.

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
- **Por qué O(k·(N + M)) y no O(k·M)** (decisión 16): en cada uno de los k pasos se recorre V (N) y se revisan los elementos de cada candidato (hasta M). El formato permite conjuntos vacíos, y con M = 0 el tiempo igual crece con k·N (medido: 0.135 s con N = 20000 y 0.683 s con N = 80000, k = 10). Si ningún C_v es vacío, N ≤ M y queda O(k·M).
- **`aportes` solo se llena con traza** (decisión 11): los Δ de cada paso son para la evidencia. Si se llenaran siempre, la ejecución medida gastaría tiempo (se midió 28.5 % más) y Θ(N) de memoria en anotar. Por eso el espacio sin traza es O(k + \|U\|).

## Cómo modificarlo
- **Desempatar por el mayor índice:** cambiar `>` por `>=` en `# línea 6 del pseudocódigo` (`if delta > mejor_delta`). La complejidad no cambia. También cambia `reparto.py`: ver la receta 1 de `docs/agente/GUIA_CAMBIOS.md`.
- **Variante (a), costos por nodo:** elegir por Δ/costo y dejar de agregar cuando se acaba el presupuesto. Cambia la cota (ya no es 1 − 1/e). Pendiente de diseño.
- Cualquier cambio aquí: correr `pruebas/test_seleccion.py`.

## Pruebas
`pruebas/test_seleccion.py`:
- Ejemplo del informe: elige [1, 3] con 5 y los Δ de cada paso son 3, 2, 2 y 1, 2.
- Contraejemplo: {1,2,3,4}, {1,2,5}, {3,4,6} con k = 2 da 5; la fuerza bruta da 6 (el voraz **no** es exacto).
- Desempate por el menor índice.
- Conteo exacto: las llamadas son k·N − k(k−1)/2 en 4 tamaños.
- 200 instancias al azar: siempre f(S) ≥ (1 − 1/e)·OPT.
- Sin traza no se guardan los aportes (memoria medida con `tracemalloc`); con traza sí.

## Preguntas probables en la sustentación
- **¿Por qué Θ(N·k) y no solo O(N·k)?** Porque se hacen exactamente k·N − k(k−1)/2 llamadas, y como k < N eso está entre kN/2 y kN (encierro). No hay salida anticipada, así que mejor, peor y promedio coinciden.
- **¿El voraz da el óptimo?** No; el contraejemplo da 5 contra 6. Garantiza al menos 63 % del óptimo (Nemhauser, Wolsey y Fisher, 1978), porque la cobertura es monótona, submodular y f(∅) = 0.
- **¿Dónde se usa la submodularidad?** En la garantía de aproximación, no en el funcionamiento del código.
- **¿Θ(N·k) es el tiempo?** Es el número de llamadas. El tiempo con cobertura es O(k·(N + M)), porque cada llamada cuesta O(\|C_v\|) y cada paso recorre V.

_Última actualización: 2026-11-02 · `aportes` solo con traza; O(k·(N + M)); precondición documentada_
