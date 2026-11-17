# 12. Resumen de eficiencia

La tabla reúne todos los algoritmos del proyecto. La deducción de cada T(n) está en su sección y en la ficha de su módulo (`docs/modulos/`); aquí solo se resume.

**Notación.** N es el número de nodos candidatos y k el cupo. B es el presupuesto de la ronda. U es el universo de la cobertura, M = Σ_v |C_v| y A es el número de aristas del grafo (influencia). L es el presupuesto de participación y c_mín el menor costo. F es el número de subconjuntos que caben en L. m = |S| ≤ k. A_S son las aristas con las dos puntas en S, y d(S) = Σ_{i∈S} grado(i). T es el número de rondas y R el de repeticiones medidas. ρ(k) = 1 − (1 − 1/k)ᵏ ≥ 1 − 1/e ≈ 0,632. **Exacto** significa que devuelve el óptimo en toda entrada válida; una **razón** ρ significa que devuelve al menos ρ·OPT en toda entrada válida.

## 12.1 Tabla general

| Algoritmo | Tamaño | Operación básica y cuántas | Tiempo | Espacio | Garantía | Serie (pendiente contra T) |
|---|---|---|---|---|---|---|
| **Base.** Voraz de selección, Parte 2 (`seleccionar_nodos`) | (N, k) | llamadas a Δ: exactamente k·N − k(k − 1)/2, Θ(N·k), igual en el mejor, el peor y el caso promedio | O(k·(N + M)) con cobertura; O(k·(N + A)) con influencia | O(k) + el estado del oráculo (O(\|U\|) con cobertura, O(N) con influencia); Θ(N·k) más con traza | razón ρ(k) | a, b y c (1,02; 1,04; 1,01) |
| **Base.** Fuerza bruta, Parte 2 (`seleccionar_exacto`) | (N, k) | evaluaciones de f: exactamente C(N, k) | O(C(N, k)·(N + A)) con influencia | O(k) + el estado del oráculo | exacto | f y g (1,09; 0,98) |
| **Base.** Voraz de reparto con montículo, Parte 1 (`repartir_presupuesto`) | (N = \|S\|, B) | extracciones e inserciones: a lo sumo B de cada una | Θ(N + B(1 + lg N)) sin topes, para toda entrada; peor caso O(N + B lg N) | Θ(N) | exacto si las u_i son crecientes y cóncavas | d y e (2,18; 0,97) |
| **Base.** PD de reparto, Parte 1 (`repartir_pd`) | (N, B) | candidatos t: Σ_i Σ_b (mín(c_i, b) + 1) | peor caso Θ(N·B²) (topes ≥ B); mejor caso Θ(N·B) (topes 0) | Θ(N·B) | exacto con cualquier u_i | h (0,94) |
| **Base.** Ronda completa | (N, k, B) | la suma de los dos voraces | O(k·(N + M) + B(1 + lg k)) con cobertura; O(k·(N + A) + B(1 + lg k)) con influencia | O(k + \|U\|) con cobertura; O(N) con influencia | la de cada parte | — |
| **(a)** Fuerza bruta con presupuesto, backtracking con poda (`seleccionar_exacto_costos`) | (N, L) | evaluaciones de f: exactamente F ≤ 2ᴺ | O(F·(N + A)); peor caso Θ(2ᴺ) evaluaciones (L ≥ Σ c); mejor caso 1 evaluación y Θ(N) (L < c_mín) | O(N) + el estado del oráculo | exacto | k (1,02) |
| **(a)** Voraz por cociente (`voraz_por_cociente`) | (N, L) | evaluaciones de f: ≤ 1 + \|S\|·N − \|S\|(\|S\| − 1)/2, con \|S\| ≤ mín(N, ⌊L/c_mín⌋) | O(\|S\|·(N + A)); peor caso 1 + N(N + 1)/2 = Θ(N²) evaluaciones; mejor caso 1 | O(N) + el estado del oráculo | ninguna constante (razón 2/(2M − 1) → 0) | ic (1,02) |
| **(a)** Voraz modificado (`voraz_modificado`, el de la ronda) | (N, L) | las mismas evaluaciones del voraz por cociente: cero extra | igual que el voraz por cociente | O(N) + el estado del oráculo | razón 0,405 (Tang et al., 2021); (1 − 1/e)/2 ≈ 0,316 según Khuller, Moss y Naor (1999) | im (1,02) |
| **(a)** Enumeración parcial (`enumeracion_parcial`) | (N, L) | evaluaciones de f: O(N⁴·mín(N, L/c_mín)) ⊆ O(N⁵); peor caso E(N) = 1 + N + C(N, 2) + C(N, 3)·(1 + (N − 3)(N − 2)/2) | O(N³·\|S\|·(N + A)) | O(N) + el estado del oráculo | razón 1 − 1/e (Sviridenko, 2004) | j (0,96) |
| **(b)** T rondas, los dos voraces por ronda (`ejecutar_rondas`) | (N, k, B, T) | por ronda: k_r·n_r − k_r(k_r − 1)/2 llamadas a Δ y a lo sumo B extracciones | O(T·[(R + 1)·(k·(N + A) + B lg k) + N]) sin el exacto; con R = 1, O(T·(k·(N + A) + B lg k)); con el exacto de cada ronda, + O(T·C(N, k)·(N + A)) | O(N + A) por oráculo + O(N) del restante + O(T·(k·N + B)) del resultado | razón ρ(k_r) en cada ronda; **ninguna** sobre las T rondas juntas | l (1,06) |
| **(c1)** Voraz de reparto con a'_i (`repartir_c1`) | (m, B, d(S)) | restringir el grafo a S + las operaciones del montículo | Θ(m + d(S)) + Θ(m + B(1 + lg m)) | Θ(m + A_S) | exacto | — |
| **(c2)** Voraz unidad por unidad (`repartir_c2`) | (m, B, A_S) | ganancias recalculadas: m + B·m con S completo y m + B sin aristas en S | O(m + d(S) + B·(m + A_S)); peor caso (S completo) O(B·k²); mejor caso (sin aristas en S) Θ(m + B·m) | Θ(m + A_S) | razón ρ(B) ≥ 1 − 1/e | m (1,06) |
| **(c1 y c2)** Exacto por enumeración de repartos (`repartir_exacto`) | (m, B) | repartos evaluados: R_B = C(B + m, m) sin topes (menos con topes) | Θ(m·B) para contarlos + O(R_B·(m + A_S)) | O(m + A_S) | exacto | — |

Notas:
- La serie d tiene una pendiente de 2,18 contra T, la única fuera del rango de 0,94 a 1,09. Lo explica sobre todo que T suma N y B lg N con el mismo peso, cuando en la máquina el término en N cuesta unas 6 veces más por unidad (sección 11.3).
- Los exactos de las variantes (fuerza bruta con presupuesto, enumeración de repartos y el exacto de cada ronda en (b)) se niegan a correr, sin evaluar nada, si el número de subconjuntos o de repartos pasa de 200 000. Con la opción `--limite-repartos` se puede subir ese límite para la enumeración.

## 12.2 Los mismos algoritmos en el caso de la docente

N = 15, k = 5, B = 30, topes de 18, L = 24, T = 3 y β = 0,2. Las operaciones salen de los `salida.json` de `resultados/profesora/` y `resultados/variantes/`, y de `resultados/variantes/a_tabla_cota.csv`. Los tiempos son medianas de 21 repeticiones, salvo los de la enumeración, que corre una sola vez.

| Algoritmo | Operaciones | Tiempo | Valor obtenido / OPT |
|---|---|---|---|
| Voraz de selección | 65 llamadas a Δ | 0,171 ms | 145,5795 / 145,9072 = 0,9978 |
| Fuerza bruta, Parte 2 | 3 003 evaluaciones | no se registra | exacto |
| Voraz de reparto | 30 extracciones + 30 inserciones | 0,038 ms | exacto: 88,5640 |
| PD de reparto | 2 090 candidatos (por fórmula, comprobado al correrla) | no se registra | exacto: 88,5640 |
| (a) Fuerza bruta con presupuesto | 4 502 factibles | no se registra | exacto: 146,2714 |
| (a) Voraz modificado | 74 evaluaciones | 0,223 ms | 145,9911 / 146,2714 = 0,9981 |
| (a) Enumeración parcial | 13 117 evaluaciones | no se registra | 146,2714 (alcanza el OPT) |
| (b) 3 rondas | 65 + 60 + 55 llamadas a Δ; exacto de 3 003 + 2 002 + 1 287 | 0,15 a 0,28 ms por ronda (Parte 2) | razones 0,9978; 1; 1 |
| (c1) Voraz con a'_i | 30 extracciones + 30 inserciones | 0,057 ms | exacto: 91,5670 |
| (c2) Voraz unidad por unidad | 30 pasos, 155 ganancias recalculadas | 1,528 ms | 99,2470 / 99,2470 = 1 |
| (c) Enumeración de repartos | 302 792 repartos | 1,19 s (c1) y 3,52 s (c2) | exacto |

La tabla muestra la diferencia de escala entre técnicas en una instancia pequeña. El voraz de selección hace 65 operaciones donde la fuerza bruta hace 3 003. En c2, el voraz tarda 1,5 ms y la enumeración 3,5 s, más de 2 000 veces más, y en este caso los dos dan el mismo reparto.
