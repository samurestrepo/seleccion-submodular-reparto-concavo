# 11. Validación experimental

En esta sección se contrasta el tiempo medido de cada algoritmo con la T(n) deducida en las secciones anteriores y en las fichas de cada módulo. Todo lo que se cita sale de los CSV de `resultados/experimentos/`, generados por `scripts/experimentos.py`. Los comandos están en la sección 8 del manual técnico.

## 11.1 Metodología

**Series.** Una serie es un algoritmo que se mide en varios tamaños crecientes de la entrada, cambiando un solo parámetro a la vez. Hay 14 series: de la a a la h para la solución base y sus exactos de referencia, y de la i a la m para las variantes (la serie i son dos: ic, voraz por cociente, e im, voraz modificado).

**Generación de instancias.** Todas las instancias se generan en memoria con semilla 1 y no pasan por disco.
- Series a, d, e y h: `generar_instancia` (formato propio, cobertura). El universo tiene 2N elementos, cada nodo cubre entre 1 y 5 de ellos, y cada u_i es log o raíz, con coeficiente entre 1 y 10.
- Las demás series: `generar_instancia_influencia` (formato de la docente). Cada par de nodos tiene una arista con probabilidad igual a la densidad, con peso uniforme en [0,05; 0,70]. Los coeficientes están en [1; 10] y los costos son enteros en [1; 5]. Con densidad 1 el grafo es completo; con densidad 5/(N − 1), cada nodo tiene en promedio unos 5 vecinos.

**Tamaños.** En casi todas las series el tamaño se duplica de un punto al siguiente, para ver el exponente en una gráfica log-log. En los exactos exponenciales (f, g, j y k) los tamaños se eligieron para no pasar de 200 000 subconjuntos ni de 2 s por repetición.

**Medición.**
- Reloj: `time.perf_counter`, el reloj de mayor resolución de la biblioteca estándar. Solo envuelve la llamada al algoritmo: la instancia y el oráculo nuevo de cada repetición se crean antes, fuera del reloj, y no se lee ni escribe ningún archivo. La única excepción es la serie l, que cronometra `ejecutar_rondas` completo, porque esa función crea sus propios oráculos en cada ronda.
- Repeticiones: 21 por tamaño. Si una repetición pasa de 2 s, se hacen solo 5 (series h e i a m). Esto no ocurrió en ninguna: la repetición más lenta fue la de la serie k con N = 16, con 0,77 s.
- Se guardan el mínimo y la mediana de las 21. **Las tablas y las gráficas usan el mínimo** (decisión 30 del repositorio). El ruido del sistema (otros procesos, interrupciones, cambios de frecuencia) solo puede sumar tiempo, nunca restarlo, así que el mínimo es la medición menos contaminada. La mediana queda en los CSV como dato de control.
- Conteo: en cada tamaño se cuenta además la operación básica que usa la T del algoritmo (llamadas a Δ, operaciones del montículo, evaluaciones de f, candidatos de la PD o ganancias recalculadas). En todos los tamaños el conteo coincide con su fórmula exacta (`docs/modulos/experimentos.md`).

**Análisis.** Para cada tamaño se calcula el **cociente** t_min / T(n). Si T(n) describe bien el crecimiento, el cociente tiende a una constante, y su rango (máximo/mínimo) mide cuánto se aparta de serlo. Además se ajusta por mínimos cuadrados una recta a log t_min contra log n. Su pendiente es el **exponente aparente**: si t ≈ c·nᵖ, la pendiente es p. Se compara con la **pendiente esperada**, que es la de log T(n) contra log n en los mismos puntos y que ya incluye los términos de menor orden. También se ajusta log t_min contra log T(n): si el tiempo es proporcional a T, esa pendiente vale 1.

**Máquina.** Intel Core i5-6300U a 2,40 GHz (2 núcleos y 4 hilos; caché L2 de 512 KB y L3 de 3 MB), 15,9 GB de RAM, Windows 10 Pro (versión 10.0.19045), Python 3.14.7 (CPython) y el reloj `time.perf_counter`. Las series i a m (2026-11-17) se corrieron en este equipo, que queda registrado en `docs/modulos/experimentos.md` y en el manual técnico. **Supuesto ❓:** de las series a a h (2026-11-12) no quedó registro del equipo; se supone que es el mismo.

## 11.2 Resultados por serie

Columnas de cada tabla: n es el tamaño que varía; t_min, el mínimo de las 21 repeticiones; conteo, las operaciones básicas contadas; T(n), la función teórica evaluada en ese punto; y el cociente t_min/T(n), en la escala que indica el encabezado. Cada serie tiene dos gráficas en `resultados/experimentos/`: `<serie>_tiempo.png` (t_min contra n, con la curva c·T(n) ajustada en el n mayor) y `<serie>_cociente.png`.

### Resumen

| Serie | Algoritmo | n | T(n) | Pendiente contra n (esperada) | Pendiente contra T | Cociente máx/mín |
|---|---|---|---|---|---|---|
| a | voraz Parte 2, cobertura, k = 5 | N | k·N | 1,017 (1,000) | 1,017 | 1,09 |
| b | voraz Parte 2, influencia, grafo completo, k = 5 | N | k·N² | 2,086 (2,000) | 1,043 | 1,38 |
| c | voraz Parte 2, influencia, grado ~ 5, k = 5 | N | k·N | 1,014 (1,000) | 1,014 | 1,08 |
| d | reparto Parte 1, B = 1 000 | N | N + B lg N | 0,781 (0,359) | **2,182** | **3,19** |
| e | reparto Parte 1, N = 100 | B | N + B lg N | 0,965 (0,995) | 0,970 | 1,11 |
| f | fuerza bruta Parte 2, k = 3 | N | C(N, k)·k·N | 4,572 (4,205) | 1,087 | 1,64 |
| g | fuerza bruta Parte 2, k = N/2 | N | C(N, k)·k·N | 9,262 (9,486) | 0,976 | 1,34 |
| h | PD Parte 1, N = 10 | B | N·B² | 1,883 (2,000) | 0,941 | 1,46 |
| ic | (a) voraz por cociente, L = 5N | N | N²·(1 + 2A/N) | 2,049 (2,011) | 1,019 | 1,16 |
| im | (a) voraz modificado, L = 5N | N | N²·(1 + 2A/N) | 2,053 (2,011) | 1,021 | 1,16 |
| j | (a) enumeración parcial, L = 5N | N | E(N)·(1 + 2A/N) | 5,015 (5,218) | 0,960 | 1,32 |
| k | (a) fuerza bruta con presupuesto, L = 5N | N | 2ᴺ·(N + A) | 8,635 (8,458) | 1,023 | 1,25 |
| l | (b) T rondas, N = 100, k = 5, B = 100 | T | T·[2(k(N + A) + B lg k) + N] | 1,059 (1,000) | 1,059 | 1,16 |
| m | (c2) voraz unidad por unidad, \|S\| = 10 completo | B | m + d(S) + B·(m + A_S) | 1,046 (0,988) | 1,059 | 1,18 |

Las pendientes de las series a–h no estaban escritas en el repositorio. Se calcularon a partir de sus CSV con la misma regresión de `scripts/experimentos.py` (función `pendiente`). Las de i–m coinciden con las de `docs/modulos/experimentos.md`.

En la tabla, A es el número de aristas del grafo; E(N) = 1 + N + C(N, 2) + C(N, 3)·(1 + (N − 3)(N − 2)/2) es el número de evaluaciones del peor caso de la enumeración parcial; m = |S|; A_S, las aristas dentro de S; y d(S), la suma de los grados de los nodos de S. En las series de un exacto exponencial (f, g, j y k) la pendiente contra n solo dice cuánto crece el tiempo entre el primer tamaño y el último, porque T no es un polinomio en n. Lo que importa en ellas es la pendiente contra T.

### Serie a: voraz de la Parte 2 con cobertura (`a_cobertura.csv`)

T = k·N: hay k·N − k(k − 1)/2 llamadas a Δ, y cada una cuesta O(|C_v|) = O(1), porque cada nodo cubre a lo sumo 5 elementos. Gráficas: `a_cobertura_tiempo.png` y `a_cobertura_cociente.png`.

| n | t_min (ms) | conteo | T(n) | cociente (×10⁻⁷) |
|---|---|---|---|---|
| 20 | 0,047 | 90 | 100 | 4,67 |
| 40 | 0,090 | 190 | 200 | 4,49 |
| 80 | 0,190 | 390 | 400 | 4,76 |
| 160 | 0,391 | 790 | 800 | 4,89 |
| 320 | 0,762 | 1 590 | 1 600 | 4,76 |
| 640 | 1,555 | 3 190 | 3 200 | 4,86 |

### Serie b: voraz de la Parte 2 con influencia, grafo completo (`b_influencia_completo.csv`)

T = k·N²: las llamadas siguen siendo k·N − k(k − 1)/2, pero cada una cuesta O(1 + grado(v)) = O(N) en un grafo completo. El conteo no ve este factor, porque está dentro de cada llamada. Gráficas: `b_influencia_completo_tiempo.png` y `b_influencia_completo_cociente.png`.

| n | t_min (ms) | conteo | T(n) | cociente (×10⁻⁷) |
|---|---|---|---|---|
| 25 | 0,438 | 115 | 3 125 | 1,40 |
| 50 | 1,601 | 240 | 12 500 | 1,28 |
| 100 | 6,231 | 490 | 50 000 | 1,25 |
| 200 | 30,996 | 990 | 200 000 | 1,55 |
| 400 | 137,427 | 1 990 | 800 000 | 1,72 |

### Serie c: voraz de la Parte 2 con influencia, grado medio ~ 5 (`c_influencia_grado5.csv`)

T = k·N: con grado constante, cada llamada vuelve a costar O(1). Gráficas: `c_influencia_grado5_tiempo.png` y `c_influencia_grado5_cociente.png`.

| n | t_min (ms) | conteo | T(n) | cociente (×10⁻⁶) |
|---|---|---|---|---|
| 25 | 0,137 | 115 | 125 | 1,09 |
| 50 | 0,267 | 240 | 250 | 1,07 |
| 100 | 0,517 | 490 | 500 | 1,03 |
| 200 | 1,115 | 990 | 1 000 | 1,12 |
| 400 | 2,241 | 1 990 | 2 000 | 1,12 |

### Serie d: reparto de la Parte 1, varía N con B = 1 000 (`d_reparto_varia_N.csv`)

T = N + B lg N: BUILD-HEAP en Θ(N) y B vueltas de O(lg N). El conteo, extracciones más inserciones, vale 2B = 2 000 en todos los tamaños: lo que crece es el trabajo de armar el montículo y su altura. Gráficas: `d_reparto_varia_N_tiempo.png` y `d_reparto_varia_N_cociente.png`.

| n | t_min (ms) | conteo | T(n) | cociente (×10⁻⁷) |
|---|---|---|---|---|
| 1 000 | 2,784 | 2 000 | 10 966 | 2,54 |
| 2 000 | 3,710 | 2 000 | 12 966 | 2,86 |
| 4 000 | 5,892 | 2 000 | 15 966 | 3,69 |
| 8 000 | 10,960 | 2 000 | 20 966 | 5,23 |
| 16 000 | 24,249 | 2 000 | 29 966 | 8,09 |

### Serie e: reparto de la Parte 1, varía B con N = 100 (`e_reparto_varia_B.csv`)

La misma T, N + B lg N; aquí domina B lg N. Gráficas: `e_reparto_varia_B_tiempo.png` y `e_reparto_varia_B_cociente.png`.

| n = B | t_min (ms) | conteo | T(n) | cociente (×10⁻⁷) |
|---|---|---|---|---|
| 1 000 | 1,483 | 2 000 | 6 744 | 2,20 |
| 2 000 | 2,697 | 4 000 | 13 388 | 2,01 |
| 4 000 | 5,285 | 8 000 | 26 675 | 1,98 |
| 8 000 | 10,627 | 16 000 | 53 251 | 2,00 |
| 16 000 | 21,213 | 32 000 | 106 402 | 1,99 |

**Ajuste con dos constantes (series d y e juntas).** T suma N y B lg N con el mismo peso, pero en la máquina cada término tiene su propia constante. Un ajuste por mínimos cuadrados de t_min ≈ a·N + b·B·lg N con los 10 puntos da a = 1,26·10⁻⁶ s por nodo y b = 1,96·10⁻⁷ s por unidad y nivel del montículo (`ajuste_reparto.png`, columna `t_ajustado` de los dos CSV). El error relativo del ajuste va de −3,9 % a +1,0 % en la serie e y de −5,6 % a +25,8 % en la serie d.

### Serie f: fuerza bruta de la Parte 2, k = 3, grafo completo (`f_exacto_k3.csv`)

T = C(N, k)·k·N: hay C(N, k) evaluaciones de f, y cada `valor(S)` con grafo completo cuesta O(N + Σ_{v∈S} grado(v)) = O(k·N). Gráficas: `f_exacto_k3_tiempo.png` y `f_exacto_k3_cociente.png`.

| n | t_min (ms) | conteo | T(n) | cociente (×10⁻⁷) |
|---|---|---|---|---|
| 10 | 1,143 | 120 | 3 600 | 3,17 |
| 15 | 8,726 | 455 | 20 475 | 4,26 |
| 20 | 21,966 | 1 140 | 68 400 | 3,21 |
| 25 | 78,002 | 2 300 | 172 500 | 4,52 |
| 30 | 190,305 | 4 060 | 365 400 | 5,21 |

### Serie g: fuerza bruta de la Parte 2, k = N/2, grafo completo (`g_exacto_k_mitad.csv`)

La misma T, con k = N/2: C(N, N/2) crece casi como 2ᴺ. Gráficas (eje y logarítmico): `g_exacto_k_mitad_tiempo.png` y `g_exacto_k_mitad_cociente.png`.

| n | t_min (ms) | conteo | T(n) | cociente (×10⁻⁷) |
|---|---|---|---|---|
| 8 | 0,861 | 70 | 2 240 | 3,84 |
| 10 | 5,212 | 252 | 12 600 | 4,14 |
| 12 | 27,332 | 924 | 66 528 | 4,11 |
| 14 | 103,475 | 3 432 | 336 336 | 3,08 |
| 16 | 599,960 | 12 870 | 1 647 360 | 3,64 |

### Serie h: PD de la Parte 1, varía B con N = 10 y sin topes (`h_pd_varia_B.csv`)

T = N·B². El conteo exacto es N·(B + 1)(B + 2)/2 candidatos, que es aproximadamente la mitad de T. Gráficas: `h_pd_varia_B_tiempo.png` y `h_pd_varia_B_cociente.png`.

| n = B | t_min (ms) | conteo | T(n) | cociente (×10⁻⁸) |
|---|---|---|---|---|
| 25 | 0,485 | 3 510 | 6 250 | 7,77 |
| 50 | 1,572 | 13 260 | 25 000 | 6,29 |
| 100 | 5,617 | 51 510 | 100 000 | 5,62 |
| 200 | 21,303 | 203 010 | 400 000 | 5,33 |
| 400 | 89,940 | 806 010 | 1 600 000 | 5,62 |

### Series ic e im: variante (a), voraz por cociente y voraz modificado (`i_costos_cociente.csv`, `i_costos_modificado.csv`)

Con L = 5N todo cabe, que es el peor caso: hay N pasos y exactamente 1 + N(N + 1)/2 evaluaciones. Cada evaluación cuesta O(1 + grado), así que T = N²·(1 + 2A/N), con el A real de cada instancia. Gráficas: `i_costos_cociente_tiempo.png`, `i_costos_cociente_cociente.png`, `i_costos_modificado_tiempo.png` e `i_costos_modificado_cociente.png`.

| n | t_min ic (ms) | t_min im (ms) | conteo (los dos) | T(n) | cociente ic (×10⁻⁷) | cociente im (×10⁻⁷) |
|---|---|---|---|---|---|---|
| 50 | 1,701 | 1,634 | 1 276 | 15 000 | 1,13 | 1,09 |
| 100 | 6,192 | 6,211 | 5 051 | 55 000 | 1,13 | 1,13 |
| 200 | 28,363 | 28,529 | 20 101 | 250 400 | 1,13 | 1,14 |
| 400 | 106,158 | 107,617 | 80 201 | 948 000 | 1,12 | 1,14 |
| 800 | 498,185 | 483,365 | 320 401 | 3 838 400 | 1,30 | 1,26 |

### Serie j: variante (a), enumeración parcial (`j_costos_enumeracion.csv`)

Peor caso, con L = 5N: exactamente E(N) evaluaciones, Θ(N⁵), y T = E(N)·(1 + 2A/N). Gráficas (eje y logarítmico): `j_costos_enumeracion_tiempo.png` y `j_costos_enumeracion_cociente.png`.

| n | t_min (ms) | conteo | T(n) | cociente (×10⁻⁷) |
|---|---|---|---|---|
| 8 | 2,759 | 933 | 6 064 | 4,55 |
| 10 | 8,240 | 3 536 | 23 338 | 3,53 |
| 12 | 17,140 | 10 199 | 49 295 | 3,48 |
| 14 | 46,243 | 24 494 | 125 969 | 3,67 |
| 16 | 77,619 | 51 657 | 225 999 | 3,43 |
| 18 | 169,287 | 98 908 | 450 581 | 3,76 |

### Serie k: variante (a), fuerza bruta con presupuesto (`k_costos_fuerza_bruta.csv`)

Con L = 5N los 2ᴺ subconjuntos son factibles: exactamente 2ᴺ evaluaciones, cada una O(N + A), así que T = 2ᴺ·(N + A). Gráficas (eje y logarítmico): `k_costos_fuerza_bruta_tiempo.png` y `k_costos_fuerza_bruta_cociente.png`.

| n | t_min (ms) | conteo | T(n) | cociente (×10⁻⁷) |
|---|---|---|---|---|
| 8 | 1,915 | 256 | 7 680 | 2,49 |
| 10 | 8,517 | 1 024 | 38 912 | 2,19 |
| 12 | 34,512 | 4 096 | 143 360 | 2,41 |
| 14 | 180,743 | 16 384 | 704 512 | 2,57 |
| 16 | 769,634 | 65 536 | 2 818 048 | 2,73 |

### Serie l: variante (b), varía el número de rondas T (`l_rondas_varia_T.csv`)

N = 100, k = 5, B = 100, q = 0,2, modo transitorio y sin exacto. Los topes se subieron a B·128 para que el presupuesto restante nunca se agote y todas las rondas cuesten lo mismo. T(n) = T·[2(k(N + A) + B lg k) + N], porque cada ronda se ejecuta dos veces (medida y con traza). El conteo son las llamadas a Δ de todas las rondas. Gráficas: `l_rondas_varia_T_tiempo.png` y `l_rondas_varia_T_cociente.png`.

| n = T | t_min (ms) | conteo | T(n) | cociente (×10⁻⁷) |
|---|---|---|---|---|
| 8 | 11,326 | 3 165 | 30 515 | 3,71 |
| 16 | 22,737 | 6 350 | 61 030 | 3,73 |
| 32 | 45,040 | 12 495 | 122 060 | 3,69 |
| 64 | 102,474 | 24 980 | 244 121 | 4,20 |
| 128 | 209,562 | 49 615 | 488 241 | 4,29 |

### Serie m: variante (c2), varía B (`m_c2_varia_B.csv`)

N = 50 con grafo completo y S = el equipo del voraz base con m = 10 nodos, que también es completo: A_S = 45 y d(S) = 490. β = 0,2 y no hay topes. El conteo son las ganancias recalculadas, exactamente m + B·m. Gráficas: `m_c2_varia_B_tiempo.png` y `m_c2_varia_B_cociente.png`.

| n = B | t_min (ms) | conteo | T(n) | cociente (×10⁻⁶) |
|---|---|---|---|---|
| 250 | 16,423 | 2 510 | 14 250 | 1,15 |
| 500 | 33,211 | 5 010 | 28 000 | 1,19 |
| 1 000 | 66,310 | 10 010 | 55 500 | 1,19 |
| 2 000 | 140,811 | 20 010 | 110 500 | 1,27 |
| 4 000 | 299,612 | 40 010 | 220 500 | 1,36 |

## 11.3 Discusión

**Lo que confirman los datos.** En 13 de las 14 series la pendiente de log t_min contra log T queda entre 0,94 y 1,09: el tiempo crece en proporción a la T deducida. En particular:
- **El voraz de la Parte 2 es lineal en N con k fijo** cuando cada llamada cuesta O(1) (series a y c, pendientes 1,017 y 1,014, cociente estable dentro de un 9 %). Es cuadrático en un grafo completo (serie b, 2,086), como predice O(k·(N + A)) con A = N(N − 1)/2. Esto separa los dos factores de la T: el número de llamadas, Θ(N·k), y el costo de cada llamada.
- **El reparto crece como B lg N cuando varía B** (serie e: pendiente contra T de 0,970 y cociente estable dentro de un 2 % sin el primer punto).
- **Los exactos son exponenciales y su tiempo sigue al conteo:** la serie g pasa de 0,86 ms a 600 ms al subir N de 8 a 16 (pendiente contra T de 0,976), y la k de 1,9 ms a 770 ms (1,023). Con la misma N = 16, la fuerza bruta con presupuesto (k) tarda 770 ms, mientras que el voraz modificado tarda menos de 2 ms aun con N = 50 (serie im).
- **Variante (a):** el voraz por cociente y el modificado tardan lo mismo (series ic e im: las mismas evaluaciones, y tiempos que difieren menos de un 5 %), como dice su análisis: el mejor nodo solo no cuesta evaluaciones extra. La enumeración parcial (j) crece como N⁵: su pendiente contra n es 5,02, frente a la esperada de 5,22. La diferencia viene de los términos de menor orden de E(N), que con N ≤ 18 todavía pesan. Contra la T exacta del peor caso, la pendiente es 0,96.
- **Variante (b):** el tiempo es lineal en el número de rondas (serie l, pendiente 1,06), como dice la T: T veces una ronda de la base.
- **Variante (c2):** el voraz unidad por unidad es lineal en B con S fijo (serie m, pendiente 1,05 contra una esperada de 0,99).

**Ruido en los tamaños pequeños.** Cuando una medición dura menos de 1 ms, los costos fijos (la llamada a la función, crear las estructuras iniciales) y el ruido del sistema pesan más que el trabajo que cuenta T. Se ve en el primer punto de varias series: el cociente de j con N = 8 vale 4,55 contra 3,4 a 3,8 en el resto (sin ese punto, el rango baja de 1,32 a 1,09), y el de h con B = 25 vale 7,77 contra 5,3 a 6,3. La serie f tiene un cociente que sube y baja (3,17; 4,26; 3,21; 4,52; 5,21) sin un patrón claro. El mínimo de 21 repeticiones reduce el ruido, pero no lo elimina. En la docente, con tiempos de décimas de milisegundo, la misma selección midió 0,171 ms en una corrida y 0,441 ms en otra (sección 10.1.4).

**Serie d: la única que no ajusta.** Su pendiente contra T es 2,18 y su cociente se multiplica por 3,2. Hay dos causas, y la primera es la principal:
1. **T usa la misma constante para los dos términos.** El ajuste con dos constantes da a = 1,26·10⁻⁶ s por nodo, unas 6 veces b = 1,96·10⁻⁷ s por unidad y nivel. Armar el montículo cuesta por nodo mucho más que una vuelta del ciclo: hay que evaluar Δ_i(0) y crear la pareja (−Δ_i(0), i) de cada nodo. Con B = 1 000 fijo, el término a·N pasa de 1,26 ms a 20,2 ms, mientras que b·B·lg N solo va de 1,95 ms a 2,74 ms. El tiempo de la serie d es casi todo el término lineal en N. Con las dos constantes, la pendiente esperada es 0,71 y no 0,36, mucho más cerca de la medida, 0,78. La cota O(N + B lg N) no se contradice: es asintótica y no fija las constantes.
2. **Aun con dos constantes, el costo por nodo crece con N.** El ajuste sobrestima los tamaños medios (+25 % en N = 2 000 y 4 000) y subestima el mayor (−5,6 % en N = 16 000). La explicación de la decisión 32 del repositorio es que, a partir de unos miles de nodos, el montículo y las utilidades dejan de caber en la caché del procesador (512 KB de L2 y 3 MB de L3 en esta máquina) y cada acceso se vuelve más lento. **Supuesto ❓:** esta explicación no se comprobó con contadores de caché; es compatible con los datos, pero no es la única posible.

**Otras series cuyo cociente sube en los tamaños mayores.**
- **Serie b** (grafo completo): el cociente sube de 1,25 a 1,72 entre N = 100 y N = 400, cuando el grafo pasa de 4 950 a 79 800 aristas, y la pendiente es 2,09 contra 2,00. Podría ser el mismo efecto de memoria de la serie d. **No comprobado.**
- **Series ic e im:** el cociente sube un 15 % y un 11 % en N = 800, el tamaño mayor, después de quedar plano entre N = 50 y 400. **No se investigó.**
- **Serie l:** el cociente es plano hasta T = 32 (3,69 a 3,73) y desde T = 64 sube cerca de un 14 % (4,20 y 4,29), aunque la pendiente total sigue siendo 1,06. La explicación propuesta en la decisión 51 es que el resultado guarda O(T·(k·N + B)) de trazas y restantes, y esa memoria acumulada encarece las rondas finales. **No comprobado.**
- **Serie m:** el cociente crece despacio con B, de 1,15 a 1,36 (un 18 % en un rango de B de 16 veces). **No se encontró la causa.**
- **Serie h:** el cociente baja en vez de subir (7,77 a 5,33 y luego 5,62), porque T = N·B² ignora el factor 1/2 y los términos N·B del conteo exacto N·(B + 1)(B + 2)/2: con B = 25, el conteo es 0,56·T, y con B = 400, 0,50·T. La pendiente contra B, 1,88, se acerca a 2 a medida que B crece.

En ninguna de estas series el apartamiento cambia el orden de crecimiento. Fuera de la serie d, el cociente varía a lo sumo en un factor de 1,64 (serie f), mientras que T(n) crece entre 15 y 735 veces dentro de cada serie. La serie d es la excepción, y la explica sobre todo la diferencia de constantes entre sus dos términos.
