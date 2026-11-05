# Ficha: `red/entrada.py`

## Para qué existe
Lee un caso desde un archivo JSON y lo convierte en una `Instancia`. Reconoce dos formatos: el de la profesora y el propio. Es el **único** archivo que conoce los formatos.

## Funciones públicas
| Función | Recibe | Devuelve | Complejidad (tiempo · espacio) |
|---|---|---|---|
| `leer_instancia(ruta)` | ruta de un .json (UTF-8, con o sin BOM) | `Instancia` (nombre = nombre del archivo) | formato propio: O(N + M + ΣL) · O(N + M + ΣL); de la profesora: O(N + A) · O(N + A) (más ordenar los nodos) |
| `instancia_desde_diccionario(datos, nombre)` | contenido ya leído | `Instancia` | igual |
| `nombre_del_caso(ruta)` | ruta | nombre del archivo sin `.json` (en mayúsculas o minúsculas) | O(largo de la ruta) |
| `Instancia.ids()`, `.conjuntos()`, `.utilidades()`, `.N` | — | ids en orden, id → C_v, id → u_i, número de nodos | O(N) |
| `Instancia.crear_oraculo()` | — | un oráculo **nuevo**, con los contadores en cero: influencia si hay grafo; si no, cobertura | O(N) |
| `Instancia.numero_aristas()` | — | aristas del grafo (0 si el formato no trae grafo) | O(N) |
| `Instancia.topes()` | — | id → c_i, solo de los nodos que tienen tope | O(N) |

M = total de elementos listados en los "cubre". L = largo de cada tabla de ganancias. A = número de aristas.

Además, `Instancia.vecinos` (id → {vecino: peso}) y `Instancia.variantes` (`numero_rondas` y `presupuesto_costos_participacion_por_ronda`) valen `None` en el formato propio. `Nodo.costo_participacion` y `Nodo.presupuesto_total` también. `Nodo.tope` es c_i; `None` significa sin tope.

## Cómo funciona
`instancia_desde_diccionario` revisa que la raíz sea un objeto. **Si tiene "parametros", es el formato de la profesora; si no, es el propio**, que no cambió en nada.

**Formato propio:**
1. Revisa que existan `k`, `B` y `nodos`, y que k y B sean enteros.
2. `_leer_nodo` revisa cada nodo: que sea un objeto, que traiga `id`, `cubre` (lista, sin listas ni objetos adentro) y `utilidad` (objeto), y construye la utilidad con `crear_utilidad`, que exige `a` finito y > 0 y ganancias finitas.
3. Ordena los nodos por id: ese es el "orden creciente de índice" que recorre el voraz.

**Formato de la profesora** (`_instancia_de_la_profesora`):
1. Lee `parametros`: k ← `cupo_participantes_por_ronda_k`, B ← `presupuesto_ruido_por_ronda_B`. Guarda en `variantes` lo que solo se reporta.
2. `_leer_nodo_profesora` lee cada nodo: u_i = `UtilidadLog(coeficiente_utilidad)` (decisión 25). `cubre` queda vacío, `costo_participacion` se guarda sin aplicarse (decisión 26), y `presupuesto_total_nodo` se guarda y es el tope del nodo (decisión 28).
3. Revisa que `numero_nodos` coincida con la lista.
4. `_leer_grafo` convierte las aristas en id → {vecino: peso}, con cada arista en sus dos puntas, porque el grafo no es dirigido.

Es `ErrorDeFormato` si: falta un campo; `numero_nodos` no coincide con la lista; una arista nombra un nodo inexistente, es un lazo (u = v) o está repetida (también {u, v} y {v, u}); un valor no es numérico (incluye `true`, NaN e Infinity); un `id` no es texto; un entero no es entero; el coeficiente no es > 0 (decisión 27); `presupuesto_total_nodo` no es un entero ≥ 0 (decisión 28). Un campo `tope` en este formato no se lee. Un peso fuera de [0, 1] **no** es error de forma, y unos ids repetidos tampoco: los revisa `verificacion.py`, para que queden en la traza.

En los dos formatos, si algo no cuadra lanza `ErrorDeFormato` con un mensaje que dice qué campo falla. Eso incluye un archivo que no es UTF-8, que no es JSON, o que trae un entero o un anidamiento que Python no puede interpretar. Si el archivo no se puede abrir, sale `OSError`, que atiende `ejecutar.py`.

## Por qué así
- Revisa la **forma** y que los números de las utilidades sirvan. Las restricciones del problema (k < N, concavidad, ids únicos) las revisa `verificacion.py`, para que queden escritas en la traza.
- **`a` inválido es error de forma** (decisión 17), aunque "a > 0" sea también una condición del problema: un `a` que no es un número finito positivo ni siquiera define una utilidad de la familia. El motivo igual queda en la traza (decisión 22).
- **BOM:** es la marca invisible que algunos editores de Windows agregan al inicio de un archivo UTF-8. Se lee con `utf-8-sig`, que la acepta si está y no exige que esté.
- **Los ids de la profesora se conservan como texto.** Con ceros a la izquierda ("N01", …, "N15"), el orden de texto coincide con el numérico, y el desempate por menor índice no cambia. Sin ceros, "N10" iría antes que "N2": ahí mandaría el orden de texto (`test_sin_ceros_a_la_izquierda_manda_el_orden_de_texto`). `reparto.py` tampoco cambia: los compara en la pareja (−Δ, id) igual que a los enteros.
- **`crear_oraculo` vive aquí** porque esta clase es la que sabe de qué formato vino. Así `ronda.py` no pregunta por el tipo, y cada una de sus tres ejecuciones tiene sus contadores en cero.
- **`_es_numero_finito` se importa de `utilidades.py`** para no duplicar la misma regla (decisión 17).
- **El tope (decisión 28):** en la profesora sale de `presupuesto_total_nodo`; en el propio, del campo opcional `tope`. `_exigir_tope` pide un entero ≥ 0 en los dos, porque x_i es entero: con 18.5, la condición x_i < c_i dejaría llegar a 19. Por lo mismo, 18.0 también se rechaza, igual que k y B. El tope es lo que le queda al nodo para todo el proyecto, y en una ronda lo puede gastar completo.

## Formato de la profesora
```json
{"parametros": {"numero_nodos": 2, "numero_rondas": 3, "cupo_participantes_por_ronda_k": 1,
                "presupuesto_ruido_por_ronda_B": 30, "presupuesto_costos_participacion_por_ronda": 24},
 "grafo": [{"u": "N01", "v": "N02", "peso_influencia": 0.25}],
 "nodos": [{"id": "N01", "coeficiente_utilidad": 8.5, "presupuesto_total_nodo": 18, "costo_participacion": 3},
           {"id": "N02", "coeficiente_utilidad": 10.2, "presupuesto_total_nodo": 18, "costo_participacion": 5}]}
```

## Formato propio (provisional, informe 6.5)
```json
{"k": 2, "B": 4, "nodos": [
  {"id": 1, "cubre": ["a", "b", "c"], "utilidad": {"tipo": "log", "a": 9.0}, "tope": 3},
  {"id": 2, "cubre": ["c", "d"], "utilidad": {"tipo": "raiz", "a": 7.0}},
  {"id": 3, "cubre": ["d", "e"], "utilidad": {"tipo": "tabla", "ganancias": [6, 3, 1]}}]}
```

## Cómo modificarlo
- **Llega otro formato:** agregar otra rama en `instancia_desde_diccionario`, con su función de lectura, para producir la misma `Instancia` (y cambiar `leer_instancia` si no es JSON). Agregar un caso de ejemplo y una prueba en `test_entrada.py`. Si f cambia, también `crear_oraculo`.
- **Un campo opcional por nodo:** leerlo en `_leer_nodo` y guardarlo en `Nodo`, como `tope`.
- **Descontar el presupuesto ronda a ronda (variante b):** el tope de cada ronda sería `presupuesto_total` menos lo ya gastado. `Nodo` ya guarda los dos campos por separado.

## Pruebas
`pruebas/test_entrada.py`: lee el ejemplo del informe y ordena por id; rechaza formatos inválidos, incluidos los que antes tumbaban el programa (raíz, nodo o utilidad que no son objetos, `cubre` con listas); coeficientes y ganancias inválidos; archivos en latin-1, mal escritos, vacíos o con anidamiento sin fin; acepta BOM; nombre del caso con `.json` y `.JSON`. `pruebas/test_ejecutar.py` comprueba el efecto en un lote completo.

Formato de la profesora, en `pruebas/test_entrada.py`: el archivo oficial se lee bien (N = 15, k = 5, B = 30, 105 aristas); falta cada campo de cada nivel; `numero_nodos` no coincide; aristas con nodo inexistente, lazo o repetidas en los dos sentidos; cada valor no numérico (cadena, `null`, `true`, lista, objeto, NaN, Infinity, 10⁴⁰⁰); tipos que no deben tumbar el programa; un peso fuera de rango no es error de forma; `crear_oraculo` da el tipo correcto y uno nuevo cada vez.

Topes, en `pruebas/test_entrada.py`: `tope` es opcional en el formato propio; sin él, `topes()` queda vacío; un tope inválido (negativo, con decimales, texto, `true`, `null`, lista, NaN) es `ErrorDeFormato`; en la profesora el tope es `presupuesto_total_nodo`, acepta 0, rechaza −1, 18.5 y 18.0, e ignora un campo `tope`.

## Preguntas probables en la sustentación
- **¿Qué hay que cambiar si el formato es otro?** Este archivo, y un oráculo nuevo si f es otra; los algoritmos reciben ids, un oráculo y utilidades, no el JSON.
- **¿Qué pasa con un archivo malo?** Lanza `ErrorDeFormato`; `ejecutar.py` lo reporta como `[ERROR]` y sigue con los demás.
- **¿Cómo distingue los dos formatos?** Si el objeto tiene "parametros", es el de la profesora; si no, es el propio.
- **¿Por qué un peso de 1.5 no es error de forma?** Porque es un número bien escrito que no cumple una restricción del problema: lo reporta la verificación de entrada, igual que la concavidad, y el caso no corre.
- **¿Qué pasa con el desempate si los ids son texto?** Con ceros a la izquierda, el orden de texto coincide con el numérico.

_Última actualización: 2026-11-04 · topes por nodo; formato de la profesora, `crear_oraculo`, `numero_aristas`_
