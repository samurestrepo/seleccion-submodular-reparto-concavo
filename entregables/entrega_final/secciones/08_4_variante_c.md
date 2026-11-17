## 8.4 Algoritmos de la variante (c): vecinos que alteran la utilidad

La selección no cambia (S es el del voraz de §8.1); cambia el reparto. Se usan las dos formulaciones de §5.3. La pregunta de esta sección es si el voraz de §7.1 sigue siendo exacto, y la respuesta depende de las cuatro hipótesis de la prueba de §7.1.1, definidas en §2.1: **H1** separación por nodo (la utilidad total es una suma de funciones de un solo xᵢ), **H2** monotonía, **H3** concavidad y **H4** topes enteros por nodo.

### 8.4.1 Modelo c1: se reduce a la Parte 1 y sigue siendo exacto

**Reducción.** Se reagrupa U₁ por el nodo que gasta. El término β·w_ij·ln(1 + xᵢ) aparece en la utilidad de cada vecino j ∈ S de i; como el grafo es no dirigido (w_ij = w_ji), todos los términos que dependen de xᵢ se juntan en uno:

U₁(x) = Σ_{j∈S} [ a_j·ln(1 + x_j) + Σ_{i∈N_S(j)} β·w_ij·ln(1 + xᵢ) ] = Σ_{i∈S} a'ᵢ·ln(1 + xᵢ), con **a'ᵢ = aᵢ + β·Σ_{j∈N_S(i)} w_ij**.

Es la Parte 1 con otros coeficientes. Se cumplen las cuatro hipótesis de §7.1.1:

- **H1 (separación):** después de reagrupar, U₁ es una suma de funciones de un solo xᵢ.
- **H2 (monotonía):** a'ᵢ ≥ aᵢ > 0, porque β ≥ 0 y w_ij ≥ 0, y ln(1 + x) es creciente.
- **H3 (concavidad):** a'ᵢ·ln(1 + x) es cóncava, porque a'ᵢ > 0 y ln es cóncava.
- **H4 (topes):** los topes cᵢ son los mismos de la Parte 1.

Por lo tanto el voraz con montículo de §7.1 sobre las utilidades a'ᵢ·ln(1 + x) es **exacto**, con la misma prueba por intercambio. El algoritmo es: calcular los a'ᵢ y llamar a REPARTIR-PRESUPUESTO sin cambiarlo.

```
REPARTIR-C1(S, B, a, w, β, c)
1  para cada i ∈ S hacer Nᵢ ← {(j, w_ij) : j vecino de i y j ∈ S}   # restringir el grafo a S
2  para cada i ∈ S hacer a'ᵢ ← aᵢ + β·Σ_{(j, w)∈Nᵢ} w
3  devolver REPARTIR-PRESUPUESTO(S, B, u' con u'ᵢ(x) = a'ᵢ·ln(1 + x), c)   # §7.1
```

**Función de eficiencia.** Sea m = |S|.

- **Paso 1: restringir el grafo (línea 1).** Para saber cuáles vecinos de i están en S hay que mirar **todos** los vecinos de i: Θ(m + d(S)), con d(S) = Σ_{i∈S} grado(i).
- **Paso 2: los a'ᵢ (línea 2).** Cada arista dentro de S se mira desde sus dos extremos: Θ(m + A_S) ⊆ O(m + d(S)).
- **Paso 3: el reparto (línea 3).** §7.1.2 con m nodos: Θ(m + B(1 + lg m)) sin topes; con topes, peor caso O(m + B lg m) y mejor caso Θ(m).
- **Suma:** **T = Θ(m + d(S)) + Θ(m + B(1 + lg m))** sin topes; con m ≤ k, O(k + d(S) + B lg k). **Espacio:** Θ(m + A_S) (el grafo restringido y los a'ᵢ) más el montículo de §7.1.

**Docente** (β = 0,2, S = N11, N14, N09, N15, N13; grafo completo: A_S = 10, d(S) = 70). a' = 7,96; 10,48; 10,26; 9,70; 8,54. El voraz da x = 5, 7, 7, 6, 5 y U₁ = 91,566977, igual al óptimo por enumeración de los 302792 repartos posibles (`resultados/variantes/c1_profesora/entrada_G2_red_15_nodos/salida.json`). En este caso el reparto coincide con el de la solución base; lo que cambia es la utilidad (88,563953 sin vecinos). La comparación de c1 y c2 con la base, con tiempos, está en §10.1.4.

### 8.4.2 Modelo c2: falla H1 y el voraz deja de ser exacto

**Qué hipótesis se rompe.** En U₂ = Σ_j a_j·ln(1 + z_j), con z_j = x_j + β·Σ_{i∈N_S(j)} w_ij·xᵢ, cada término mezcla el x de un nodo con los de sus vecinos: **U₂ no se separa por nodo y falla H1.** Las otras tres siguen valiendo: U₂ es creciente en cada xᵢ (H2), es cóncava porque compone ln con una función lineal (H3) y los topes son los mismos (H4). Pero la prueba de §7.1.1 usa H1: compara la ganancia de cada nodo como si dependiera solo de lo que ese nodo ya recibió. Aquí lo que aporta una unidad a i cambia cuando reciben sus vecinos, y el intercambio de unidades deja de funcionar. Por la misma razón tampoco aplica la programación dinámica de §7.2, cuyo estado M[i][b] supone que la utilidad se suma nodo por nodo.

**Contraejemplo.** Trayecto 1 – 2 – 3 con a = (3, 2, 3), w₁₂ = w₂₃ = 1, β = 0,2, B = 2 y sin topes.

- Primera unidad: al nodo central le rinde 2·ln 2 + 2·(3·ln 1,2) ≈ 2,4802, porque también sube a los dos extremos; a cada extremo le rinde 3·ln 2 + 2·ln 1,2 ≈ 2,4441. El voraz se la da al centro.
- Segunda unidad: empatan los nodos 1 y 3 y gana el menor índice. Voraz: x = (1, 1, 0), U₂ ≈ **4,489251**.
- Óptimo: x = (1, 0, 1), U₂ = 6·ln 2 + 2·ln 1,4 ≈ **4,831828**. Razón ≈ 0,9291.

El voraz elige bien la primera unidad, pero esa elección no forma parte del óptimo de dos unidades: eso es lo que H1 impedía en la Parte 1. (Fuente: la ficha `docs/modulos/variante_vecinos.md` y la prueba del contraejemplo en `pruebas/test_variante_vecinos.py`; las ganancias paso a paso están en §10.2.6.)

**Algoritmo: voraz unidad por unidad.** Cada unidad va al nodo que todavía no llegó a su tope y cuya unidad siguiente aumenta más U₂. Se mantiene z para calcular cada ganancia sin recalcular U₂ entera.

```
REPARTIR-C2(S, B, a, w, β, c)
1  para cada i ∈ S: xᵢ ← 0 ; zᵢ ← 0
2  activos ← {i ∈ S : cᵢ > 0} ; para cada i activo: Δᵢ ← GANANCIA(i, z)
3  para t ← 1 hasta B hacer
4      si activos = ∅ entonces terminar                      # todos en su tope: sobra presupuesto
5      i ← el activo de mayor Δᵢ (empate: menor índice)      # barrido lineal, O(m)
6      xᵢ ← xᵢ + 1 ; zᵢ ← zᵢ + 1 ; z_j ← z_j + β·w_ij para cada j ∈ N_S(i)
7      si xᵢ = cᵢ entonces sacar i de activos
8      para cada l activo en {i} ∪ N_S(i) ∪ N_S(N_S(i)) hacer Δ_l ← GANANCIA(l, z)
9  devolver x y U₂(x) = Σ_j a_j·ln(1 + z_j), recalculada desde x
```

GANANCIA(l, z) = a_l·[ln(2 + z_l) − ln(1 + z_l)] + Σ_{j∈N_S(l)} a_j·[ln(1 + z_j + β·w_lj) − ln(1 + z_j)], en O(1 + grado_S(l)).

**Función de eficiencia.** Operaciones básicas: las ganancias calculadas (GANANCIA) y los nodos revisados en el barrido de la línea 5. Sea m = |S|.

- **Paso 1: preparación.** Restringir el grafo a S, Θ(m + d(S)); la línea 1, Θ(m); las ganancias iniciales de la línea 2, Σ_l (1 + grado_S(l)) = m + 2·A_S, O(m + A_S).
- **Paso 2: una unidad.** Línea 5: un recorrido de los m nodos, Θ(m). Línea 6: O(1 + grado_S(i)). Línea 8: a lo sumo todos los nodos, cada uno a O(1 + grado_S(l)): O(m + A_S).
- **Paso 3: B unidades.** B·O(m + A_S).
- **Paso 4: final.** Línea 9: O(m + A_S).
- **Suma:** **T = O(m + d(S) + B·(m + A_S))**.

**Peor caso:** S completo (como en la docente), A_S = m(m − 1)/2: en cada unidad todos están a distancia ≤ 1, se recalculan las m ganancias a Θ(m) cada una: **Θ(B·m²) ⊆ O(B·k²)**. Si nadie llega a su tope, se calculan exactamente m + B·m ganancias y se revisan B·m nodos. **Mejor caso:** sin aristas dentro de S (A_S = 0): cada unidad solo recalcula la ganancia de i y domina el barrido: Θ(m + d(S) + B·m), con m + B ganancias. **Espacio:** Θ(m + A_S) (el grafo restringido, x, z, las ganancias y los activos).

**Docente** (β = 0,2): 30 unidades, 155 ganancias calculadas (= 5 + 30·5) y 150 nodos revisados (= 30·5). El voraz da x = 4, 8, 7, 6, 5 (N11, N14, N09, N15, N13) y U₂ = 99,247037, igual al óptimo por enumeración (razón 1,0; cota ρ(30) ≈ 0,6383). El reparto de la solución base, evaluado con U₂, da 99,224645: un poco menos (`resultados/variantes/c2_profesora/entrada_G2_red_15_nodos/salida.json`). El reparto tardó 1,53 ms (mediana de 21 repeticiones) contra 0,057 ms del de c1 (`resultados/variantes/c2_profesora/resumen.csv` y `c1_profesora/resumen.csv`). En el experimento (serie m: S completo de 10 nodos, B = 250 a 4000) el tiempo creció con pendiente 1,046 contra B (esperada 0,988) (`resultados/experimentos/m_c2_varia_B.csv`).

### 8.4.3 La cota del voraz de c2, en 3 pasos

Aunque no es exacto, el voraz de c2 conserva una cota del tipo de la Parte 2:

U₂(voraz) ≥ ρ(B)·OPT = (1 − (1 − 1/B)ᴮ)·OPT ≥ (1 − 1/e)·OPT.

1. **U₂ es monótona y tiene rendimientos decrecientes en enteros (§2.1).** Sea d_ij lo que sube z_j cuando i recibe una unidad: d_ii = 1, d_ij = β·w_ij si j ∈ N_S(i), y 0 si no. Entonces Δᵢ(x) = Σ_j a_j·[ln(1 + z_j + d_ij) − ln(1 + z_j)]. Cada término es ≥ 0, porque ln es creciente, y no aumenta cuando z_j aumenta, porque ln es cóncava. Como β, w ≥ 0, cada z_j crece con cualquier x_l. Por lo tanto Δᵢ(x + e_l) ≤ Δᵢ(x) para todo par i, l (también l = i), y Δᵢ > 0. Además U₂(0) = 0.
2. **Copias.** Cada nodo i se reemplaza por cᵢ copias (B si no tiene tope). Para un conjunto A de copias se define g(A) = U₂(x), con xᵢ = número de copias de i en A. Si A ⊆ A' y e es una copia de i que no está en A', entonces x ≤ x' coordenada a coordenada y, aplicando el punto 1 varias veces, g(A' ∪ {e}) − g(A') = Δᵢ(x') ≤ Δᵢ(x) = g(A ∪ {e}) − g(A). Así, g es monótona, submodular y g(∅) = 0.
3. **Voraz de Nemhauser, Wolsey y Fisher.** Repartir a lo sumo B unidades es elegir a lo sumo B copias, y el voraz unidad por unidad es exactamente el voraz de §8.1 aplicado a g con k = B. Por el resultado de Nemhauser, Wolsey y Fisher (1978), U₂(voraz) ≥ ρ(B)·OPT.

En la batería de abajo, en las corridas de la docente y en el contraejemplo (0,9291 ≥ ρ(2) = 0,75) la cota se cumple.

### 8.4.4 Exacto de referencia y comparación contra el óptimo

**Exacto por enumeración.** Como en c2 no sirven ni el voraz ni la PD, el único exacto general es recorrer todos los repartos enteros con Σ xᵢ ≤ B y xᵢ ≤ cᵢ, evaluar U en cada uno y quedarse con el primero de mayor valor (en orden lexicográfico). Sin topes hay R_B = C(B + m, m) repartos; con topes, menos (se cuentan antes por programación dinámica, en O(m·B)). Cada evaluación de U₂ cuesta O(m + A_S): **T = Θ(m·B) + O(R_B·(m + A_S))**, con espacio O(m) de la recursión. Con m fijo, C(B + m, m) ∈ Θ(Bᵐ): es pseudopolinomial en B y exponencial en m. Se niega sin evaluar si R_B > 200000. En la docente, m = 5, B = 30 y topes 18: como a lo sumo un nodo puede pasar de 18, R_B = C(35, 5) − 5·C(16, 5) = 324632 − 21840 = **302792**. Esas corridas se hicieron con el límite subido a ese valor exacto, y la enumeración tardó unos 1,2 s en c1 y 3,5 s en c2 (`salida.json` de `c1_profesora` y `c2_profesora`).

**Batería.** Instancias de influencia con N ∈ {8, 10, 12}, k = 4, densidad ∈ {0,3; 0,6; 1,0}, semillas 1, 2 y 3, β ∈ {0,2; 0,5; 1,0; 2,0} y B ∈ {3, 6, 10}: 324 filas, a lo sumo C(14, 4) = 1001 repartos por fila. Razón = U₂(voraz)/OPT.

**c1:** el voraz coincidió con la enumeración en las 324 filas, como predice §8.4.1.

**c2, por β:**

| β | Filas | Con razón < 1 | Razón mínima |
|---|---|---|---|
| 0,2 | 81 | 0 | 1,0 |
| 0,5 | 81 | 3 | 0,997731 |
| 1,0 | 81 | 2 | 0,997373 |
| 2,0 | 81 | 2 | **0,986703** |

**c2, por B:**

| B | Filas | Con razón < 1 | Razón mínima | Cota ρ(B) | Repartos por fila (máximo) |
|---|---|---|---|---|---|
| 3 | 108 | 2 | 0,986703 | 0,7037 | 35 |
| 6 | 108 | 2 | 0,997373 | 0,6651 | 210 |
| 10 | 108 | 3 | 0,997331 | 0,6513 | 1001 |

Fuente: `resultados/variantes/c_tabla_cota.csv` (generado por `scripts/tabla_cota_variante_c.py`). Estas son las tablas de referencia de la batería de (c); §10.2.4 remite a ellas.

**Lectura.** Todas las filas cumplen la cota. El voraz de c2 pierde poco y pocas veces: 7 de 324 filas, ninguna con el β = 0,2 que se usa por omisión. La peor (N = 8, densidad 0,3, semilla 1, B = 3, β = 2) da 0,986703 contra una cota de 0,7037. Las pérdidas aparecen cuando el acople es fuerte (β grande), que es justo cuando la utilidad de un nodo depende más de sus vecinos y H1 está «más rota».

### 8.4.5 Dos precisiones halladas al implementar

1. **En c2, al dar una unidad cambian las ganancias de todos los nodos a distancia ≤ 2 del elegido dentro de S, no solo las del elegido y sus vecinos.** La ganancia de l incluye los términos de sus vecinos j (lo que sube z_j cuando l recibe), y esos z_j cambian cuando recibe cualquier vecino de j. Por eso la línea 8 recalcula {i} ∪ N_S(i) ∪ N_S(N_S(i)). Ejemplo: en el trayecto 1 – 2 – 3, darle una unidad al nodo 1 sube z₂, y con eso cambia la ganancia del nodo 3, que está a distancia 2. Una versión que solo recalculara 1 + grado_S(i) ganancias dejaría ganancias desactualizadas y ya no sería el voraz descrito. El costo por unidad sigue acotado por O(m + A_S).
2. **Calcular los a'ᵢ de c1 (y preparar c2) cuesta Θ(|S| + Σ_{i∈S} grado(i)), no O(|S| + A_S).** A_S solo se puede recorrer después de restringir el grafo a S, y para restringirlo hay que mirar todos los vecinos de cada nodo de S, también los que están fuera. En la docente, d(S) = 70 frente a A_S = 10.
