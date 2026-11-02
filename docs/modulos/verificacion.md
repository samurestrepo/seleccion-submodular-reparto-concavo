# Ficha: `red/verificacion.py`

## Para qué existe
Comprueba las restricciones de la entrada y de las dos salidas (informe 6.6). La guía de la entrega pide la verificación de restricciones en la traza de cada caso.

## Funciones públicas
| Función | Comprueba | Complejidad |
|---|---|---|
| `verificar_entrada(instancia)` | 1 ≤ k < N; B ≥ 0; ids únicos; cada u_i creciente y cóncava en {0, …, B} | O(N + Σ_i min(L_i, B)) esperado, con L_i = largo de la tabla del nodo i (0 en log y raíz). Fuera de los tiempos medidos |
| `verificar_seleccion(instancia, oraculo, S, valorS)` | S ⊆ V; sin repetidos; \|S\| ≤ k; valorS = f(S) recalculada | O(N + M) |
| `verificar_conteo_llamadas(N, k, llamadas)` | llamadas a Δ = k·N − k(k−1)/2 | O(1) |
| `verificar_reparto(S, B, utilidades, resultado)` | cada x_i entero en [0, B]; Σ x_i = B; utilidad finita e igual a Σ u_i(x_i) recalculada; extracciones = inserciones = B | O(\|S\|) |

Cada una devuelve una lista de `Verificacion(nombre, cumple, detalle)`. Ninguna lanza excepciones: así **todas** quedan en la traza aunque alguna falle. Por eso no evalúan datos que ya fallaron: un id de S ajeno a V no entra al recálculo de f(S), y un x_i fuera de rango no se evalúa en u_i (decisión 23).

## Cómo funciona
1. **Ids únicos:** `_ids_repetidos` recorre los ids una vez con un `set` de vistos. Es O(N) esperado.
2. **Concavidad:** cada familia responde con `revisar_forma(B, tolerancia)`, que devuelve `None` o el motivo. `verificar_entrada` no sabe qué familia está revisando (ver `docs/modulos/utilidades.md`).

## Por qué así
- **Por qué no se recorren las B unidades** (decisión 20): recorrerlas costaba O(N·B), mucho más que los algoritmos. Medido: la ronda con N = 1000, B = 16000 bajó de 46.6 s a 0.10 s. La forma de log y raíz se conoce con cálculo: basta a > 0.
- **Por qué `set` y no `ids.count`:** `count` recorre toda la lista cada vez, así que eran O(N²) comparaciones. Medido con B = 0: N = 80000 bajó de 107 s a 0.10 s.
- **Ruido flotante:** restar logaritmos o raíces con x ≥ 1e8 y a ≥ 1000 daba falsos "no cóncava". Al no restar nada, ese falso aviso desapareció.
- **Solo importan las unidades entregables** (decisión 21): Δ(x) ≥ 0 si x < B, y Δ(x + 1) ≤ Δ(x) si x + 1 < B. Δ(B) nunca se entrega, así que [3, 2, 5] con B = 2 es válida.
- Los números con decimales (logaritmos y raíces) se comparan con tolerancia 1e-9, no con `==`.
- El informe pide "1 ≤ k" implícitamente (k ∈ ℕ y se elige al menos un nodo); se dejó explícito.
- La comprobación del conteo de llamadas no estaba en la tabla 6.6 original del informe; se agregó porque es la evidencia en vivo de la fórmula de eficiencia (decisión 12).

## Cómo modificarlo
- **Restricción "≤ B":** cambiar `suma == B` por `suma <= B` y `extracciones == B == inserciones` por `extracciones == suma == inserciones` en `verificar_reparto`. También cambian `reparto.py` y `utilidades.py`: receta 2 de `docs/agente/GUIA_CAMBIOS.md`.
- **Topes por nodo:** comprobar x_i ≤ c_i, Σ x_i = mín(B, Σ c_i) e inserciones = extracciones − nodos que llegaron a su tope. Receta 3 de la guía.
- **Nueva familia de utilidad:** no se toca aquí; basta su `revisar_forma`.

## Pruebas
`pruebas/test_verificacion.py`:
- **Costo sin reloj:** un id que cuenta sus comparaciones (ya no son O(N²)); log y raíz con B = 10¹² sin llamar a `ganancia`; tabla con B = 10¹² en un número de llamadas proporcional a su largo.
- **Bordes de la concavidad:** lo que queda fuera del presupuesto se acepta y lo que queda dentro se rechaza; tablas cortas; coeficientes malos creados directamente.
- **Ramas de fallo:** cada comprobación de `verificar_seleccion`, `verificar_conteo_llamadas` y `verificar_reparto`, incluida la utilidad infinita.

`pruebas/test_ronda.py` cubre la entrada inválida con k = N y la utilidad no cóncava reportada.

## Preguntas probables en la sustentación
- **¿Cómo sabe que el valor de f(S) es correcto?** Lo recalcula desde cero con un oráculo aparte y lo compara con el acumulado del voraz.
- **¿Cómo revisa la concavidad sin recorrer B?** En log y raíz basta a > 0, porque la derivada es positiva y decrece para todo x. En tabla recorre su lista: después de ella todo vale 0.
- **¿Cuánto cuesta verificar la entrada?** O(N + Σ min(L_i, B)) esperado, y no entra en los tiempos medidos.

_Última actualización: 2026-11-02 · concavidad por familia, ids con set, solo unidades entregables, sin excepciones al recalcular_
