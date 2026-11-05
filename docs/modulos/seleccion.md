# Ficha: `red/seleccion.py`

## Para qué existe
Resuelve la **Parte 2** de la ronda: elige k nodos que maximicen la utilidad conjunta f(S), que el oráculo define (cobertura o influencia). Como el problema es NP-difícil, usa el voraz aproximado del informe (sección 6.3).

## Funciones públicas
| Función | Recibe | Devuelve | Complejidad (tiempo · espacio) |
|---|---|---|---|
| `seleccionar_nodos(oraculo, V, k, traza=None)` | oráculo (cobertura o influencia), ids en orden creciente, k, traza opcional | `(S, valorS)`: S en el orden en que se eligió, valorS = f(S) | k·N − k(k−1)/2 llamadas a Δ = Θ(N·k) en todos los casos; en tiempo, O(k·(N + M)) con cobertura y O(k·(N + A)) con influencia · O(k) más el estado del oráculo (O(\|U\|) con cobertura, O(N) con influencia) sin traza; con traza, además Θ(N·k) |

M = Σ \|C_v\|, el total de elementos en los conjuntos. A = número de aristas del grafo.

**Interfaz que usa del oráculo:** `estado_inicial()`, `ganancia(v, estado)`, `agregar(estado, v)` y `valor(S)`. El voraz no sabe qué hay dentro del estado.

**Precondición** (en el docstring; aquí no se comprueba, para seguir el pseudocódigo, decisión 19): 1 ≤ k ≤ \|V\|, con V ordenado y sin repetidos. `ronda.py` ya lo valida antes de llamar. Si no se cumple: k > \|V\| lanza `KeyError: None`; k ≤ 0 devuelve S vacío; V desordenado rompe el desempate.

## Cómo funciona
1. **Línea 1:** S vacío, `cubiertos` = el estado inicial del oráculo y valorS ← f(∅) = 0. La variable conserva el nombre `cubiertos`, porque solo cambiaron las dos líneas del estado; con influencia guarda los q_w.
2. **Línea 2:** se repite k veces (un paso por cada nodo que entra).
3. **Líneas 3 a 7:** se recorre V en orden creciente y se salta lo que ya está en S. Por cada candidato v se pide Δ(v | S) al oráculo (**línea 5**, una llamada) y se guarda el mejor.
4. **Línea 8:** el mejor entra a S, `oraculo.agregar` actualiza el estado en su lugar y valorS sube en Δ.
5. **Línea 9:** si hay traza, se anotan los Δ de ese paso, el elegido y f(S).

## Por qué así
- **Δ sin recalcular f:** el estado guarda lo necesario para calcular Δ. Con cobertura es cub(S), así que Δ(v | S) = \|C_v ∖ cub(S)\| se calcula recorriendo solo C_v (informe 6.3). Con influencia son los q_w, y Δ recorre solo a v y sus vecinos (`docs/modulos/influencia.md`).
- **Tiempo con influencia, O(k·(N + A)):** en cada paso, las llamadas tocan a lo sumo Σ_v (1 + grado(v)) = N + 2A posiciones del estado. Con el grafo completo, A = N(N−1)/2, así que el tiempo es O(k·N²) aunque las llamadas sigan siendo Θ(N·k).
- **Empates por el menor índice** (decisión 6): como se recorre en orden creciente y se usa `>` estricto, un candidato con el mismo Δ no reemplaza al que ya estaba.
- `en_S` es un `set` para que preguntar "¿v ya está en S?" sea O(1).
- El ciclo de la línea 4 recorre todo V aunque salte a los de S: eso cuesta O(N) por paso, pero no son llamadas a f.
- **Por qué O(k·(N + M)) y no O(k·M)** (decisión 16): en cada uno de los k pasos se recorre V (N) y se revisan los elementos de cada candidato (hasta M). El formato permite conjuntos vacíos, y con M = 0 el tiempo igual crece con k·N (medido: 0.135 s con N = 20000 y 0.683 s con N = 80000, k = 10). Si ningún C_v es vacío, N ≤ M y queda O(k·M).
- **`aportes` solo se llena con traza** (decisión 11): los Δ de cada paso son para la evidencia. Si se llenaran siempre, la ejecución medida gastaría tiempo (se midió 28.5 % más) y Θ(N) de memoria en anotar. Por eso el espacio sin traza es O(k) más el estado del oráculo.

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

`pruebas/test_influencia.py` corre este mismo voraz con el oráculo de influencia: conteo de llamadas y cota (1 − 1/e) en 150 instancias, y el mismo S que cobertura con pesos 0 o 1. La regresión del caso de la profesora está en `pruebas/test_bateria.py`.

## Preguntas probables en la sustentación
- **¿Por qué Θ(N·k) y no solo O(N·k)?** Porque se hacen exactamente k·N − k(k−1)/2 llamadas, y como k < N eso está entre kN/2 y kN (encierro). No hay salida anticipada, así que mejor, peor y promedio coinciden.
- **¿El voraz da el óptimo?** No; el contraejemplo da 5 contra 6. Garantiza al menos 63 % del óptimo (Nemhauser, Wolsey y Fisher, 1978), porque la cobertura y la influencia son monótonas, submodulares y con f(∅) = 0. En el caso de la profesora, la fuerza bruta da 145.9072 y el voraz 145.5795 (99.8 %).
- **¿Dónde se usa la submodularidad?** En la garantía de aproximación, no en el funcionamiento del código.
- **¿Θ(N·k) es el tiempo?** Es el número de llamadas. El tiempo con cobertura es O(k·(N + M)), porque cada llamada cuesta O(\|C_v\|) y cada paso recorre V. Con influencia es O(k·(N + A)), porque cada llamada cuesta O(1 + grado(v)).
- **¿Qué cambió para aceptar el oráculo de influencia?** Solo las dos líneas que crean y actualizan el estado. El ciclo, el desempate y el conteo son los mismos.

_Última actualización: 2026-11-04 · el estado lo maneja el oráculo; tiempo y espacio con influencia_
