## 8.2 Algoritmos aproximados de la variante (a)

La variante (a) es NP-difícil (§6.9), así que se usan algoritmos aproximados. Se presentan tres: el voraz por cociente, que es la idea natural pero no tiene garantía; el voraz modificado, que la corrige sin costo extra y es el que corre en la ronda; y la enumeración parcial, que alcanza la cota 1 − 1/e de la Parte 2 a un costo mucho mayor y queda como referencia. En los tres la operación básica es la evaluación de f (una llamada a la ganancia marginal o al valor de un conjunto), como en §8.1, y los empates se rompen por el menor índice.

### 8.2.1 Voraz por cociente

**Idea.** Como en §8.1, se agrega un nodo por paso; pero ahora un nodo caro gasta más presupuesto, así que se compara la ganancia **por unidad de costo**, Δ(v | S)/c(v), y solo entre los nodos que todavía caben. Se para cuando no cabe ninguno. De paso, en el primer paso (S = ∅) se anota el mejor nodo solo, porque Δ(v | ∅) = f({v}); lo usa §8.2.2.

```
VORAZ-COCIENTE(V, f, c, L)
1  S ← ∅ ; valorS ← f(∅) ; costoS ← 0 ; mejorSolo ← NIL
2  repetir
3      mejor ← NIL ; mejorCociente ← −∞
4      para cada v ∈ V \ S, en orden creciente de índice, hacer
5          si costoS + c(v) ≤ L entonces                    # los que no caben se saltan sin evaluar
6              Δ ← f(S ∪ {v}) − valorS                      # evaluación de ganancia marginal
7              si S = ∅ y (mejorSolo = NIL o Δ > f({mejorSolo})) entonces mejorSolo ← v
8              si Δ / c(v) > mejorCociente entonces
9                  mejor ← v ; mejorΔ ← Δ ; mejorCociente ← Δ / c(v)
10     si mejor = NIL entonces salir del ciclo               # no cabe ningún nodo
11     S ← S ∪ {mejor} ; valorS ← valorS + mejorΔ ; costoS ← costoS + c(mejor)
12 devolver S, valorS, mejorSolo
```

**Función de eficiencia.** Operación básica: la evaluación de f (líneas 1 y 6). Sea s = |S| el tamaño final; como cada nodo cuesta al menos c_mín, s ≤ mín(N, ⌊L / c_mín⌋).

- **Paso 1: un paso del ciclo.** En el paso j el equipo tiene j − 1 nodos, así que se evalúan a lo sumo N − j + 1 candidatos (solo los que caben).
- **Paso 2: número de pasos.** Hay s pasos que agregan un nodo y uno final que no encuentra a nadie; en ese último no cabe ningún candidato y no se evalúa nada.
- **Paso 3: suma.** Evaluaciones ≤ 1 + Σ_{j=1}^{s} (N − j + 1) = **1 + s·N − s(s − 1)/2 ∈ O(N · mín(N, L/c_mín))**.
- **Paso 4: tiempo.** Con la cobertura por influencia cada evaluación de la línea 6 cuesta O(1 + grado(v)) y cada paso recorre los N nodos: un paso cuesta O(N + A) y el total **O((s + 1)·(N + A))**.

**Peor caso:** L ≥ Σ c, todo cabe siempre: s = N y cada paso evalúa a todos los que faltan: exactamente **1 + N(N + 1)/2 evaluaciones, Θ(N²)**. **Mejor caso:** L < c_mín: la línea 5 descarta a todos; 1 evaluación (f(∅)) y tiempo **Θ(N)**. Con costos 1 y L = k hace 1 + k·N − k(k − 1)/2 evaluaciones: las de §8.1 más f(∅). **Espacio:** S y la marca de pertenencia, **O(N)**, más el estado del oráculo.

**No tiene garantía constante.** Contraejemplo con cobertura: el nodo 1 cuesta 1 y cubre 2 elementos (cociente 2); el nodo 2 cuesta M = L y cubre otros 2M − 1 elementos (cociente (2M − 1)/M < 2). El voraz toma el nodo 1 y después el nodo 2 ya no cabe (1 + M > L): obtiene 2, contra OPT = 2M − 1. La razón 2/(2M − 1) tiende a 0 cuando M crece; con M = 10 es 2/19 ≈ 0,105 (`pruebas/test_variante_costos.py`, con M = 10, 100 y 1000; la tabla del contraejemplo está en §10.2.5). El defecto: un nodo barato con un cociente apenas mejor bloquea a uno caro que vale mucho más.

### 8.2.2 Voraz modificado (el que corre en la ronda)

**Idea.** Devolver el mejor entre el conjunto del voraz por cociente y el mejor nodo que cabe solo (Khuller, Moss y Naor, 1999). En el contraejemplo, el nodo 2 solo vale 2M − 1 y gana.

```
VORAZ-MODIFICADO(V, f, c, L)
1  (S, valorS, mejorSolo) ← VORAZ-COCIENTE(V, f, c, L)
2  si mejorSolo ≠ NIL y f({mejorSolo}) > valorS entonces devolver {mejorSolo}, f({mejorSolo})
3  devolver S, valorS                                        # en empate se queda el del cociente
```

**Función de eficiencia.** f({mejorSolo}) ya se calculó en el primer paso del cociente (línea 7 de VORAZ-COCIENTE), así que la línea 2 no evalúa nada: **las mismas evaluaciones que el voraz por cociente, ninguna extra**, con el mismo peor caso Θ(N²), el mismo mejor caso Θ(N) y espacio O(N). El experimento lo confirma: las series ic e im tardan lo mismo (pendientes 2,049 y 2,053 contra N, esperada 2,011; `resultados/experimentos/i_costos_cociente.csv` e `i_costos_modificado.csv`).

**Garantía.** Khuller, Moss y Naor (1999) probaron f(S) ≥ ((1 − 1/e)/2)·OPT ≈ 0,316·OPT para la cobertura con presupuesto. Tang et al. (2021) la mejoran a **0,405·OPT** para cualquier f monótona y submodular con restricción de mochila, y cierran el hueco que tenía la prueba de la cota 1 − 1/√e ≈ 0,393 de Khuller et al. En este informe se aplica la de Tang et al., porque la f de influencia del caso de la docente es submodular en general, no solo una cobertura.

### 8.2.3 Enumeración parcial (referencia)

**Idea.** El caso malo del voraz es equivocarse en los primeros nodos. Si se prueban todos los comienzos posibles de 3 nodos y se completa cada uno con el voraz por cociente, alguno de ellos empieza con los 3 nodos más valiosos del óptimo, y desde ahí el voraz ya no puede perder tanto. Los conjuntos de 1 y 2 nodos se evalúan directamente (Sviridenko, 2004).

```
ENUMERACION-PARCIAL(V, f, c, L)
1  caben ← {v ∈ V : c(v) ≤ L}
2  mejorS ← ∅ ; mejorValor ← f(∅)
3  para cada T ⊆ caben con |T| = 1 o |T| = 2, en orden lexicográfico, hacer
4      si c(T) ≤ L y f(T) > mejorValor entonces mejorS ← T ; mejorValor ← f(T)
5  para cada T ⊆ caben con |T| = 3, en orden lexicográfico, hacer
6      si c(T) ≤ L entonces
7          (S', valor') ← VORAZ-COCIENTE(V, f, c, L) empezando con S = T
8          si valor' > mejorValor entonces mejorS ← S' ; mejorValor ← valor'
9  devolver mejorS, mejorValor
```

**Función de eficiencia.** Operación básica: la evaluación de f. Sea F_j el número de subconjuntos factibles de tamaño j (F_j ≤ C(N, j)).

- **Paso 1:** f(∅), 1 evaluación (línea 2).
- **Paso 2:** líneas 3 y 4, F₁ + F₂ ≤ N + C(N, 2) evaluaciones (f solo se evalúa en los factibles).
- **Paso 3:** cada completación (línea 7) evalúa f(T) una vez y luego hace a lo sumo N − 3 pasos, el j-ésimo con a lo sumo N − 3 − j + 1 candidatos: ≤ 1 + (N − 3)(N − 2)/2 evaluaciones.
- **Paso 4:** hay F₃ ≤ C(N, 3) completaciones.
- **Suma:** evaluaciones ≤ 1 + N + C(N, 2) + C(N, 3)·(1 + (N − 3)(N − 2)/2). Como C(N, 3) ≈ N³/6 y (N − 3)(N − 2)/2 ≈ N²/2, el término dominante es ≈ N⁵/12: **O(N⁵)**. Con L pequeño cada completación tiene a lo sumo ⌊L/c_mín⌋ pasos y el total es O(N⁴ · mín(N, L/c_mín)).

**Peor caso:** L ≥ Σ c, la suma anterior con igualdad: **Θ(N⁵)**. **Mejor caso:** L < c_mín, caben = ∅: 1 evaluación y Θ(N). **Espacio:** O(N) más el estado del oráculo. **Garantía:** f(S) ≥ (1 − 1/e)·OPT, con O(n⁵) evaluaciones de f, para f monótona y submodular con restricción de mochila (Sviridenko, 2004); Khuller, Moss y Naor (1999) la prueban para la cobertura. Es la misma cota de la Parte 2, pero cuesta Θ(N⁵) frente a Θ(N²): por eso no corre en la ronda. En el experimento (serie j, N = 8 a 18) el tiempo creció con pendiente 0,96 contra la fórmula exacta del peor caso (`resultados/experimentos/j_costos_enumeracion.csv`).

### 8.2.4 Comparación contra el óptimo

Se compararon los tres aproximados con la fuerza bruta de §7.4 en el caso de la docente (N = 15, L = 24) y en 36 instancias aleatorias de influencia: N ∈ {10, 12, 14, 16}, densidad ∈ {0,3; 0,6; 1,0}, semillas 1, 2 y 3, costos enteros entre 1 y 5 y L = 12. Razón = f(S)/OPT. El cociente y el modificado dieron el mismo conjunto en todas las filas, así que comparten columna.

| Instancias | Razón mínima (cociente = modificado) | Razón media | Con razón < 1 | Razón de la enumeración | Evaluaciones: fuerza bruta / modificado / enumeración |
|---|---|---|---|---|---|
| Docente (N = 15) | 0,998084 | — | 1 de 1 | 1,0 | 4502 / 74 / 13117 |
| N = 10 (9 instancias) | 0,946839 | 0,981999 | 6 de 9 | 1,0 en todas | 217–606 / 35–50 / 417–2116 |
| N = 12 (9) | 0,974322 | 0,994199 | 6 de 9 | 1,0 en todas | 470–1421 / 44–64 / 1189–4744 |
| N = 14 (9) | 0,947397 | 0,979351 | 8 de 9 | 1,0 en todas | 727–2432 / 56–79 / 1888–7979 |
| N = 16 (9) | 0,962408 | 0,993519 | 5 de 9 | 1,0 en todas | 1876–3486 / 76–93 / 6057–11349 |
| Las 36 aleatorias | **0,946839** | 0,987267 | 25 de 36 | 1,0 en todas | — |

Fuente: `resultados/variantes/a_tabla_cota.csv` (generado por `scripts/tabla_cota_variante_a.py`) y la corrida de la docente en `resultados/variantes/a_profesora/`. Esta es la tabla de referencia de la batería de (a); §10.2.2 solo agrega dónde está la razón mínima.

**Lectura.**
- Ninguna instancia incumple las cotas: el modificado queda muy por encima de 0,405 (mínimo 0,946839) y la enumeración alcanzó el óptimo en las 37.
- En las 37 filas el voraz modificado devolvió el conjunto del cociente: el mejor nodo solo nunca ganó. El contraejemplo de §8.2.1 necesita un nodo que valga más que todo lo demás junto, y en estas instancias no lo hay. El nodo solo protege el peor caso; no es lo que mejora el promedio.
- El precio de la garantía 1 − 1/e: en la docente, 13117 evaluaciones de la enumeración contra 74 del modificado y 4502 de la fuerza bruta. Con N = 15 la enumeración ya es más cara que recorrer todos los factibles.
- **Docente.** El modificado elige S = {N05, N09, N14, N11, N15, N01} (en el orden en que entran), con f(S) = 145,9911 y costo 21 ≤ 24, en 74 evaluaciones (cota 1 + 6·15 − 6·5/2 = 76). El óptimo es {N05, N09, N11, N12, N14, N15}, con 146,27141 y costo 23. Después, el reparto de la Parte 1 sobre los 6 nodos da x = 4, 6, 6, 4, 5, 5 (en el mismo orden) y U = 95,955217 (`resultados/variantes/a_profesora/entrada_G2_red_15_nodos/traza.txt`). La comparación completa con la base está en §10.1.2.
