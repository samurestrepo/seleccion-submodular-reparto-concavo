# Ficha: `red/verificacion.py`

## Para qué existe
Comprueba las restricciones de la entrada y de las dos salidas (informe 6.6). La guía de la entrega pide la verificación de restricciones en la traza de cada caso.

## Funciones públicas
| Función | Comprueba | Complejidad |
|---|---|---|
| `verificar_entrada(instancia)` | 1 ≤ k < N; B ≥ 0; ids únicos; cada u_i creciente y cóncava en {0, …, B}; **solo con influencia:** cada peso de influencia en [0, 1] | O(N + Σ_i min(L_i, B)) esperado, con L_i = largo de la tabla del nodo i (0 en log y raíz); con influencia, O(N + A). Fuera de los tiempos medidos |
| `verificar_seleccion(instancia, oraculo, S, valorS)` | S ⊆ V; sin repetidos; \|S\| ≤ k; valorS = f(S) recalculada, con tolerancia | O(N + M) con cobertura; O(N + A) con influencia |
| `verificar_conteo_llamadas(N, k, llamadas)` | llamadas a Δ = k·N − k(k−1)/2 | O(1) |
| `verificar_reparto(S, B, utilidades, resultado, topes=None)` | cada x_i entero en [0, B]; si hay topes, cada x_i ≤ c_i; Σ x_i = mín(B, Σ c_i); utilidad finita e igual a Σ u_i(x_i) recalculada; extracciones = Σ x_i e inserciones = Σ x_i − nodos en su tope | O(\|S\|) |

Cada una devuelve una lista de `Verificacion(nombre, cumple, detalle)`. Ninguna lanza excepciones: así **todas** quedan en la traza aunque alguna falle. Por eso no evalúan datos que ya fallaron: un id de S ajeno a V no entra al recálculo de f(S), y un x_i fuera de rango no se evalúa en u_i (decisión 23).

## Cómo funciona
1. **Ids únicos:** `_ids_repetidos` recorre los ids una vez con un `set` de vistos. Es O(N) esperado.
2. **Concavidad:** cada familia responde con `revisar_forma(B, tolerancia)`, que devuelve `None` o el motivo. `verificar_entrada` no sabe qué familia está revisando (ver `docs/modulos/utilidades.md`).
3. **Pesos de influencia:** `_verificar_pesos` recorre el grafo. Cada arista está guardada en sus dos puntas, y con `v < w` se reporta una sola vez. El formato propio no tiene grafo y por eso no lleva esta línea: sus evidencias no cambian.

## Por qué así
- **Por qué no se recorren las B unidades** (decisión 20): recorrerlas costaba O(N·B), mucho más que los algoritmos. Medido: la ronda con N = 1000, B = 16000 bajó de 46.6 s a 0.10 s. La forma de log y raíz se conoce con cálculo: basta a > 0.
- **Por qué `set` y no `ids.count`:** `count` recorre toda la lista cada vez, así que eran O(N²) comparaciones. Medido con B = 0: N = 80000 bajó de 107 s a 0.10 s.
- **Ruido flotante:** restar logaritmos o raíces con x ≥ 1e8 y a ≥ 1000 daba falsos "no cóncava". Al no restar nada, ese falso aviso desapareció.
- **Solo importan las unidades entregables** (decisión 21): Δ(x) ≥ 0 si x < B, y Δ(x + 1) ≤ Δ(x) si x + 1 < B. Δ(B) nunca se entrega, así que [3, 2, 5] con B = 2 es válida.
- Los números con decimales (logaritmos, raíces y ahora f de influencia) se comparan con tolerancia 1e-9, no con `==`. El voraz suma los Δ uno a uno y `valor` calcula f desde cero: son el mismo número salvo redondeo, y `test_el_redondeo_de_verdad_pasa_con_tolerancia_y_no_con_igualdad` muestra un caso donde `==` daría una falsa falla. La tolerancia es relativa: en cobertura, un error de una unidad solo se escaparía con f(S) cerca de 10⁹.
- **Topes (decisión 28):** sin topes, mín(B, Σ c_i) = B y las inserciones valen Σ x_i, así que se exige lo mismo de antes con otro nombre. Con Σ c_i < B, el sobrante no es una falla, pero gastar menos de mín(B, Σ c_i) sí. Un nodo con tope 0 no se descuenta de las inserciones, porque nunca entró al montículo. La línea "cada x_i ≤ c_i" solo aparece si la instancia tiene topes.
- **La concavidad sigue juzgándose hasta B, no hasta c_i:** una tabla que se dañe entre c_i y B se rechaza, aunque esas unidades nunca se entreguen. Es más estricto de lo necesario, pero nunca deja pasar un caso sin garantía. Log y raíz no se afectan.
- **Por qué los pesos se exigen en [0, 1]:** fuera de ese rango, 1 − p ya no es un factor entre 0 y 1, y f deja de ser monótona y submodular. Sin eso no vale la cota (1 − 1/e). Por eso el caso no corre, igual que con la concavidad. NaN también falla, porque `0 <= NaN <= 1` es falso.
- El informe pide "1 ≤ k" implícitamente (k ∈ ℕ y se elige al menos un nodo); se dejó explícito.
- La comprobación del conteo de llamadas no estaba en la tabla 6.6 original del informe; se agregó porque es la evidencia en vivo de la fórmula de eficiencia (decisión 12).

## Cómo modificarlo
- **Restricción "≤ B":** cambiar `suma == esperado` por `suma <= esperado` en `verificar_reparto`. También cambian `reparto.py` y `utilidades.py`: receta 2 de `docs/agente/GUIA_CAMBIOS.md`.
- **Topes por nodo:** ya está hecho (receta 3, decisión 28).
- **Nueva familia de utilidad:** no se toca aquí; basta su `revisar_forma`.

## Pruebas
`pruebas/test_verificacion.py`:
- **Costo sin reloj:** un id que cuenta sus comparaciones (ya no son O(N²)); log y raíz con B = 10¹² sin llamar a `ganancia`; tabla con B = 10¹² en un número de llamadas proporcional a su largo.
- **Bordes de la concavidad:** lo que queda fuera del presupuesto se acepta y lo que queda dentro se rechaza; tablas cortas; coeficientes malos creados directamente.
- **Ramas de fallo:** cada comprobación de `verificar_seleccion`, `verificar_conteo_llamadas` y `verificar_reparto`, incluida la utilidad infinita.
- **Topes:** tope activo; topes que no alcanzan B; tope 0 sin descontar; y que se detecte un x_i por encima del tope, gastar menos de mín(B, Σ c_i), y extracciones o inserciones mal contadas. Con R repeticiones, `test_ronda.py` comprueba que una repetición distinta se detecte (esa verificación vive en `ronda.py`).
- **Influencia:** pesos en 0, 0.5 y 1 cumplen; −0.1, 1.5, NaN e Infinity fallan, la arista se reporta una vez y la ronda no corre; el formato propio no tiene esa línea; f real se compara con tolerancia.

`pruebas/test_ronda.py` cubre la entrada inválida con k = N y la utilidad no cóncava reportada.

## Preguntas probables en la sustentación
- **¿Cómo sabe que el valor de f(S) es correcto?** Lo recalcula desde cero con un oráculo aparte y lo compara con el acumulado del voraz.
- **¿Cómo revisa la concavidad sin recorrer B?** En log y raíz basta a > 0, porque la derivada es positiva y decrece para todo x. En tabla recorre su lista: después de ella todo vale 0.
- **¿Cuánto cuesta verificar la entrada?** O(N + Σ min(L_i, B)) esperado, y no entra en los tiempos medidos.

_Última actualización: 2026-11-04 · topes en `verificar_reparto`; pesos de influencia en [0, 1]; valor de f con tolerancia_
