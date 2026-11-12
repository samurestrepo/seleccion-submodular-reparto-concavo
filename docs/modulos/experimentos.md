# Ficha: `scripts/experimentos.py`

## Para qué existe
Contrasta lo medido con la T(n) del informe. Corre 7 series (voraz de la Parte 2 con cobertura y con influencia, reparto de la Parte 1 y fuerza bruta), y para cada tamaño guarda tiempo, conteo de operaciones y el cociente t_min / T_teorica. Uso, desde la raíz: `python scripts/experimentos.py` (opciones: `--series a d`, `--sin-graficas`, `--repeticiones R`).

## Funciones públicas
| Función | Recibe | Devuelve | Complejidad |
|---|---|---|---|
| `medir(preparar, repeticiones)` | una función que crea el estado fresco y devuelve `(ejecutar, contar)` | `(t_min, t_mediana, conteo)` | R · T(algoritmo); el reloj solo envuelve `ejecutar()` |
| `ejecutar_serie(clave, repeticiones)` | letra de la serie (`a` a `g`) | lista de filas con las columnas del CSV | suma de `medir` sobre sus tamaños |
| `pendiente(xs, ys)` / `pendiente_loglog(filas, variable)` | datos | pendiente de la regresión (de log t_min contra log n o log T) | O(n) |
| `ajustar_reparto(filas)` / `error_relativo(fila)` | filas de las series d y e juntas | `(a, b)` de t_min ≈ a·N + b·B·lg N (ecuaciones normales 2x2, sin término independiente, con el N y el B reales) y agrega `t_ajustado` a cada fila | O(filas) |
| `escribir_csv`, `graficar`, `graficar_ajuste`, `imprimir`, `imprimir_ajuste`, `main` | — | CSV, dos PNG por serie, `ajuste_reparto.png` (t medido contra predicho, con y = x) y tablas por consola | — |

## Las series
| Serie | Qué mide | Tamaños | T teórica | Conteo |
|---|---|---|---|---|
| a | voraz, cobertura, k = 5 | N = 20 a 640 | k·N | llamadas a Δ |
| b | voraz, influencia, grafo completo, k = 5 | N = 25 a 400 | k·N² | llamadas a Δ |
| c | voraz, influencia, densidad 5/(N−1), k = 5 | N = 25 a 400 | k·N | llamadas a Δ |
| d | reparto, B = 1000 | N = 1000 a 16000 | N + B·lg N | extracciones + inserciones |
| e | reparto, N = 100 | B = 1000 a 16000 | N + B·lg N | extracciones + inserciones |
| f | fuerza bruta, k = 3, grafo completo | N = 10 a 30 | C(N, k)·k·N | evaluaciones de f |
| g | fuerza bruta, k = N/2, grafo completo | N = 8 a 16 | C(N, k)·k·N | evaluaciones de f |

Columnas de `resultados/experimentos/<serie>.csv`: `n` (la variable que cambia: N, salvo en la serie e, que es B), `N`, `k`, `B`, `densidad`, `semilla`, `t_min`, `t_mediana`, `conteo`, `T_teorica`, `cociente`. Las gráficas son `<serie>_tiempo.png` (t_min contra n y la curva c·T_teorica, con c = t_min / T_teorica en el n más grande) y `<serie>_cociente.png`; en la serie g el eje y es logarítmico. Los CSV de d y e agregan al final `t_ajustado` (el ajuste solo se hace si d y e se corren juntas); `ajuste_reparto.png` grafica t_min contra t_ajustado con la recta y = x, y la consola imprime a, b y el error relativo de cada punto.

## Por qué así
- **Solo el algoritmo en el reloj** (decisión 8): instancia y oráculo nuevo se crean antes; no se lee ni escribe ningún archivo. Las instancias salen directo de los generadores, sin pasar por disco.
- **Mínimo y mediana de 21 repeticiones** (decisiones 29 y 30): el ruido solo suma tiempo, así que el mínimo es el de las gráficas.
- **Semilla 1 en todas las series** (decisión 32).
- **Conteos que ya existen:** `oraculo.llamadas_ganancia`, `extracciones + inserciones` y las evaluaciones que devuelve `seleccionar_exacto`. No se agregó ningún contador. Límite: con influencia el conteo es Θ(k·N) aunque el grafo sea completo; el factor N de la serie b está dentro de cada llamada (O(1 + grado)) y el conteo no lo ve.
- Si C(N, k) superara 200000, `seleccionar_exacto` lanzaría `DemasiadasCombinaciones`; en las series f y g el máximo es 4060 y 12870.

## Cómo modificarlo
Cambiar tamaños: la lista de la serie en `SERIES`. Otra serie: una función `construir(n)` que devuelva `(parámetros, preparar)` y una entrada en `SERIES`. `matplotlib` se importa solo dentro de `graficar` (con `--sin-graficas` no hace falta).

## Pruebas
`pruebas/test_experimentos.py`: `medir`, conteos de las series a, d y f contra k·N − k(k−1)/2, 2B y C(N, k), columnas del CSV, la pendiente y `ajustar_reparto` (recupera a y b de datos exactos).

## Preguntas probables en la sustentación
- **¿Por qué el mínimo y no el promedio?** El ruido del sistema solo suma tiempo.
- **¿Qué se espera del cociente?** Que tienda a una constante si T teórica describe bien el crecimiento; si crece o decrece sin parar, falta un término.
- **¿Por qué el conteo de la serie b no crece como N²?** Cuenta llamadas a Δ, y cada una recorre los vecinos del nodo.

_Última actualización: 2026-11-12 · ajuste del reparto (a·N + b·B·lg N)_
