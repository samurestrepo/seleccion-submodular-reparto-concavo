# Ficha: `red/reparto.py`

## Para qué existe
Resuelve la **Parte 1** de la ronda: reparte B unidades entre los nodos que eligió la Parte 2 para maximizar Σ u_i(x_i). Es el voraz con montículo del informe (sección 6.4), y es **óptimo** porque cada u_i es creciente y cóncava.

## Funciones públicas
| Función | Recibe | Devuelve | Complejidad (tiempo · espacio) |
|---|---|---|---|
| `repartir_presupuesto(S, B, utilidades, traza=None)` | ids elegidos, B, diccionario id → utilidad, traza opcional | `ResultadoReparto` con `x`, `utilidad`, `extracciones` e `inserciones` | Peor caso O(N + B lg N). Con `heapq`, Θ(N + B(1 + lg N)) para toda entrada, con N = \|S\| · Θ(N) |

**Precondiciones** (en el docstring; aquí no se comprueban, para seguir el pseudocódigo, decisión 19): B ≥ 0, S sin repetidos y cada u_i creciente y cóncava. `ronda.py` ya las valida antes de llamar. Si no se cumplen: con B < 0 devuelve x en 0 sin avisar; con ids repetidos da un resultado sin sentido; sin concavidad pierde la garantía de óptimo. La única comprobación es la que ya existía: S vacío con B > 0 lanza `ValueError`.

## Cómo funciona
1. **Línea 1:** x[i] ← 0 para cada nodo.
2. **Línea 2:** se arma la lista de parejas (−Δ_i(0), i) y `heapq.heapify` la vuelve montículo en O(N) (BUILD-HEAP).
3. **Línea 3:** se repite B veces.
4. **Línea 4:** `heappop` saca la raíz: el nodo cuya siguiente unidad aporta más. O(lg N).
5. **Línea 5:** ese nodo recibe la unidad.
6. **Línea 6:** se calcula Δ_i de su **siguiente** unidad y se vuelve a meter con `heappush`. O(lg N). Así el montículo siempre tiene N elementos.
7. **Línea 7:** traza (unidad, nodo, ganancia).
8. **Línea 8:** se suma la utilidad total.

## Por qué así
- **`heapq` es de mínimos** (decisión 7). Se guarda **−ganancia**: la ganancia más grande tiene el negativo más pequeño, así que queda en la raíz. **Pregunta probable de sustentación.**
- **Desempate por el menor índice** (decisión 6): si dos negativos son iguales, Python compara el segundo elemento de la pareja, el índice, y sale primero el menor.
- Las líneas 4 y 6 se podrían fusionar en `heapq.heapreplace` (el informe lo menciona). Se dejaron separadas para que el código se lea como el pseudocódigo; la complejidad es la misma.
- Los contadores `extracciones` e `inserciones` deben valer B; la verificación lo revisa.

### Por qué no hay un mejor caso Θ(N + B) (decisión 15)
Un montículo de libro (MAX-HEAPIFY) pone el último elemento en la raíz y lo baja comparando con sus hijos; **puede parar pronto** si ya quedó en su lugar. `heapq.heappop` no hace eso. Su función interna `_siftup` trabaja así:

1. Saca la raíz y deja un **hueco** arriba.
2. Sube el hijo menor al hueco, y repite: el hueco baja un nivel en cada paso **hasta llegar a una hoja, sin parar antes**.
3. Pone en ese hueco el elemento que estaba de último y lo sube lo que haga falta (normalmente muy poco).

¿Por qué lo hacen así? Porque el último elemento casi siempre pertenece cerca del fondo: compararlo en cada nivel sería gastar comparaciones. Pero la consecuencia es que **cada extracción cuesta unas lg N comparaciones, sea cual sea la entrada**. Medido: exactamente lg N con ganancias empatadas, con un nodo dominante y con log de a igual, y un poco más (hasta lg N + 0.46) con a distintos, para N de 64 a 131072. `heappush` sí puede costar 1 comparación, pero el `heappop` de cada vuelta no se puede evitar. Esa medición es de cuatro familias de entradas; lo que la extiende a toda entrada es la lectura de `_siftup`.

Por eso el costo es **Θ(N + B(1 + lg N))**:
- **N:** armar la lista y `heapify`, y sumar la utilidad al final.
- **B·lg N:** un `heappop` y un `heappush` por vuelta.
- **El 1 (caso N = 1):** lg 1 = 0, así que la fórmula O(N + B lg N) daría O(1), pero el ciclo **igual da B vueltas**. Con un solo nodo el tiempo es Θ(B) (medido: 0.13 s con B = 10⁵ y 7.7 s con B = 4·10⁶). Para N ≥ 2, 1 + lg N y lg N son del mismo orden y el peor caso O(N + B lg N) sigue siendo correcto.

## Cómo modificarlo
Las recetas completas, con todo lo que hay que tocar, están en `docs/agente/GUIA_CAMBIOS.md`; se probaron aplicándolas en copias.
- **Desempatar por el mayor índice:** receta 1. Aquí: guardar `(-ganancia, -i)` en `# línea 2` y `# línea 6 del pseudocódigo`, y deshacer el signo del índice en `# línea 4`.
- **Permitir gastar menos de B ("≤ B") con Δ negativas:** receta 2. Aquí: antes de `# línea 4 del pseudocódigo`, `if -H[0][0] < 0: break`. También cambian `utilidades.py` y `verificacion.py`.
- **Tope por nodo (x_i ≤ c_i):** receta 3. Aquí: parámetro `topes`, filtrar en `# línea 2`, `if not H: break` antes de `# línea 4` y reinsertar solo si no llegó a su tope en `# línea 6`. También cambian `entrada.py`, `ronda.py` y `verificacion.py`.
- Cualquier cambio aquí: correr `pruebas/test_reparto.py` y después `python -m pytest`.

## Pruebas
`pruebas/test_reparto.py`:
- Ejemplo del informe: P = 9, 5, 2, 1 y Q = 7, 6, 1, 0 con B = 4 da 27 en el orden P, Q, Q, P.
- Contraejemplo convexo: P = 1, 10 y Q = 3, 0 con B = 2 da 4; la fuerza bruta da 11 (sin concavidad, el voraz falla).
- Desempate, B = 0, error si no hay nodos, contadores = B.
- 150 instancias al azar con log y raíz: la utilidad coincide con la fuerza bruta (el voraz es óptimo).

## Preguntas probables en la sustentación
- **¿Por qué el negativo?** Porque `heapq` solo hace montículos de mínimos; con −ganancia, el mínimo es la mayor ganancia.
- **¿De dónde sale O(N + B lg N)?** heapify es O(N); el ciclo corre B veces y cada vuelta hace un pop y un push de O(lg N), porque el montículo siempre tiene N elementos (altura ⌊lg N⌋). Calcular Δ es O(1).
- **¿Cuál es el mejor caso?** No hay uno más barato con `heapq`: `heappop` siempre baja hasta una hoja, así que es Θ(N + B(1 + lg N)) para toda entrada. El 1 es por N = 1: lg 1 = 0, pero el ciclo igual da B vueltas.
- **¿Por qué es óptimo?** Con concavidad, la lista de ganancias de cada nodo no aumenta; tomar siempre la mayor equivale a quedarse con las B mayores de todas las listas (argumento de intercambio, entrega posterior).

_Última actualización: 2026-11-02 · complejidad real con heapq, precondiciones y recetas completas; sin cambio de lógica_
