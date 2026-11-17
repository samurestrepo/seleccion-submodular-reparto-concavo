# Ficha: `red/pd_reparto.py`

## Para qué existe
Resuelve la Parte 1 por **programación dinámica** como algoritmo de referencia: reparte hasta B unidades entre los nodos de S maximizando Σ u_i(t_i), con t_i ≤ c_i, **sin suponer que las u_i sean cóncavas**. El voraz de `reparto.py` es óptimo solo con u_i crecientes y cóncavas; esta PD lo es siempre, a cambio de Θ(N·B²). No forma parte de la ronda: sirve para contrastar (misma utilidad que el voraz si todas las u son cóncavas; más utilidad si alguna es convexa) y para la serie h de los experimentos.

## Funciones públicas
| Función | Recibe | Devuelve | Complejidad (tiempo · espacio) |
|---|---|---|---|
| `repartir_pd(S, B, utilidades, topes=None)` | ids sin repetir, B ≥ 0, diccionario id → utilidad (interfaz `valor(t)`, la de `reparto.py`), topes opcional (id → c_i; sin tope, c_i = B) | `ResultadoPD` con `x` (id → unidades), `utilidad` y `candidatos` | T = Σ_i Σ_b (mín(c_i, b) + 1) candidatos, cada uno O(1). Peor caso (c_i ≥ B): N·(B+1)(B+2)/2 = Θ(N·B²). Mejor caso (todos los c_i = 0): N·(B+1) = Θ(N·B). Espacio Θ(N·B) (tabla P; de M solo dos filas) |

## Cómo funciona
Bottom-up. M[i][b] = mejor utilidad repartiendo **a lo sumo** b unidades entre los primeros i nodos de S.
1. M[0][b] = 0 para todo b.
2. M[i][b] = máx sobre t = 0..mín(c_i, b) de u_i(t) + M[i−1][b−t]. Se recorre t de menor a mayor y solo se reemplaza con `>` estricto, así que P[i][b] (el t ganador) es el **menor** t en caso de empate.
3. La utilidad es M[N][B]. Reconstrucción: desde (N, B), x_N = P[N][B]; se resta ese t a b y se sigue con el nodo N−1, hasta el nodo 1.
Cada candidato t evaluado suma 1 a `candidatos`. u_i(0..c_i) se calcula una vez por nodo (O(c_i) extra, no cambia el orden).

## Por qué así
- **Sin líneas numeradas:** el autor confirmó que el informe no tenía pseudocódigo de la PD; la §7.2 es nueva y no usa líneas numeradas, así que el código no lleva comentarios `# línea N del pseudocódigo` (decisión 33).
- **"A lo sumo b" en lugar de "exactamente b":** con M[0][b] = 0 para todo b, la PD admite que sobre presupuesto cuando Σ c_i < B, igual que el voraz (que gasta mín(B, Σ c_i) y deja el resto). Con u crecientes las dos utilidades coinciden; con ganancias nulas en una tabla, x puede diferir del voraz (el voraz entrega unidades de ganancia 0; la PD, ante empate, usa el menor t).
- **Desempate por el menor t**, en la línea de "menor índice" del proyecto (decisión 6).
- **Variante (c):** la PD sirve en el modelo c1 (es separable con a'_i) pero **no en c2**: la recurrencia M[i][b] = máx_t u_i(t) + M[i−1][b−t] supone que la utilidad de i depende solo de x_i (H1), y en c2 depende también de los x de sus vecinos. Por eso el exacto de la variante es una enumeración (`red/variante_vecinos.py`, decisión 46).
- **Tope por nodo** igual que en el voraz: c_i = `topes.get(i, B)`, acotado por B.
- **Solo dos filas de M:** la reconstrucción necesita P completa, no M.

## Cómo modificarlo
Para otra regla de empate, cambiar `>` por `>=` (gana el mayor t) y actualizar `test_ante_empate_gana_el_menor_t`. Para reducir tiempo a Θ(N·B lg B) con u cóncavas habría que usar la estructura de Δ, pero entonces es el voraz.

## Pruebas
`pruebas/test_pd_reparto.py` (29 con las parametrizaciones): utilidad igual a la del voraz en los 15 casos propios y de la profesora (con los k primeros nodos, y todos si es barato) y en 200 instancias aleatorias cóncavas con topes (semilla 7); una u convexa donde la PD da 10 y el voraz 7, y el contraejemplo del informe (11 contra 4); B = 0, topes en 0, N = 1, S vacío, empate y orden de S; y el conteo exacto N·(B+1)(B+2)/2.

## Preguntas probables en la sustentación
- **¿Por qué la PD cuesta Θ(N·B²) y el voraz Θ(N + B lg N)?** La PD prueba todas las cantidades t para cada nodo y cada b; el voraz usa la concavidad para entregar de a una unidad por la mayor ganancia.
- **¿Cuándo da lo mismo?** Con todas las u_i crecientes y cóncavas (misma utilidad; el x puede diferir por empates).
- **¿Y si Σ c_i < B?** Sobra presupuesto en ambos: la PD lo permite porque M es "a lo sumo b".

_Última actualización: 2026-11-17 · nota: por qué la PD no sirve en el modelo c2 de la variante (c); sin cambios de código (P-4 fase 3)_
