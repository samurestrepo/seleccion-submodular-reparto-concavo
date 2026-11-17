# 13. Supuestos y limitaciones

**Todos los supuestos de esta sección son decisiones de modelado del equipo, porque el enunciado y el archivo de la docente no las fijan. La docente no los ha confirmado.** Por eso cada uno se marca **Supuesto ❓**. Si la docente indica otra interpretación, cambia el modelo, pero no la técnica: los algoritmos reciben f, las u_i y las restricciones como entradas, y cambiar un supuesto solo cambia el oráculo o los parámetros que se les pasan. El número entre paréntesis es el de la decisión en `docs/agente/DECISIONES.md`.

## 13.1 Supuestos de la solución base (primera entrega)

| # | Supuesto ❓ | Por qué |
|---|---|---|
| 1 (25) | La utilidad de cada nodo en la Parte 1 es u_i(x) = a_i·ln(1 + x), con a_i = `coeficiente_utilidad` | El archivo trae un coeficiente, no la forma de la función. ln(1 + x) es creciente y cóncava con a_i > 0, que es lo que pide la Parte 1 |
| 2 (24) | La utilidad conjunta de la Parte 2 es la cobertura por influencia: f(S) = Σ_w a_w·(1 − Π_{v∈S} (1 − p_vw)), con p_vw = `peso_influencia` y p_ww = 1 | El archivo no trae los conjuntos que usa la cobertura, sino un grafo con pesos. Esta f es monótona, submodular y vale 0 en ∅, así que la cota del voraz se sigue aplicando. Con pesos 0 o 1 es una cobertura |
| 3 (26) | La solución base corre una sola ronda con k y B. Los datos de las variantes (`numero_rondas`, `costo_participacion`, `presupuesto_costos_participacion_por_ronda`) se leen y se reportan, pero solo se aplican si se pide la variante | La primera entrega era la solución base. Ahora cada variante los usa con `--variante` |
| 4 (28) | `presupuesto_total_nodo` es un tope por nodo, x_i ≤ c_i. En una ronda, el nodo lo puede gastar completo | El enunciado dice que cada nodo tiene un presupuesto total para todo el proyecto. Con u_i truncadas en c_i el voraz sigue siendo óptimo |

## 13.2 Supuestos de las variantes

**Variante (a), costos de participación (35).**
- La restricción Σ_{v∈S} c(v) ≤ L **reemplaza** a |S| ≤ k; no se usan las dos a la vez. Con L = 24, en la docente entran 6 nodos, uno más que k = 5.
- c(v) = `costo_participacion` y L = `presupuesto_costos_participacion_por_ronda`. Si se pide la variante, un costo ≤ 0 o un L < 0 rechazan el caso, porque la poda de la fuerza bruta necesita costos positivos.

**Variante (b), T rondas con fallos (39 y 40).**
- T = `numero_rondas` (3 en la docente).
- Antes de cada ronda, cada nodo falla de forma independiente con probabilidad q. En el modo **transitorio** falla solo esa ronda; en el **permanente**, no vuelve. El enunciado no da q ni cómo fallan los nodos: q = 0,2 y la semilla 0 son valores elegidos por el equipo y se pueden cambiar.
- El tope de cada nodo es su **presupuesto restante**: empieza en `presupuesto_total_nodo` y se le descuenta lo que recibe en cada ronda. Sin tope en el archivo, empieza en B.
- Los candidatos de una ronda son los nodos que no fallaron y tienen restante > 0. Se elige con k_r = mín(k, número de candidatos).
- Cada ronda se optimiza sola, con el mismo k y el mismo B, y f se mide sobre el grafo completo: solo cambia quién se puede elegir.

**Variante (c), vecinos (43 a 45).**
- Solo cuentan los vecinos que **están en S**, porque la utilidad de la ronda es la de los participantes.
- w_ij es el `peso_influencia` de la arista {i, j}: el mismo grafo define f en la Parte 2 y el efecto de los vecinos en la Parte 1.
- β = 0,2 es un valor elegido por el equipo («las utilidades se mueven un poco»). Se acepta β = 0, que reproduce la base.
- El enunciado admite dos lecturas de «afectar a los vecinos», y se implementaron las dos. En c1, el efecto se suma aparte y U sigue siendo separable. En c2, el efecto entra en la utilidad del vecino y U deja de ser separable. No se sabe cuál quiere la docente.
- La variante necesita grafo y u_i logarítmicas. El formato propio no trae grafo, así que la variante solo corre con el formato de la docente.

## 13.3 Limitaciones

**Del modelo y los algoritmos**
- **Las T rondas se optimizan una por una.** Cada ronda elige el mejor equipo y el mejor reparto para sí misma, sin pensar en las siguientes. Gastar hoy el presupuesto de un nodo bueno puede dejarlo sin presupuesto para rondas futuras: en la docente, N09, N14 y N15 terminan la ronda 3 con restante 0. Planear las T rondas juntas, con fallos aleatorios, es otro problema (optimización bajo incertidumbre) y no se aborda. Por la misma razón, la garantía ρ(k_r) vale **ronda por ronda** y no hay ninguna garantía sobre la suma de las T rondas.
- **La cota de c2 se derivó en este proyecto.** El argumento ve cada unidad como un elemento y aplica Nemhauser, Wolsey y Fisher (1978) a la función de conjuntos que resulta. No se encontró una fuente publicada para este modelo en particular. El argumento se verificó en 324 filas de datos y en las pruebas, y ninguna lo contradice, pero eso no reemplaza a una revisión externa de la demostración.
- **No se estudió la complejidad de c2.** No se sabe si el problema es NP-difícil o si tiene un algoritmo exacto polinomial que no sea la enumeración.
- **En la variante (a), k y L no se combinan.** Si la docente quiere las dos restricciones a la vez, cambian el voraz por cociente, la fuerza bruta y sus garantías (la cota 0,405 es para una sola restricción de mochila).
- **Caso de borde de la variante (b).** Con B = 0 y sin topes, ningún nodo tiene presupuesto, así que la ronda queda vacía, mientras que la base elige S y reparte 0. Es una consecuencia del supuesto «sin tope, B».

**De los exactos de referencia**
- Todos se niegan a correr si su espacio de búsqueda pasa de 200 000: C(N, k) en la Parte 2 y en cada ronda de (b); 2ᴺ en (a), es decir, N ≤ 17; y el número de repartos en (c). En la docente, (c) tiene 302 792 repartos, así que sus evidencias se generaron subiendo el límite justo a ese número.
- Por ese límite, las baterías que comparan con el OPT usan instancias pequeñas: N ≤ 20 en la Parte 2, N ≤ 16 en (a), N ≤ 12 en (b) y (c). Las razones medidas en las baterías aleatorias (todas ≥ 0,93) describen esas instancias; no dicen nada del peor caso, que lo dan las cotas teóricas.

**De la validación experimental**
- Cada tamaño se mide en una sola instancia (semilla 1) y en una sola máquina. El tiempo depende del equipo; lo que se compara con la teoría es el crecimiento, no los valores absolutos.
- De las series a a h no quedó registro del equipo en que se corrieron; se supone que es el mismo de las series i a m, que sí está registrado (sección 11.1, **Supuesto ❓**).
- La serie d no ajusta a su T. La causa principal está medida: los dos términos de T, N y B lg N, tienen constantes distintas, y con las del ajuste la pendiente esperada pasa de 0,36 a 0,71, contra 0,78 medida. Lo que queda sin explicar (el ajuste aún se equivoca hasta en un 25,8 %) se atribuye a la caché, pero esa explicación no se comprobó con contadores de hardware. Otros apartamientos del cociente tampoco tienen una explicación comprobada: la serie b, la l (se propone la memoria acumulada de las trazas) y el último punto de ic e im; el de la serie m no tiene ninguna explicación propuesta (sección 11.3).
- La batería de la variante (b) solo existe dentro de las pruebas y no deja un CSV. En ella, 30 de las 162 rondas quedan por debajo del OPT; una comparación estricta, sin tolerancia, cuenta 64, porque en 34 rondas el voraz alcanza el OPT y solo difiere en el último dígito de punto flotante (sección 10.2.3).
