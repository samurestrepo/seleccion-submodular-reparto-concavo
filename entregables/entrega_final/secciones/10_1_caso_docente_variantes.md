## 10.1 El caso de la docente con las variantes

El caso `entrada_G2_red_15_nodos.json` (15 nodos, grafo completo de 105 aristas, k = 5, B = 30, topes de 18, L = 24, 3 rondas) se corrió con cada variante, con 21 repeticiones medidas. La base de comparación es la corrida de la primera entrega (`resultados/profesora/entrada_G2_red_15_nodos/salida.json`), que no se regeneró. Los comandos de cada corrida están en la sección 9 del manual técnico. Cada corrida deja `salida.json`, `traza.json`, `traza.txt` y `resumen.csv` en su carpeta de `resultados/variantes/`. Todas las verificaciones de las seis corridas se cumplen (`todas_cumplen` = true).

### 10.1.1 Resultado de la base

| Dato | Valor |
|---|---|
| S, en el orden de elección | N11, N14, N09, N15, N13 |
| f(S) | 145,5795, con 65 llamadas a Δ |
| x | 5, 7, 7, 6, 5 (30 unidades; ningún nodo llega a su tope) |
| U(x) | 88,5640, con 30 extracciones y 30 inserciones |
| Tiempo (mediana) | Parte 2: 0,171 ms; Parte 1: 0,038 ms |

### 10.1.2 Variante (a): costos de participación, L = 24

Carpeta: `resultados/variantes/a_profesora/`. La Parte 2 es el voraz modificado y Σ c(S) ≤ 24 reemplaza a |S| ≤ 5 (**Supuesto ❓**, sección 13).

| Dato | Base | Variante (a) |
|---|---|---|
| S | N11, N14, N09, N15, N13 | N05, N09, N14, N11, N15, N01 |
| \|S\| y Σ c(S) | 5 y 23 | 6 y 21 (≤ 24) |
| f(S) | 145,5795 | 145,9911 |
| Evaluaciones de f | 65 llamadas a Δ | 74 (73 a Δ y 1 a f(∅)); dentro de la cota 1 + \|S\|·N − \|S\|(\|S\| − 1)/2 = 76 |
| De dónde sale S | voraz | del voraz por cociente (el mejor nodo solo no ganó) |
| x | 5, 7, 7, 6, 5 | 4, 6, 6, 4, 5, 5 |
| U(x) | 88,5640 | 95,9552 |
| Tiempo (mediana) | 0,171 ms y 0,038 ms | 0,223 ms y 0,040 ms |

Contra el OPT de la variante (`resultados/variantes/a_tabla_cota.csv`): OPT = 146,27141, con costo 23; la razón del modificado es 0,998084, muy por encima de la cota 0,405. La enumeración parcial alcanza el OPT con 13 117 evaluaciones, y la fuerza bruta evalúa los 4 502 subconjuntos factibles.

**Lectura.** Con costos, entra un sexto nodo: los nodos de costo bajo (N05 cuesta 2, y N01, N09 y N14 cuestan 3) dejan espacio que con k = 5 no se podía usar. El S de la base también cabía en L (costo 23), pero vale menos (145,5795). U sube porque las 30 unidades se reparten entre 6 nodos: con u_i cóncavas, más nodos significa que cada unidad llega a una parte más empinada de alguna curva. Las dos U no son comparables como «mejor» o «peor», porque los equipos son distintos. El tiempo de la selección sube con las evaluaciones (74 contra 65).

### 10.1.3 Variante (b): 3 rondas con fallos, q = 0,2, semillas 0 y 3

Carpetas: `resultados/variantes/b_profesora_transitorio/` y `b_profesora_permanente/`. Con la semilla 0, los fallados son ∅ en la ronda 1, {N11} en la 2 y {N06, N11} en la 3. El modo transitorio y el permanente dan **exactamente la misma trayectoria**: las dos salidas coinciden en todo, salvo en los tiempos. Coinciden porque los fallados de cada ronda quedan contenidos en los de la siguiente (∅ ⊆ {N11} ⊆ {N06, N11}). En el modo permanente, los excluidos de la ronda r son la unión de los fallados de las rondas 1 a r, y con esta cadena esa unión es igual a los fallados de la ronda r: el modo permanente no excluye a nadie más que el transitorio.

| Ronda | Candidatos | S_r | f(S_r) | OPT_r (evaluaciones) | Razón | x | U_r | Restante total tras la ronda |
|---|---|---|---|---|---|---|---|---|
| 1 | 15 | N11, N14, N09, N15, N13 | 145,5795 | 145,9072 (3 003) | 0,9978 | 5, 7, 7, 6, 5 | 88,5640 | 240 |
| 2 | 14 (sin N11) | N09, N14, N07, N15, N10 | 144,7351 | 144,7351 (2 002) | 1 | 6, 6, 5, 6, 7 | 99,1361 | 210 |
| 3 | 13 (sin N06 ni N11) | N09, N14, N07, N15, N10 | 144,7351 | 144,7351 (1 287) | 1 | 5, 5, 6, 6, 8 | 98,8855 | 180 |

Llamadas a Δ por ronda: 65, 60 y 55 (k·n_r − k(k − 1)/2, con n_r = 15, 14 y 13). La cota de cada ronda es ρ(5) = 0,67232. Suma de las 3 rondas: Σ f(S_r) = 435,0497 y Σ U_r = 286,5856, sin rondas vacías. El restante total empieza en 15·18 = 270. Fuente: `resumen.csv` y `salida.json` de las dos carpetas. Esta es la tabla de referencia de la docente en (b); §8.3.3 comprueba con ella el análisis de la variante.

**Lectura.**
- La ronda 1 reproduce la base: mismos S, f, x y U.
- En la ronda 2 salen N11 (falló) y N13, y entran N07 (coeficiente 8,9) y N10 (12,4, el mayor de la red) en lugar de N11 (7,6) y N13 (8,3). Por eso U sube a 99,1361.
- En la ronda 3 el presupuesto restante empieza a limitar. N09, N14 y N15 tenían 5, 5 y 6 unidades, y las gastan completas: el reparto hace 30 extracciones pero solo 27 inserciones, porque esos tres nodos llegan a su tope y no vuelven al montículo. Al final de la ronda les queda 0, así que no podrían participar en una cuarta ronda.
- Los tiempos de cada ronda (mediana: Parte 2 de 0,15 a 0,28 ms, Parte 1 de 0,036 a 0,063 ms) son del mismo orden que los de la base, como predice la T de la variante: T veces una ronda de la base.

**Semilla 3: los dos modos se separan.** Carpetas: `resultados/variantes/b_profesora_transitorio_s3/` y `b_profesora_permanente_s3/`, generadas con los mismos parámetros que las de la semilla 0 salvo `--semilla-fallos 3` (q = 0,2, T = 3, R = 21). Los fallados son {N06, N07} en la ronda 1, {N01, N07, N11} en la 2 y {N08, N09} en la 3. Como no forman una cadena, en el modo permanente los excluidos se acumulan: {N06, N07}, {N01, N06, N07, N11} y {N01, N06, N07, N08, N09, N11}.

| Ronda | Modo | Fallados | Candidatos | S_r | f(S_r) | OPT_r (evaluaciones) | Razón | x | U_r | Restante total tras la ronda |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | los dos | N06, N07 | 13 (sin N06 ni N07) | N11, N14, N09, N15, N13 | 145,5795 | 145,9072 (1 287) | 0,9978 | 5, 7, 7, 6, 5 | 88,5640 | 240 |
| 2 | transitorio | N01, N07, N11 | 12 (sin N01, N07 ni N11) | N09, N14, N12, N15, N10 | 144,5000 | 144,5000 (792) | 1 | 5, 6, 7, 5, 7 | 104,7363 | 210 |
| 2 | permanente | N01, N07, N11 | 11 (sin N01, N06, N07 ni N11) | N09, N14, N12, N15, N10 | 144,5000 | 144,5000 (462) | 1 | 5, 6, 7, 5, 7 | 104,7363 | 210 |
| 3 | transitorio | N08, N09 | 13 (sin N08 ni N09) | N11, N14, N07, N15, N12 | 145,2431 | 145,4935 (1 287) | 0,9983 | 5, 5, 6, 6, 8 | 93,4461 | 180 |
| 3 | permanente | N08, N09 | 9 (sin N01, N06, N07, N08, N09 ni N11) | N14, N05, N12, N15, N10 | 143,2841 | 143,2841 (126) | 1 | 5, 4, 7, 6, 8 | 100,9195 | 180 |

x va en el orden de S_r. Llamadas a Δ por ronda: 55, 50 y 55 en transitorio (n_r = 13, 12 y 13) y 55, 45 y 35 en permanente (n_r = 13, 11 y 9), las dos veces k·n_r − k(k − 1)/2. Suma de las 3 rondas: Σ f(S_r) = 435,3226 y Σ U_r = 286,7464 en transitorio; Σ f(S_r) = 433,3636 y Σ U_r = 294,2198 en permanente. Sin rondas vacías y todas las verificaciones cumplen. Fuente: `resumen.csv` y `salida.json` de las dos carpetas.

**Lectura (semilla 3).**
- La ronda 1 es igual en los dos modos y reproduce la base (mismos S, f, x y U que la ronda 1 de la semilla 0), porque N06 y N07 no estaban en el S de la base. Solo cambia el número de evaluaciones del exacto: C(13, 5) = 1 287 en lugar de 3 003.
- En la ronda 2 el modo permanente deja fuera también a N06, pero N06 tampoco está en el S_2 del transitorio: S_2, x y U coinciden y solo cambian los candidatos y las evaluaciones (792 contra 462).
- En la ronda 3 las trayectorias se separan. El transitorio recupera a N07 y N11, que fallaron en la ronda 2 pero no en la 3, y los elige; el permanente tiene 9 candidatos y elige N05 y N10 en su lugar. f(S_3) es menor en permanente (143,2841 contra 145,2431) y U_3 es mayor (100,9195 contra 93,4461), porque N10 tiene el coeficiente más alto de la red (12,4) frente a N11 (7,6) y N07 (8,9). La selección maximiza f, no U, así que nada obliga a que un modo gane en las dos sumas.
- En los dos modos N14 gasta sus 18 unidades (7 + 6 + 5) y queda en 0 tras la ronda 3; esa ronda hace 30 extracciones y 29 inserciones.

### 10.1.4 Variante (c): vecinos, β = 0,2

Carpetas: `resultados/variantes/c1_profesora/` y `c2_profesora/`. La Parte 2 no cambia: S = N11, N14, N09, N15, N13, con f = 145,5795 y 65 llamadas. Como el grafo es completo, S tiene sus 10 aristas internas. El exacto (enumeración) recorre los 302 792 repartos. Ese número pasa el límite por omisión de 200 000, y por eso las dos corridas se hicieron con `--limite-repartos 302792`, el número exacto.

| Dato | Base | c1 (efecto aparte) | c2 (efecto dentro) |
|---|---|---|---|
| Coeficientes | a = 7,6; 10,1; 9,9; 9,5; 8,3 | a' = 7,96; 10,48; 10,26; 9,70; 8,54 | a, con z_j = x_j + β·Σ w_ij·x_i |
| x (N11, N14, N09, N15, N13) | 5, 7, 7, 6, 5 | 5, 7, 7, 6, 5 | 4, 8, 7, 6, 5 |
| U(x) del modelo | 88,5640 | 91,5670 | 99,2470 |
| OPT de la enumeración | — | 91,5670 (razón 1) | 99,2470 (razón 1; cota ρ(30) = 0,6383) |
| U del x de la base con este modelo | — | 91,5670 | 99,2246 |
| Operaciones del reparto | 30 extracciones y 30 inserciones | 30 extracciones y 30 inserciones | 30 pasos, 155 ganancias recalculadas y 150 nodos revisados |
| Tiempo del reparto (mediana) | 0,038 ms | 0,057 ms | 1,528 ms |
| Tiempo del exacto (una vez) | — | 1,19 s | 3,52 s |

**Lectura.**
- **c1** no cambia el reparto. Los a'_i quedan entre 0,20 y 0,38 por encima de los a_i, las proporciones entre nodos casi no cambian y el resultado es el mismo x. U sube de 88,5640 a 91,5670 solo porque los coeficientes son mayores. El voraz coincide con el OPT, como exige la prueba de la sección 7.1.1.
- **c2** sí cambia el reparto: le quita una unidad a N11 y se la da a N14. En c2, la ganancia de darle una unidad a un nodo incluye lo que sube la entrada efectiva de sus vecinos, y eso cambia el orden en que se entregan las unidades. El reparto de la base, evaluado con el modelo c2, da 99,2246; el voraz de c2 da 99,2470, que es el OPT. En este caso el voraz de c2 fue exacto, aunque en general no lo es (contraejemplo de §8.4.2 y §10.2.6).
- **Conteos de c2.** 155 = m + B·m = 5 + 30·5 ganancias recalculadas y 150 = B·m revisados: con S completo, cada unidad cambia las ganancias de los 5 nodos (todos están a distancia ≤ 2 del que recibe). Por eso el reparto de c2 cuesta unas 40 veces más que el de la base (1,528 ms contra 0,038 ms): es O(B·k²) contra O(k + B lg k).
- **Tiempo de la selección.** En la corrida de c2 la Parte 2 midió 0,441 ms de mediana (0,412 ms de mínimo), contra 0,171 ms en la base y 0,185 ms en c1, con el mismo algoritmo, el mismo S y las mismas 65 llamadas. La diferencia no viene del algoritmo: el equipo estaba más lento durante esa corrida. Muestra el ruido de medir tiempos de décimas de milisegundo (sección 11.3).

### 10.1.5 Corrida combinada: (a) + (b) + (c)

Carpetas: `resultados/variantes/combinada_c1/` y `combinada_c2/` (`salida.json` y `traza.txt`), generadas con `python scripts/corrida_combinada.py`. Se combinan las tres variantes sin cambiar ninguna: 3 rondas con fallos (q = 0,2, semilla 0, modo transitorio); en cada ronda, el voraz modificado de (a) sobre los candidatos con Σ c(S_r) ≤ L = 24; y el reparto de (c) con β = 0,2 y topes = presupuesto restante. **Supuesto ❓:** en cada ronda L reemplaza a k, como en la variante (a) sola. OPT_r es la fuerza bruta con presupuesto sobre los candidatos (§7.4). Con la semilla 0 los fallados de cada ronda contienen a los de la anterior, así que el modo permanente da exactamente lo mismo.

| Ronda | Candidatos | S_r | Σ c(S_r) | f(S_r) | OPT_r (subconjuntos factibles) | Razón | x (c1) | U_r (c1) | x (c2) | U_r (c2) | Restante total |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 15 | N05, N09, N14, N11, N15, N01 | 21 | 145,9911 | 146,2714 (4 502) | 0,9981 | 4, 6, 6, 4, 5, 5 | 101,6339 | 4, 6, 6, 4, 5, 5 | 115,1394 | 240 |
| 2 | 14 (sin N11) | N05, N09, N14, N01, N07, N15 | 21 | 145,5303 | 145,9281 (3 013) | 0,9973 | 4, 5, 6, 5, 5, 5 | 103,6683 | 4, 6, 6, 4, 5, 5 | 117,4837 | 210 |
| 3 | 13 (sin N06 ni N11) | N05, N09, N14, N01, N07, N15 | 21 | 145,5303 | 145,9281 (2 333) | 0,9973 | 4, 5, 6, 5, 5, 5 | 103,6683 | 4, 6, 6, 4, 5, 5 | 117,4837 | 180 |

x va en el orden de S_r. Suma de las 3 rondas: Σ f(S_r) = 437,0517; Σ U_r = 308,9705 con c1 y 350,1068 con c2. Todas las verificaciones cumplen (Σ c(S_r) ≤ L, S_r ⊆ candidatos, f recalculada, f(S_r) ≥ 0,405·OPT_r, topes y restante ≥ 0).

**Lectura.**
- La ronda 1 es la variante (a) de §10.1.2 (mismo S_r y f), con el reparto de c1 o c2 en lugar del de la base.
- La selección no depende del modelo de reparto: las dos corridas eligen los mismos S_r. Solo cambian x y U_r.
- Las rondas 2 y 3 eligen lo mismo: la caída de N06 en la ronda 3 no afecta, porque N06 no estaba en S_r, y el restante alcanza justo: el reparto de la ronda 3 es el mismo de la ronda 2. Al final, N14 queda con 0 unidades en las dos corridas (6 por ronda) y N09 también en c2; no podrían participar en una cuarta ronda.
- En c2 el exacto del reparto no corre: con 6 nodos, B = 30 y topes hay entre 0,5 y 1,9 millones de repartos por ronda, por encima del límite de 200 000. La referencia de c2 en este caso está en §10.1.4. En c1 el voraz es exacto (§7.1.1).
- Costo: cada ronda cuesta lo mismo que la variante (a) más el reparto del modelo; la corrida completa es O(T·(m·(N + A) + B lg m)) con c1 y O(T·(m·(N + A) + B·(m + A_S))) con c2, con m = |S_r| (manual técnico, §9.4).
