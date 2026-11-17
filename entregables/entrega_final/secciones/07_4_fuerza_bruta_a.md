## 7.4 Algoritmo exacto de la variante (a): fuerza bruta con presupuesto

**Idea.** Se recorren todos los subconjuntos factibles, se evalúa f en cada uno y se guarda el mejor. Como ya no hay un tamaño fijo, el espacio de búsqueda son los 2ᴺ subconjuntos de V, no los C(N, k) de §7.3. Se recorren con una búsqueda en profundidad en orden lexicográfico de índices (∅, {1}, {1, 2}, {1, 2, 3}, …, {2}, …) y con **poda**: si al agregar v el costo pasa de L, no se exploran los conjuntos que contienen a v desde ahí, porque los costos son positivos y ninguno cabría. En un empate gana el primer conjunto en ese orden.

```
FUERZA-BRUTA-COSTOS(V, f, c, L)
1  si 2ᴺ > 200000 entonces negarse sin evaluar nada
2  mejorS ← ∅ ; mejorValor ← −∞ ; evaluaciones ← 0
3  EXPLORAR(∅, 0, 1)
4  devolver mejorS, mejorValor, evaluaciones

EXPLORAR(S, costoS, desde)
5  valor ← f(S) ; evaluaciones ← evaluaciones + 1          # evaluación de f
6  si valor > mejorValor entonces mejorS ← S ; mejorValor ← valor
7  para p ← desde hasta N hacer
8      v ← V[p]
9      si costoS + c(v) ≤ L entonces                         # poda
10         EXPLORAR(S ∪ {v}, costoS + c(v), p + 1)
```

**Por qué es correcto.** Cada conjunto S = {v₁ < v₂ < … < v_j} se alcanza por un único camino: agregando sus elementos en orden creciente. Si S es factible, todos sus prefijos también lo son (los costos son positivos), así que la poda de la línea 9 nunca corta ese camino: se visitan **todos** los factibles y solo ellos. Por eso devuelve OPT.

**Límite.** La línea 1 se niega si 2ᴺ > 200000, es decir, con N ≥ 18. Es el mismo límite de la fuerza bruta de §7.3, aplicado a 2ᴺ.

**Función de eficiencia.** La operación básica es la evaluación de f (línea 5). Sea F el número de subconjuntos factibles, incluido ∅; F ≤ 2ᴺ.

- **Paso 1: evaluaciones.** Cada llamada a EXPLORAR evalúa f una vez, y hay exactamente una llamada por subconjunto factible. Evaluaciones = F.
- **Paso 2: trabajo del ciclo.** Cada llamada recorre a lo sumo N posiciones en las líneas 7 a 9, cada una en O(1). En total, a lo sumo F·N iteraciones.
- **Paso 3: costo de cada evaluación.** Con la cobertura por influencia, f(S) se calcula desde cero en O(N + Σ_{v∈S} (1 + grado(v))) ⊆ O(N + A); con la cobertura, O(N + M).
- **Suma.** T(N) = F·O(N + A) + O(F·N) = **O(F·(N + A))**, con F evaluaciones de f.

**Peor caso:** si L ≥ Σ_v c(v), todo cabe y F = 2ᴺ: exactamente 2ᴺ evaluaciones, **Θ(2ᴺ)**, y tiempo O(2ᴺ·(N + A)). **Mejor caso:** si L < c_mín no cabe ningún nodo; solo se evalúa ∅ (1 evaluación) y la línea 7 recorre los N nodos sin entrar: **Θ(N)**. **Caso promedio:** depende de cuántos subconjuntos caben, es decir, de la distribución de los costos frente a L; no se da una fórmula. En el caso de la docente (N = 15, L = 24) caben F = 4502 de los 2¹⁵ = 32768 subconjuntos, un 13,7 % (`resultados/variantes/a_tabla_cota.csv`, columna `eval_exacto`).

**Caso particular.** Con costos 1 y L = k los factibles son los conjuntos de tamaño ≤ k, y F = Σ_{j=0}^{k} C(N, j): un poco más que las C(N, k) evaluaciones de §7.3, que solo recorre los de tamaño exactamente k (ahí la monotonía garantiza que basta).

**Espacio.** La recursión tiene profundidad a lo sumo \|S\| + 1 ≤ N + 1 y guarda S y mejorS: **O(N)** adicional, más el estado del oráculo.

**En el caso de la docente.** OPT = 146,27141 con S* = {N05, N09, N11, N12, N14, N15}, costo 23 ≤ 24, en 4502 evaluaciones (`resultados/variantes/a_tabla_cota.csv`; el conjunto S* se obtiene con `seleccionar_exacto_costos` sobre `casos/profesora/entrada_G2_red_15_nodos.json`). En el experimento de tiempos (serie k, N = 8 a 16 con L ≥ Σ c), el tiempo medido creció con pendiente 1,02 contra 2ᴺ·(N + A) en escala log-log (`resultados/experimentos/k_costos_fuerza_bruta.csv`).
