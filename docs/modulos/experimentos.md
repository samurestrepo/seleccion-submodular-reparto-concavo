# Ficha: `scripts/experimentos.py`

## Para qué existe
Contrasta lo medido con la T(n) del informe y de las fichas de las variantes. Corre 13 series por nombre, que dan **14 curvas y 14 CSV** porque la serie i se divide en ic e im: a–h de la solución base y sus referencias (voraz de la Parte 2 con cobertura y con influencia, reparto de la Parte 1 voraz y por PD, y fuerza bruta) e i–m de las variantes (ic e im: voraz por cociente y modificado de la variante a; j: enumeración parcial; k: fuerza bruta con presupuesto; l: variante b variando T; m: voraz de c2 variando B). Para cada tamaño guarda tiempo, conteo de operaciones y el cociente t_min / T_teorica. Uso, desde la raíz: `python scripts/experimentos.py` (todas; opciones: `--series a d`, `--sin-graficas`, `--repeticiones R`). **Solo las de las variantes, sin regenerar las a–h:** `python scripts/experimentos.py --series i j k l m` (unos 2 min; `i` es el alias de `ic` e `im`).

## Funciones públicas
| Función | Recibe | Devuelve | Complejidad |
|---|---|---|---|
| `medir_con_limite(preparar, repeticiones, limite)` | igual que `medir` y un límite en segundos para la primera repetición | `(t_min, t_mediana, conteo, repeticiones_usadas)`; si la primera repetición pasa el límite, se hacen solo 5 | igual que `medir` |
| `medir(preparar, repeticiones)` | una función que crea el estado fresco y devuelve `(ejecutar, contar)` | `(t_min, t_mediana, conteo)` | R · T(algoritmo); el reloj solo envuelve `ejecutar()` |
| `ejecutar_serie(clave, repeticiones)` | clave de la serie (`a` a `h`, `ic`, `im`, `j` a `m`) | lista de filas con las columnas del CSV; T_teorica se calcula con la fila completa (incluye n) | suma de `medir_con_limite` sobre sus tamaños |
| `expandir_series(claves)` / `columnas_de(clave, ajustada)` | claves pedidas / una clave | las series sin alias (`i` → `ic`, `im`) / las columnas de su CSV (comunes + `COLUMNAS_EXTRA`) | O(claves) |
| `instancia_rondas()` | — | la instancia fija de la serie l (topes subidos a B·128) | O(N²) del generador |
| `pendiente_esperada(filas)` | filas | pendiente de log T_teorica contra log n | O(n) |
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
| h | PD de la Parte 1 (`red/pd_reparto.py`), N = 10, sin topes | B = 25 a 400 | N·B² | candidatos t evaluados (exactamente N·(B+1)(B+2)/2) |
| ic | variante (a), `voraz_por_cociente`, L = 5N ≥ Σ c (peor caso), grado ~ 5 | N = 50 a 800 | N·mín(N, L/c_mín)·(1 + 2A/N) = N²·(1 + 2A/N) | evaluaciones de f (exactamente 1 + N(N + 1)/2) |
| im | variante (a), `voraz_modificado`, igual que ic | N = 50 a 800 | igual que ic | igual que ic (cero evaluaciones extra) |
| j | variante (a), `enumeracion_parcial`, L = 5N, grado ~ 5 | N = 8 a 18 | E(N)·(1 + 2A/N), E(N) = 1 + N + C(N, 2) + C(N, 3)·(1 + (N − 3)(N − 2)/2) = Θ(N⁵) | evaluaciones (exactamente E(N)) |
| k | variante (a), `seleccionar_exacto_costos`, L = 5N (F = 2^N), grado ~ 5 | N = 8 a 16 | 2^N·(N + A) | evaluaciones (exactamente 2^N) |
| l | variante (b), `ejecutar_rondas` sin exacto, R = 1, N = 100, k = 5, B = 100, q = 0,2 transitorio, semilla de fallos 1, topes B·128 | T = 8 a 128 rondas | T·[2(k(N + A) + B lg k) + N] | llamadas a Δ (exactamente Σ_r k_r·n_r − k_r(k_r − 1)/2) |
| m | variante (c2), `repartir_c2`, N = 50, grafo completo, S del voraz base (m = 10, A_S = 45), β = 0,2, sin topes | B = 250 a 4000 | m + d(S) + B·(m + A_S) | ganancias recalculadas (exactamente m + B·m) |

Las series i–m llevan el límite de 2 s por repetición de la serie h (ninguna lo pasó: la más lenta, k con N = 16, tarda 0,77 s) y agregan al final sus columnas propias: ic, im, j y k `L`, `A`, `repeticiones`; l `A`, `modo`, `q`, `semilla_fallos`, `repeticiones`; m `A`, `A_S`, `d_S`, `beta`, `repeticiones`. En ic, im, j y k las columnas `k` y `B` van vacías (L reemplaza a k, decisión 35). En l, `n` = T. Para las series nuevas la consola imprime además la pendiente contra T_teorica, la pendiente esperada y el rango del cociente; las gráficas de j y k van con eje y logarítmico.

Columnas de `resultados/experimentos/<serie>.csv`: `n` (la variable que cambia: N, salvo en las series e y h, que es B), `N`, `k`, `B`, `densidad`, `semilla`, `t_min`, `t_mediana`, `conteo`, `T_teorica`, `cociente`. Las gráficas son `<serie>_tiempo.png` (t_min contra n y la curva c·T_teorica, con c = t_min / T_teorica en el n más grande) y `<serie>_cociente.png`; en la serie g el eje y es logarítmico. El CSV de h agrega al final `repeticiones` (las usadas en cada tamaño): 21, o 5 si una repetición pasa de 2 s (decisión 33); con n = B, los 5 tamaños de h terminan en menos de 0,2 s por repetición. Los CSV de d y e agregan al final `t_ajustado` (el ajuste solo se hace si d y e se corren juntas); `ajuste_reparto.png` grafica t_min contra t_ajustado con la recta y = x, y la consola imprime a, b y el error relativo de cada punto.

**El ajuste conjunto es descriptivo (decisiones 32 y 60):** sus constantes salen en parte de los mismos puntos de d que luego «predice». La evidencia que cita el informe (sección 11.3, punto 2) es la **prueba fuera de muestra** de `scripts/serie_d_fuera_de_muestra.py`: a y b solo de la serie e, predicción de la d (a = 7,98·10⁻⁷ s, b = 1,99·10⁻⁷ s; errores de −0,2 % a −35,9 %; pendiente predicha 0,62 contra 0,78 medida). Se corre con `python scripts/serie_d_fuera_de_muestra.py`, no mide nada (lee los CSV de d y e) y escribe `resultados/experimentos/d_fuera_de_muestra.csv`; ficha propia: `docs/modulos/serie_d_fuera_de_muestra.md`. Usa la función `pendiente` de este script.

## Resultados de las series i–m (semilla 1, 21 repeticiones, 2026-11-17)
| Serie | Pendiente log-log contra n (esperada) | Contra T_teorica | Cociente t_min/T (máx/mín) | ¿Ajusta? |
|---|---|---|---|---|
| ic | 2,049 (2,011) | 1,019 | 1,12e-7 a 1,30e-7 (1,16) | sí |
| im | 2,053 (2,011) | 1,021 | 1,09e-7 a 1,26e-7 (1,16) | sí; tiempos iguales a ic, como dice la ficha |
| j | 5,015 (5,218) | 0,960 | 3,43e-7 a 4,55e-7 (1,32; sin N = 8, 1,09) | sí |
| k | 8,635 (8,458) | 1,023 | 2,19e-7 a 2,73e-7 (1,25) | sí (contra n la pendiente no es constante: T es exponencial) |
| l | 1,059 (1,000) | 1,059 | 3,69e-7 a 4,29e-7 (1,16) | sí; el cociente sube ~14 % desde T = 64 |
| m | 1,046 (0,988) | 1,059 | 1,15e-6 a 1,36e-6 (1,18) | sí; el cociente crece despacio con B |

**Máquina de las mediciones.** Las series i–m se corrieron el 2026-11-17 en un Intel Core i5-6300U a 2,40 GHz (2 núcleos, 4 hilos; caché L2 de 512 KB y L3 de 3 MB), 15,9 GB de RAM, Windows 10 Pro 10.0.19045, Python 3.14.7 (CPython), con el reloj `time.perf_counter`. De las series a–h (2026-11-12) no quedó registro del equipo: se supone el mismo (**Supuesto ❓**). Los tiempos absolutos dependen de la máquina; lo que se compara con la teoría es el crecimiento.

Los conteos coinciden con las fórmulas exactas en todos los tamaños (la prueba lo verifica con tamaños pequeños). En l, con q = 0,2, cada ronda tuvo k_r = 5 y el restante nunca se agotó. **Nota:** la primera corrida de ic e im se contaminó porque pytest corría al mismo tiempo (im tardaba el doble que ic con el mismo trabajo); se repitió `--series i` sola y esos son los datos del repositorio.

## Por qué así
- **Solo el algoritmo en el reloj** (decisión 8): instancia y oráculo nuevo se crean antes; no se lee ni escribe ningún archivo. Las instancias salen directo de los generadores, sin pasar por disco.
- **Mínimo y mediana de 21 repeticiones** (decisiones 29 y 30): el ruido solo suma tiempo, así que el mínimo es el de las gráficas.
- **Semilla 1 en todas las series** (decisión 32).
- **Conteos que ya existen:** `oraculo.llamadas_ganancia`, `extracciones + inserciones` y las evaluaciones que devuelve `seleccionar_exacto`. No se agregó ningún contador. Límite: con influencia el conteo es Θ(k·N) aunque el grafo sea completo; el factor N de la serie b está dentro de cada llamada (O(1 + grado)) y el conteo no lo ve.
- **Series i–m (decisiones 48 a 53):** peor caso de la variante (a) con L = 5N, porque así el conteo es exacto y el número de pasos crece (= N); grado ~ 5 para que cada evaluación cueste O(1) en promedio y T sea el número de evaluaciones por (1 + 2A/N). En l se cronometra `ejecutar_rondas` completo (incluye la ejecución con traza, las verificaciones y los oráculos de cada ronda, que crea la propia variante): es lo que la ficha de variante_rondas mide con R = 1, y separarlo exigiría cambiar la variante. En m, S se calcula fuera del reloj con el voraz base, y el grafo completo hace S completo para que el conteo sea exacto.
- Si C(N, k) superara 200000, `seleccionar_exacto` lanzaría `DemasiadasCombinaciones`; en las series f y g el máximo es 4060 y 12870.

## Cómo modificarlo
Cambiar tamaños: la lista de la serie en `SERIES`. Otra serie: una función `construir(n)` que devuelva `(parámetros, preparar)` y una entrada en `SERIES`. `matplotlib` se importa solo dentro de `graficar` (con `--sin-graficas` no hace falta).

## Pruebas
`pruebas/test_experimentos.py` (16 pruebas): `medir`, conteos de las series a, d y f contra k·N − k(k−1)/2, 2B y C(N, k), serie h (conteo y repeticiones), `medir_con_limite`, columnas del CSV, la pendiente y `ajustar_reparto` (recupera a y b de datos exactos). Series nuevas: ic e im cuentan 1 + N(N + 1)/2 y coinciden con los contadores del oráculo; j cuenta E(N); k cuenta 2^N; l cuenta Σ_r k_r·n_r − k_r(k_r − 1)/2, con k_r = k, sin exacto y sin agotar el restante, y su T es lineal en T; m cuenta m + B·m ganancias y B·m revisados; el alias `i`, las columnas de los CSV nuevos y que las a–h no cambian de columnas.

## Preguntas probables en la sustentación
- **¿Por qué el mínimo y no el promedio?** El ruido del sistema solo suma tiempo.
- **¿Qué se espera del cociente?** Que tienda a una constante si T teórica describe bien el crecimiento; si crece o decrece sin parar, falta un término.
- **¿Por qué el conteo de la serie b no crece como N²?** Cuenta llamadas a Δ, y cada una recorre los vecinos del nodo.
- **¿Por qué el voraz modificado tarda lo mismo que el de cociente (series ic e im)?** El mejor nodo solo sale del primer paso del cociente, f({v}) = Δ(v | ∅): no hay evaluaciones extra, y los conteos son idénticos.
- **¿Por qué la pendiente de j es 5,0 y no 5,2?** Con N ≤ 18 los términos de menor orden pesan; contra la T exacta del peor caso la pendiente es 0,96.

_Última actualización: 2026-11-17 · remite a la prueba fuera de muestra de la serie d (P-6 fase 1)_
