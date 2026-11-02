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
| Tiempo con cobertura | O(k·M), con M = Σ |C_v| |
| Espacio adicional | O(k + |U|) |
| Garantía | f(S) ≥ (1 − 1/e)·OPT (Nemhauser, Wolsey y Fisher, 1978) |

### 1.2 Parte 1 — REPARTIR-PRESUPUESTO (voraz óptimo con montículo) · `red/reparto.py`
Entrega B unidades una por una; cada unidad va al nodo cuya siguiente unidad aporta más. Montículo de máximos simulado con `heapq` (de mínimos) guardando parejas (−Δ_i(x_i), i). Empates: el menor índice.

| | |
|---|---|
| Construir el montículo | O(N) (`heapify`) |
| Ciclo | B vueltas, cada una con un `heappop` y un `heappush` de O(lg N) |
| Tiempo | peor caso **O(N + B lg N)**; mejor caso Θ(N + B) |
| Espacio | Θ(N) |
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
| `utilidad` | `{"tipo": "log", "a": a}` → a·ln(1 + x); `{"tipo": "raiz", "a": a}` → a·√x; `{"tipo": "tabla", "ganancias": [Δ(0), Δ(1), …]}` → ganancias explícitas por unidad (para ejemplos y contraejemplos) |

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

### 3.3 Verificaciones
| Parte | Comprobación |
|---|---|
| Entrada | 1 ≤ k < N; B ≥ 0; ids únicos; cada u_i creciente y cóncava en {0, …, B} |
| Parte 2 | S ⊆ V; sin repetidos; |S| ≤ k; valor acumulado = f(S) recalculada; llamadas = k·N − k(k−1)/2 |
| Parte 1 | x_i entero en [0, B]; Σ x_i = B; utilidad = Σ u_i(x_i) recalculada; extracciones = inserciones = B |
| Ejecución | la ejecución con traza da lo mismo que la medida |

Si la entrada no cumple sus restricciones, los algoritmos no se ejecutan y la traza lo reporta.

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
- La revisión de concavidad cuesta O(N·B); con B muy grande la verificación tarda más que los algoritmos (no afecta los tiempos reportados).
- No se incluyen todavía: el algoritmo exacto de la Parte 2, las variantes de la sección 4.4 del enunciado ni la validación experimental.
