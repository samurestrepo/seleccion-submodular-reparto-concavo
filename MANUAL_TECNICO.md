# Manual técnico — Proyecto Red (G2), entrega final

Versión: entrega final (rama `main`). Las secciones 1 a 7 describen la solución base de la primera entrega (etiqueta `primera-entrega`; informe en `entregables/primera_entrega/1_Informe_Primera_Entrega_G2.pdf`), que no cambió de lógica. La entrega final agrega los campos opcionales del formato propio (sección 3), los experimentos de tiempo (sección 8), las variantes (a), (b) y (c) (sección 9) y las tablas de la cota (sección 10). Los textos del informe final están en `entregables/entrega_final/secciones/`.

Solución base: selección de nodos (Parte 2) y reparto de presupuesto (Parte 1).
Las demostraciones (NP-dureza, eficiencia) están en el informe; este manual describe el código. Cuando el manual cita una sección del informe, dice de cuál: la numeración del informe de la primera entrega y la del informe final no coinciden.

## 1. Algoritmos

### 1.1 Parte 2 — SELECCIONAR-NODOS (voraz aproximado) · `red/seleccion.py`
En k pasos agrega al equipo S el nodo de mayor ganancia marginal Δ(v | S). Empates: el menor índice. El voraz no conoce f: se la pide a un oráculo con la interfaz `estado_inicial`, `ganancia`, `agregar` y `valor`. Con cobertura (formato propio), Δ(v | S) = |C_v ∖ cub(S)|. Con influencia (formato de la profesora), Δ(v | S) = a_v·q_v + Σ_{w vecino de v} a_w·p_vw·q_w.

| Aspecto | Detalle |
|---|---|
| Operación básica | una evaluación de Δ (llamada al oráculo) |
| Conteo | k·N − k(k−1)/2, exacto y para toda entrada; entre kN/2 y kN ⇒ **Θ(N·k)** en mejor, peor y promedio |
| Tiempo con cobertura | O(k·(N + M)), con M = Σ \|C_v\|. El N pesa porque cada paso recorre V; si ningún C_v es vacío, N ≤ M y queda O(k·M) |
| Tiempo con influencia | O(k·(N + A)), con A = \|E\|, el número de aristas (en el informe se escribe \|E\|): cada llamada cuesta O(1 + grado(v)). Con grafo completo, O(k·N²) |
| Espacio adicional | O(k) más el estado del oráculo (O(\|U\|) con cobertura, O(N) con influencia) sin traza; la ejecución con traza guarda además los Δ de cada paso, Θ(N·k) |
| Precondición | El modelo exige 1 ≤ k < N, y lo comprueba la verificación de entrada. El algoritmo por sí solo funciona con 1 ≤ k ≤ \|V\|, con V ordenado y sin repetidos. La valida la ronda; el algoritmo no la comprueba, para seguir el pseudocódigo |
| Garantía | f(S) ≥ (1 − 1/e)·OPT (Nemhauser, Wolsey y Fisher, 1978). Las dos f son monótonas, submodulares y con f(∅) = 0 |

### 1.2 Parte 1 — REPARTIR-PRESUPUESTO (voraz óptimo con montículo) · `red/reparto.py`
Entrega hasta B unidades una por una; cada unidad va al nodo cuya siguiente unidad aporta más. Montículo de máximos simulado con `heapq` (de mínimos) guardando parejas (−Δ_i(x_i), i). Empates: el menor índice. Un nodo que llega a su tope c_i no vuelve al montículo; si todos llegan, el ciclo termina y el sobrante queda sin gastar.

| Aspecto | Detalle |
|---|---|
| Construir el montículo | O(N) (`heapify`) |
| Ciclo | B vueltas, cada una con un `heappop` y un `heappush` de O(lg N). Con topes, mín(B, Σ c_i) vueltas, y quien llega a su tope no hace `heappush` |
| Tiempo | peor caso **O(N + B lg N)**, también con topes. Sin topes y con `heapq`, **Θ(N + B(1 + lg N))** para toda entrada: `heappop` siempre baja hasta una hoja, así que no hay un mejor caso más barato. El 1 cubre N = 1: lg 1 = 0, pero el ciclo igual da B vueltas |
| Espacio | Θ(N) |
| Precondiciones | B ≥ 0, S sin repetidos, c_i entero ≥ 0, u_i crecientes y cóncavas. Las valida la ronda; el algoritmo no las comprueba, para seguir el pseudocódigo |
| Optimalidad | por concavidad de las u_i (argumento de intercambio, entrega posterior) |

Dentro de una ronda, N de la Parte 1 es k (los nodos elegidos).

## 2. Estructura del código

| Archivo | Responsabilidad |
|---|---|
| `ejecutar.py` | Línea de comandos: casos → ronda → evidencias |
| `red/entrada.py` | Leer y validar la forma del JSON en los dos formatos; único archivo que los conoce; crea el oráculo que corresponde |
| `red/utilidades.py` | Familias u_i (log, raiz, tabla) con Δ en O(1) |
| `red/cobertura.py` | Oráculo f de cobertura (formato propio) y contadores de llamadas |
| `red/influencia.py` | Oráculo f de cobertura por influencia (formato de la profesora) y contadores de llamadas |
| `red/seleccion.py` | Parte 2 |
| `red/reparto.py` | Parte 1 |
| `red/verificacion.py` | Restricciones de entrada y salida |
| `red/traza.py` | Paso a paso en texto y JSON |
| `red/ronda.py` | Orquesta la ronda y mide tiempos |
| `red/generador.py` | Instancias sintéticas con semilla, en los dos formatos |
| `red/exacto.py` | Parte 2, referencia: fuerza bruta con C(N, k) evaluaciones (no entra a la ronda) |
| `red/pd_reparto.py` | Parte 1, referencia: programación dinámica Θ(N·B²) (no entra a la ronda) |
| `red/variante_costos.py` | Variante (a): costos de participación (sección 9.1) |
| `red/variante_rondas.py` | Variante (b): T rondas con nodos que fallan (sección 9.2) |
| `red/variante_vecinos.py` | Variante (c): vecinos que alteran la utilidad, modelos c1 y c2 (sección 9.3) |
| `scripts/experimentos.py` | Experimentos de tiempo, series a–m (sección 8) |
| `scripts/tabla_cota.py`, `tabla_cota_variante_a.py`, `tabla_cota_variante_c.py` | Aproximados contra el óptimo exacto (sección 10) |

Flujo de una ronda:
```
leer_instancia → verificar_entrada → seleccionar_nodos (Parte 2) → repartir_presupuesto (Parte 1 sobre S)
              → verificar_seleccion / verificar_reparto → traza y tiempos → archivos
```
Cada archivo tiene su ficha en `docs/modulos/` con su complejidad, cómo modificarlo y preguntas de sustentación.

## 3. Formatos

`red/entrada.py` reconoce dos formatos de entrada: si el objeto tiene `"parametros"`, es el de la profesora (3.1); si no, es el propio (3.1.1). Los dos producen la misma salida (3.2).

### 3.1 Entrada: formato de la profesora
```json
{
  "parametros": {
    "numero_nodos": 2,
    "numero_rondas": 3,
    "cupo_participantes_por_ronda_k": 1,
    "presupuesto_ruido_por_ronda_B": 30,
    "presupuesto_costos_participacion_por_ronda": 24
  },
  "grafo": [{"u": "N01", "v": "N02", "peso_influencia": 0.25}],
  "nodos": [
    {"id": "N01", "coeficiente_utilidad": 8.5, "presupuesto_total_nodo": 18, "costo_participacion": 3},
    {"id": "N02", "coeficiente_utilidad": 10.2, "presupuesto_total_nodo": 18, "costo_participacion": 5}
  ]
}
```
| Campo | Uso en la solución base |
|---|---|
| `numero_nodos` | se comprueba contra la lista de nodos |
| `cupo_participantes_por_ronda_k` | k |
| `presupuesto_ruido_por_ronda_B` | B |
| `grafo` | aristas {u, v} no dirigidas, con p_vw = `peso_influencia`; definen f. El peso debe estar en [0, 1] |
| `id` | texto. Con ceros a la izquierda, el orden de texto coincide con el numérico y define los desempates. Sin ceros, "N10" iría antes que "N2" |
| `coeficiente_utilidad` | a de u_i y a_w de f. Debe ser un número finito > 0 |
| `numero_rondas`, `costo_participacion`, `presupuesto_costos_participacion_por_ronda` | de las variantes (b) y (a): **se leen y se reportan** en `informativo`; la solución base no los aplica. Con `--variante a`, `costo_participacion` es c(v) y `presupuesto_costos_participacion_por_ronda` es L (sección 9.1); con `--variante b`, `numero_rondas` es T (sección 9.2) |
| `presupuesto_total_nodo` | tope c_i de x_i ≤ c_i. Entero ≥ 0 |

**Supuestos de modelado adoptados** (se declaran en el informe de la primera entrega, sección 6.9, y en el informe final, sección 13):

- f(S) = Σ_w a_w · (1 − Π_{v∈S} (1 − p_vw)), con p_vw = 0 si no hay arista y p_ww = 1.
- u_i(x) = `coeficiente_utilidad` · ln(1 + x).
- La solución base corre una sola ronda.
- `presupuesto_total_nodo` es lo que le queda al nodo para todo el proyecto, y en una ronda lo puede gastar completo. En la variante (b) se descuenta ronda a ronda (sección 9.2).

Es error de forma (`[ERROR]`): falta un campo; `numero_nodos` no coincide con la lista; una arista nombra un nodo inexistente, es un lazo o está repetida ({u, v} y {v, u} son la misma); un valor no es numérico (incluye `true`, `NaN` e `Infinity`); un id no es texto; k, B, `numero_nodos` o `numero_rondas` no son enteros; un coeficiente no es > 0; `presupuesto_total_nodo` no es un entero ≥ 0. Un peso fuera de [0, 1] no es error de forma, sino una verificación de entrada que falla (`[FALLA]`), y el caso no corre.

### 3.1.1 Entrada: formato propio (batería propia; informe de la primera entrega, 6.5)
```json
{
  "k": 2,
  "B": 4,
  "nodos": [
    {"id": 1, "cubre": ["a", "b", "c"], "utilidad": {"tipo": "log",  "a": 9.0}},
    {"id": 2, "cubre": ["c", "d"],      "utilidad": {"tipo": "raiz", "a": 7.0}},
    {"id": 3, "cubre": ["d", "e"],      "utilidad": {"tipo": "log",  "a": 6.0}}
  ]
}
```
| Campo | Significado |
|---|---|
| `k` | nodos a seleccionar (1 ≤ k < N) |
| `B` | unidades de presupuesto (entero ≥ 0) |
| `id` | entero único; define el orden y los desempates |
| `tope` | opcional: tope c_i de x_i ≤ c_i, entero ≥ 0. Sin él, el nodo no tiene tope (en la variante (b), sin tope el restante arranca en B) |
| `rondas` | opcional (variante b): T, entero ≥ 1. Sin él, T = 1. Solo se usa con `--variante b` |
| `costo` | opcional, por nodo (variante a): c(v), número finito > 0. Solo se usa con `--variante a`; si se pide la variante y falta o es ≤ 0, el caso se rechaza |
| `presupuesto_costos` | opcional, en la raíz (variante a): L, número finito ≥ 0. Solo se usa con `--variante a`; si se pide la variante y falta o es < 0, el caso se rechaza |
| `cubre` | elementos que aporta el nodo (cadenas o números); definen f como cobertura |
| `utilidad` | `{"tipo": "log", "a": a}` → a·ln(1 + x); `{"tipo": "raiz", "a": a}` → a·√x; `{"tipo": "tabla", "ganancias": [Δ(0), Δ(1), …]}` → ganancias explícitas por unidad (para ejemplos y contraejemplos). `a` debe ser un número finito con a > 0, y las ganancias, números finitos. Valores como `true`, `"3"`, `NaN` o `Infinity` son error de forma |

El archivo debe estar en UTF-8, con o sin BOM. En una carpeta, la extensión `.json` se reconoce sin distinguir mayúsculas. El nombre del caso es el del archivo sin esa extensión.

### 3.2 Salida
Por cada caso se escribe `<salida>/<caso>/salida.json`, `traza.json` y `traza.txt`. Además, `<salida>/resumen.csv` tiene una fila por caso.

**`salida.json`**
| Campo | Contenido |
|---|---|
| `caso` | nombre del archivo, sin `.json` |
| `entrada` | N, k, B |
| `seleccion` | `S` (en el orden en que se eligió), `valor` = f(S), `llamadas_ganancia`, `llamadas_valor` |
| `reparto` | `x` (id → unidades), `utilidad` = Σ u_i(x_i), `extracciones`, `inserciones` |
| `tiempos_segundos` | `repeticiones` (R), y para `seleccion` y `reparto`: `mediana`, `minimo` y `maximo` de las R repeticiones (solo el algoritmo) |
| `verificaciones` | listas `entrada`, `seleccion`, `reparto`, `ejecucion`, cada una con nombre, cumple y detalle |
| `todas_cumplen` | true si todas las verificaciones cumplen |
| `informativo` | solo en el formato de la profesora, y solo si el caso corrió. `variante_a`: `suma_costos_de_S`, `presupuesto_costos_participacion_por_ronda` y `nota`. `variante_b`: `numero_rondas` y `nota`. La nota dice "no se aplica en la solución base". **No es una verificación ni entra en `todas_cumplen`** |

`valor` y `utilidad` son números reales con toda su precisión; en el formato propio, `valor` es un entero.

**`traza.json`** tiene `pasos_seleccion` (por paso: `paso`, `aportes` con el Δ de cada candidato, `elegido`, `ganancia_elegido`, `valor_despues`) y `unidades_reparto` (por unidad: `unidad`, `nodo`, `ganancia`).

**`traza.txt`** es el reporte legible, con estas secciones en orden: encabezado (caso, N, k, B); verificación de la entrada; Parte 2 (Δ de cada candidato, elegido y f(S) por paso, y el resultado con las llamadas a Δ); Parte 1 (nodo y Δ de cada unidad, y el reparto con la utilidad total); verificaciones de Parte 2, Parte 1 y Ejecución; `Informativo` (solo en el formato de la profesora); mediana de los tiempos y R; y una línea final `TODAS LAS VERIFICACIONES: CUMPLEN` o `HAY FALLAS`. Muestra los números con 4 decimales; los valores exactos están en `salida.json`.

**Caso rechazado:** `salida.json` trae solo `caso`, `entrada`, `verificaciones.entrada` y `todas_cumplen = false`; `traza.json` trae las listas vacías y `motivo_rechazo`; `traza.txt` trae las verificaciones y el motivo. Si el archivo tiene forma inválida, N, k y B quedan en `null`. Si no se pudo ni abrir, no se escriben evidencias.

**`<salida>/resumen.csv`:** columnas `caso, N, k, B, S, f(S), utilidad_reparto, tiempo_seleccion_s, tiempo_reparto_s, minimo_seleccion_s, minimo_reparto_s, repeticiones, todas_cumplen`. S va separado por espacios, la utilidad con 6 decimales y los tiempos con 9: `tiempo_*` son las medianas y `minimo_*` los mínimos de las R repeticiones. **Para la gráfica de T(n) se usa el mínimo:** el ruido del sistema solo suma tiempo, así que el mínimo es la medición menos contaminada. Tiene una fila por caso de la **última corrida**, sin acumular. Un caso rechazado deja vacíos S, f(S), utilidad, tiempos, mínimos y repeticiones, con `todas_cumplen` en False. Si ya existía, se reemplaza y se avisa por consola. Dos archivos con el mismo nombre de caso (sin distinguir mayúsculas) son un error: corre el primero y el segundo no se ejecuta ni tiene fila.

### 3.3 Verificaciones
| Parte | Comprobación |
|---|---|
| Entrada | 1 ≤ k < N; B ≥ 0; ids únicos; cada u_i creciente y cóncava en {0, …, B}; solo con influencia, cada peso en [0, 1] |
| Parte 2 | S ⊆ V; sin repetidos; \|S\| ≤ k; valor acumulado = f(S) recalculada, con tolerancia 1e-9; llamadas = k·N − k(k−1)/2 |
| Parte 1 | x_i entero en [0, B]; si hay topes, x_i ≤ c_i; Σ x_i = mín(B, Σ c_i); utilidad finita e igual a Σ u_i(x_i) recalculada; extracciones = Σ x_i e inserciones = Σ x_i − nodos en su tope |
| Ejecución | todas las repeticiones dan el mismo S y el mismo reparto; la ejecución con traza da lo mismo que la medida |

La concavidad se revisa solo en las unidades que se pueden entregar: en log y raíz basta a > 0 (O(1)); en tabla, Δ(x) ≥ 0 si x < B y Δ(x + 1) ≤ Δ(x) si x + 1 < B (O(min(L, B))).

Si la entrada no cumple sus restricciones, los algoritmos no se ejecutan y la traza lo reporta con el motivo.

## 4. Ejecución paso a paso
1. Instalar Python 3.11+. La ejecución usa solo la biblioteca estándar de Python; `pytest` es solo para las pruebas (`python -m pip install -r requirements-dev.txt`). En Windows el comando puede ser `py` en lugar de `python`.
2. Abrir una terminal en la raíz del repositorio.
3. `python -m pytest` → todas las pruebas deben pasar.
4. `python ejecutar.py casos/profesora --salida resultados/profesora` (o cualquier archivo o carpeta de casos).
5. Revisar `resultados/profesora/resumen.csv` y la carpeta de cada caso.
6. Variantes (sección 9), siempre con una carpeta de salida en `resultados/variantes/`; **no** se escribe sobre `resultados/profesora/`:
   - (a) `python ejecutar.py casos/profesora --variante a --salida resultados/variantes/a_profesora`
   - (b) `python ejecutar.py casos/profesora --variante b --modo-fallo transitorio --prob-fallo 0.2 --semilla-fallos 0 --salida resultados/variantes/b_profesora_transitorio` (y lo mismo con `--modo-fallo permanente` y `b_profesora_permanente`); `--rondas T` cambia el número de rondas del archivo.
   - (c1) `python ejecutar.py casos/profesora --variante c1 --beta 0.2 --limite-repartos 302792 --salida resultados/variantes/c1_profesora`
   - (c2) `python ejecutar.py casos/profesora --variante c2 --beta 0.2 --limite-repartos 302792 --salida resultados/variantes/c2_profesora`
7. Experimentos (sección 8): `python scripts/experimentos.py` (todas las series) o `python scripts/experimentos.py --series i j k l m` (solo las de las variantes).
8. Tablas de la cota (sección 10): `python scripts/tabla_cota.py`, `python scripts/tabla_cota_variante_a.py` y `python scripts/tabla_cota_variante_c.py`.

**Opciones de `ejecutar.py`.**

| Opción | Para qué | Por omisión |
|---|---|---|
| `--salida CARPETA` | carpeta de evidencias | `resultados` |
| `--repeticiones R` | repeticiones medidas; se reporta la mediana | 21 |
| `--variante a\|b\|c1\|c2` | aplica una variante; sin ella, la solución base | ninguna |
| `--modo-fallo transitorio\|permanente` | (b) el nodo falla solo esa ronda, o no vuelve | `transitorio` |
| `--prob-fallo q` | (b) probabilidad de fallo de cada nodo antes de cada ronda | 0.2 |
| `--semilla-fallos s` | (b) semilla del sorteo de fallos | 0 |
| `--rondas T` | (b) número de rondas; manda sobre `numero_rondas` o `rondas` del archivo | el del archivo, o 1 |
| `--beta β` | (c1, c2) intensidad del efecto de los vecinos, número finito ≥ 0 | 0.2 |
| `--limite-repartos L` | (c1, c2) máximo de repartos que enumera el exacto de referencia; si hay más, no corre (no es falla) | 200000 |

Las opciones de una variante se ignoran si no se pide esa variante.

## 5. Casos de prueba utilizados
**Caso oficial:** `casos/profesora/entrada_G2_red_15_nodos.json` (N = 15, k = 5, B = 30), con evidencias en `resultados/profesora/`. Resultado: S = N11, N14, N09, N15, N13; f(S) ≈ 145.5795; 65 llamadas a Δ; reparto 5, 7, 7, 6, 5; U ≈ 88.5640; 30 extracciones y 30 inserciones. Todas las verificaciones cumplen. Depende de los supuestos de la sección 3.1. El informe de la primera entrega reporta estos mismos valores en su sección 6.9, y el informe final en su sección 10.1.1. Las corridas de la docente con cada variante están en `resultados/variantes/` (sección 9).

**Batería propia:** 14 casos válidos y 3 inválidos, descrita caso por caso (qué comprueba, esperado y obtenido) en `casos/CATALOGO.md`, con evidencias en `resultados/propios/` y `resultados/invalidos/`.

`pruebas/test_bateria.py` comprueba automáticamente que los válidos cumplen todas las verificaciones, que los inválidos se rechazan y que el caso oficial da esos valores.

## 6. Medición de tiempos
Se usa `time.perf_counter()` alrededor de cada algoritmo, en ejecuciones **sin traza**; no incluye lectura, escritura, traza ni verificaciones. La ejecución medida se repite R veces (21 por omisión, `--repeticiones`), cada una con un oráculo nuevo, y se reporta la **mediana** de cada parte; `salida.json` trae también el mínimo y el máximo. Se verifica que todas las repeticiones den el mismo S y el mismo reparto. Luego se ejecuta otra vez con traza para la evidencia y se comprueba que coincide. En casos muy pequeños los tiempos son de microsegundos y tienen ruido del sistema: la mediana no se deja arrastrar por una repetición lenta, pero no resiste una ráfaga que cubra más de la mitad de las repeticiones (por eso para T(n) se usa el mínimo, que trae `salida.json` y `resumen.csv`: el ruido del sistema solo suma tiempo, así que el mínimo es la medición menos contaminada). La comparación contra T(n), con instancias de tamaño creciente, está en la sección 8.

## 7. Limitaciones
- El archivo de la docente no dice cómo usar sus datos: f, u_i y el alcance de una ronda son supuestos de modelado (informe de la primera entrega, sección 6.9; informe final, sección 13), no confirmados todavía con la docente. Otro formato solo requiere cambiar `red/entrada.py`.
- La solución base no aplica `numero_rondas`, `costo_participacion` ni `presupuesto_costos_participacion_por_ronda`; las variantes (a) y (b) los aplican solo con `--variante` (sección 9).
- En la base el tope se aplica en una sola ronda y no se descuenta; descontarlo ronda a ronda es la variante (b) (sección 9.2). Si los topes de S suman menos que B, el sobrante queda sin gastar. La selección no mira los topes, así que puede elegir un nodo con tope 0.
- La concavidad se juzga hasta B, no hasta c_i: una tabla que se dañe entre c_i y B se rechaza, aunque esas unidades nunca se entreguen.
- Otra función submodular requiere solo otro oráculo con la misma interfaz y devolverlo en `Instancia.crear_oraculo`.
- Con influencia, f es real: un empate exacto en teoría podría romperse por el redondeo y no por el menor índice. En el caso oficial no hay empates (la menor brecha es 0.1037, medida con aritmética exacta).
- Con ids de texto sin ceros a la izquierda, manda el orden de texto ("N10" antes que "N2").
- La Parte 2 es aproximada: el voraz no siempre da el óptimo (ejemplo: `casos/propios/contraejemplo_seleccion.json` da 5 y el óptimo es 6).
- La Parte 1 solo es óptima si cada u_i es cóncava; si no lo es, la verificación de entrada lo reporta y la ronda no se ejecuta.
- El contraejemplo convexo de la Parte 1 solo se puede mostrar por llamada directa a `repartir_presupuesto`; por `ejecutar.py` esa entrada se rechaza sin correr los algoritmos.
- La verificación de entrada cuesta O(N + Σ min(L_i, B)) esperado, con L_i el largo de cada tabla, y O(N + A) con influencia; no afecta los tiempos reportados.
- Con coeficientes extremos (a cerca de 1e308) los valores se desbordan a infinito: el caso se reporta como FALLA en la verificación de la utilidad, y `salida.json` puede traer `Infinity`, que no es JSON estándar.
- La ejecución con traza guarda Θ(N·k + B) anotaciones; con instancias muy grandes, la traza y sus archivos pesan.
- La variante (a) depende del Supuesto ❓ de que L reemplaza a k (sección 9.1). La variante (b) depende de los Supuestos ❓ de la sección 9.2 y **optimiza cada ronda por separado**: la cota 1 − (1 − 1/k_r)^k_r vale ronda por ronda y no sobre las T rondas; planear las T rondas juntas (con fallos inciertos) es otro problema que no se resuelve. La variante (c) depende de los Supuestos ❓ de la sección 9.3 (solo cuentan los vecinos en S; necesita grafo, así que el formato propio se rechaza); en el modelo c2 el voraz **no es exacto** (contraejemplo de tres nodos) y su exacto por enumeración crece como C(B + k, k): en la docente (302792 repartos) solo corre si se sube `--limite-repartos`.

## 8. Experimentos
`scripts/experimentos.py` mide el tiempo de los algoritmos y lo contrasta con la T(n) del informe. Necesita `matplotlib` solo para las gráficas (`python -m pip install -r requirements-dev.txt`). Desde la raíz del repositorio:

```
python scripts/experimentos.py
```

Las series a–h de la solución base son 8, con semilla 1 y 21 repeticiones: voraz de la Parte 2 con cobertura (a) y con influencia en grafo completo (b) y de grado medio 5 (c); reparto de la Parte 1 variando N (d) y B (e); fuerza bruta con k = 3 (f) y k = N/2 (g); y la programación dinámica de la Parte 1 (`red/pd_reparto.py`, solo referencia: Θ(N·B²), correcta aun con u no cóncavas) con N = 10 y B = 25 a 400 (h; su CSV agrega la columna `repeticiones`). Por serie escribe `resultados/experimentos/<serie>.csv` (columnas `n`, `N`, `k`, `B`, `densidad`, `semilla`, `t_min`, `t_mediana`, `conteo`, `T_teorica`, `cociente`) y dos gráficas PNG: t_min contra n con la curva c·T_teorica, y el cociente t_min / T_teorica. Se cronometra solo el algoritmo y se usa el mínimo (el de las gráficas). Con d y e juntas se ajusta además t_min ≈ a·N + b·B·lg N por mínimos cuadrados (columna `t_ajustado` y `ajuste_reparto.png`). Opciones: `--series a d` (solo algunas), `--sin-graficas` y `--repeticiones R`. Para generar instancias de influencia a mano: `python -m red.generador --N 50 --k 5 --B 100 --formato influencia --densidad 0.1 --semilla 1 --salida caso.json`.

**Series de las variantes (i a m, entrega final).** Se corren aparte, sin regenerar las a–h:

```
python scripts/experimentos.py --series i j k l m
```

(tarda unos 2 minutos; `i` corre dos series, `ic` e `im`). Mismo método: semilla 1, 21 repeticiones (5 si una pasa de 2 s; la columna `repeticiones` lo anota), mínimo para las gráficas, instancia y oráculo fuera del reloj. Todas usan instancias de influencia del generador.

| Serie | Qué mide | Varía | T teórica |
|---|---|---|---|
| ic, im | Variante (a): voraz por cociente y voraz modificado, L = 5N (todo cabe: peor caso), grado medio ~ 5 | N = 50 a 800 | N²·(1 + 2A/N) |
| j | Variante (a): enumeración parcial, L = 5N, grado ~ 5 | N = 8 a 18 | evaluaciones del peor caso · (1 + 2A/N), Θ(N⁵) |
| k | Variante (a): fuerza bruta con presupuesto, L = 5N (F = 2^N), grado ~ 5 | N = 8 a 16 | 2^N·(N + A) |
| l | Variante (b): `ejecutar_rondas` sin exacto, N = 100, k = 5, B = 100, q = 0,2 transitorio | T = 8 a 128 rondas | T·[2(k(N + A) + B lg k) + N] |
| m | Variante (c2): voraz unidad por unidad, N = 50, S del voraz base con m = 10 en grafo completo, β = 0,2 | B = 250 a 4000 | m + d(S) + B·(m + A_S) |

Los CSV agregan al final las columnas propias de cada serie (`L`, `A`, `A_S`, `d_S`, `beta`, `modo`, `q`, `semilla_fallos`, `repeticiones`). La consola imprime, además, la pendiente log-log contra n y contra T_teorica, la pendiente esperada (la de T_teorica) y el rango del cociente. Sin `--series` el script corre las 13 series por nombre (a–m), que dan 14 curvas y 14 CSV porque `i` se divide en `ic` e `im`, y regenera también las a–h.

**Máquina de las mediciones.** Las series i–m se corrieron el 2026-11-17 en un Intel Core i5-6300U a 2,40 GHz (2 núcleos, 4 hilos; caché L2 de 512 KB y L3 de 3 MB), 15,9 GB de RAM, Windows 10 Pro 10.0.19045 y Python 3.14.7 (CPython), con el reloj `time.perf_counter`. De las series a–h (2026-11-12) no quedó registro del equipo; se supone el mismo (**Supuesto ❓**). En otra máquina los tiempos absolutos cambian; lo que se compara con la teoría es el crecimiento (pendiente log-log y cociente t_min/T).

## 9. Variantes (entrega final)

Las variantes se piden con `--variante` en `ejecutar.py`; por omisión no se aplica ninguna y todo queda como en la solución base. Sus salidas van en `resultados/variantes/`; `resultados/profesora/` no se toca. Todo lo que depende de un supuesto no confirmado por la docente se marca **Supuesto ❓**.

### 9.1 Variante (a): costos de participación · `red/variante_costos.py`
Cada nodo v tiene un costo c(v) > 0 y hay un presupuesto de participación L. Se busca S que maximice f(S) con Σ_{v∈S} c(v) ≤ L. **Supuesto ❓:** esa restricción **reemplaza** a |S| ≤ k; no se usan las dos a la vez.

**Campos.** Formato de la profesora: c(v) = `costo_participacion`, L = `presupuesto_costos_participacion_por_ronda` (24 en el caso oficial). Formato propio: campo opcional `costo` por nodo y `presupuesto_costos` en la raíz; sin ellos, nada cambia. Cuando se pide la variante, un costo ausente o ≤ 0, o un L ausente o < 0, es una falla de entrada (`[FALLA]`, con el motivo en la traza).

**Ejecución.** `python ejecutar.py casos/profesora --variante a --salida resultados/variantes/a_profesora`. La Parte 2 pasa a ser el voraz modificado; el reparto de la Parte 1 no cambia (recibe el S elegido, con sus topes). `salida.json` trae además `variante` (nombre, L, algoritmo, supuesto) y, en `seleccion`, `costo`, `evaluaciones` y `origen`; la verificación «Σ c(S) ≤ L» reemplaza a «|S| ≤ k»; `traza.txt` muestra Δ/c de cada candidato que cabe. Las columnas de `resumen.csv` no cambian.

| Algoritmo | Qué hace | Evaluaciones de f (T) | Garantía |
|---|---|---|---|
| Fuerza bruta con presupuesto (`seleccionar_exacto_costos`, referencia) | búsqueda en profundidad por los subconjuntos en orden lexicográfico, con poda (si S no cabe, ningún superconjunto cabe); se niega si 2^N > 200000 | F = subconjuntos factibles ≤ 2^N; peor caso Θ(2^N), mejor (L < c_mín) 1 evaluación y Θ(N) | exacta (OPT) |
| Voraz por cociente (`voraz_por_cociente`) | en cada paso, entre los que todavía caben, el de mayor Δ(v \| S)/c(v); los que no caben se saltan sin evaluar | ≤ 1 + \|S\|·N − \|S\|(\|S\| − 1)/2, con \|S\| ≤ mín(N, ⌊L/c_mín⌋); peor caso 1 + N(N + 1)/2 = Θ(N²), mejor 1 y Θ(N) | ninguna constante: con un nodo barato de cociente apenas mayor que uno caro que ocupa todo L, la razón tiende a 0 |
| Voraz modificado (`voraz_modificado`, **el de la ronda**) | el mejor entre el cociente y el mejor nodo que cabe solo | las mismas del cociente: el mejor nodo solo sale de su paso 1 (f({v}) = Δ(v \| ∅)) | (1 − 1/e)/2 ≈ 0,316 (Khuller, Moss y Naor, 1999); **0,405** para f monótona y submodular con mochila (Tang et al., 2021), que es la que se aplica porque la f de influencia es submodular general |
| Enumeración parcial (`enumeracion_parcial`, referencia) | todos los factibles de tamaño ≤ 2 y, desde cada factible de tamaño 3, se completa con el cociente | O(N⁴ · mín(N, L/c_mín)) ⊆ O(N⁵); peor caso 1 + N + C(N, 2) + C(N, 3)·(1 + (N − 3)(N − 2)/2) | **1 − 1/e** (Sviridenko, 2004) |

Con influencia, cada `ganancia` cuesta O(1 + grado(v)) y cada `valor(S)` O(N + Σ_{v∈S}(1 + grado(v))): el cociente cuesta O(|S|·(N + A)) y la fuerza bruta O(F·(N + A)). Espacio O(N) en los cuatro, más el estado del oráculo. Empates: el menor índice en los voraces y el primer subconjunto lexicográfico en la fuerza bruta.

**Resultados** (`scripts/tabla_cota_variante_a.py` → `resultados/variantes/a_tabla_cota.csv`). Caso oficial con L = 24: OPT = 146,2714 (costo 23); el voraz modificado elige S = N05, N09, N14, N11, N15, N01 con f(S) = 145,9911, costo 21 ≤ 24 (razón 0,998, 74 evaluaciones) y el reparto da x = 4, 6, 6, 4, 5, 5 con U ≈ 95,9552; la enumeración alcanza el OPT (13117 evaluaciones); la fuerza bruta evalúa 4502 factibles. En 36 instancias aleatorias de influencia (N = 10 a 16, L = 12), la razón mínima del modificado fue 0,947 (cota 0,405) y la enumeración alcanzó el OPT en todas (cota 0,632). Ningún caso incumple su cota.

Referencias: Khuller, Moss y Naor (1999), *Information Processing Letters* 70(1), 39–45, doi:10.1016/S0020-0190(99)00031-9. Sviridenko (2004), *Operations Research Letters* 32(1), 41–43, doi:10.1016/S0167-6377(03)00062-2. Tang, Tang, Lim, Han, Li y Yuan (2021), *Proc. ACM Meas. Anal. Comput. Syst.* 5(1), art. 8, doi:10.1145/3447386.

### 9.2 Variante (b): T rondas con nodos que fallan · `red/variante_rondas.py`
La red entrena T rondas y antes de cada una algunos nodos fallan. Por ronda corren los mismos dos voraces de la solución base sobre los nodos que pueden participar, y el presupuesto de cada nodo se descuenta ronda a ronda. **Supuestos ❓** (la docente no ha dicho cómo fallan los nodos ni cómo se gasta `presupuesto_total_nodo` entre rondas):
- Cada nodo falla antes de cada ronda, de forma independiente, con probabilidad q (`--prob-fallo`, 0,2 por omisión; `random.Random(semilla)`, `--semilla-fallos` 0 por omisión). Modo **transitorio** (`--modo-fallo transitorio`, por omisión): falla solo esa ronda. Modo **permanente**: no vuelve. Con la misma semilla, los fallados de cada ronda coinciden en los dos modos.
- El tope de cada nodo es su **presupuesto restante**: empieza en `presupuesto_total_nodo` (o `tope`; sin tope, B) y se le descuenta lo que recibe en cada ronda; nunca queda negativo. (Consecuencia: un nodo sin tope recibe a lo sumo B en total; con B = 0 nadie puede participar.)
- Candidatos de la ronda: los nodos que no fallaron y tienen restante > 0. Se elige entre ellos con k_r = mín(k, |candidatos|): si son k o menos, participan todos; si no queda ninguno, la ronda es vacía y no es falla.
- Cada ronda se optimiza sola, con el mismo k y el mismo B; f se mide sobre el grafo completo, solo cambia quién se puede elegir. **Limitación:** no se planean las T rondas juntas (eso es planeación con incertidumbre, otro problema).

**Campos.** Formato de la profesora: T = `numero_rondas` (3 en el caso oficial), que **solo se aplica con `--variante b`**; tope inicial = `presupuesto_total_nodo`. Formato propio: campo opcional `rondas` (entero ≥ 1) y `tope` por nodo. `--rondas` manda sobre el archivo; sin ninguno, T = 1. T < 1 rechaza el caso.

**Ejecución.** `python ejecutar.py casos/profesora --variante b --modo-fallo permanente --prob-fallo 0.2 --semilla-fallos 0 --salida resultados/variantes/b_profesora_permanente` (y lo mismo con `transitorio`). `salida.json` trae `rondas`: por ronda, fallados, caídos, candidatos, k_r, S_r y f(S_r), el exacto (S*, OPT_r, evaluaciones), la razón f(S_r)/OPT_r y la cota 1 − (1 − 1/k_r)^k_r, el reparto y U_r, el presupuesto restante de todos los nodos tras la ronda, los tiempos (mediana de R) y las verificaciones; además `resumen` (Σ f(S_r), Σ U_r, rondas sin participantes) y las verificaciones globales (restante ≥ 0; en permanente, candidatos que nunca aumentan). `traza.txt` muestra cada ronda con su paso a paso. **`resumen.csv` trae una fila por ronda** (columnas distintas a las de la base). Con q = 0 y T = 1 se reproduce exactamente la solución base (mismo S, f(S), reparto y U) en todos los casos con B > 0.

**Algoritmo por ronda y verificación.** Parte 2: `seleccionar_nodos` con V = candidatos y k_r (k_r·n_r − k_r(k_r − 1)/2 llamadas a Δ). Parte 1: `repartir_presupuesto` con topes = restante. Referencia: `seleccionar_exacto` sobre los candidatos (C(n_r, k_r) evaluaciones; si supera 200000, OPT_r queda vacío). **Cota:** f(S_r) ≥ (1 − (1 − 1/k_r)^k_r)·OPT_r **ronda por ronda**, porque f restringida a los candidatos sigue siendo monótona y submodular; no es una cota sobre las T rondas.

**T(n) y espacio.** Por ronda: sorteo Θ(N); selección O(k·(N + A)) con influencia (O(k·(N + M)) con cobertura); reparto O(k + B lg k) (montículo de a lo sumo k nodos); descuento y copia del restante O(N); exacto O(C(N, k)·(N + A)). Total con R repeticiones medidas: **O(T·[(R + 1)·(k·(N + A) + B lg k) + N])** sin el exacto, más O(T·C(N, k)·(N + A)) con él; con R = 1 y sin exacto, O(T·(k·(N + A) + B lg k)): T veces una ronda de la base más el sorteo. Espacio: O(N + A) por oráculo, O(N) del restante y O(T·(k·N + B)) del resultado con sus trazas.

**Resultados** (`resultados/variantes/b_profesora_transitorio/` y `b_profesora_permanente/`, q = 0,2, semilla 0, T = 3). Con esa semilla fallan ∅, {N11} y {N06, N11}; como N11 ya había caído, los dos modos dan la misma trayectoria. Ronda 1 (15 candidatos): S = N11, N14, N09, N15, N13; f = 145,5795; OPT = 145,9072 (razón 0,9978); x = 5, 7, 7, 6, 5; U = 88,5640. Ronda 2 (14 candidatos, sin N11): S = N09, N14, N07, N15, N10; f = OPT = 144,7351 (razón 1); x = 6, 6, 5, 6, 7; U = 99,1361. Ronda 3 (13 candidatos, sin N06 ni N11): mismo S; f = OPT = 144,7351; x = 5, 5, 6, 6, 8; U = 98,8855; tras ella N09, N14 y N15 quedan con restante 0 y no podrían participar en una cuarta ronda. En una batería de 27 instancias aleatorias de influencia (N = 8 a 12, k = 3) × 2 modos × 3 rondas con q = 0,3, la razón mínima por ronda fue 0,938 (cota 0,704) y ninguna ronda incumplió la cota.

### 9.3 Variante (c): vecinos que alteran la utilidad · `red/variante_vecinos.py`
La Parte 2 no cambia (S es el del voraz base); cambia la utilidad del reparto de B entre los nodos de S. w_ij es el `peso_influencia` de la arista {i, j} y β ≥ 0 un parámetro (0,2 por omisión: las utilidades «se mueven un poco»). Las u_i de la docente son a_i·ln(1 + x_i). **Supuestos ❓** (decisión 43): solo cuentan los vecinos que **están en S** (la utilidad de la ronda es la de los participantes); la variante **necesita grafo**: en el formato propio el caso se rechaza (`[FALLA]`, «la instancia trae grafo»), igual que si alguna u_i no es log.

| Modelo | Utilidad | Algoritmo | T(n) · espacio | Garantía |
|---|---|---|---|---|
| **c1**, el efecto va aparte | lo que gasta i le suma β·w_ij·ln(1 + x_i) a cada vecino j ∈ S; al reagrupar, U = Σ_{i∈S} a'_i·ln(1 + x_i) con a'_i = a_i + β·Σ_{j∈S vecino de i} w_ij | `repartir_presupuesto` sin cambios, con u_i = a'_i·ln(1 + x) | Θ(k + d(S)) para restringir el grafo y calcular a' + Θ(k + B(1 + lg k)) · Θ(k + A_S) | **exacto** (§7.1.1: valen H1 a H4) |
| **c2**, el efecto va dentro | u_j = a_j·ln(1 + x_j + β·Σ_{i∈S vecino de j} w_ij·x_i); cóncava pero **no separable** (falla H1; tampoco aplica la PD de §7.2) | voraz unidad por unidad: cada unidad al nodo (sin tope) de mayor U(x + e_i) − U(x), barrido lineal, empate por el menor id; tras cada unidad recalcula las ganancias a distancia ≤ 2 del elegido | O(k + d(S) + B·(k + A_S)); O(B·k²) con S completo · Θ(k + A_S) | U ≥ (1 − (1 − 1/B)^B)·OPT ≥ (1 − 1/e)·OPT |
| Exacto por enumeración (referencia) | la del modelo | todos los x enteros con Σ x_i ≤ B y x_i ≤ c_i, en orden lexicográfico; gana el primero; se niega si pasan del límite | R_B·O(k + A_S), R_B = C(B + k, k) sin topes · O(k) | OPT |

Con m = |S| ≤ k, A_S = aristas dentro de S y d(S) = Σ_{i∈S} grado(i): para quedarse con los vecinos en S hay que mirar todos los vecinos de cada nodo de S, así que restringir el grafo cuesta Θ(m + d(S)); después todo depende solo de A_S. En c2, darle una unidad a i sube z_i y los z de sus vecinos, y la ganancia de un nodo l depende de su z y de los de sus vecinos: **cambian las ganancias de todos los nodos a distancia ≤ 2 de i**, no solo las de i y sus vecinos. Con S completo (la docente) se recalculan las m ganancias en cada paso (m + B·m en total). El barrido lineal Θ(m) por paso no cambia ese orden y es más claro que un montículo con claves que bajan.

**Por qué la cota de c2.** (1) U(0) = 0 y U tiene rendimientos decrecientes en cada coordenada: la ganancia de darle una unidad a i no crece cuando crece cualquier x_l (incluido x_i), porque ln(1 + ·) es cóncava y creciente y a, β, w ≥ 0. (2) Si cada unidad posible es un elemento (el nodo i aporta c_i copias) y g(A) = U(x) con x_i = copias de i en A, g es monótona y submodular. (3) Repartir a lo sumo B unidades es elegir a lo sumo B copias, y el voraz unidad por unidad es el voraz de Nemhauser, Wolsey y Fisher (1978) sobre g. **En los datos se cumple** (abajo).

**Contraejemplo de c2** (el mínimo hallado): trayecto 1 – 2 – 3, a = (3, 2, 3), w = 1, β = 0,2, B = 2. La primera unidad va al centro (le sube a los dos extremos: 2,4802 contra 2,4441), la segunda al nodo 1; voraz x = (1, 1, 0) con U = 4,4893; óptimo x = (1, 0, 1) con U = 4,8318; razón 0,9291 ≥ 0,75.

**Campos y parámetros.** No hay campos nuevos: usa el grafo y los coeficientes del formato de la profesora. `--variante c1` o `--variante c2`; `--beta` (número finito ≥ 0; por omisión 0,2; β = 0 da exactamente el reparto base); `--limite-repartos` (entero ≥ 1; por omisión 200000, el de `exacto.py`): si hay más repartos, el exacto no corre y se reporta el motivo (no es falla). Sin `--variante c1|c2`, `--beta` y `--limite-repartos` no se usan.

**Ejecución.** `python ejecutar.py casos/profesora --variante c2 --beta 0.2 --limite-repartos 302792 --salida resultados/variantes/c2_profesora` (y lo mismo con `c1`). `salida.json` trae las claves de la base más `variante_c` (modelo, β, supuesto, aristas en S y, en c1, los a'_i), `exacto` (repartos, límite y, si corrió, x*, OPT, razón U/OPT y cota) y `reparto_base` (el x de la base y su U con vecinos); `traza.txt` muestra la selección, los a'_i, cada unidad y el exacto. Las columnas de `resumen.csv` no cambian. Verificaciones nuevas: «la instancia trae grafo», «cada u_i es log»; en c2, x_i ≤ mín(B, c_i), Σ x_i = mín(B, Σ c_i), pasos = Σ x_i y U recalculada; con el exacto, c1: U = OPT; c2: U ≤ OPT y U ≥ (1 − (1 − 1/B)^B)·OPT.

**Resultados** (`resultados/variantes/c1_profesora/`, `c2_profesora/`, β = 0,2, R = 21). S = N11, N14, N09, N15, N13 (el de la base; 10 aristas dentro de S). Con topes 18 hay C(35, 5) − 5·C(16, 5) = **302792** repartos, más que el límite por omisión: las corridas usan `--limite-repartos 302792`, el número exacto (decisión 46). **c1:** a' = 7,96, 10,48, 10,26, 9,70, 8,54; x = 5, 7, 7, 6, 5 (el mismo de la base); U = 91,5670 = OPT. **c2:** x = 4, 8, 7, 6, 5; U = 99,2470 = OPT (razón 1; cota 0,6383); 155 ganancias recalculadas y 150 nodos revisados en 30 pasos; el x de la base daría U = 99,2246 con este modelo. **Batería** (`scripts/tabla_cota_variante_c.py` → `resultados/variantes/c_tabla_cota.csv`): 27 instancias de influencia (N = 8 a 12, k = 4, tres densidades, semillas 1 a 3) × β ∈ {0,2; 0,5; 1; 2} × B ∈ {3, 6, 10} = 324 filas. c1 coincide con la enumeración en las 324; en c2 solo 7 filas quedan por debajo del óptimo (ninguna con β = 0,2) y la razón mínima es 0,9867 (B = 3, β = 2, cota 0,7037): **la cota se cumple en todas**.

Referencia: Nemhauser, Wolsey y Fisher (1978), *Mathematical Programming* 14, 265–294, doi:10.1007/BF01588971.

## 10. Tablas de la cota (aproximados contra el óptimo)

Tres scripts comparan los aproximados con su algoritmo exacto de referencia. No tienen opciones (ignoran cualquier argumento), usan semillas fijas, reescriben su CSV con el mismo contenido en cada corrida y no escriben en `resultados/profesora/`. Se corren desde la raíz:

| Script | Escribe | Qué compara |
|---|---|---|
| `python scripts/tabla_cota.py` | `resultados/cota/tabla_cota.csv` y `tabla_cota_aleatoria.csv` | Parte 2: voraz contra la fuerza bruta (`red/exacto.py`) en la docente, los casos propios con N ≤ 20 y 45 instancias aleatorias de influencia, con las cotas 1 − (1 − 1/k)ᵏ y 1 − 1/e |
| `python scripts/tabla_cota_variante_a.py` | `resultados/variantes/a_tabla_cota.csv` (37 filas) | Variante (a): voraz por cociente, voraz modificado y enumeración parcial contra la fuerza bruta con presupuesto, en la docente (L = 24) y 36 instancias aleatorias (N = 10 a 16, L = 12); cotas 0,405 y 1 − 1/e |
| `python scripts/tabla_cota_variante_c.py` | `resultados/variantes/c_tabla_cota.csv` (324 filas) | Variante (c): c1 y c2 contra la enumeración de repartos en 27 instancias × β ∈ {0,2; 0,5; 1; 2} × B ∈ {3, 6, 10}; c1 debe coincidir y c2 cumplir 1 − (1 − 1/B)ᴮ |

La consola imprime el número de filas, las razones mínimas y si todas cumplen. Detalle de columnas en las fichas `docs/modulos/tabla_cota.md`, `tabla_cota_variante_a.md` y `tabla_cota_variante_c.md`.
