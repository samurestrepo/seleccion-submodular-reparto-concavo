# Ficha: `ejecutar.py`

## Para qué existe
Es la línea de comandos: corre una ronda por cada caso y guarda las evidencias que pide la entrega (resultado, tiempo y traza por caso).

## Funciones públicas
| Función | Recibe | Devuelve |
|---|---|---|
| `main(argumentos)` | rutas de archivos o carpetas, `--salida`, `--repeticiones` (entero ≥ 1; por omisión, 21), `--variante a`, `b`, `c1` o `c2` (por omisión ninguna: solución base); con `b`: `--modo-fallo transitorio\|permanente` (transitorio), `--prob-fallo` (q ∈ [0, 1], 0,2), `--semilla-fallos` (0), `--rondas` (T ≥ 1; por omisión el del caso, o 1); con `c1` o `c2`: `--beta` (β finito ≥ 0, 0,2) y `--limite-repartos` (entero ≥ 1, 200000) | código 0 si todo cumple, 1 si algo falla o no hay casos; un `--repeticiones` o `--variante` inválido termina con el error de `argparse` |
| `buscar_casos(rutas)` | rutas | lista de casos (una carpeta aporta sus `.json`, sin distinguir mayúsculas, en orden alfabético) |
| `correr_caso(ruta, salida, repeticiones=REPETICIONES, variante=None, fallos=None, vecinos=None)` | ruta de un caso, carpeta de salida, R, la variante y, con `b`, el diccionario de parámetros de fallo (modo, prob_fallo, semilla, rondas); con `c1` o `c2`, el de la variante (c) (beta, limite) | el resultado; escribe evidencias e imprime una línea (con la variante (a), también `costo(S) <= L`; con la (b), una línea por ronda: candidatos, fallados, S_r, f(S_r), OPT_r, razón y U_r) |
| `guardar_evidencias(resultado, carpeta)` | resultado de la ronda (o de las T rondas) | escribe siempre salida.json, traza.json y traza.txt (el texto con `a_texto_rondas` si el resultado trae `rondas`, con `a_texto_vecinos` si trae `variante_c`) |
| `fila_resumen(resultado)` | resultado | la fila de `resumen.csv`: medianas, mínimos (`minimo_seleccion_s`, `minimo_reparto_s`) y R |
| `filas_resumen_rondas(resultado)` | resultado de la variante (b) | **una fila por ronda** (`ENCABEZADO_RONDAS`: caso, modo, q, semilla, T, ronda, N, k, B, fallados, candidatos, k_ronda, S_r, f(S_r), OPT_r, razón, utilidad, restante total, medianas, R, cumple); un caso rechazado deja una fila |
| `escribir_resumen(filas, salida, encabezado=ENCABEZADO)` | filas, carpeta y el encabezado | escribe `resumen.csv`; avisa si reemplaza uno anterior |

## Cómo funciona
Para cada caso: `leer_instancia` → `ejecutar_ronda` → `guardar_evidencias` en `<salida>/<caso>/`. Al final escribe `<salida>/resumen.csv` con una fila por caso (S, f(S), utilidad, mediana y mínimo de los tiempos, `repeticiones`, si cumple) e imprime una línea por caso.

Qué pasa con cada tipo de problema:

| Problema | Consola | Evidencias | Fila en el resumen |
|---|---|---|---|
| Forma inválida (no es JSON, tipos, a ≤ 0…) | `[ERROR]` | las tres, con el motivo; N, k y B no se conocen | sí, con `todas_cumplen` = False |
| Entrada inválida (k ≥ N, no cóncava…) | `[FALLA]` | las tres, con el motivo | sí, con N, k y B |
| No se puede abrir el archivo | `[ERROR]` | ninguna; no toca las anteriores | sí, solo con el nombre |
| Mismo nombre de caso que uno ya corrido | `[ERROR]` | ninguna; quedan las del primero | no |

Ejemplos:
```
python ejecutar.py casos/propios/ejemplo_informe.json
python ejecutar.py casos/profesora --salida resultados/profesora
python ejecutar.py casos/propios --repeticiones 5
python ejecutar.py casos/profesora --variante a --salida resultados/variantes/a_profesora
```
**`--variante b`** (P-4 fase 2, decisiones 39 a 42): corre `red/variante_rondas.py` (T rondas con nodos que fallan y presupuesto por nodo que se descuenta; Supuesto ❓). Los parámetros `--modo-fallo`, `--prob-fallo`, `--semilla-fallos` y `--rondas` solo se usan con `b`. `salida.json` trae `rondas` (una entrada por ronda, con OPT_r y la razón), `traza.json` trae `rondas` con los pasos de cada una y `resumen.csv` cambia de columnas: **una fila por ronda**. Ejemplo: `python ejecutar.py casos/profesora --variante b --modo-fallo permanente --salida resultados/variantes/b_profesora_permanente`.

**`--variante c1` o `c2`** (P-4 fase 3, decisiones 43 a 47): corre `ejecutar_variante_c` de `red/variante_vecinos.py`: la Parte 2 base y el reparto con vecinos que alteran la utilidad (c1: coeficientes a'_i y el voraz de `reparto.py`; c2: voraz unidad por unidad). Solo con grafo (formato de la profesora); el propio se rechaza con `[FALLA]`. `--beta` y `--limite-repartos` solo se usan con `c1` o `c2`. `salida.json` trae además `variante_c` (modelo, β, a'_i en c1), `exacto` (la enumeración, si cabe en el límite) y `reparto_base`; la consola agrega el modelo, β y OPT con la razón; `traza.txt` se escribe con `a_texto_vecinos`. **Las columnas de `resumen.csv` no cambian** (la utilidad es la del modelo). `_beta` rechaza lo que no sea un número finito ≥ 0 antes de correr. En la docente hay 302792 repartos: con el límite por omisión el exacto no corre; las evidencias se generaron con `--limite-repartos 302792`.

**`--variante a`** (P-4 fase 1, decisión 35): la Parte 2 es el voraz modificado de `red/variante_costos.py` con Σ c(S) ≤ L en lugar de |S| ≤ k (Supuesto ❓); el reparto, las evidencias y `resumen.csv` son los mismos (las columnas del CSV no cambian; el costo va en `salida.json` y en la consola). Las salidas de las variantes van en `resultados/variantes/`; `resultados/profesora/` no se toca.

## Por qué así
- La guía exige que sea reproducible **sin editar la lógica**: los casos entran por archivo y la salida va a una carpeta. Un archivo con formato inválido se reporta como `[ERROR]` y no detiene a los demás.
- **Siempre se escriben los tres archivos** (decisión 22): así un caso rechazado reemplaza la traza de una corrida anterior y no queda una con "CUMPLEN" que lo contradiga. Por eso no hace falta borrar nada aparte.
- **`resumen.csv` refleja solo la última corrida** (decisión 18): no acumula. Si ya existe, se reemplaza y se avisa por consola. Las carpetas de casos de corridas anteriores no se tocan. Para tener el resumen completo, correr la carpeta entera.
- **`--repeticiones`** (decisión 29): cambia R sin editar el código. `_entero_positivo` rechaza lo que no sea un entero ≥ 1 antes de correr cualquier caso. Un caso rechazado no se mide, y deja vacías las columnas `repeticiones` y de mínimos. **Para la gráfica de T(n) se usa el mínimo** (decisión 30).
- **Colisión de nombres** (decisión 18): el nombre del caso es el del archivo. Dos archivos con el mismo nombre, en distintas carpetas, usarían la misma carpeta de evidencias: corre el primero y el segundo es un error. Se compara sin distinguir mayúsculas porque en Windows `c` y `C` serían la misma carpeta.

## Cómo modificarlo
- **Otra columna en el resumen:** agregarla en `fila_resumen` (también en la fila del caso rechazado) y en `ENCABEZADO`; para la variante (b), en `filas_resumen_rondas` y `ENCABEZADO_RONDAS`.

## Pruebas
`pruebas/test_ejecutar.py`: un archivo malo en medio del lote (10 formas), el motivo en la traza, archivo inexistente, entrada inválida con traza y fila, traza vieja reemplazada, colisión de nombres, resumen de la última corrida con aviso, extensión `.JSON` y BOM; `--repeticiones` llega a `salida.json` y al resumen, el resumen trae la mediana y el mínimo (igual al de `salida.json` y ≤ la mediana), 21 por omisión, columnas vacías en un caso rechazado, y valores inválidos rechazados. `test_ronda.py::test_ejecutar_escribe_las_evidencias`: el caso normal. `pruebas/test_variante_rondas.py`: `--variante b` con sus parámetros, resumen por ronda, caso rechazado con una fila, resumen de la base intacto y parámetros inválidos. `pruebas/test_variante_vecinos.py`: `--variante c1` y `c2` en la docente (sin exacto con el límite por omisión, `resumen.csv` con las columnas de la base, Supuesto ❓ en la traza) y `--beta` o `--limite-repartos` inválidos.

## Preguntas probables en la sustentación
- **¿Cómo se corre un caso nuevo?** Se pone el .json en una carpeta y se pasa la ruta; no se toca el código.
- **¿Qué pasa si un caso está mal?** No detiene a los demás: da `[ERROR]` o `[FALLA]`, deja el motivo en la traza y el programa termina con código 1.

_Última actualización: 2026-11-17 · opciones `--variante c1|c2`, `--beta` y `--limite-repartos`; traza con `a_texto_vecinos` (P-4 fase 3)_
