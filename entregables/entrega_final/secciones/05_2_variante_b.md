## 5.2 Variante (b): T rondas con nodos que pueden fallar

La red entrena T rondas. Antes de cada ronda algunos nodos fallan y no pueden participar. En cada ronda se decide, como en la solución base, quién participa (Parte 2) y cómo se reparte el presupuesto de la ronda (Parte 1), y lo que cada nodo recibe se descuenta de su presupuesto total para todo el proyecto.

| Componente | Definición |
|---|---|
| Entrada | N, k ∈ ℕ con 1 ≤ k < N; B ∈ ℕ, el presupuesto de cada ronda; T ≥ 1, el número de rondas; V = {1, …, N}; el oráculo f de la Parte 2; para cada nodo una utilidad uᵢ creciente y cóncava y un presupuesto total Pᵢ ∈ ℕ para todo el proyecto; la probabilidad de fallo q ∈ [0, 1], el modo de fallo (transitorio o permanente) y una semilla. |
| Variables | Para cada ronda r = 1, …, T: Sᵣ ⊆ V, los nodos que participan, y xᵣ = (x_{r,i}), las unidades que recibe cada uno. |
| Restricciones | Sea Fᵣ el conjunto de nodos que fallan antes de la ronda r y R_{r,i} lo que le queda al nodo i al empezar la ronda r (R_{1,i} = Pᵢ; R_{r+1,i} = R_{r,i} − x_{r,i}). Los candidatos son Cᵣ = {i ∉ Fuera_r : R_{r,i} > 0}, con Fuera_r = Fᵣ (transitorio) o F₁ ∪ … ∪ Fᵣ (permanente). Entonces Sᵣ ⊆ Cᵣ; \|Sᵣ\| ≤ kᵣ = mín(k, \|Cᵣ\|); x_{r,i} ∈ ℤ, 0 ≤ x_{r,i} ≤ R_{r,i}, x_{r,i} = 0 si i ∉ Sᵣ; y Σᵢ x_{r,i} = mín(B, Σ_{i∈Sᵣ} R_{r,i}). |
| Objetivo | En cada ronda, en el orden de la solución base: maximizar f(Sᵣ) sobre los candidatos y, con Sᵣ fijo, maximizar Uᵣ = Σ_{i∈Sᵣ} uᵢ(x_{r,i}). |
| Salida | Por ronda: los fallados, los candidatos, Sᵣ con f(Sᵣ), xᵣ con Uᵣ y el presupuesto restante de cada nodo; al final, Σᵣ f(Sᵣ) y Σᵣ Uᵣ. |
| Tamaño de la entrada | (N, k, B, T), más A (o M) por la descripción de f. T es lo nuevo: el trabajo crece linealmente con el número de rondas (§8.3). |

**Supuestos ❓** (el enunciado da `numero_rondas` y un presupuesto total por nodo, pero no dice cómo fallan los nodos ni cómo se gasta ese presupuesto entre rondas):

1. **Fallos.** Antes de cada ronda, cada nodo falla de forma independiente con probabilidad q (0,2 por omisión), sorteada con un generador con semilla fija (0 por omisión). En modo **transitorio** el nodo falla solo esa ronda; en modo **permanente** no vuelve. Se sortean los N nodos en cada ronda en los dos modos, para que con la misma semilla los fallados de cada ronda coincidan y las dos corridas sean comparables.
2. **Presupuesto restante.** Pᵢ es `presupuesto_total_nodo` (18 en el caso oficial); si un nodo no trae tope, Pᵢ = B. Lo que recibe en cada ronda se descuenta, y el restante es el tope de la ronda siguiente: nunca queda negativo.
3. **Candidatos.** Participan los que no fallaron y tienen restante > 0. Si son k o menos, participan todos (kᵣ = \|Cᵣ\|); si no queda ninguno, la ronda queda vacía (Sᵣ = ∅, f = 0, Uᵣ = 0) y no es una falla.
4. **Cada ronda se optimiza sola**, con el mismo k y el mismo B, sin mirar las siguientes. f mide la influencia sobre todo el grafo; solo cambia a quién se puede elegir. Planear las T rondas juntas es otro problema (planeación con incertidumbre) y queda fuera del alcance.
5. T es `numero_rondas` del archivo (3 en el caso oficial); sin ese dato, T = 1.

**Observación.** Con q = 0 y T = 1 la variante reproduce la solución base: mismo S, mismo f(S), mismo reparto y misma utilidad en el caso de la docente y en los casos propios con B > 0. Con B = 0 y sin topes no la reproduce: por el supuesto 2 nadie tiene presupuesto, así que no hay candidatos y la ronda queda vacía, mientras que la base elige S y reparte 0.

**Relación con el escenario.** Es el escenario completo del enunciado: T rondas de entrenamiento, nodos que se caen y un presupuesto de ruido tolerable por nodo que se va gastando.
