# Guía de cambios rápidos (modo sustentación)

Recetas para los cambios que es probable que pidan en vivo. Cada receta dice dónde tocar, qué pasa con la complejidad y qué prueba correr.
Los lugares se indican por el comentario `# línea N del pseudocódigo` del código, que no cambia aunque se muevan las líneas del archivo.

| Cambio pedido | Dónde | Efecto en la complejidad | Verificar |
|---|---|---|---|
| Desempatar por el mayor índice | Ver receta 1 | Ninguno | `python -m pytest`; 3 pruebas cambian lo esperado |
| Mostrar cuántas llamadas a f se hicieron | Ya está: `llamadas_ganancia` en `salida.json`, en la traza y verificado contra la fórmula | Ninguno; confirma Θ(N·k) | Debe dar k·N − k(k−1)/2 |
| Contar las operaciones del montículo | Ya está: `extracciones` e `inserciones` en `reparto.py` | Ninguno | Deben valer B |
| Nueva familia de utilidad (por ejemplo, a·x/(1+x)) | `utilidades.py`: clase nueva con `valor`, `ganancia`, `revisar_forma` y `describir`, más un `if` en `crear_utilidad` | Ninguno si Δ sigue siendo O(1) | Prueba de creciente y cóncava |
| Mostrar que el voraz falla con una utilidad convexa | **Solo por llamada directa:** `repartir_presupuesto([1, 2], 2, {1: UtilidadTabla([1, 10]), 2: UtilidadTabla([3, 0])})` da 4 y el óptimo es 11. Por `ejecutar.py` esa entrada se rechaza sin correr los algoritmos (decisión 14): reporta `Δ(1) > Δ(0) (no es cóncava)` | — | `test_contraejemplo_convexo` |
| Restricción "≤ B" en vez de "= B" con Δ negativas | Ver receta 2 | Ninguno (a lo sumo B vueltas) | `python -m pytest`; agregar el caso con Δ negativas |
| Tope de presupuesto por nodo (x_i ≤ c_i) | Ver receta 3 | Ninguno (a lo sumo B vueltas y el montículo solo se achica) | `python -m pytest`; agregar el caso con topes |
| Variante (a): costos de participación con presupuesto | `seleccion.py`: elegir por Δ/costo; nueva restricción | Cambia la cota: ya no es 1 − 1/e (cobertura con presupuesto) | Pendiente de diseño |
| Cambiar el formato de entrada | Solo `entrada.py` (`instancia_desde_diccionario` y `_leer_nodo`) | Ninguno | Pruebas de `entrada.py` |
| Medir varias veces y tomar el mínimo | `ronda.py`, bloque "1. Ejecución medida" dentro de un ciclo | Ninguno | `test_ronda.py` |

Las recetas 1, 2 y 3 se aplicaron completas en copias del repositorio el 2026-11-02, y `python -m pytest` quedó en verde en cada copia con los cambios de pruebas que indican.

## Receta 1: desempatar por el mayor índice
1. `seleccion.py`, `# línea 6 del pseudocódigo`: cambiar `>` por `>=`. Como V se recorre en orden creciente, el último empatado gana.
2. `reparto.py`, `# línea 2 del pseudocódigo` (la lista H): guardar `(-utilidades[i].ganancia(0), -i)`.
3. `reparto.py`, `# línea 4 del pseudocódigo`: `menos_delta, menos_i = heapq.heappop(H)` y después `i = -menos_i`.
4. `reparto.py`, `# línea 6 del pseudocódigo`: `heapq.heappush(H, (-siguiente, -i))`.
5. Pruebas que cambian lo esperado:
   - `test_seleccion.py::test_empate_gana_el_menor_indice`: `S == [3, 2]`.
   - `test_seleccion.py::test_contraejemplo_el_voraz_no_es_exacto`: `S == [1, 3]` (el valor sigue en 5, porque Δ(2) y Δ(3) empatan).
   - `test_reparto.py::test_empate_gana_el_menor_indice`: el nodo es 2.
6. Las evidencias cambian: `contraejemplo_seleccion` da S = [1, 3] con la misma utilidad 27. Hay que regenerar `resultados/propios/` y actualizar los comentarios de desempate y la decisión 6.

**Complejidad:** ninguna. Solo cambia a quién favorece el empate.

## Receta 2: gastar a lo sumo B cuando Δ se vuelve negativa
1. `reparto.py`, justo antes de `# línea 4 del pseudocódigo`: `if -H[0][0] < 0: break`. `H[0]` es la raíz: se mira sin sacarla, en O(1). Así no queda una extracción sin su inserción.
2. `utilidades.py`, `UtilidadTabla.revisar_forma`: quitar la comprobación `Δ(x) < 0`, que hoy rechaza la entrada antes de llegar al algoritmo. La de concavidad se queda: el voraz sigue necesitándola.
3. `verificacion.py`, `verificar_reparto`: `suma == B` pasa a `suma <= B` (nombre "Σ x_i ≤ B"), y `extracciones == B == inserciones` pasa a `extracciones == suma == inserciones` (nombre "extracciones = inserciones = Σ x_i").
4. Pruebas que cambian en `test_verificacion.py`:
   - `test_tabla_mala_dentro_del_presupuesto_se_rechaza`: quitar `([1, -1], 2, ...)` y `([-1, -2], 1, ...)`.
   - `test_reparto_malo_se_detecta`: los nombres nuevos, y cambiar la fila `({1: 1, 2: 1}, 4, 3, 3, "Σ x_i = B")` por `({1: 2, 2: 2}, 7, 4, 4, "Σ x_i ≤ B")`.
5. Prueba nueva: P = 5, 2, −1, −3 y Q = 1, −1, −2, −3 con B = 4 da x = {1: 2, 2: 1}, utilidad 8, y 3 extracciones y 3 inserciones. Comparar además contra fuerza bruta sobre todos los presupuestos de 0 a B.

**Cuidado:** una tabla con Δ negativas debe traer al menos B ganancias. Después de la lista se asume Δ = 0, y un salto de −1 a 0 no es cóncavo: `[5, -1]` con B = 4 se rechaza con `Δ(2) > Δ(1)`. Log y raíz no cambian, porque con a > 0 nunca dan Δ negativa.

**Complejidad:** ninguna en el peor caso: a lo sumo B vueltas, y la revisión de la raíz es O(1).

## Receta 3: tope de presupuesto por nodo (x_i ≤ c_i)
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
