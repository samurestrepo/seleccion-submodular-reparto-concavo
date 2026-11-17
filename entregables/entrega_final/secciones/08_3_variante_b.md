## 8.3 Algoritmo de la variante (b): T rondas con nodos que fallan

**Idea.** No hace falta un algoritmo nuevo. En cada ronda se sortean los fallos, se arman los candidatos y se corren, sobre ellos, los dos voraces de la solución base: SELECCIONAR-NODOS (§8.1) con V = candidatos y kᵣ = mín(k, |Cᵣ|), y REPARTIR-PRESUPUESTO (§7.1) con el presupuesto restante de cada nodo como tope. Después se descuenta lo gastado. Cada ronda se optimiza sola (Supuesto ❓ 4 de §5.2).

```
RONDAS-CON-FALLOS(V, f, u, k, B, P, T, q, modo, semilla)
1  para cada i ∈ V hacer R[i] ← Pᵢ                         # sin tope: Pᵢ = B
2  caídos ← ∅ ; azar ← GENERADOR(semilla)
3  para r ← 1 hasta T hacer
4      Fᵣ ← {i ∈ V : azar.aleatorio() < q}                  # se sortean los N nodos, en orden creciente
5      si modo = permanente entonces caídos ← caídos ∪ Fᵣ ; fuera ← caídos
6      si no fuera ← Fᵣ
7      Cᵣ ← {i ∈ V \ fuera : R[i] > 0}                      # candidatos, en orden creciente
8      kᵣ ← mín(k, |Cᵣ|)
9      si kᵣ = 0 entonces Sᵣ ← ∅ ; xᵣ ← 0 ; pasar a la ronda siguiente
10     Sᵣ ← SELECCIONAR-NODOS(Cᵣ, kᵣ, f)                    # §8.1
11     xᵣ ← REPARTIR-PRESUPUESTO(Sᵣ, B, u, R)               # §7.1, tope de i = R[i]
12     para cada i ∈ Sᵣ hacer R[i] ← R[i] − xᵣ[i]
13 devolver, por ronda, Fᵣ, Cᵣ, Sᵣ, f(Sᵣ), xᵣ, Uᵣ y R
```

**Por qué el restante nunca es negativo.** En la línea 11 el tope de cada nodo es R[i], y el reparto respeta los topes (§7.1), así que xᵣ[i] ≤ R[i] y la línea 12 deja R[i] ≥ 0.

### 8.3.1 Función de eficiencia

Sean nᵣ = |Cᵣ| ≤ N, kᵣ ≤ k y A el número de aristas del grafo (M con la cobertura). Por ronda:

- **Paso 1: fallos y candidatos (líneas 4 a 8).** Un sorteo por nodo y un recorrido de los N nodos: Θ(N).
- **Paso 2: selección (línea 10).** Es §8.1 con nᵣ candidatos y kᵣ pasos: exactamente kᵣ·nᵣ − kᵣ(kᵣ − 1)/2 evaluaciones de ganancia marginal (más f(∅)); en tiempo, O(kᵣ·(nᵣ + A)) ⊆ **O(k·(N + A))**.
- **Paso 3: reparto (línea 11).** Es §7.1.2 con |Sᵣ| ≤ k nodos: Θ(|Sᵣ| + B(1 + lg |Sᵣ|)) sin que nadie llegue a su tope; con topes, peor caso **O(k + B lg k)**.
- **Paso 4: descuento (línea 12).** O(k).
- **Suma de una ronda:** Θ(N) + O(k·(N + A)) + O(k + B lg k) = O(k·(N + A) + B lg k), porque k·(N + A) ≥ N.
- **Suma de las T rondas:**

  **T(N, k, B, A, T) = O(T·(k·(N + A) + B lg k))**

  Es T veces el costo de una ronda de la solución base, más Θ(N) por ronda del sorteo: la variante no agrega ningún factor nuevo.

**Peor caso:** nadie falla y nadie agota su presupuesto: kᵣ = k y nᵣ = N en todas las rondas, la fórmula anterior. **Mejor caso:** fallan todos (q = 1) o nadie tiene presupuesto: cada ronda solo sortea y arma una lista vacía, **Θ(T·N)**. **Caso promedio:** con q fijo, en modo transitorio se espera nᵣ ≈ (1 − q)·N mientras haya presupuesto, y el costo sigue siendo Θ(T·k·N) evaluaciones; en modo permanente los candidatos solo disminuyen, así que el costo por ronda no aumenta.

**Referencia exacta (opcional).** Para medir la calidad, en cada ronda se calcula además OPTᵣ con la fuerza bruta de §7.3 sobre los candidatos: C(nᵣ, kᵣ) evaluaciones, O(T·C(N, k)·(N + A)) en total. No entra en el algoritmo; se niega sin evaluar si C(nᵣ, kᵣ) > 200000.

**Espacio.** R y los caídos, Θ(N); cada ronda usa el espacio de los voraces base, O(N) más el estado del oráculo. Guardar el resultado de cada ronda (incluido el restante de los N nodos) suma O(T·N).

**Experimento.** Con N = 100, k = 5, B = 100, q = 0,2 y T = 8 a 128 rondas, el tiempo creció con pendiente 1,059 contra T en escala log-log (esperada 1) y el cociente tiempo/T(n) varió 1,16 veces entre el menor y el mayor (`resultados/experimentos/l_rondas_varia_T.csv`).

### 8.3.2 Garantía: ronda por ronda

Restringida a los candidatos de una ronda, f sigue siendo monótona, submodular y con f(∅) = 0: esas propiedades valen para todo subconjunto de V. Entonces la cota de §8.1 se aplica a cada ronda con V = Cᵣ y kᵣ nodos:

f(Sᵣ) ≥ ρ(kᵣ)·OPTᵣ ≥ (1 − 1/e)·OPTᵣ, con ρ la función de §2.1 evaluada en kᵣ,

donde OPTᵣ es el óptimo sobre los candidatos de esa ronda. **No hay una cota sobre las T rondas juntas**, y no se afirma ninguna: lo que se gasta en una ronda cambia el restante y, con él, los candidatos de las siguientes, así que optimizar cada ronda por separado no garantiza nada sobre la suma. El reparto de cada ronda sí es óptimo para su Sᵣ y sus topes (§7.1.1).

### 8.3.3 Comprobación: el caso de la docente y una batería

**Docente** (N = 15, k = 5, B = 30, T = 3, presupuesto total 18 por nodo, q = 0,2, semilla 0). La tabla por ronda, con los fallados, los equipos, los repartos y el restante, está en §10.1.3; aquí solo se comprueba lo que dice el análisis.
- Las evaluaciones del voraz son exactamente kᵣ·nᵣ − kᵣ(kᵣ − 1)/2: 5·15 − 10 = 65, 5·14 − 10 = 60 y 5·13 − 10 = 55. El exacto evalúa C(15, 5) = 3003, C(14, 5) = 2002 y C(13, 5) = 1287 conjuntos.
- Las razones f(Sᵣ)/OPTᵣ son 0,997754, 1 y 1, muy por encima de ρ(5) ≈ 0,6723.
- El restante actúa como tope y nunca queda negativo: las tres rondas gastan B = 30 y el restante total baja de 270 a 240, 210 y 180; tras la ronda 3, N09, N14 y N15 quedan en 0.

Fuente: `resultados/variantes/b_profesora_transitorio/` y `b_profesora_permanente/` (`resumen.csv` y `salida.json`).

Con la semilla 0 los dos modos coinciden porque los fallados de cada ronda quedan contenidos en los de la siguiente (∅, {N11}, {N06, N11}): el modo permanente no excluye a nadie más que el transitorio. Para ver los dos modos separados se corrió también la **semilla 3** (fallados {N06, N07}, {N01, N07, N11} y {N08, N09}); su tabla por ronda, en los dos modos, está en §10.1.3. Lo que comprueba del análisis:
- Las evaluaciones del voraz siguen siendo kᵣ·nᵣ − kᵣ(kᵣ − 1)/2: 55, 50 y 55 en transitorio (nᵣ = 13, 12, 13) y 55, 45 y 35 en permanente (nᵣ = 13, 11, 9). En el modo permanente los candidatos solo disminuyen, como dice el caso promedio de §8.3.1.
- Las razones son 0,997754, 1 y 0,998279 en transitorio y 0,997754, 1 y 1 en permanente, todas por encima de ρ(5) ≈ 0,6723.
- El restante total baja de 270 a 240, 210 y 180 en los dos modos y nunca es negativo; tras la ronda 3, N14 queda en 0.

Fuente: `resultados/variantes/b_profesora_transitorio_s3/` y `b_profesora_permanente_s3/` (`resumen.csv` y `salida.json`).

**Batería.** 27 instancias aleatorias de influencia (N = 8, 10, 12; k = 3; B = 20), en los dos modos, con 3 rondas y q = 0,3: 162 rondas, todas cumplen su cota. La razón mínima es 0,938153, con cota 0,7037. Hay 30 rondas con razón < 1; las otras 132 alcanzan el OPT de su ronda (detalle, y por qué una comparación estricta cuenta 64, en §10.2.3; `pruebas/test_variante_rondas.py`, sin CSV).
