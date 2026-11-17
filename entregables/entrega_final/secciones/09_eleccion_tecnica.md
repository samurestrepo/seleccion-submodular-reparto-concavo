# 9. Elección de la técnica

En esta sección se explica por qué cada parte y cada variante se resuelve con la técnica que usa el código y no con las otras técnicas del curso. Amplía la tabla de la sección 6.2 de la primera entrega: agrega las variantes y los costos de cada técnica en el caso de la docente.

## 9.1 Las técnicas que se comparan

- **Fuerza bruta:** genera todas las soluciones posibles, evalúa cada una y se queda con la mejor. Es exacta, y cuesta tanto como soluciones haya.
- **Divide y vencerás:** parte el problema en subproblemas independientes del mismo tipo, los resuelve por separado y combina sus respuestas.
- **Voraz:** arma la solución tomando en cada paso la mejor decisión local, y no la deshace. Es exacto solo si una propiedad del problema lo garantiza. Si no lo es, puede tener una razón de aproximación (sección 2.1).
- **Programación dinámica (PD):** guarda en una tabla las respuestas de subproblemas que se repiten (sección 2.1). Sirve si el valor de una solución se arma con los de soluciones más pequeñas y si hay pocos estados distintos.
- **Backtracking (vuelta atrás):** recorre en profundidad el árbol de soluciones parciales y abandona una rama en cuanto esta viola una restricción. En el peor caso visita lo mismo que la fuerza bruta.
- **Ramificación y poda:** es un backtracking que además abandona una rama cuando una cota superior de lo mejor que se puede lograr desde ella no supera la mejor solución que ya se conoce.

**Separabilidad.** Un objetivo es separable si es una suma de términos en la que cada término depende de una sola decisión. Σ_i u_i(x_i) es separable. f(S) no lo es, porque el aporte de un nodo depende de quiénes más están en S. La separabilidad es la hipótesis H1 de la prueba de optimalidad del voraz de la Parte 1 (sección 7.1.1); las cuatro hipótesis, H1 separación, H2 monotonía, H3 concavidad y H4 topes, están definidas en la sección 2.1.

## 9.2 Árbol de decisión

Para cada problema se hicieron las mismas preguntas, en este orden:

```
ELEGIR-TÉCNICA(problema)
1  si hay un voraz con prueba de optimalidad (argumento de intercambio)
2      usar ese voraz: es exacto y es lo más barato
3  si no, si el objetivo es separable y la PD tiene un número polinomial de estados
4      usar la PD: exacta y polinomial
5  si no, si el problema es NP-difícil
6      en la ronda: un voraz con razón de aproximación demostrada o citada
7      como referencia: un exacto exponencial (fuerza bruta o backtracking),
8          solo en tamaños pequeños y con un límite explícito
9  divide y vencerás solo si hay subproblemas independientes (aquí nunca los hay)
```

La línea 9 descarta divide y vencerás en todo el proyecto. En la Parte 1, lo que conviene darle a una mitad de los nodos depende de lo que reciba la otra mitad, porque las dos comparten B. En la Parte 2, el valor de la unión de dos equipos no es la suma de sus valores. Por ejemplo, en el contraejemplo de la Parte 2 (nodos {1, 2, 3, 4}, {1, 2, 5} y {3, 4, 6}), el nodo 1 cubre 4 elementos y el nodo 2 cubre 3, pero juntos cubren 5, no 7.

## 9.3 Parte 2: selección de nodos

| Técnica | Qué haría | Costo en la docente (N = 15, k = 5) | ¿Se usa? |
|---|---|---|---|
| Fuerza bruta | evaluar f en los C(N, k) equipos de tamaño k | C(15, 5) = 3 003 evaluaciones de f | sí, como referencia (`red/exacto.py`) |
| PD | el estado tendría que ser el equipo completo, porque f no es una suma | hasta 2¹⁵ = 32 768 estados (4 944 si solo se cuentan los de tamaño ≤ 5), y en cada uno hay que evaluar f | no |
| Backtracking | recorrer los equipos en profundidad; la única restricción es \|S\| = k | las mismas 3 003 hojas: no hay nada que podar | no (es la fuerza bruta) |
| Ramificación y poda | podar con la cota f(S) + suma de los k − \|S\| mayores Δ(v \| S), válida por monotonía y submodularidad | depende de la instancia; el peor caso sigue siendo exponencial | no (no implementada) |
| Voraz | en cada paso, agregar el nodo de mayor Δ(v \| S) | 65 llamadas a Δ (k·N − k(k − 1)/2) | **sí, en la ronda** |

**Por qué el voraz.** El problema es NP-difícil (sección 6), así que aplica la línea 5 del árbol: no se conoce un algoritmo exacto polinomial. El voraz hace Θ(N·k) llamadas a Δ. Como f es monótona, submodular y f(∅) = 0, garantiza f(S) ≥ ρ(k)·OPT ≥ (1 − 1/e)·OPT (Nemhauser, Wolsey y Fisher, 1978). Con k = 5, ρ(5) = 0,67232. En la docente el voraz obtuvo 145,57952 contra OPT = 145,907178, una razón de 0,997754 (`resultados/cota/tabla_cota.csv`).

**Por qué no la PD.** La PD funciona cuando el valor de un estado se calcula combinando los valores de estados más pequeños. Con f eso no pasa: f(S ∪ {v}) = f(S) + Δ(v | S), y Δ(v | S) depende de todo S, no de un resumen pequeño de él. El estado tendría que ser el conjunto S entero. Entonces la PD visita tantos estados como subconjuntos hay (2ᴺ en general) y no ahorra nada frente a la fuerza bruta.

**Por qué la fuerza bruta queda solo como referencia.** Da el OPT real, con el que se mide la razón del voraz. Pero su costo, C(N, k) evaluaciones, crece de forma exponencial cuando k crece con N. En la serie g de la sección 11 (k = N/2) pasa de 70 evaluaciones con N = 8 a 12 870 con N = 16. Por eso no corre si C(N, k) > 200 000.

## 9.4 Parte 1: reparto del presupuesto

| Técnica | Qué haría | Costo en la docente (\|S\| = 5, B = 30, topes de 18) | ¿Se usa? |
|---|---|---|---|
| Fuerza bruta | evaluar U en todos los repartos enteros con Σ x_i ≤ B y x_i ≤ c_i | 302 792 repartos (C(35, 5) − 5·C(16, 5)) | no (el enunciado la prohíbe en esta parte) |
| Backtracking | el mismo recorrido, abandonando las ramas que pasan de B o de un tope | las mismas 302 792 hojas | no |
| PD (sección 7.2) | M[i][b] = mejor utilidad con los i primeros nodos y a lo sumo b unidades | Σ_i Σ_b (mín(c_i, b) + 1) = 5·418 = 2 090 candidatos; peor caso Θ(N·B²) | sí, como referencia (`red/pd_reparto.py`) |
| Voraz con montículo | cada unidad va al nodo de mayor ganancia marginal | 30 extracciones y 30 inserciones; Θ(N + B(1 + lg N)) | **sí, en la ronda** |

**Por qué el voraz.** Con u_i crecientes y cóncavas el voraz es exacto: es la línea 1 del árbol, y la prueba es el argumento de intercambio de la sección 7.1.1. Su costo, O(N + B lg N), es menor que el de la PD en un factor del orden de B/lg N.

**Por qué la PD queda solo como referencia.** La Parte 1 sí admite PD, porque Σ u_i(x_i) es separable (H1): el mejor reparto de b unidades entre los i primeros nodos solo depende de cuántas unidades se les dejan a los i − 1 anteriores. La PD es correcta aunque las u_i no sean cóncavas, y por eso sirve para contrastar. En la docente da el mismo reparto (x = 5, 7, 7, 6, 5) y la misma utilidad que el voraz (88,563953), pero revisa 2 090 candidatos, mientras que el voraz hace 60 operaciones del montículo. El número 2 090 sale de la fórmula de conteo de `docs/modulos/pd_reparto.md` y se comprobó corriendo `repartir_pd` sobre el S de la docente; no está en un archivo de evidencias.

## 9.5 Variantes

**(a) Costos de participación (mochila submodular).** Se maximiza f(S) sujeto a Σ_{v∈S} c(v) ≤ L. Con c(v) = 1 y L = k es exactamente la Parte 2, así que también es NP-difícil (sección 6.9), y aplican las líneas 5 a 8 del árbol. La PD de la mochila clásica, por capacidad restante, no sirve, porque f no es una suma de valores por objeto: es el mismo obstáculo de la sección 9.3.

| Técnica | Costo en la docente (L = 24) | Garantía | ¿Se usa? |
|---|---|---|---|
| Backtracking con poda por factibilidad (si S no cabe, ningún superconjunto cabe; sección 7.4) | 4 502 subconjuntos factibles de 32 768 | exacto | como referencia |
| Voraz por cociente Δ(v \| S)/c(v) | 74 evaluaciones | ninguna constante (contraejemplo en las secciones 8.2.1 y 10.2.5) | no solo |
| Voraz modificado: el mejor entre el del cociente y el mejor nodo que cabe solo | 74 evaluaciones (las mismas) | 0,405 (Tang et al., 2021) | **sí, en la ronda** |
| Enumeración parcial: todos los factibles de tamaño ≤ 2 y, desde cada factible de tamaño 3, el voraz por cociente | 13 117 evaluaciones | 1 − 1/e (Sviridenko, 2004) | como referencia |

Las cifras son de `resultados/variantes/a_tabla_cota.csv`. Se elige el voraz modificado porque cuesta lo mismo que el del cociente y tiene garantía constante. La enumeración parcial tiene mejor garantía, pero hace O(N⁵) evaluaciones: en la docente, 177 veces las del modificado.

**(b) T rondas con nodos que fallan.** Cada ronda es la Parte 2 seguida de la Parte 1 sobre los nodos que pueden participar. Por eso el árbol da las mismas respuestas que en las secciones 9.3 y 9.4: en cada ronda, el voraz de selección y el voraz de reparto. En la docente, el exacto de cada ronda evalúa 3 003, 2 002 y 1 287 equipos, y el voraz hace 65, 60 y 55 llamadas a Δ (`resultados/variantes/b_profesora_transitorio/entrada_G2_red_15_nodos/salida.json`). Planear las T rondas juntas es otro problema, porque el presupuesto restante de cada nodo las acopla y los fallos son aleatorios. No se aborda (sección 13).

**(c1) Vecinos: el efecto va aparte.** Al agrupar los términos por nodo queda U(x) = Σ_{i∈S} a'_i·ln(1 + x_i), con a'_i = a_i + β·Σ_{j∈S vecino de i} w_ij. Es la Parte 1 con otros coeficientes: sigue siendo separable, creciente y cóncava. El árbol termina en la línea 1, y el voraz con montículo sigue siendo exacto.

**(c2) Vecinos: el efecto va dentro.** u_j = a_j·ln(1 + z_j), con z_j = x_j + β·Σ_{i∈S vecino de j} w_ij·x_i. Como z_j mezcla los x de los vecinos, U deja de ser separable y se pierde H1. Sin H1 no vale el argumento de intercambio (línea 1) ni la PD de la sección 7.2 (línea 3), porque el estado de la PD tendría que incluir los x de los vecinos ya repartidos. Queda la línea 5:

| Técnica | Costo en la docente (\|S\| = 5, B = 30, topes de 18) | Garantía | ¿Se usa? |
|---|---|---|---|
| Enumeración de repartos (backtracking) | 302 792 repartos | exacto | como referencia |
| Voraz unidad por unidad | 30 pasos, 155 ganancias recalculadas | U ≥ ρ(B)·OPT; con B = 30, ρ(30) = 0,6383 | **sí** |

Las cifras son de `resultados/variantes/c2_profesora/entrada_G2_red_15_nodos/salida.json`. La garantía sale de ver cada unidad de presupuesto como un elemento. U tiene rendimientos decrecientes en cada coordenada (sección 2.1), y así el voraz unidad por unidad es el voraz de Nemhauser, Wolsey y Fisher (1978) sobre una función de conjuntos monótona y submodular.

## 9.6 Resumen

| Problema | ¿NP-difícil? | Técnica en la ronda | ¿Exacta? | Referencia exacta |
|---|---|---|---|---|
| Parte 2 | sí | voraz | no: ≥ ρ(k)·OPT | fuerza bruta, C(N, k) evaluaciones |
| Parte 1 | no | voraz con montículo | sí (concavidad) | PD, Θ(N·B²) |
| (a) | sí | voraz modificado | no: ≥ 0,405·OPT | backtracking con poda, ≤ 2ᴺ; enumeración parcial (1 − 1/e) |
| (b) | cada ronda, como la Parte 2 | los dos voraces, ronda por ronda | por ronda, como la base | fuerza bruta en cada ronda |
| (c1) | no | voraz con montículo, con los a'_i | sí | enumeración |
| (c2) | no se estudió | voraz unidad por unidad | no: ≥ ρ(B)·OPT | enumeración, C(B + k, k) repartos sin topes |

**Supuesto ❓:** no se demostró si el problema de c2 es NP-difícil. El árbol no lo necesita: basta saber que el voraz deja de ser exacto (contraejemplo de las secciones 8.4.2 y 10.2.6) y que la PD de la sección 7.2 deja de aplicar.
