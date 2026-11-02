# Manual técnico — Proyecto Red (G2), primera entrega

Solución base: selección de nodos (Parte 2) y reparto de presupuesto (Parte 1).
Las demostraciones (NP-dureza, eficiencia) están en el informe; este manual describe el código.

## 1. Algoritmos

### 1.1 Parte 2 — SELECCIONAR-NODOS (voraz aproximado) · `red/seleccion.py`
En k pasos agrega al equipo S el nodo de mayor ganancia marginal Δ(v | S) = |C_v ∖ cub(S)|. Empates: el menor índice.

| | |
|---|---|
| Operación básica | una evaluación de Δ (llamada al oráculo) |
| Conteo | k·N − k(k−1)/2, exacto y para toda entrada; entre kN/2 y kN ⇒ **Θ(N·k)** en mejor, peor y promedio |
| Tiempo con cobertura | O(k·(N + M)), con M = Σ |C_v|. El N pesa porque cada paso recorre V; si ningún C_v es vacío, N ≤ M y queda O(k·M) |
| Espacio adicional | O(k + |U|) sin traza; la ejecución con traza guarda además los Δ de cada paso, Θ(N·k) |
| Precondición | 1 ≤ k ≤ |V|, con V ordenado y sin repetidos. La valida la ronda; el algoritmo no la comprueba, para seguir el pseudocódigo |
| Garantía | f(S) ≥ (1 − 1/e)·OPT (Nemhauser, Wolsey y Fisher, 1978) |

### 1.2 Parte 1 — REPARTIR-PRESUPUESTO (voraz óptimo con montículo) · `red/reparto.py`
Entrega B unidades una por una; cada unidad va al nodo cuya siguiente unidad aporta más. Montículo de máximos simulado con `heapq` (de mínimos) guardando parejas (−Δ_i(x_i), i). Empates: el menor índice.

| | |
|---|---|
| Construir el montículo | O(N) (`heapify`) |
| Ciclo | B vueltas, cada una con un `heappop` y un `heappush` de O(lg N) |
| Tiempo | peor caso **O(N + B lg N)**. Con `heapq`, **Θ(N + B(1 + lg N))** para toda entrada: `heappop` siempre baja hasta una hoja, así que no hay un mejor caso más barato. El 1 cubre N = 1: lg 1 = 0, pero el ciclo igual da B vueltas |
| Espacio | Θ(N) |
| Precondiciones | B ≥ 0, S sin repetidos, u_i crecientes y cóncavas. Las valida la ronda; el algoritmo no las comprueba, para seguir el pseudocódigo |
| Optimalidad | por concavidad de las u_i (argumento de intercambio, entrega posterior) |

Dentro de una ronda, N de la Parte 1 es k (los nodos elegidos).

## 2. Estructura del código

| Archivo | Responsabilidad |
|---|---|
| `ejecutar.py` | Línea de comandos: casos → ronda → evidencias |
| `red/entrada.py` | Leer y validar la forma del JSON; único archivo que conoce el formato |
| `red/utilidades.py` | Familias u_i (log, raiz, tabla) con Δ en O(1) |
| `red/cobertura.py` | Oráculo f de cobertura y contadores de llamadas |
| `red/seleccion.py` | Parte 2 |
| `red/reparto.py` | Parte 1 |
| `red/verificacion.py` | Restricciones de entrada y salida |
| `red/traza.py` | Paso a paso en texto y JSON |
| `red/ronda.py` | Orquesta la ronda y mide tiempos |
| `red/generador.py` | Instancias sintéticas con semilla |

Flujo de una ronda:
```
leer_instancia → verificar_entrada → seleccionar_nodos (Parte 2) → repartir_presupuesto (Parte 1 sobre S)
              → verificar_seleccion / verificar_reparto → traza y tiempos → archivos
```
Cada archivo tiene su ficha en `docs/modulos/` con su complejidad, cómo modificarlo y preguntas de sustentación.

## 3. Formatos

### 3.1 Entrada (provisional, informe 6.5)
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
| `cubre` | elementos que aporta el nodo (cadenas o números); definen f como cobertura |
| `utilidad` | `{"tipo": "log", "a": a}` → a·ln(1 + x); `{"tipo": "raiz", "a": a}` → a·√x; `{"tipo": "tabla", "ganancias": [Δ(0), Δ(1), …]}` → ganancias explícitas por unidad (para ejemplos y contraejemplos). `a` debe ser un número finito con a > 0, y las ganancias, números finitos. Valores como `true`, `"3"`, `NaN` o `Infinity` son error de forma |

El archivo debe estar en UTF-8, con o sin BOM. En una carpeta, la extensión `.json` se reconoce sin distinguir mayúsculas. El nombre del caso es el del archivo sin esa extensión.

### 3.2 Salida (`<salida>/<caso>/salida.json`)
| Campo | Contenido |
|---|---|
| `entrada` | N, k, B |
| `seleccion` | `S` (en el orden en que se eligió), `valor` = f(S), `llamadas_ganancia`, `llamadas_valor` |
| `reparto` | `x` (id → unidades), `utilidad` = Σ u_i(x_i), `extracciones`, `inserciones` |
| `tiempos_segundos` | `seleccion` y `reparto` (solo el algoritmo) |
| `verificaciones` | listas `entrada`, `seleccion`, `reparto`, `ejecucion`, cada una con nombre, cumple y detalle |
| `todas_cumplen` | true si todas las verificaciones cumplen |

`traza.json` tiene `pasos_seleccion` (por paso: Δ de cada candidato, elegido, f(S) después) y `unidades_reparto` (por unidad: nodo y ganancia). `traza.txt` es la versión legible de todo lo anterior.

**Caso rechazado:** `salida.json` trae solo `caso`, `entrada`, `verificaciones.entrada` y `todas_cumplen = false`; `traza.json` trae las listas vacías y `motivo_rechazo`; `traza.txt` trae las verificaciones y el motivo. Si el archivo tiene forma inválida, N, k y B quedan en `null`. Si no se pudo ni abrir, no se escriben evidencias.

**`<salida>/resumen.csv`:** una fila por caso de la **última corrida**, sin acumular. Un caso rechazado deja vacíos S, f(S), utilidad y tiempos, con `todas_cumplen` en False. Si ya existía, se reemplaza y se avisa por consola. Dos archivos con el mismo nombre de caso (sin distinguir mayúsculas) son un error: corre el primero y el segundo no se ejecuta ni tiene fila.

### 3.3 Verificaciones
| Parte | Comprobación |
|---|---|
| Entrada | 1 ≤ k < N; B ≥ 0; ids únicos; cada u_i creciente y cóncava en {0, …, B} |
| Parte 2 | S ⊆ V; sin repetidos; |S| ≤ k; valor acumulado = f(S) recalculada; llamadas = k·N − k(k−1)/2 |
| Parte 1 | x_i entero en [0, B]; Σ x_i = B; utilidad finita e igual a Σ u_i(x_i) recalculada; extracciones = inserciones = B |
| Ejecución | la ejecución con traza da lo mismo que la medida |

La concavidad se revisa solo en las unidades que se pueden entregar: en log y raíz basta a > 0 (O(1)); en tabla, Δ(x) ≥ 0 si x < B y Δ(x + 1) ≤ Δ(x) si x + 1 < B (O(min(L, B))).

Si la entrada no cumple sus restricciones, los algoritmos no se ejecutan y la traza lo reporta con el motivo.

## 4. Ejecución paso a paso
1. Instalar Python 3.11+ (y `pytest` para las pruebas: `python -m pip install -r requirements-dev.txt`).
2. Abrir una terminal en la raíz del repositorio.
3. `python -m pytest` → todas las pruebas deben pasar.
4. `python ejecutar.py casos/profesora --salida resultados/profesora` (o cualquier archivo o carpeta de casos).
5. Revisar `resultados/profesora/resumen.csv` y la carpeta de cada caso.

## 5. Medición de tiempos
Se usa `time.perf_counter()` alrededor de cada algoritmo, en una ejecución **sin traza**; no incluye lectura, escritura, traza ni verificaciones. Luego se ejecuta otra vez con traza para la evidencia y se comprueba que ambas coinciden. En casos muy pequeños los tiempos son de microsegundos y tienen ruido del sistema; la comparación contra T(n) se hará en la entrega de experimentación con instancias grandes y repeticiones.

## 6. Limitaciones
- El formato de entrada es provisional hasta recibir los casos de la docente; adaptarlo solo requiere cambiar `red/entrada.py`.
- La utilidad conjunta es la de cobertura; otra función submodular requiere solo otro oráculo con la misma interfaz.
- La Parte 2 es aproximada: el voraz no siempre da el óptimo (ejemplo: `casos/propios/contraejemplo_seleccion.json` da 5 y el óptimo es 6).
- La Parte 1 solo es óptima si cada u_i es cóncava; si no lo es, la verificación de entrada lo reporta y la ronda no se ejecuta.
- El contraejemplo convexo de la Parte 1 solo se puede mostrar por llamada directa a `repartir_presupuesto`; por `ejecutar.py` esa entrada se rechaza sin correr los algoritmos.
- La verificación de entrada cuesta O(N + Σ min(L_i, B)) esperado, con L_i el largo de cada tabla; no afecta los tiempos reportados.
- Con coeficientes extremos (a cerca de 1e308) los valores se desbordan a infinito: el caso se reporta como FALLA en la verificación de la utilidad, y `salida.json` puede traer `Infinity`, que no es JSON estándar.
- La ejecución con traza guarda Θ(N·k + B) anotaciones; con instancias muy grandes, la traza y sus archivos pesan.
- No se incluyen todavía: el algoritmo exacto de la Parte 2, las variantes de la sección 4.4 del enunciado ni la validación experimental.
