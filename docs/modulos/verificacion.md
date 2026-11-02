# Ficha: `red/verificacion.py`

## Para qué existe
Comprueba las restricciones de la entrada y de las dos salidas (informe 6.6). La guía de la entrega pide la verificación de restricciones en la traza de cada caso.

## Funciones públicas
| Función | Comprueba | Complejidad |
|---|---|---|
| `verificar_entrada(instancia)` | 1 ≤ k < N; B ≥ 0; ids únicos; cada u_i creciente y cóncava en {0, …, B} | O(N·B) por la concavidad (fuera de los tiempos medidos) |
| `verificar_seleccion(instancia, oraculo, S, valorS)` | S ⊆ V; sin repetidos; \|S\| ≤ k; valorS = f(S) recalculada | O(N + M) |
| `verificar_conteo_llamadas(N, k, llamadas)` | llamadas a Δ = k·N − k(k−1)/2 | O(1) |
| `verificar_reparto(S, B, utilidades, resultado)` | cada x_i entero en [0, B]; Σ x_i = B; utilidad = Σ u_i(x_i) recalculada; extracciones = inserciones = B | O(\|S\|) |

Cada una devuelve una lista de `Verificacion(nombre, cumple, detalle)`. Ninguna lanza excepciones: así **todas** quedan en la traza aunque alguna falle.

## Por qué así
- Los números con decimales (logaritmos y raíces) se comparan con tolerancia 1e-9, no con `==`.
- El informe pide "1 ≤ k" implícitamente (k ∈ ℕ y se elige al menos un nodo); se dejó explícito.
- La comprobación del conteo de llamadas no está en la tabla 6.6 del informe; se agregó porque es la evidencia en vivo de la fórmula de eficiencia (decisión 12).

## Cómo modificarlo
- **Restricción "≤ B":** cambiar `suma == B` por `suma <= B` en `verificar_reparto`.
- **Topes por nodo:** agregar una comprobación x_i ≤ c_i.

## Pruebas
Las cubren `pruebas/test_ronda.py` (entrada inválida con k = N; utilidad no cóncava reportada) y todas las rondas que deben salir en OK.

## Preguntas probables en la sustentación
- **¿Cómo sabe que el valor de f(S) es correcto?** Lo recalcula desde cero con un oráculo aparte y lo compara con el acumulado del voraz.

_Última actualización: 2026-11-02 · creación_
