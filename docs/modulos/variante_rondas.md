# Ficha: `red/variante_rondas.py`

## Para qué existe
Resuelve la **variante (b)**: la red entrena T rondas (`numero_rondas` en el formato de la profesora, 3 en el caso oficial; el campo opcional `rondas` en el propio; 1 si no viene) y antes de cada ronda algunos nodos fallan. Por ronda corre los mismos dos voraces de la solución base (`seleccionar_nodos` y `repartir_presupuesto`) sobre los nodos que pueden participar, descuenta lo gastado del presupuesto de cada nodo y calcula como referencia el óptimo exacto de esa ronda (`exacto.py`). Solo corre con `ejecutar.py --variante b`; sin la opción nada cambia. **Todo lo que sigue depende de supuestos no confirmados por la docente (Supuesto ❓, decisión 39).**

**Supuestos ❓ (decisiones 39 y 40):**
1. Cada nodo falla antes de cada ronda, de forma independiente, con probabilidad q (`--prob-fallo`, 0,2 por omisión), con `random.Random(semilla)` (`--semilla-fallos`, 0 por omisión). Modo **transitorio**: falla solo esa ronda. Modo **permanente**: no vuelve.
2. El tope de cada nodo es su **presupuesto restante**: empieza en `presupuesto_total_nodo` (o `tope` en el propio; **sin tope, B**) y se le descuenta lo que recibe en cada ronda. Nunca queda negativo, porque el reparto respeta el tope. Consecuencia de «sin tope, B»: un nodo sin tope recibe a lo sumo B en total en las T rondas, y con B = 0 nadie tiene presupuesto (ver Pruebas).
3. Candidatos de la ronda r: los nodos que no fallaron y tienen restante > 0. El voraz recibe esa lista como V y k_r = mín(k, |candidatos|): **si son k o menos, participan todos**; si no hay ninguno, la ronda queda vacía (S_r = ∅, f = 0, U_r = 0) y no es una falla.
4. Cada ronda se optimiza **sola**, con el mismo k y el mismo B, sin mirar las siguientes. El oráculo es el de la instancia completa (f mide la influencia sobre todo el grafo); solo cambia quién se puede elegir. Planear las T rondas juntas es otro problema (planeación con incertidumbre) y queda como limitación.
5. En cada ronda se sortean los N nodos, también los ya caídos en modo permanente, para que con la misma semilla los fallados de cada ronda coincidan en los dos modos: los caídos del permanente en la ronda r son la unión de los fallados de las rondas 1 a r.

## Funciones públicas
| Función | Recibe | Devuelve | Complejidad (tiempo · espacio) |
|---|---|---|---|
| `ejecutar_rondas(instancia, modo="transitorio", prob_fallo=0.2, semilla=0, rondas=None, repeticiones=1, exacto=True)` | la instancia, el modo, q, la semilla, T (si es None, el de la instancia o 1), R y si se calcula OPT_r | diccionario: `caso`, `entrada` (N, k, B, T, modo, q, semilla), `variante` (supuestos), `verificaciones` (`entrada`, `globales`), `rondas` (una entrada por ronda), `resumen` (Σ f(S_r), Σ U_r, rondas sin participantes), `traza` (`rondas`: fallados, candidatos, pasos y unidades por ronda), `todas_cumplen`. Si la entrada no cumple (o T < 1), el rechazo de `ronda._resultado_rechazado` | ver T(n) abajo · O(R·(N + A)) durante la medición más O(N) del restante y O(T·(k·N + B)) del resultado con sus trazas |
| `sortear_fallos(ids, prob_fallo, azar)` | ids en orden creciente, q, un `random.Random` sembrado | lista de fallados en orden creciente | Θ(N) · O(N) |
| `candidatos_de_la_ronda(ids, fuera, restante)` | ids, conjunto de los que están fuera, id → restante | lista de candidatos en orden creciente | Θ(N) · O(N) |
| `a_texto_rondas(resultado)` | el resultado de `ejecutar_rondas` | el reporte `traza.txt` | O(tamaño del resultado) |

Cada entrada de `rondas`: `ronda`, `fallados`, `caidos` (acumulados en permanente; = fallados en transitorio), `candidatos`, `k_ronda`, `seleccion` (S_r, valor = f(S_r), llamadas), `exacto` (`disponible`, S*, OPT_r, evaluaciones; o el motivo), `razon` = f(S_r)/OPT_r (None si OPT_r = 0 o no está), `cota` = 1 − (1 − 1/k_r)^k_r, `reparto` (x, utilidad = U_r, extracciones, inserciones), `presupuesto_restante` tras la ronda (todos los nodos), `tiempos_segundos` (mediana, mínimo y máximo de R), `verificaciones` y `todas_cumplen`.

## Cómo funciona
`ejecutar_rondas` valida los parámetros (modo, q ∈ [0, 1], R ≥ 1), fija T, corre `verificar_entrada` y `verificar_variante_b` (T ≥ 1) y, si algo falla, devuelve el rechazo sin correr nada (como `ronda.py`). Luego inicializa `restante` (Supuesto 2), `azar = random.Random(semilla)` y `caidos = ∅`, y por cada ronda r = 1..T:
1. `sortear_fallos`: un `azar.random() < q` por nodo (con q = 0 nadie falla porque `random()` está en [0, 1); con q = 1 fallan todos). En permanente, `caidos ∪= fallados`.
2. `candidatos_de_la_ronda`: fuera de `caidos` (permanente) o de `fallados` (transitorio), y con restante > 0. `topes_r` = restante de cada candidato.
3. `_ejecutar_una_ronda`: igual que `ronda.ejecutar_ronda` pero sobre los candidatos: R ejecuciones medidas sin traza (`_correr_ronda`, un oráculo nuevo por ejecución, reloj alrededor de cada parte; decisiones 11 y 29), una con traza, el exacto (`_exacto_de_la_ronda`: `seleccionar_exacto` sobre los candidatos con k_r; con k_r = 0, OPT = 0 sin evaluar; si C(n_r, k_r) > 200000 queda `disponible = False` con el motivo y no es falla) y las verificaciones. Con k_r = 0 no corre ningún algoritmo.
4. Se descuenta x_v del restante de cada v ∈ S_r; como x_v ≤ tope = restante, nunca queda negativo. Se guarda el restante de todos los nodos.
Al final, `_verificaciones_globales`: restante ≥ 0 en todos los nodos y, en permanente, cada lista de candidatos ⊆ la anterior.

**Verificaciones por ronda:** `verificar_seleccion_ronda` (S_r ⊆ candidatos, sin repetidos, |S_r| ≤ k_r, f(S_r) recalculada), `verificar_conteo_llamadas(|candidatos|, k_r, llamadas)` (k_r·n_r − k_r(k_r − 1)/2, la fórmula de la base con N = n_r), `verificar_cota_ronda` (f(S_r) ≥ (1 − (1 − 1/k_r)^k_r)·OPT_r, solo si OPT_r está), `verificar_reparto` con `topes_r`, y las dos de ejecución (R repeticiones iguales; traza = medida).

**Cota.** Vale **ronda por ronda**: f(S_r) ≥ (1 − (1 − 1/k_r)^k_r)·OPT_r, con OPT_r el óptimo sobre los candidatos de esa ronda (la f sigue siendo monótona y submodular restringida a cualquier subconjunto de V). **No** es una cota sobre las T rondas juntas: la decisión de una ronda cambia el restante y, con él, los candidatos de las siguientes.

## T(n) y espacio
Sea n_r = |candidatos| ≤ N, k_r ≤ k, A las aristas (M = Σ |C_v| con cobertura), R las repeticiones. Por ronda:
- sorteo y candidatos: Θ(N) cada uno;
- selección: k_r pasos que recorren los candidatos, cada `ganancia` O(1 + grado(v)): O(k_r·(n_r + A)) ⊆ **O(k·(N + A))**, con exactamente k_r·n_r − k_r(k_r − 1)/2 llamadas a Δ;
- reparto: montículo de |S_r| ≤ k nodos: Θ(|S_r| + B(1 + lg |S_r|)) ⊆ **O(k + B lg k)**;
- descuento O(k) y copia del restante Θ(N); verificaciones O(N + A + k);
- exacto (opcional): C(n_r, k_r) evaluaciones de `valor`, cada una O(N + A): O(C(N, k)·(N + A)).

Total: **T(N, k, B, A, T, R) = O(T·[(R + 1)·(k·(N + A) + B lg k) + N])** sin el exacto, y **+ O(T·C(N, k)·(N + A))** con él. Con R = 1 y sin exacto: O(T·(k·(N + A) + B lg k)); con cobertura, A se reemplaza por M. Es T veces el costo de una ronda de la base (`ronda.md`) más Θ(N) por el sorteo: la variante no agrega ningún factor nuevo. **Espacio:** O(N + A) por oráculo (R vivos durante la medición, como en `ronda.py`), O(N) del restante y los caídos, y O(T·(k·N + B)) del resultado (aportes de la traza k·n_r por ronda, B unidades del reparto, N restantes por ronda).

## Por qué así
- **Reutiliza los voraces y el exacto tal cual** (`seleccionar_nodos` con V = candidatos, `repartir_presupuesto` con topes = restante, `seleccionar_exacto` sobre los candidatos): la variante no toca ningún algoritmo ni oráculo, y sus conteos y verificaciones son los de la base con N = n_r.
- **Sorteo de los N nodos en los dos modos** (Supuesto 5): así una misma semilla da los mismos fallados por ronda en transitorio y en permanente, y las dos corridas son comparables. En la docente con semilla 0, los fallados son ∅, {N11} y {N06, N11}: en permanente N11 ya estaba caído en la ronda 3, así que las dos trayectorias coinciden; con otra semilla (p. ej. 3) se separan (`test_con_la_misma_semilla_los_fallados_de_cada_ronda_coinciden_en_los_dos_modos`).
- **`fallados` en orden creciente** y candidatos en orden creciente: el voraz recorre V en ese orden y el desempate por el menor índice (decisión 6) se conserva.
- **Ronda vacía no es falla:** con q = 1 o sin presupuesto, no hay nada que elegir; se reporta S_r = ∅ y se cuenta en `resumen.rondas_sin_participantes`.
- **El exacto corre dentro de la corrida** (`exacto=True` por omisión) porque la cota por ronda solo se puede mostrar con OPT_r; se niega sin evaluar si C(n_r, k_r) > 200000 (decisión 31) y la razón queda vacía. En la docente, C(15, 5) = 3003 por ronda.
- **q y el modo se validan con `ValueError`**, no con un rechazo del caso: son parámetros de la línea de comandos, no del archivo; `argparse` los filtra antes.

## Cómo modificarlo
- **Que los nodos sin tope no tengan límite:** en `ejecutar_rondas`, `restante[v] = None` para los nodos sin tope, saltarlos en `candidatos_de_la_ronda` (siempre candidatos) y no descontarles; `topes_r` solo con los que tienen tope. Con eso q = 0 y T = 1 reproduce la base también con B = 0.
- **Fallos con probabilidad por nodo:** `sortear_fallos` recibe id → q_v en lugar de q.
- **Planear las T rondas juntas:** es otro algoritmo; no cabe como cambio local.
- Correr `pruebas/test_variante_rondas.py`.

## Pruebas
`pruebas/test_variante_rondas.py` (105 pruebas): con q = 0 y T = 1, mismo S, f(S), llamadas, reparto y U que `ejecutar_ronda` en los 13 casos propios con B > 0 y en la docente; `borde_B_cero` aparte (con B = 0 y sin topes no hay candidatos, a diferencia de la base); los dos modos coinciden con q = 0; sorteo con q = 0 (nadie), q = 1 (todos, en orden) y reproducible por semilla; q = 1 deja las 3 rondas sin participantes y el restante intacto; el restante se descuenta exactamente y nunca es negativo (8 rondas en la docente, con nodos que se agotan) y un nodo con restante 0 no es candidato; con topes 0 participan todos los que quedan (k_r = 1); el tope de la ronda es el restante; en permanente los candidatos nunca aumentan (4 semillas) y los caídos son la unión de los fallados; misma semilla = mismos fallados en los dos modos, y en transitorio los fallados vuelven; batería aleatoria de influencia (N = 8, 10, 12; k = 3; B = 20; densidad 0,3, 0,6 y 1,0; semillas 1 a 3; q = 0,3; T = 3; los dos modos): f(S_r) ≤ OPT_r y razón ≥ cota en todas las rondas, mínima 0,938153; sin exacto disponible (N = 320) la razón queda vacía y todo cumple; ramas de fallo de las tres verificaciones nuevas; rechazos (T = 0, k = N) y parámetros inválidos; `numero_rondas` = 3 de la docente solo se aplica en la variante, `rondas` opcional del propio y `--rondas` manda; regresión de la docente (fallados, S_r, reparto, razones, restante) y de las evidencias de `resultados/variantes/b_profesora_*`; `ejecutar.py --variante b` (evidencias, resumen por ronda, caso rechazado con una fila, resumen de la base intacto, parámetros inválidos).

## Preguntas probables en la sustentación
- **¿Qué garantiza el voraz en la variante?** Por ronda, f(S_r) ≥ (1 − (1 − 1/k_r)^k_r)·OPT_r, porque f restringida a los candidatos sigue siendo monótona y submodular. Sobre las T rondas juntas no hay cota: cada ronda se optimiza sola (Supuesto ❓).
- **¿Cuánto cuesta?** T veces una ronda de la base más Θ(N) por el sorteo: O(T·(k·(N + A) + B lg k)); el exacto suma O(T·C(N, k)·(N + A)) y es solo referencia.
- **¿Por qué el restante nunca es negativo?** Porque el reparto respeta el tope (decisión 28) y el tope de la ronda es el restante.
- **¿Qué pasa si fallan más de N − k nodos?** Participan todos los que quedan (k_r = |candidatos|); si no queda ninguno, la ronda es vacía y no es falla.

_Última actualización: 2026-11-16 · archivo nuevo (P-4 fase 2)_
