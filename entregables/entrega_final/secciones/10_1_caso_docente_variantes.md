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

### 10.1.3 Variante (b): 3 rondas con fallos, q = 0,2, semilla 0

Carpetas: `resultados/variantes/b_profesora_transitorio/` y `b_profesora_permanente/`. Con la semilla 0, los fallados son ∅ en la ronda 1, {N11} en la 2 y {N06, N11} en la 3. Como N11 vuelve a fallar en la ronda 3, el modo transitorio y el permanente dan **exactamente la misma trayectoria**: las dos salidas coinciden en todo, salvo en los tiempos.

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
