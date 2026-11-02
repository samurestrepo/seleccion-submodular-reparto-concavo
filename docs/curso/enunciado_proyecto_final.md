**Proyecto Semestral 2026-2**

**Análisis y Diseño de Algoritmos**

# 1. Presentación

Este documento formula un proyecto de optimización algorítmica, que no depende de ninguna tecnología propietaria, y puede formularse, resolverse y evaluarse íntegramente con las herramientas del curso.

Recuerden que no basta con programar algo que funcione. Cada equipo debe demostrar formalmente qué tan eficiente es su solución, tanto para el caso exacto como para cualquier aproximación o heurística que proponga.

# 2. Qué significa "eficiente"

Esto es lo que se exige demostrar — no es opcional ni queda a discreción del equipo:

> **Deben demostrar:** la definición precisa del tamaño de entrada n del problema (qué está creciendo cuando el problema se vuelve más grande).
>
> **Deben demostrar:** la función de eficiencia T(n) del algoritmo exacto, obtenida contando operaciones o resolviendo una recurrencia (no una estimación intuitiva: una deducción explícita, paso a paso, con su notación resultante).
>
> **Deben demostrar:** para cualquier algoritmo aproximado o heurístico: su propia función de eficiencia T(n), y — cuando exista una garantía demostrable conocida (por ejemplo, una razón de aproximación) — su demostración o su aplicación correcta citando el resultado del que proviene.
>
> **Deben demostrar:** una validación experimental, esto implica medir el tiempo real de ejecución para valores crecientes de n, graficar los resultados, y contrastar el crecimiento observado contra el crecimiento que predice la función T(n) deducida teóricamente, como lo hemos hecho en clase.

Un informe que solo reporte "......tardó X segundos" sin la formalidad requerida, no cumple el nivel del curso, sin importar qué tan bien funcione el código.

# 3. Estructura general

| **Problema** | **Técnica central** | **Tipo de dificultad** |
|---|---|---|
| Reparto de un presupuesto limitado y selección de participantes | Algoritmo voraz óptimo (asignación cóncava) + aproximación submodular | Parte polinomial exacta + parte NP-difícil (reducción desde Cobertura de Conjuntos) |

# 4. Proyecto Red — Reparto de presupuesto y selección de participantes

## 4.1 Escenario

Una red de N nodos entrena de forma colaborativa un modelo a lo largo de T rondas, sin compartir datos crudos entre ellos, protegiendo cada actualización con un mecanismo que introduce ruido calibrado (más ruido protege más, pero reduce la utilidad de la actualización). Cada nodo tiene un presupuesto total de "ruido tolerable" a lo largo de todo el proyecto. En cada ronda hay que decidir qué subconjunto de nodos participa y cuánto de su presupuesto se gasta.

## 4.2 Parte 1 — Reparto óptimo del presupuesto

**Tamaño de la entrada:** N, el número de nodos ya seleccionados para participar en una ronda.

**Entrada:** para cada nodo, una función de utilidad u_i(x) cóncava y creciente (cada unidad adicional de presupuesto gastada aporta una ganancia marginal menor que la anterior), y un presupuesto total B a repartir entre los N nodos.

**Objetivo:** repartir B entre los N nodos para maximizar Σ u_i(x_i).

Este problema sí tiene solución exacta en tiempo polinomial, y se exige demostrarlo: el algoritmo voraz que, en cada paso, entrega la siguiente unidad de presupuesto al nodo cuya ganancia marginal es mayor en ese momento, es óptimo. La demostración de optimalidad se hace por un argumento de intercambio: si una solución no reparte el presupuesto por orden de ganancia marginal decreciente, siempre es posible reordenar dos unidades de presupuesto sin empeorar la utilidad total, lo que contradice que esa solución no ordenada fuera óptima.

**Función de eficiencia:** usando una cola de prioridad (montículo) para encontrar siempre la mayor ganancia marginal disponible, cada una de las B unidades de presupuesto se asigna en O(log N), dando T(N, B) = O(B log N) — polinomial, y por lo tanto la parte más "fácil" del proyecto en términos de dificultad computacional. Se exige, aun así, la demostración completa: esta parte no se debe resolver por fuerza bruta ni por metaheurísticas.

## 4.3 Parte 2 — Selección de nodos participantes

**Tamaño de la entrada:** N, el número total de nodos candidatos, y k, el número de nodos que se pueden seleccionar en la ronda (k < N).

**Entrada:** una función de utilidad conjunta que, dado un subconjunto de nodos, reporta la utilidad total obtenida; esta función es submodular (agregar un nodo nuevo a un subconjunto grande aporta menos utilidad marginal que agregarlo a uno pequeño).

**Objetivo:** elegir el subconjunto de tamaño k que maximiza la utilidad conjunta.

Se pide demostrar que este problema es NP-difícil mediante una reducción desde Cobertura Máxima (Maximum Coverage), ya NP-difícil por reducción conocida desde Cobertura de Conjuntos: dado un universo de elementos y una colección de subconjuntos, Cobertura Máxima pregunta cuáles k subconjuntos cubren más elementos del universo — que es exactamente un caso particular de este problema, tomando como utilidad conjunta el tamaño de la unión de los subconjuntos elegidos.

**El algoritmo aproximado y su cota demostrable:** el algoritmo voraz que, en cada uno de los k pasos, agrega el nodo de mayor ganancia marginal, garantiza una utilidad de al menos (1 − 1/e) ≈ 63% de la utilidad óptima — un resultado clásico de optimización submodular (Nemhauser, Wolsey y Fisher, 1978) que el equipo debe citar correctamente y aplicar, verificando en sus propios datos que la utilidad obtenida respeta esa cota.

**Función de eficiencia del algoritmo voraz:** en cada uno de los k pasos hay que evaluar la ganancia marginal de cada uno de los nodos restantes, un costo de O(N) por paso, dando T(N, k) = O(N·k) en total.

## 4.4 Variantes (todas obligatorias)

- Nodos con costos de participación distintos además de su utilidad (versión con presupuesto de participación, no solo cupo k fijo): la cota (1 − 1/e) cambia de forma y debe redemostrarse o citarse en su versión correcta para cobertura con presupuesto (budgeted maximum coverage).
- Repetir la decisión de selección en T rondas con nodos que pueden fallar entre rondas.
- Los nodos ahora se relacionan entre sí, o sea, poner una cantidad b del presupuesto va a afectar directamente a los nodos vecinos, haciendo que sus funciones de utilidad se muevan un poco.

# 5. Entregables

- Informe técnico, con una sección de análisis de complejidad: definición de n, deducción de T(n) para el algoritmo exacto, prueba de NP-dureza por reducción, algoritmo aproximado con su cota (demostrada o correctamente citada y aplicada), y validación experimental que compare el crecimiento medido contra el crecimiento teórico (más adelante se darán los detalles de este informe).
- Implementación: código reproducible con generación de instancias sintéticas de tamaño creciente (al menos 5 tamaños distintos de n, en un rango suficiente para observar el crecimiento asintótico), medición de tiempos, y gráfica de tiempo contra n.
- Sustentación grupal de 15 a 20 minutos, donde el equipo debe poder explicar y defender, sin ayuda de notas, la reducción de NP-dureza de su problema y la deducción de la función de eficiencia de su algoritmo exacto.
- Sustentación individual donde cada estudiante debe desarrollar lo que se le indique.

# 6. Cronograma (11 semanas)

| **Semanas** | **Hito** |
|---|---|
| 1 - 2 | Formación de equipos y elección de la variante; entrega escrita de la formalización del problema (n, entrada, salida, objetivo) — sin código todavía |
| 3 - 4 | Prueba formal de NP-dureza por reducción (entrega parcial, revisada por el docente antes de continuar) |
| 5 - 6 | Algoritmo exacto (fuerza bruta o programación dinámica) + deducción formal de su T(n) |
| 7 - 8 | Algoritmo aproximado o heurístico + su propia función de eficiencia + cota de aproximación cuando exista |
| 9 - 10 | Experimentación: generación de instancias, medición de tiempos, comparación contra la función teórica |
| 11 | Entrega final y sustentaciones |

# 7. Criterios de evaluación

| **Componente** | **Peso** |
|---|---|
| Formalización del problema (n, entrada, salida, objetivo) | 10% |
| Prueba de NP-dureza por reducción, correcta y completa | 10% |
| Deducción formal de función de eficiencia del algoritmo exacto | 10% |
| Algoritmo aproximado/heurístico: diseño, función de eficiencia y cota de aproximación | 15% |
| Validación experimental (medición y comparación contra la teoría) | 10% |
| Sustentación | 45% |

# 8. Notas finales

El proyecto no requiere datos reales de ningún proyecto externo: todas las instancias son sintéticas, generadas por los propios estudiantes según los parámetros descritos en cada sección. El criterio de éxito de este proyecto no es "que el código corra", sino que cada equipo pueda, al final del semestre, sostener con rigor por qué su solución es eficiente — y qué tan eficiente es, exactamente, en el lenguaje formal del curso.
