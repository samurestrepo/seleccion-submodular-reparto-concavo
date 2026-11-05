# Guía de cambios rápidos (modo sustentación)

Recetas para los cambios que es probable que pidan en vivo. Cada receta dice dónde tocar, qué pasa con la complejidad y qué prueba correr.
Los lugares se indican por el comentario `# línea N del pseudocódigo` del código, que no cambia aunque se muevan las líneas del archivo.

| Cambio pedido | Dónde | Efecto en la complejidad | Verificar |
|---|---|---|---|
| Desempatar por el mayor índice | Ver receta 1 | Ninguno en la ronda; el reparto solo suma ordenar S | `python -m pytest`; 7 pruebas cambian lo esperado |
| Mostrar cuántas llamadas a f se hicieron | Ya está: `llamadas_ganancia` en `salida.json`, en la traza y verificado contra la fórmula | Ninguno; confirma Θ(N·k) | Debe dar k·N − k(k−1)/2 |
| Contar las operaciones del montículo | Ya está: `extracciones` e `inserciones` en `reparto.py` | Ninguno | Sin topes deben valer B; con topes, extracciones = Σ x_i e inserciones = Σ x_i − nodos en su tope |
| Nueva familia de utilidad (por ejemplo, a·x/(1+x)) | `utilidades.py`: clase nueva con `valor`, `ganancia`, `revisar_forma` y `describir`, más un `if` en `crear_utilidad` | Ninguno si Δ sigue siendo O(1) | Prueba de creciente y cóncava |
| Mostrar que el voraz falla con una utilidad convexa | **Solo por llamada directa:** `repartir_presupuesto([1, 2], 2, {1: UtilidadTabla([1, 10]), 2: UtilidadTabla([3, 0])})` da 4 y el óptimo es 11. Por `ejecutar.py` esa entrada se rechaza sin correr los algoritmos (decisión 14): reporta `Δ(1) > Δ(0) (no es cóncava)` | — | `test_contraejemplo_convexo` |
| Restricción "≤ B" en vez de "= B" con Δ negativas | Ver receta 2 | Ninguno (a lo sumo B vueltas) | `python -m pytest`; agregar el caso con Δ negativas |
| Tope de presupuesto por nodo (x_i ≤ c_i) | **Ya está hecho** (decisión 28): `presupuesto_total_nodo` en la profesora, `tope` en el propio. Ver receta 3 | Ninguno (a lo sumo B vueltas y el montículo solo se achica) | `casos/propios/tope_activo.json` da x = 2 y 3, con 5 extracciones y 4 inserciones |
| Variante (a): costos de participación con presupuesto | `seleccion.py`: elegir por Δ/costo; nueva restricción | Cambia la cota: ya no es 1 − 1/e (cobertura con presupuesto) | Pendiente de diseño |
| Cambiar el formato de entrada | Solo `entrada.py`: `instancia_desde_diccionario` elige el formato, y `_leer_nodo` o `_instancia_de_la_profesora` lo leen | Ninguno | Pruebas de `entrada.py` |
| Otra función f submodular | Clase nueva con `estado_inicial`, `ganancia`, `agregar` y `valor`, y devolverla en `Instancia.crear_oraculo`. `seleccion.py` y `ronda.py` no cambian. Ejemplo: `red/influencia.py` | Las llamadas siguen en Θ(N·k); el tiempo depende del costo de cada llamada | Resta de valores, monotonía y submodularidad, como en `test_influencia.py` |
| Otra combinación de los pesos de influencia | `influencia.py`: `ganancia`, `agregar` y `valor`, los tres a la vez | Ninguno si cada llamada sigue tocando solo a v y sus vecinos | `test_influencia.py`; `test_bateria.py` cambia lo esperado |
| Medir varias veces | **Ya está hecho** (decisión 29): `_ejecucion_medida` en `ronda.py`, `REPETICIONES = 21` y `--repeticiones`. Se reporta la mediana. Para reportar otra medida, cambiar qué columna y qué línea leen `fila_resumen` y `a_texto`: `salida.json` ya trae el mínimo y el máximo | Ninguno en cada repetición; el tiempo total de la corrida se multiplica por R | `test_ronda.py` |

Las recetas 1 y 2 se volvieron a aplicar en copias el 2026-11-04, sobre el código con topes y con el formato de la profesora: fallan justo las pruebas que indican. La receta 3 ya está aplicada en el código.

## Receta 1: desempatar por el mayor índice
1. `seleccion.py`, `# línea 6 del pseudocódigo`: cambiar `>` por `>=`. Como V se recorre en orden creciente, el último empatado gana.
2. `reparto.py`, `# línea 2 del pseudocódigo` (la lista H): **los ids de la profesora son texto y `-"N01"` lanza `TypeError`**, así que se guarda la posición del id en S ordenado. Antes de H: `orden = sorted(S)` y `posicion = {v: p for p, v in enumerate(orden)}`. H guarda `(-utilidades[i].ganancia(0), -posicion[i])`, con el mismo filtro de topes.
3. `reparto.py`, `# línea 4 del pseudocódigo`: `menos_delta, menos_p = heapq.heappop(H)` y después `i = orden[-menos_p]`.
4. `reparto.py`, `# línea 6 del pseudocódigo`: `heapq.heappush(H, (-siguiente, -posicion[i]))`.
5. Pruebas que cambian lo esperado:
   - `test_seleccion.py::test_empate_gana_el_menor_indice`: `S == [3, 2]`.
   - `test_seleccion.py::test_contraejemplo_el_voraz_no_es_exacto`: `S == [1, 3]` (el valor sigue en 5, porque Δ(2) y Δ(3) empatan).
   - `test_reparto.py::test_empate_gana_el_menor_indice`: el nodo es 2.
   - `test_reparto.py::test_el_que_llega_a_su_tope_no_gana_el_empate_despues`: con mayor índice, el orden es otro.
   - `test_bateria.py::ESPERADOS`: las filas de `borde_B_cero`, `contraejemplo_seleccion` y `empates`.
6. Las evidencias cambian: `contraejemplo_seleccion` da S = [1, 3] con la misma utilidad 27. Hay que regenerar `resultados/propios/` y actualizar los comentarios de desempate y la decisión 6. El caso de la profesora no cambia: no tiene empates.

**Complejidad:** en la ronda, ninguna. El reparto suma O(k lg k) una sola vez, por ordenar S, y ese término queda absorbido por la selección. Si solo se usa el formato propio, de ids enteros, se puede guardar `-i` directamente, sin ordenar.

Esta receta se reescribió y se probó en una copia el 2026-11-04: con `-i` fallaba el caso de la profesora; con la posición, ese caso corre y solo fallan las 7 pruebas de arriba, que cambian lo esperado.

## Receta 2: gastar a lo sumo B cuando Δ se vuelve negativa
1. `reparto.py`, después de `if not H: break` y justo antes de `# línea 4 del pseudocódigo`: `if -H[0][0] < 0: break`. `H[0]` es la raíz: se mira sin sacarla, en O(1). Así no queda una extracción sin su inserción. Debe ir después del `if not H`, porque un montículo vacío no tiene raíz.
2. `utilidades.py`, `UtilidadTabla.revisar_forma`: quitar la comprobación `Δ(x) < 0`, que hoy rechaza la entrada antes de llegar al algoritmo. La de concavidad se queda: el voraz sigue necesitándola.
3. `verificacion.py`, `verificar_reparto`: `suma == esperado` pasa a `suma <= esperado` (nombre "Σ x_i ≤ mín(B, Σ c_i)"). El conteo ya está escrito con Σ x_i: no cambia.
4. Pruebas que cambian en `test_verificacion.py`:
   - `test_tabla_mala_dentro_del_presupuesto_se_rechaza`: quitar `([1, -1], 2, ...)` y `([-1, -2], 1, ...)`.
   - `test_reparto_malo_se_detecta`: cambiar la fila `({1: 1, 2: 1}, 4, 3, 3, "Σ x_i = mín(B, Σ c_i)")` por `({1: 2, 2: 2}, 7, 4, 4, "Σ x_i ≤ mín(B, Σ c_i)")`.
   - `test_reparto_con_topes_malo_se_detecta`: quitar las dos filas de "Σ x_i = mín(B, Σ c_i)", porque gastar de menos ya no es una falla.
5. Prueba nueva: P = 5, 2, −1, −3 y Q = 1, −1, −2, −3 con B = 4 da x = {1: 2, 2: 1}, utilidad 8, y 3 extracciones y 3 inserciones. Comparar además contra fuerza bruta sobre todos los presupuestos de 0 a B.

**Cuidado:** una tabla con Δ negativas debe traer al menos B ganancias. Después de la lista se asume Δ = 0, y un salto de −1 a 0 no es cóncavo: `[5, -1]` con B = 4 se rechaza con `Δ(2) > Δ(1)`. Log y raíz no cambian, porque con a > 0 nunca dan Δ negativa.

**Complejidad:** ninguna en el peor caso: a lo sumo B vueltas, y la revisión de la raíz es O(1).

## Receta 3: tope de presupuesto por nodo (x_i ≤ c_i). **Ya está hecho** (decisión 28)
Se aplicó el 2026-11-04. Queda como descripción de dónde está cada parte. Las diferencias con la receta original son: en la profesora, el tope sale de `presupuesto_total_nodo`, que debe ser entero ≥ 0 (`_exigir_tope`); la línea "cada x_i ≤ c_i" solo aparece si la instancia tiene topes; y el nombre del conteo es "extracciones = Σ x_i e inserciones = Σ x_i − nodos en su tope".

1. `entrada.py`: `Nodo` recibe `tope=None`; `_leer_nodo` lee el campo opcional `"tope"` (entero ≥ 0, con `_exigir_entero`); `Instancia.topes()` devuelve `{id: tope}` solo de los nodos que lo tienen.
2. `reparto.py`: agregar el parámetro `topes=None` a `repartir_presupuesto`, con `topes = topes or {}` y `sin_tope = float("inf")`.
   - `# línea 2 del pseudocódigo`: meter en H solo los nodos con `topes.get(i, sin_tope) > 0`.
   - Antes de `# línea 4 del pseudocódigo`: `if not H: break` (todos llegaron a su tope).
   - `# línea 6 del pseudocódigo`: reinsertar y contar la inserción solo si `x[i] < topes.get(i, sin_tope)`.
3. `ronda.py`: pasar `topes=instancia.topes()` a las dos llamadas de `repartir_presupuesto` y a `verificar_reparto`.
4. `verificacion.py`, `verificar_reparto`: agregar el parámetro `topes=None` y
   - comprobar x_i ≤ c_i;
   - cambiar `suma == B` por `suma == min(B, sum(topes.get(i, B) for i in S))` (nombre "Σ x_i = mín(B, Σ c_i)");
   - cambiar el conteo por `extracciones == suma` e `inserciones == suma − (nodos con 0 < c_i = x_i)`, porque el nodo que llega a su tope no vuelve al montículo.
5. Pruebas que cambian en `test_verificacion.py::test_reparto_malo_se_detecta`: solo los dos nombres nuevos.
6. Pruebas nuevas: tope 2 con B = 3 da extracciones 3 e inserciones 2; topes que no alcanzan (c = 2 y 0, B = 9) dan x = {1: 2, 2: 0}; un tope negativo es `ErrorDeFormato`; comparar contra fuerza bruta restringida a x_i ≤ c_i.

**Complejidad:** sigue en O(N + B lg N): a lo sumo B vueltas, y el montículo solo se achica. El voraz sigue siendo óptimo, porque cada u_i truncada en c_i sigue siendo cóncava.

**Si Σ c_i < B:** el montículo se vacía, el ciclo termina y el sobrante queda sin gastar. No se le da a otro nodo, ni es una falla: la verificación exige Σ x_i = mín(B, Σ c_i).
