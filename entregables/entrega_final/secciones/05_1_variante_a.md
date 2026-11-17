## 5.1 Variante (a): selección con costos de participación

Cada nodo tiene un costo por participar en la ronda (comunicación, cómputo) y hay un presupuesto de participación por ronda. Ya no se eligen «a lo sumo k nodos», sino nodos cuyos costos quepan en ese presupuesto. La función f es la misma de la Parte 2.

| Componente | Definición |
|---|---|
| Entrada | N ∈ ℕ; el conjunto de nodos V = {1, …, N}; un oráculo f : 2ⱽ → ℝ≥0 monótono, submodular y con f(∅) = 0; para cada nodo v un costo de participación c(v) > 0; y un presupuesto de participación L ≥ 0. |
| Variable | S ⊆ V, el conjunto de nodos seleccionados. |
| Restricción | c(S) = Σ_{v∈S} c(v) ≤ L (restricción de mochila). |
| Objetivo | Maximizar f(S). |
| Salida | Un conjunto S que cumple la restricción, junto con f(S) y su costo c(S). |
| Tamaño de la entrada | N, el número de nodos. Como en la Parte 2, el costo de los algoritmos se mide en evaluaciones de f, y el tiempo depende además del tamaño de la descripción de f (A aristas con la cobertura por influencia, M = Σ \|C_v\| con la cobertura). L y los costos solo influyen a través del número máximo de nodos que caben, mín(N, ⌊L / c_mín⌋) ≤ N, así que ningún algoritmo de esta variante depende del valor numérico de L: no son pseudopolinomiales. |

**Supuesto ❓ (k y L).** El enunciado da costos y un presupuesto de participación, pero no dice si conviven con el cupo k. Se toma que la restricción c(S) ≤ L **reemplaza** a \|S\| ≤ k; no se usan las dos a la vez. Es la lectura más simple y la que usan las referencias de cobertura con presupuesto (Khuller, Moss y Naor, 1999).

**Supuesto ❓ (datos del caso de la docente).** c(v) es el campo `costo_participacion` de cada nodo y L es `presupuesto_costos_participacion_por_ronda`. En el caso oficial los costos van de 2 a 7 y L = 24 (`casos/profesora/entrada_G2_red_15_nodos.json`). Un costo ausente o ≤ 0, o un L ausente o negativo, rechaza el caso.

**Observación.** Con costos distintos ya no existe un tamaño fijo del óptimo: un nodo caro puede valer por varios baratos. Como f es monótona, sí existe un óptimo **maximal** (no le cabe ningún nodo más), y los algoritmos solo paran cuando no cabe nadie. Que los costos sean positivos importa: garantiza que todo subconjunto de un conjunto factible también es factible, y la fuerza bruta (§7.4) lo usa para podar.

**Relación con el escenario.** En el caso de la docente, el S de la solución base (k = 5) cuesta 23 ≤ 24. Con la variante, el voraz modificado elige 6 nodos con costo 21 (`resultados/variantes/a_profesora/`): al cambiar el cupo por un presupuesto entra un nodo más, porque hay nodos baratos.
