# Ficha: `scripts/corrida_combinada.py`

## Para qué existe
Corre juntas las tres variantes en el caso de la docente (`casos/profesora/entrada_G2_red_15_nodos.json`): T = 3 rondas con fallos (b); en cada ronda, selección con costos y L = 24 (a, voraz modificado) sobre los candidatos de la ronda; y reparto con vecinos (c1 o c2, β = 0,2) con topes = presupuesto restante. **No cambia ninguna variante ni la base:** solo llama a sus funciones públicas. Escribe `resultados/variantes/combinada_c1/` y `combinada_c2/` (`salida.json` y `traza.txt`). Fase 6 (opcional) de P-4; decisiones 56 y 57.

## Funciones públicas
n_r = candidatos de la ronda r, m = |S_r|, c_mín = menor costo, A = aristas del grafo, A_S = aristas dentro de S_r, d(S) = Σ_{i∈S} grado(i).

| Función | Recibe | Devuelve | Complejidad (tiempo · espacio) |
|---|---|---|---|
| `ejecutar_combinada(instancia, modelo="c1", modo="transitorio", prob_fallo=0.2, semilla=0, rondas=None, beta=0.2, exacto=True)` | instancia de la docente (costos, L y grafo), modelo `c1`\|`c2`, modo de fallo, q, semilla, T (None: `numero_rondas` del archivo, o 1), β, si calcula OPT_r | diccionario: `entrada`, `supuestos`, `rondas` (fallados, candidatos, `seleccion` con S_r, f, costo, evaluaciones, origen, OPT_r, S*_r, razón; `reparto` con x, U y, en c2, repartos, cota y OPT si cupo; `restante` y `restante_total`), `verificaciones_globales`, `resumen` (Σ f, Σ U), `todas_cumplen`. Lanza `ValueError` si la instancia no admite alguna variante | ver «Costo» abajo · O(N + A) del oráculo y del restante, más O(T·N) del resultado |
| `a_texto(resultado)` | el diccionario anterior | la traza legible (cabecera, supuestos y un bloque por ronda) | O(tamaño del resultado) |
| `main()` | — | 0 si todo cumple; corre c1 y c2 en modo transitorio y permanente, escribe las carpetas y compara los dos modos | lo de 4 corridas |

**Costo de una ronda** (influencia, cada evaluación de f es O(1 + grado)):
1. sorteo y candidatos: Θ(N);
2. voraz modificado sobre los candidatos: a lo sumo 1 + m·n_r − m(m − 1)/2 evaluaciones, con m ≤ mín(n_r, ⌊L/c_mín⌋): O(n_r·mín(n_r, L/c_mín)·(1 + grado)) ⊆ O(m·(N + A));
3. reparto: c1 Θ(m + d(S)) + O(m + B lg m); c2 Θ(m + d(S)) + O(B·(m + A_S));
4. descontar: O(m).

**T de la corrida** sin el exacto: T·[N + m·(N + A) + d(S) + reparto], o sea O(T·(m·(N + A) + B lg m)) con c1 y O(T·(m·(N + A) + B·(m + A_S))) con c2. **El exacto (OPT_r)** suma F_r ≤ 2^{n_r} evaluaciones de f por ronda (las de `seleccionar_exacto_costos`, cada una O(N + A)): O(T·2^N·(N + A)). **Espacio:** O(N + A) (oráculo, grafo restringido y restante) más la pila O(N) del exacto; el resultado guarda O(T·N).

## Cómo funciona
Por ronda r = 1..T, en este orden (las líneas citan el pseudocódigo de cada ficha, no hay uno propio):
1. `sortear_fallos` y `candidatos_de_la_ronda` de `variante_rondas.py` (no fallados, con restante > 0; en permanente, los caídos no vuelven).
2. `voraz_modificado(oráculo nuevo, candidatos, costos, L)` de `variante_costos.py`: V = candidatos y Σ c(S_r) ≤ L **en lugar de** |S_r| ≤ k (decisión 56). Con `exacto=True`, `seleccionar_exacto_costos` sobre los candidatos da OPT_r (2^{n_r} ≤ 2^15 = 32768, bajo el límite de la decisión 37).
3. topes_r = restante de cada nodo de S_r; `repartir_c1` o `repartir_c2` de `variante_vecinos.py` con esos topes. En c2 se cuenta los repartos (`contar_repartos`) y el exacto solo corre si caben en 200000 (decisión 57).
4. restante[v] −= x_v. Como x_v ≤ topes_r[v] = restante[v], nunca queda negativo.

Verifica por ronda: S_r ⊆ candidatos, sin repetidos, Σ c(S_r) ≤ L, f(S_r) recalculada, f(S_r) ≥ 0,405·OPT_r; el reparto con `verificar_reparto` (c1, con u_i = a'_i·ln(1 + x)) o `verificar_reparto_c2` (c2); y al final, restante ≥ 0.

## Por qué así
- **Un script y no un módulo de `red/`:** es una demostración en un solo caso, sin opción nueva en `ejecutar.py`; así ninguna variante cambia.
- **Oráculo nuevo por llamada:** los contadores de evaluaciones empiezan en cero, como en las variantes.
- **El modo permanente** se corre también (es barato) y se compara: con la semilla 0 los fallados son ∅, {N11} y {N06, N11}, cada uno contiene al anterior, así que los candidatos y todo lo demás coinciden en los dos modos. Se guarda `modo_permanente.coincide_con_transitorio` en `salida.json`.
- **La consola** solo imprime un resumen ASCII (la de Windows no tiene β ni Σ); la traza completa va a `traza.txt` en UTF-8.

## Cómo modificarlo
- Otro caso o parámetros: llamar `ejecutar_combinada` con otra instancia o argumentos; `main` usa la docente.
- Usar k y L a la vez: agregar un tope de tamaño en la selección exigiría cambiar `voraz_por_cociente` (no se hace; decisión 56).
- Exacto de c2 con más repartos: pasar el límite a `repartir_exacto` (cuesta segundos por ronda).
Pruebas a revisar: `pruebas/test_corrida_combinada.py`.

## Pruebas
`pruebas/test_corrida_combinada.py` (9): con q = 0, T = 1, β = 0, costos 1 y L = k reproduce la base (S, f, x y U) en c1 y c2; Σ c(S_r) ≤ L y S_r ⊆ candidatos; con T = 12 el presupuesto se agota (270 = 9·30) y el restante nunca es negativo, nadie sin restante es candidato y x ≤ restante; misma semilla, mismo resultado; con q = 1 nadie participa; el formato propio (sin grafo) se rechaza.

## Preguntas probables en la sustentación
- *¿Por qué la ronda 1 de la combinada no es la de la base?* Porque la restricción es L = 24 y no k = 5: la ronda 1 es exactamente la variante (a) (S = N05, N09, N14, N11, N15, N01), y el reparto es el de c1 o c2 sobre ese S.
- *¿El restante puede quedar negativo?* No: el tope de cada nodo en la ronda es su restante y el reparto respeta x_i ≤ c_i.
- *¿Por qué c2 no tiene OPT del reparto?* Con 6 nodos, B = 30 y topes, hay de 0,5 a 1,9 millones de repartos por ronda: pasa el límite de 200000 (decisión 57). La referencia de c2 en la docente está en §10.1.4 y su cota en la batería.

_Última actualización: 2026-11-17 · creación (P-4 fase 6)_
