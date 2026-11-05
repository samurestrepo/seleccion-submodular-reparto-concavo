# Ficha: `red/reparto.py`

## Para qué existe
Resuelve la **Parte 1** de la ronda: reparte hasta B unidades entre los nodos que eligió la Parte 2 para maximizar Σ u_i(x_i), con x_i ≤ c_i si el nodo tiene tope. Es el voraz con montículo del informe (sección 6.4), y es **óptimo** porque cada u_i es creciente y cóncava.

## Funciones públicas
| Función | Recibe | Devuelve | Complejidad (tiempo · espacio) |
|---|---|---|---|
| `repartir_presupuesto(S, B, utilidades, traza=None, topes=None)` | ids elegidos, B, diccionario id → utilidad, traza opcional, topes opcional (id → c_i; quien no aparece no tiene tope) | `ResultadoReparto` con `x`, `utilidad`, `extracciones` e `inserciones` | Peor caso O(N + B lg N). Sin topes y con `heapq`, Θ(N + B(1 + lg N)) para toda entrada, con N = \|S\| · Θ(N) |

**Precondiciones** (en el docstring; aquí no se comprueban, para seguir el pseudocódigo, decisión 19): B ≥ 0, S sin repetidos, c_i entero ≥ 0 y cada u_i creciente y cóncava. `ronda.py` ya las valida antes de llamar. Si no se cumplen: con B < 0 devuelve x en 0 sin avisar; con ids repetidos da un resultado sin sentido; sin concavidad pierde la garantía de óptimo. La única comprobación es la que ya existía: S vacío con B > 0 lanza `ValueError`.

## Cómo funciona
1. **Línea 1:** x[i] ← 0 para cada nodo.
2. **Línea 2:** se arma la lista de parejas (−Δ_i(0), i), sin los nodos con tope 0, y `heapq.heapify` la vuelve montículo en O(N) (BUILD-HEAP).
3. **Línea 3:** se repite hasta B veces. Si el montículo se vacía, todos llegaron a su tope y el ciclo termina (`if not H: break`).
4. **Línea 4:** `heappop` saca la raíz: el nodo cuya siguiente unidad aporta más. O(lg N).
5. **Línea 5:** ese nodo recibe la unidad.
6. **Línea 6:** si el nodo no llegó a su tope, se calcula Δ_i de su **siguiente** unidad y se vuelve a meter con `heappush`. O(lg N). Si llegó, no vuelve. Sin topes, el montículo siempre tiene N elementos.
7. **Línea 7:** traza (unidad, nodo, ganancia).
8. **Línea 8:** se suma la utilidad total.

## Por qué así
- **`heapq` es de mínimos** (decisión 7). Se guarda **−ganancia**: la ganancia más grande tiene el negativo más pequeño, así que queda en la raíz. **Pregunta probable de sustentación.**
- **Desempate por el menor índice** (decisión 6): si dos negativos son iguales, Python compara el segundo elemento de la pareja, el índice, y sale primero el menor.
- Las líneas 4 y 6 se podrían fusionar en `heapq.heapreplace` (el informe lo menciona). Se dejaron separadas para que el código se lea como el pseudocódigo; la complejidad es la misma.
- Sin topes, los contadores `extracciones` e `inserciones` valen B. Con topes, extracciones = Σ x_i, e inserciones = Σ x_i menos los nodos que llegaron a su tope, porque esos no se reinsertan. La verificación lo revisa.

### Topes por nodo (decisión 28)
- **De dónde sale c_i:** en el formato de la profesora, de `presupuesto_total_nodo`; en el propio, del campo opcional `tope`. Sin tope, todo se comporta como antes.
- **Qué significa:** es lo que le queda al nodo para todo el proyecto, y en una ronda lo puede gastar completo. En la variante (b) se descontará ronda a ronda.
- **Sigue siendo óptimo:** cortar u_i en c_i deja una lista de ganancias que no aumenta. El voraz toma las mejores unidades disponibles, igual que antes.
- **Si Σ c_i < B:** el montículo se vacía, el ciclo para y el sobrante queda **sin gastar**. No pasa a nodos fuera de S, porque S ya se eligió. No es una falla: se verifica Σ x_i = mín(B, Σ c_i).
- **Tope 0:** el nodo nunca entra al montículo y queda con x_i = 0. La selección no mira los topes, así que puede elegirlo igual.
- **Complejidad:** a lo sumo B vueltas, y el montículo solo se achica: el peor caso sigue en O(N + B lg N). La Θ(N + B(1 + lg N)) de abajo es sin topes; con topes, las vueltas son mín(B, Σ c_i).
- **Se aparta del pseudocódigo del informe** en esas tres líneas, y por eso está en la decisión 28.

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
- **Desempatar por el mayor índice:** receta 1. Aquí: guardar `(-ganancia, -posicion[i])` en `# línea 2` y `# línea 6 del pseudocódigo`, y recuperar el id en `# línea 4`.
- **Permitir gastar menos de B ("≤ B") con Δ negativas:** receta 2. Aquí: después de `if not H: break`, `if -H[0][0] < 0: break`. También cambian `utilidades.py` y `verificacion.py`.
- **Tope por nodo (x_i ≤ c_i):** ya está hecho (receta 3, decisión 28).
- Cualquier cambio aquí: correr `pruebas/test_reparto.py` y después `python -m pytest`.

## Pruebas
`pruebas/test_reparto.py`:
- Ejemplo del informe: P = 9, 5, 2, 1 y Q = 7, 6, 1, 0 con B = 4 da 27 en el orden P, Q, Q, P.
- Contraejemplo convexo: P = 1, 10 y Q = 3, 0 con B = 2 da 4; la fuerza bruta da 11 (sin concavidad, el voraz falla).
- Desempate, B = 0, error si no hay nodos, contadores = B.
- 150 instancias al azar con log y raíz: la utilidad coincide con la fuerza bruta (el voraz es óptimo).
- **Topes:** tope 2 con B = 3 da 3 extracciones y 2 inserciones; el caso activo da x = 2 y 3 (sin tope serían 5 y 0); topes que no alcanzan (c = 2 y 0, B = 9); todos en tope 0; tope justo en la última unidad; tope mayor que B no cambia nada; ids de texto; 300 instancias al azar contra fuerza bruta restringida a x_i ≤ c_i.

`pruebas/test_bateria.py`: con el archivo real de la profesora, todos los `presupuesto_total_nodo` valen 18 y el reparto es igual con y sin topes; `casos/propios/tope_activo.json` da 5 extracciones y 4 inserciones.

## Preguntas probables en la sustentación
- **¿Por qué el negativo?** Porque `heapq` solo hace montículos de mínimos; con −ganancia, el mínimo es la mayor ganancia.
- **¿De dónde sale O(N + B lg N)?** heapify es O(N); el ciclo corre B veces y cada vuelta hace un pop y un push de O(lg N), porque el montículo siempre tiene N elementos (altura ⌊lg N⌋). Calcular Δ es O(1).
- **¿Cuál es el mejor caso?** No hay uno más barato con `heapq`: `heappop` siempre baja hasta una hoja, así que es Θ(N + B(1 + lg N)) para toda entrada. El 1 es por N = 1: lg 1 = 0, pero el ciclo igual da B vueltas.
- **¿Por qué es óptimo?** Con concavidad, la lista de ganancias de cada nodo no aumenta; tomar siempre la mayor equivale a quedarse con las B mayores de todas las listas (argumento de intercambio, entrega posterior).
- **¿Qué hace el tope con el montículo?** El nodo que llega a c_i no se reinserta. Por eso inserciones = extracciones − nodos en su tope, y por eso el montículo solo se achica: la cota O(N + B lg N) se mantiene.
- **¿Y si los topes no alcanzan para B?** Se gastan Σ c_i y sobra el resto. No es un error.
- **¿Sigue siendo óptimo con topes?** Sí: cada u_i cortada en c_i sigue siendo cóncava, y la fuerza bruta lo comprueba en instancias pequeñas.

_Última actualización: 2026-11-04 · tope por nodo (x_i ≤ c_i)_
