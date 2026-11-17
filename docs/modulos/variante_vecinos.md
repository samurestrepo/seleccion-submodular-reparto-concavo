# Ficha: `red/variante_vecinos.py`

## Para qué existe
Resuelve la **variante (c)**: los vecinos alteran la utilidad del reparto (Parte 1). La Parte 2 no cambia: S es el del voraz de la solución base. Cambia la utilidad con la que se reparten las B unidades entre los nodos de S. w_ij es el peso de la arista {i, j} del grafo de la instancia (`Instancia.vecinos`) y β ≥ 0 es un parámetro (`--beta`, 0,2 por omisión: las utilidades «se mueven un poco»). Las u_i de la docente son a_i·ln(1 + x_i). Solo corre con `ejecutar.py --variante c1` o `--variante c2`; sin la opción nada cambia.

**Supuestos ❓ (decisión 43):**
1. Solo cuentan los vecinos que **están en S**, porque la utilidad de la ronda es la de los participantes.
2. La variante necesita grafo: el formato propio no lo trae y el caso **se rechaza** (verificación «la instancia trae grafo»). Necesita también que cada u_i sea de la familia log. En la docente se cumplen las dos.
3. Se acepta β = 0 (reproduce la base: prueba); el modelo pide β > 0, pero β = 0 es el caso que demuestra que la variante extiende la base.

Dos modelos:
- **c1, el efecto va aparte.** Lo que gasta i le suma β·w_ij·ln(1 + x_i) a la utilidad de cada vecino j ∈ S. Al reagrupar por nodo, U(x) = Σ_{i∈S} a'_i·ln(1 + x_i), con **a'_i = a_i + β·Σ_{j∈S vecino de i} w_ij**. Es la Parte 1 con otros coeficientes: valen H1 (separación), H2, H3 y H4, así que el voraz de `reparto.py` es **exacto** por §7.1.1.
- **c2, el efecto va dentro.** u_j(x) = a_j·ln(1 + z_j), con **z_j = x_j + β·Σ_{i∈S vecino de j} w_ij·x_i** (la «entrada efectiva» de j). U = Σ_j u_j es cóncava, pero **no se separa por nodo** (z_j mezcla los x de los vecinos): falla H1, así que ni la prueba de §7.1.1 ni la PD de §7.2 aplican. Se resuelve con un voraz unidad por unidad, que **ya no es exacto** pero conserva la cota 1 − (1 − 1/B)^B ≥ 1 − 1/e.

## Funciones públicas
| Función | Recibe | Devuelve | Complejidad (tiempo · espacio) |
|---|---|---|---|
| `vecinos_en_S(S, vecinos)` | S y el grafo completo | id → lista de (j, w_ij) con j ∈ S | O(\|S\| + Σ_{i∈S} grado(i)) · O(\|S\| + A_S) |
| `coeficientes_c1(S, coeficientes, grafo_S, beta)` | S, a_i, el grafo restringido, β | id → a'_i | O(\|S\| + A_S) · O(\|S\|) |
| `repartir_c1(S, B, coeficientes, vecinos, beta, topes=None, traza=None)` | S, B, a_i, grafo, β, topes | (`ResultadoReparto`, a') | O(\|S\| + Σ_{i∈S} grado(i)) + O(\|S\| + B lg \|S\|) · O(\|S\| + A_S) |
| `utilidad_c1(x, a_prima)` | x, a' | Σ a'_i·ln(1 + x_i) | O(\|S\|) |
| `utilidad_c2(x, coeficientes, grafo_S, beta)` | x, a_j, grafo restringido, β | Σ a_j·ln(1 + z_j) | O(\|S\| + A_S) |
| `ganancia_c2(l, z, coeficientes, grafo_S, beta)` | nodo l y el estado z | U(x + e_l) − U(x) | O(1 + grado_S(l)) |
| `repartir_c2(S, B, coeficientes, vecinos, beta, topes=None, traza=None)` | lo mismo que c1 | `ResultadoVecinos` (x, utilidad, pasos, ganancias_recalculadas, revisados) | O(\|S\| + Σ_{i∈S} grado(i)) + O(B·(\|S\| + A_S)) · O(\|S\| + A_S) |
| `contar_repartos(S, B, topes=None)` | S, B, topes | cuántos x enteros con Σ x_i ≤ B y x_i ≤ c_i | O(\|S\|·B) · O(B) |
| `repartir_exacto(S, B, valor_U, topes=None, limite=200000)` | S, B, la función U (c1 o c2), topes, límite | (x*, OPT, evaluados); `DemasiadosRepartos` sin evaluar si hay más que el límite | R·O(costo de U) · O(\|S\|) |
| `cota_c2(B)` | B | 1 − (1 − 1/B)^B (0 si B = 0) | O(1) |
| `ejecutar_variante_c(instancia, modelo="c1", beta=0.2, repeticiones=1, limite=200000)` | instancia, modelo, β, R, límite | diccionario de la ronda (ver abajo) o el rechazo de `ronda._resultado_rechazado` | ver T(n) |
| `a_texto_vecinos(resultado)` | el resultado | el reporte `traza.txt` | O(tamaño del resultado) |

A_S = aristas con las dos puntas en S. El resultado de `ejecutar_variante_c` trae las claves de una ronda base (`caso`, `entrada` con modelo y β, `verificaciones`, `seleccion`, `reparto`, `tiempos_segundos`, `traza`, `todas_cumplen`) más `variante_c` (modelo, β, supuesto, `aristas_en_S` y, en c1, `a_prima`), `exacto` (`disponible`, `repartos`, `limite`; si corrió: x*, OPT, evaluados, su tiempo, `razon` = U/OPT y `cota`; si no, `motivo`) y `reparto_base` (el x de la base, su utilidad sin vecinos y `utilidad_con_vecinos` = U del modelo evaluada en ese x). En c1, `reparto` trae extracciones e inserciones; en c2, pasos, ganancias recalculadas y revisados.

## Cómo funciona
**c1.** `repartir_c1` restringe el grafo a S, calcula a'_i sumando los pesos de los vecinos en S (cada arista se mira desde sus dos puntas), crea `UtilidadLog(a'_i)` y llama a `repartir_presupuesto` **sin tocarlo** (líneas 1 a 8 de REPARTIR-PRESUPUESTO del informe, con los topes de la instancia).

**c2.** Pseudocódigo (no está en el informe; los comentarios `# línea N del pseudocódigo` del código citan este):
```
REPARTIR-C2(S, B, a, w, β, c)
1  para cada i ∈ S: x_i ← 0; z_i ← 0
2  activos ← {i ∈ S : c_i > 0}; para cada i activo: Δ_i ← GANANCIA(i, z)
3  para t = 1 hasta B
4      si activos = ∅: terminar                          ▹ todos en su tope: sobra presupuesto
5      i ← el activo de mayor Δ_i (empate: menor id)       ▹ barrido lineal, O(|S|)
6      x_i ← x_i + 1; z_i ← z_i + 1; z_j ← z_j + β·w_ij para cada j ∈ N_S(i)
7      si x_i = c_i: sacar i de activos
8      para cada l activo en {i} ∪ N_S(i) ∪ N_S(N_S(i)): Δ_l ← GANANCIA(l, z)
9  devolver x y U(x) = Σ_j a_j·ln(1 + z_j), recalculada desde x
```
GANANCIA(l, z) = a_l·[ln(2 + z_l) − ln(1 + z_l)] + Σ_{j∈N_S(l)} a_j·[ln(1 + z_j + β·w_lj) − ln(1 + z_j)], en O(1 + grado_S(l)).

**Qué ganancias cambian (línea 8).** Cuando i recibe una unidad cambian z_i y los z_j de sus vecinos. La ganancia de l depende de z_l **y de los z de sus vecinos**, así que cambia para todo l a **distancia ≤ 2** de i dentro de S, no solo para i y sus vecinos. En el trayecto 1 – 2 – 3, darle a 1 cambia la ganancia de 3 (prueba `test_las_ganancias_cambian_hasta_distancia_dos`). Por paso se recalculan |N²_S[i] ∩ activos| ganancias, no 1 + grado_S(i).

**Exacto por enumeración.** `repartir_exacto` recorre en profundidad todos los vectores enteros (x_{i1}, …, x_{im}) con i1 < … < im, Σ x ≤ B y x_i ≤ c_i, en **orden lexicográfico**, evalúa U en cada uno y reemplaza solo con `>`: gana el **primer** reparto en ese orden. Antes cuenta los repartos con `contar_repartos` (programación dinámica con sumas prefijas: formas[b] = repartos que suman exactamente b) y se niega sin evaluar nada si pasan del límite (200000, el de `exacto.py`).

**La ronda (`ejecutar_variante_c`).** Valida los parámetros (`ValueError`), corre `verificar_entrada` y `verificar_variante_c` (rechazo como en `ronda.py`), mide R veces la Parte 2 base y el reparto del modelo (un oráculo nuevo por repetición, fuera del reloj), corre una vez con traza, corre el exacto **una vez, fuera de la medición**, calcula el reparto base para compararlo y verifica: la selección como en la base (incluido el conteo k·N − k(k−1)/2); en c1, `verificar_reparto` con las utilidades a'_i (topes, Σ x_i, utilidad, extracciones e inserciones); en c2, `verificar_reparto_c2` (x_i ≤ mín(B, c_i), Σ x_i = mín(B, Σ c_i), pasos = Σ x_i, U recalculada); si el exacto corrió, `verificar_reparto_contra_exacto` (c1: U = OPT; c2: U ≤ OPT y U ≥ (1 − (1 − 1/B)^B)·OPT); y que las R repeticiones y la de la traza coinciden.

## T(n) y espacio
Sean m = |S| ≤ k, A_S las aristas dentro de S, d(S) = Σ_{i∈S} grado(i) ≤ mín(2A, m(N − 1)) y R_B el número de repartos.
- **Restringir el grafo a S:** Θ(m + d(S)): hay que mirar todos los vecinos de cada i ∈ S para quedarse con los que están en S. Es la parte que el prompt omitía (decía O(|S| + A_S)): A_S solo se alcanza **después** de restringir. En la docente S es completo y d(S) = 5·14 = 70, A_S = 10.
- **c1:** a'_i en O(m + A_S) más el reparto base: **T = Θ(m + d(S)) + Θ(m + B(1 + lg m))** sin topes (con topes, peor O(m + B lg m)); con m ≤ k, O(k + d(S) + B lg k). Espacio Θ(m + A_S).
- **Voraz de c2:** ganancias iniciales O(m + A_S); por paso, el barrido Θ(m) (recorre siempre los m nodos de S y solo cuenta en `revisados` los activos, así que `revisados` ≤ m por paso, pero el recorrido es Θ(m)), la actualización de z O(1 + grado_S(i)), los afectados y su recálculo O(Σ_{l∈N²[i]} (1 + grado_S(l))) ≤ O(m + A_S). **T = O(m + d(S) + B·(m + A_S))**; peor caso (S completo, A_S = m(m − 1)/2) **O(B·m²) ⊆ O(B·k²)**, con exactamente m + B·m ganancias recalculadas y B·m revisados si nadie llega a su tope; mejor caso (sin aristas en S) Θ(m + B·m), dominado por el barrido, con m + B ganancias recalculadas. Espacio Θ(m + A_S) (grafo restringido, x, z, ganancias, activos).
- **Enumeración:** R_B repartos; sin topes **R_B = C(B + m, m)** (barras y estrellas con una variable de holgura); con topes, inclusión-exclusión. Cada hoja evalúa U en O(m + A_S) (c2) u O(m) (c1), y el árbol tiene a lo sumo (m + 1)·R_B nodos: **T = Θ(m·B) + O(R_B·(m + A_S))**. Espacio O(m) de la recursión más O(m + A_S).
- **Ronda completa:** (R + 1)·(selección base O(k·(N + A)) + reparto del modelo) + el exacto una vez + el reparto base O(k + B lg k) + las verificaciones O(N + A).

**Docente:** m = 5, B = 30, topes 18. Sin topes serían C(35, 5) = 324632; como solo un nodo puede pasar de 18 (dos sumarían ≥ 38 > 30), con topes son **C(35, 5) − 5·C(16, 5) = 324632 − 21840 = 302792 > 200000**. Con el límite por omisión el exacto no corre; para las evidencias se corrió con `--limite-repartos 302792` (el número exacto, decisión 46), y tardó unos 1 s en c1 y 4 s en c2.

## La cota de c2 (propuesta del autor, verificada en datos)
1. **U es monótona y con rendimientos decrecientes en cada coordenada.** Δ_i(x) = Σ_j a_j·[ln(1 + z_j + d_ij) − ln(1 + z_j)], con d_ii = 1, d_ij = β·w_ij si j es vecino de i en S y 0 si no. Cada término es > 0 o = 0 (ln creciente) y no crece cuando z_j crece (ln cóncava); y cada z_j crece con cualquier x_l, porque β, w ≥ 0. Entonces Δ_i(x + e_l) ≤ Δ_i(x) para todo i, l (también l = i), y Δ_i > 0. Además U(0) = 0. Prueba: `test_U_de_c2_es_monotona_y_con_rendimientos_decrecientes` (20 instancias, 15 puntos cada una, todos los pares i, l).
2. **Copias.** Cada nodo i aporta c_i copias (sin tope, B). Para un conjunto A de copias, g(A) = U(x) con x_i = copias de i en A. Si A ⊆ A' y e es una copia de i que no está en A', g(A' + e) − g(A') = Δ_i(x') ≤ Δ_i(x) = g(A + e) − g(A), porque x ≤ x' coordenada a coordenada (punto 1 aplicado varias veces). g es monótona, submodular y g(∅) = 0.
3. Repartir a lo sumo B unidades es elegir a lo sumo B copias, y el voraz unidad por unidad es el voraz de Nemhauser, Wolsey y Fisher (1978) sobre g. Entonces **U(voraz) ≥ (1 − (1 − 1/B)^B)·OPT ≥ (1 − 1/e)·OPT**.

**En los datos se cumple:** en la batería de 324 filas (`scripts/tabla_cota_variante_c.py`, decisión 46) la razón mínima es **0,986703** (N = 8, densidad 0,3, semilla 1, B = 3, β = 2; cota 0,7037); solo 7 filas quedan por debajo de 1, ninguna con β = 0,2. También en 30 instancias aleatorias pequeñas de las pruebas y en el contraejemplo (0,9291 ≥ 0,75).

## Contraejemplo mínimo de c2
Trayecto 1 – 2 – 3 con a = (3, 2, 3), w_12 = w_23 = 1, β = 0,2, B = 2, sin topes.
- Primera unidad: el centro gana 2·ln 2 + 6·ln 1,2 ≈ 2,4802 (le sube a los dos extremos) y cada extremo 3·ln 2 + 2·ln 1,2 ≈ 2,4441: va al **centro**. Segunda: al nodo 1 (empate con 3; gana el menor id).
- Voraz: x = (1, 1, 0), U = 5·ln 2,2 + 3·ln 1,2 ≈ **4,489251**. Óptimo: x = (1, 0, 1), U = 6·ln 2 + 2·ln 1,4 ≈ **4,831828**. Razón 0,9291 ≥ 1 − (1 − 1/2)² = 0,75.

Se buscó con una batería (coeficientes en {1, …, 10}, pesos en {0,25; 0,5; 1}): con dos nodos y B ≤ 4 no apareció ninguno (eso no prueba que no exista); con B = 1 el voraz siempre es exacto. La estrella del prompt (centro y 3 hojas, β = 0,2, B = 3) también pierde: 328 de 12288 combinaciones, peor razón 0,9106.

## Por qué así
- **c1 reutiliza `repartir_presupuesto`** sin tocarlo: es exactamente la Parte 1 con a'_i, así que hereda su prueba de optimalidad, su montículo y sus verificaciones. No hace falta otro algoritmo.
- **Barrido lineal en c2, no montículo (decisión 45).** Las ganancias solo bajan, pero cambian varias por paso (todas las de distancia ≤ 2): un montículo necesitaría DISMINUIR-CLAVE o borrado perezoso, más difícil de explicar. El recálculo ya cuesta O(m + A_S) en el peor caso, que es lo mismo o más que el barrido Θ(m); en la docente (S completo) se recalculan las 5 ganancias en cada paso de todos modos. Solo con S muy ralo y m grande el montículo ahorraría, y aquí m ≤ k.
- **Desempate:** el voraz recorre por id con `>` estricto (menor id), igual que el montículo de la base: con β = 0 da el mismo x. La enumeración se queda con el primer reparto lexicográfico, que en un empate puede ser otro: con dos nodos iguales y B = 1, el voraz da (1, 0) y la enumeración (0, 1). Las dos reglas son reproducibles; la verificación compara U, no x.
- **`_subida` escrita como resta de dos valores:** con d = 1 y z entero da bit a bit lo mismo que `UtilidadLog.ganancia`, así que con β = 0 los empates son los de la base.
- **U de c2 se recalcula desde x al final (línea 9)**, no desde el z acumulado: es la misma función que usa la enumeración, y así la comparación no depende del redondeo acumulado.
- **El exacto corre una sola vez y fuera del reloj:** es una referencia, como `exacto.py` en la base.

## Cómo modificarlo
- **Que también cuenten los vecinos fuera de S:** en `vecinos_en_S`, no filtrar por S (y sumar la utilidad de los vecinos de fuera en `utilidad_c2`); cambia el Supuesto ❓ 1 y la decisión 43.
- **Montículo en c2:** guardar (−Δ, id, versión) y descartar las entradas viejas al extraer (borrado perezoso); el conteo de operaciones cambia y hay que actualizar `test_conteos_de_c2_con_S_completo_y_con_S_sin_aristas`.
- **Otra familia de u_i:** c1 necesita una familia con coeficiente (a'·u(x)); c2 necesita la forma u(x_j + β·Σ w·x_i). Quitar la verificación «cada u_i es a_i·ln(1 + x_i)» solo si el modelo sigue siendo cóncavo y monótono.
- Correr `pruebas/test_variante_vecinos.py` y regenerar `resultados/variantes/c_tabla_cota.csv` y las corridas de la docente.

## Pruebas
`pruebas/test_variante_vecinos.py` (133 pruebas): con β = 0, c1 y c2 dan el mismo x y la misma U que el reparto base en la docente y en 6 instancias de influencia, y la ronda de la variante da el mismo S, f(S), x y U que `ejecutar_ronda`; a'_i a mano y U de c1 igual a la definición sin reagrupar; c1 = enumeración; el contraejemplo mínimo (x, U, OPT, razón 0,9291, 10 repartos) y por qué la primera unidad va al centro; monotonía y rendimientos decrecientes de U (punto 1 de la cota); la cota en 30 instancias pequeñas; las ganancias cambian hasta distancia 2; el voraz con atajos = un voraz de referencia que recalcula todo desde x (25 instancias con topes); los conteos exactos (S completo: m + B·m recalculadas; sin aristas: m + B; barrido B·m); topes, presupuesto que sobra y desempate; `contar_repartos` = C(B + m, m) sin topes y 302792 en la docente, igual al número de hojas evaluadas y en orden lexicográfico; desempate lexicográfico de la enumeración; negativa sin evaluar; la batería completa (324 filas: c1 coincide siempre, c2 ≥ cota, mínimo 0,986703, 7 filas < 1) y el CSV del repositorio igual al que genera el script; rechazo del formato propio; parámetros inválidos (`ValueError` y `SystemExit` de argparse); ramas de fallo de las verificaciones nuevas; `ejecutar.py --variante c1|c2` (sin exacto con el límite por omisión, `resumen.csv` con las columnas de la base) y las evidencias de la docente, más una corrida nueva de c2 con el límite 302792 que las reproduce.

## Preguntas probables en la sustentación
- **¿Por qué c1 sigue siendo exacto?** Porque al reagrupar queda Σ a'_i·ln(1 + x_i): separable, creciente y cóncava, con topes. Es la Parte 1 con otros coeficientes y aplica §7.1.1.
- **¿Por qué c2 no?** Porque z_j mezcla los x de los vecinos: U no es una suma de funciones de un solo x_i (falla H1) y el argumento de intercambio no aplica. Contraejemplo: el trayecto de tres nodos con B = 2.
- **¿Qué garantiza entonces el voraz de c2?** U tiene rendimientos decrecientes en cada coordenada; viendo cada unidad como una copia, U es una función de conjuntos monótona y submodular y el voraz es el de Nemhauser, Wolsey y Fisher con a lo sumo B elementos: U ≥ (1 − (1 − 1/B)^B)·OPT. En los datos, la peor razón fue 0,9867.
- **¿Cuánto cuesta?** c1: lo de la base más restringir el grafo, Θ(k + d(S)). c2: O(B·(k + A_S)), O(B·k²) con S completo. El exacto: C(B + k, k) repartos sin topes, cada uno a O(k + A_S).

_Última actualización: 2026-11-17 · archivo nuevo (P-4 fase 3)_
