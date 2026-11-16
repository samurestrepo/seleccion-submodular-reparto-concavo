# Ficha: `red/variante_costos.py`

## Para qué existe
Resuelve la **variante (a)** de la Parte 2: cada nodo v tiene un costo de participación c(v) > 0 y hay un presupuesto de participación L; se busca S que maximice f(S) con Σ_{v∈S} c(v) ≤ L (restricción de mochila). **Supuesto ❓ (decisión 35):** esa restricción **reemplaza** a |S| ≤ k; no se usan las dos a la vez. La docente no ha respondido. f es la misma de la solución base (cobertura o influencia), a través del mismo oráculo (`estado_inicial`, `ganancia`, `agregar`, `valor`), así que sigue siendo monótona, submodular y con f(∅) = 0.

Trae cuatro algoritmos: la fuerza bruta (referencia, OPT), el voraz por cociente (sin garantía), el voraz modificado (el que corre en la ronda con `--variante a`, garantía 0,405) y la enumeración parcial (garantía 1 − 1/e, O(N⁵)).

## Funciones públicas
Todas reciben el oráculo, V (ids en orden creciente), `costos` (id → c(v) > 0) y L. Todas devuelven o incluyen el número de **evaluaciones de f** (llamadas a `ganancia` más llamadas a `valor`), que es la operación básica de la Parte 2. c_mín es el menor costo.

| Función | Devuelve | T en evaluaciones de f | Peor caso | Mejor caso | Espacio |
|---|---|---|---|---|---|
| `seleccionar_exacto_costos(oraculo, V, costos, L)` | `(S*, OPT, evaluaciones)` | exactamente F, el número de subconjuntos factibles (incluido ∅), F ≤ 2^N; visita ≤ F·(N + 1) subconjuntos | L ≥ Σ c: Θ(2^N) | L < c_mín: 1 evaluación, Θ(N) tiempo | O(N) (pila de la búsqueda y S) + estado del oráculo |
| `voraz_por_cociente(oraculo, V, costos, L, traza=None, inicial=())` | `ResultadoCostos` (S, valor, costo, evaluaciones, mejor_solo) | 1 + Σ_j (candidatos del paso j) ≤ 1 + \|S\|·N − \|S\|(\|S\| − 1)/2, con \|S\| ≤ mín(N, ⌊L/c_mín⌋): O(N · mín(N, L/c_mín)) | L ≥ Σ c: exactamente 1 + N(N + 1)/2, Θ(N²) | L < c_mín: 1 evaluación, Θ(N) tiempo | O(N) + estado del oráculo |
| `voraz_modificado(oraculo, V, costos, L, traza=None)` | `ResultadoCostos` con `origen` ("cociente" o "mejor_nodo_solo") | **las mismas** que el voraz por cociente: cero extra | igual | igual | igual |
| `enumeracion_parcial(oraculo, V, costos, L)` | `ResultadoCostos` con `origen` ("enumerado" o "completado") | 1 + F₁ + F₂ + Σ_{T factible, \|T\|=3} (1 + evaluaciones del cociente desde T), con F_j ≤ C(N, j): O(N⁴ · mín(N, L/c_mín)) ⊆ **O(N⁵)** | L ≥ Σ c: 1 + N + C(N, 2) + C(N, 3)·(1 + (N − 3)(N − 2)/2), Θ(N⁵) | L < c_mín: 1 evaluación, Θ(N) tiempo | O(N) + estado del oráculo |

**Con qué crece cada uno.** La fuerza bruta con N (exponencial) y con L: cuanto más cabe, más factibles. El cociente y el modificado con N (lineal por paso) y con el número de pasos, acotado por mín(N, L/c_mín): con L pequeño frente a los costos, pocos pasos. La enumeración con N⁴ por los C(N, 3) puntos de partida, y con mín(N, L/c_mín) por cada completación.

**En operaciones, con influencia:** cada `ganancia(v)` cuesta O(1 + grado(v)) y cada `valor(S)` cuesta O(N + Σ_{v∈S} (1 + grado(v))). Un paso del cociente que evalúa a todos cuesta O(N + 2A) = O(N + A); el cociente completo, **O(|S| · (N + A))**; la fuerza bruta, O(F · (N + A)); la enumeración, O(N³ · |S|·(N + A)). Con cobertura se reemplaza (1 + grado(v)) por |C_v| y (N + A) por (N + M).

**Conteos comprobados en `pruebas/test_variante_costos.py` con los contadores** (no supuestos): con todo cabiendo, 2^N, 1 + N(N + 1)/2 y la fórmula de la enumeración para N = 4, 6, 9; con costos 1 y L = k, el cociente hace 1 + k·N − k(k − 1)/2 (el conteo del voraz base más f(∅)) y la fuerza bruta Σ_{j ≤ k} C(N, j); en el caso de la docente, 4502, 74 y 13117.

## Cómo funciona
**Fuerza bruta.** Búsqueda en profundidad que visita los subconjuntos en orden lexicográfico de ids (∅, {v₁}, {v₁, v₂}, …): `explorar(S, costo_S, desde)` evalúa f(S) y luego intenta extender S con cada id posterior que quepa. **Poda:** si v no cabe en S, tampoco cabe en ningún superconjunto, porque los costos son positivos; por eso solo se evalúan los factibles. Empates: `>` estricto, gana el primero en ese orden (decisión 36). Se niega si 2^N > 200000 (N ≥ 18), el mismo `LIMITE_COMBINACIONES` de `exacto.py` aplicado a 2^N (decisión 37).

**Voraz por cociente.** Arranca con S = `inicial` (vacío en el uso normal), el estado del oráculo con esos nodos y f(S) (una evaluación con `valor`: f(∅) = 0). En cada paso recorre V en orden creciente, **salta sin evaluar** a los que ya están en S y a los que no caben (c(v) > L − c(S)), pide Δ(v | S) a los demás y se queda con el de mayor Δ(v | S)/c(v) (`>` estricto: desempata el menor índice). Lo agrega, actualiza el estado, f(S) y c(S). Termina cuando ningún candidato cabe. **Sin garantía constante:** la prueba `test_contraejemplo_del_cociente_tan_malo_como_se_quiera` tiene un nodo barato (c = 1, cubre 2: cociente 2) y uno caro que ocupa todo L = M (cubre 2M − 1: cociente (2M − 1)/M < 2). El cociente toma al barato y el caro ya no cabe: 2 contra 2M − 1, razón 2/(2M − 1) → 0.

**Voraz modificado.** El mejor entre el S del cociente y el mejor nodo que cabe solo (Khuller, Moss y Naor, 1999). El mejor nodo solo **no cuesta evaluaciones**: f({v}) = Δ(v | ∅), que ya se evaluó en el paso 1 del cociente (`mejor_solo`). Si empatan, se queda con el del cociente. Garantía: (1 − 1/e)/2 ≈ 0,316 (Khuller, Moss y Naor, 1999). Tang et al. (2021) la mejoran a **0,405** para f monótona y submodular con restricción de mochila, y cierran el hueco que tenía la prueba de la cota 1 − 1/√e ≈ 0,393 de Khuller et al. **Se aplica la de Tang et al.**, porque la f de influencia es submodular general, no solo cobertura.

**Enumeración parcial.** Se evalúa f en todos los subconjuntos factibles de tamaño 1 y 2 (más ∅, 1 evaluación) y, desde cada subconjunto factible T de tamaño 3, se completa con el voraz por cociente (`inicial=T`). Devuelve el mejor; en empates el primero encontrado. Solo se combinan los nodos que caben solos (`caben`), para que con L < c_mín el costo sea Θ(N). Garantía: **1 − 1/e**, con O(n⁵) evaluaciones de f (Sviridenko, 2004). Khuller, Moss y Naor la prueban para cobertura.

## Por qué así
- **Mismo oráculo y mismos contadores que la solución base:** la variante no toca `seleccion.py` ni los oráculos; OPT y aproximados miden la misma f.
- **El límite 2^N ≤ 200000** reutiliza `LIMITE_COMBINACIONES` y `DemasiadasCombinaciones` de `exacto.py` (decisión 37): N ≤ 17.
- **La poda de la fuerza bruta** es correcta solo porque c(v) > 0; por eso un costo ≤ 0 es error de entrada cuando se pide la variante (`verificar_variante_a`).
- **Cociente con `>` estricto y V en orden creciente:** mantiene los empates por el menor índice (decisión 6).
- **`ResultadoCostos` en lugar de una tupla:** cuatro algoritmos devuelven lo mismo (S, valor, costo, evaluaciones) y así la ronda y el script los tratan igual.
- **En la ronda corre el voraz modificado** (decisión 35): tiene garantía constante y cuesta lo mismo que el cociente; la enumeración es O(N⁵) y es de referencia, como la fuerza bruta.

## Cómo modificarlo
- **Usar k y L a la vez:** en `voraz_por_cociente`, parar también cuando |S| = k, y en la fuerza bruta no extender S si ya tiene k; cambia la decisión 35 y las verificaciones de `ronda.py`.
- **Poner la enumeración en la ronda:** en `ronda._seleccionar` llamar `enumeracion_parcial` en lugar de `voraz_modificado`; `verificar_conteo_evaluaciones_costos` necesita otra cota.
- **Desempatar por el mayor índice:** `>` por `>=` en las comparaciones del cociente y de `mejor_solo`.
- Correr `pruebas/test_variante_costos.py`.

## Pruebas
`pruebas/test_variante_costos.py` (57 pruebas): con costos 1 y L = k la fuerza bruta da el OPT de `exacto.py`, el cociente y el modificado dan el S del voraz base y la enumeración queda entre el voraz y el OPT (casos propios con N ≤ 17 y la docente); conteos exactos del peor caso y coincidencia con los contadores del oráculo; mejor caso con nada cabiendo; poda, empate y límite 2^18 de la fuerza bruta; contraejemplo del cociente con M = 10, 100 y 1000 y el modificado que lo corrige por `mejor_nodo_solo` sin evaluaciones extra; desempate y salto de los que no caben; caso de la docente (S, costo 21, 74 evaluaciones, razones); batería aleatoria de `scripts/tabla_cota_variante_a.py` (36 filas, cotas 0,405 y 1 − 1/e, reproducible, CSV del repo coincide); generador con `presupuesto_costos`; campos opcionales del formato propio; ronda con `variante="a"` (verificación Σ c(S) ≤ L, rechazos por costo ≤ 0 o L ausente, base intacta) y `ejecutar.py --variante a`.

## Preguntas probables en la sustentación
- **¿Por qué el cociente no basta?** Un nodo barato con cociente apenas mayor bloquea a uno caro que vale mucho más: razón tan mala como se quiera. Comparar con el mejor nodo solo da la cota 0,405 (Tang et al., 2021).
- **¿Por qué la enumeración llega a 1 − 1/e?** Fijar los 3 mejores nodos del óptimo elimina el caso malo del cociente (Sviridenko, 2004); cuesta O(N⁵).
- **¿Cuántas evaluaciones hace la ronda con la variante?** Las del cociente: 1 + Σ_j (candidatos que caben en el paso j) ≤ 1 + |S|·N − |S|(|S| − 1)/2; en la docente, 74 con |S| = 6 (cota 76).
- **¿Y k?** Supuesto ❓: L reemplaza a k. En la docente el modificado elige 6 nodos con costo 21 ≤ 24, uno más que k = 5.

_Última actualización: 2026-11-16 · archivo nuevo (P-4 fase 1)_
