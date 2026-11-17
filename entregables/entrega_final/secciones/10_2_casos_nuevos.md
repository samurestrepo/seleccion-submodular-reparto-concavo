## 10.2 Casos nuevos: baterías y contraejemplos

Además del caso de la docente, cada algoritmo aproximado se comparó con su exacto en baterías de instancias aleatorias de influencia, todas con semilla fija. Las instancias salen de `generar_instancia_influencia`: pesos uniformes en [0,05; 0,70], coeficientes en [1; 10] y costos enteros en [1; 5]. Una fila **cumple** si el aproximado no supera al OPT y su razón valor/OPT no baja de la cota que le corresponde (tolerancia 10⁻⁹).

### 10.2.1 Parte 2: batería aleatoria de la cota

Archivo: `resultados/cota/tabla_cota_aleatoria.csv`. Son 45 instancias: N ∈ {12, 14, 16, 18, 20}, k = 5, densidad ∈ {0,3; 0,6; 1,0} y semillas 1, 2 y 3. La cota es ρ(5) = 0,67232.

| Densidad | Razón mínima | Filas con razón < 1 |
|---|---|---|
| 0,3 | 0,936734 (N = 18, semilla 1) | 10 de 15 |
| 0,6 | 0,955607 | 11 de 15 |
| 1,0 | 0,989501 | 12 de 15 |
| Total | 0,936734 | 33 de 45 |

Todas cumplen. El voraz no siempre alcanza el OPT (33 de 45 quedan por debajo), pero nunca se acerca a la cota: la peor razón está unos 26 puntos por encima. Las razones más bajas aparecen en los grafos ralos. No se estudió por qué.

### 10.2.2 Variante (a): batería con costos

Archivo: `resultados/variantes/a_tabla_cota.csv`. Son la docente (L = 24) y 36 instancias con N ∈ {10, 12, 14, 16}, densidad ∈ {0,3; 0,6; 1,0}, semillas 1, 2 y 3, y L = 12. La tabla por tamaño, con las razones y las evaluaciones de los tres aproximados, está en §8.2.4. En resumen: el voraz por cociente y el modificado tienen la misma razón mínima, 0,946839 (N = 10, densidad 0,3, semilla 3; cota del modificado 0,405), y quedan por debajo del OPT en 25 de las 36 aleatorias; la enumeración parcial alcanza el OPT en todas (cota 1 − 1/e ≈ 0,632).

En las 37 filas el modificado devolvió el S del cociente (columna `origen_modificado` = cociente): el mejor nodo solo nunca ganó. Por eso el cociente y el modificado tienen la misma razón en todas las filas. Sin el contraejemplo de §10.2.5, estas baterías no muestran para qué sirve el mejor nodo solo.

### 10.2.3 Variante (b): batería por ronda

La variante (b) no tiene un CSV de batería: la batería vive en `pruebas/test_variante_rondas.py` (`test_bateria_aleatoria_respeta_la_cota_por_ronda`). Son 27 instancias (N ∈ {8, 10, 12}, k = 3, B = 20, densidad ∈ {0,3; 0,6; 1,0}, semillas 1 a 3), en los dos modos y con 3 rondas cada una, con q = 0,3. En total, 162 rondas, todas con OPT_r disponible y ninguna vacía.

- Ninguna ronda incumple su cota ρ(k_r).
- La razón mínima es 0,938153 (N = 10, densidad 0,6, semilla 1, modo transitorio, ronda 3; cota ρ(3) = 0,7037).
- Rondas con razón < 1: **30**. Se cuentan con una tolerancia: una ronda queda por debajo del OPT si su razón es menor que 1 − ε, y cualquier ε entre 10⁻¹⁵ y 10⁻⁶ da las mismas 30 (la menor diferencia real con el OPT es de 0,0025). En las otras 132 rondas el voraz alcanza el OPT de su ronda. Una comparación estricta, razón < 1, cuenta 64: en 34 de esas rondas el voraz encuentra un equipo con el mismo valor que el OPT, pero las dos sumas de punto flotante difieren en el último dígito (a lo sumo 3,3·10⁻¹⁶). Las cifras se reprodujeron corriendo la batería.

Caso de borde documentado: con B = 0 y sin topes, ningún nodo tiene presupuesto, así que la variante deja la ronda vacía, mientras que la base elige S y reparte 0. Por eso `borde_B_cero` con q = 0 y T = 1 **no** reproduce la base. Los otros 13 casos propios y la docente sí la reproducen.

### 10.2.4 Variante (c): batería con vecinos

Archivo: `resultados/variantes/c_tabla_cota.csv`. Son 27 instancias (N ∈ {8, 10, 12}, k = 4, densidad ∈ {0,3; 0,6; 1,0}, semillas 1 a 3), cada una con β ∈ {0,2; 0,5; 1,0; 2,0} y B ∈ {3, 6, 10}: 324 filas. S es el del voraz base, y el exacto es la enumeración de todos los repartos (a lo sumo 1 001 por fila). Las tablas por β y por B están en §8.4.4. En resumen:

- **c1** coincide con la enumeración en las 324 filas, como predice la prueba de optimalidad.
- **c2** queda por debajo del OPT en 7 filas, todas con β ≥ 0,5. La razón mínima, 0,986703, es la de N = 8, densidad 0,3, semilla 1, B = 3 y β = 2, con cota ρ(3) = 0,7037. Con β = 0,2 (el valor de la corrida de la docente) el voraz siempre alcanzó el OPT. El número de filas por debajo del OPT no crece de forma regular con β (3, 2 y 2), y con 7 filas no se puede sacar una tendencia.

### 10.2.5 Contraejemplo del voraz por cociente (variante a)

Es el contraejemplo de §8.2.1, con su tabla. Prueba `test_contraejemplo_del_cociente_tan_malo_como_se_quiera` de `pruebas/test_variante_costos.py`, con cobertura y un parámetro M ≥ 2:

| Nodo | Cubre | Costo | Cociente Δ(v \| ∅)/c(v) |
|---|---|---|---|
| 1 | 2 elementos | 1 | 2 |
| 2 | 2M − 1 elementos | M | (2M − 1)/M < 2 |

L = M. El voraz por cociente toma primero al nodo 1, porque tiene el mayor cociente; después el nodo 2 ya no cabe (1 + M > M). Obtiene f = 2, mientras que OPT = 2M − 1 (el nodo 2 solo). La razón es 2/(2M − 1), que tiende a 0 cuando M crece: con M = 10, 100 y 1 000 vale 0,105, 0,0101 y 0,0010. Por eso el voraz por cociente no tiene ninguna garantía constante. El voraz modificado compara además con el mejor nodo que cabe solo, f({2}) = 2M − 1, y devuelve el OPT sin evaluaciones extra: f({v}) = Δ(v | ∅) ya se calculó en el primer paso del cociente.

### 10.2.6 Contraejemplo del voraz de c2

Es el contraejemplo de §8.4.2, paso a paso. Prueba `test_contraejemplo_minimo_de_c2` de `pruebas/test_variante_vecinos.py`. Es un trayecto 1 – 2 – 3, con a = (3, 2, 3), w_12 = w_23 = 1, β = 0,2, B = 2 y sin topes. La entrada efectiva es z_j = x_j + β·(suma de los x de sus vecinos), y U = Σ_j a_j·ln(1 + z_j).

| Paso | Ganancia del nodo 1 | Ganancia del nodo 2 | Ganancia del nodo 3 | Elige |
|---|---|---|---|---|
| 1 (x = 0, 0, 0) | 3·ln 2 + 2·ln 1,2 ≈ 2,4441 | 2·ln 2 + 6·ln 1,2 ≈ 2,4802 | ≈ 2,4441 | 2 (el centro le sube a los dos extremos) |
| 2 (x = 0, 1, 0) | ≈ 2,0090 | ≈ 1,7358 | ≈ 2,0090 | 1 (empata con el 3; gana el menor índice) |

- Voraz: x = (1, 1, 0), z = (1,2; 1,2; 0,2) y U = 5·ln 2,2 + 3·ln 1,2 ≈ **4,489251**.
- Óptimo: x = (1, 0, 1), z = (1; 0,4; 1) y U = 6·ln 2 + 2·ln 1,4 ≈ **4,831828**.
- Razón: 0,929100 ≥ ρ(2) = 0,75. La enumeración evalúa C(5, 3) = 10 repartos.

El primer paso muestra por qué falla el voraz. Darle la unidad al centro es lo mejor en ese momento, porque sube a la vez la entrada efectiva de los dos extremos. Con dos unidades, en cambio, conviene dárselas a los extremos: tienen mayor coeficiente y entre los dos le suben 0,4 al centro. El voraz no deshace su primera elección. La ganancia de un extremo depende de lo que recibió el centro, y esa dependencia es justo lo que rompe H1. En la búsqueda con dos nodos y B ≤ 4 (coeficientes de 1 a 10 y pesos 0,25, 0,5 y 1) no apareció ningún contraejemplo; eso no prueba que no exista. Los valores de las ganancias del paso 2 se calcularon a mano con la fórmula de GANANCIA de `docs/modulos/variante_vecinos.md`.
