# 10. Implementación

La solución base (lectura, oráculos, los dos voraces, verificación, traza y ronda) no cambió de lógica desde la primera entrega. Para esta entrega se agregaron el exacto de la Parte 2 (`red/exacto.py`), la PD de la Parte 1 (`red/pd_reparto.py`), el generador de instancias de influencia y los experimentos de tiempo. Además se agregaron los módulos de las tres variantes, que se describen aquí. Cada archivo tiene su ficha en `docs/modulos/<archivo>.md`, con sus funciones, su T(n) y sus pruebas. Los comandos para correrlo todo están en el manual técnico (`MANUAL_TECNICO.md`): la sección 9 trae las variantes y la sección 8, los experimentos.

### Principio común de las variantes

Una variante se activa solo con la opción `--variante` de `ejecutar.py` (`a`, `b`, `c1` o `c2`). Sin esa opción, el programa hace exactamente lo de la solución base. Ninguna variante modifica `seleccion.py` ni `reparto.py`: todas los llaman tal como están, o reutilizan su oráculo y sus contadores. Así, los conteos y las verificaciones de la base siguen valiendo dentro de cada variante. Las salidas van a `resultados/variantes/`; `resultados/profesora/` (la evidencia de la primera entrega) no se toca.

### Módulos nuevos

| Archivo | Para qué sirve | Algoritmos y funciones principales | Ficha |
|---|---|---|---|
| `red/variante_costos.py` | Variante (a): selección con costos c(v) y presupuesto de participación L | `seleccionar_exacto_costos` (backtracking con poda por factibilidad, exacto, se niega si 2ᴺ > 200 000), `voraz_por_cociente`, `voraz_modificado` (el de la ronda) y `enumeracion_parcial` (1 − 1/e, O(N⁵)) | `docs/modulos/variante_costos.md` |
| `red/variante_rondas.py` | Variante (b): T rondas con nodos que fallan (q y semilla; modos transitorio y permanente) y con el presupuesto de cada nodo descontado de una ronda a la siguiente | `ejecutar_rondas` (por ronda: sorteo, candidatos, los dos voraces de la base, el exacto de referencia y la cota de la ronda), `sortear_fallos`, `candidatos_de_la_ronda` | `docs/modulos/variante_rondas.md` |
| `red/variante_vecinos.py` | Variante (c): los vecinos en S alteran la utilidad del reparto | `repartir_c1` (coeficientes a'_i y el voraz de `reparto.py` sin cambios), `repartir_c2` (voraz unidad por unidad con barrido lineal), `repartir_exacto` y `contar_repartos` (enumeración de referencia), `ejecutar_variante_c` | `docs/modulos/variante_vecinos.md` |
| `scripts/tabla_cota_variante_a.py` | Compara los tres aproximados de (a) con el OPT exacto: la docente (L = 24) y 36 instancias aleatorias (L = 12) | escribe `resultados/variantes/a_tabla_cota.csv` | `docs/modulos/tabla_cota_variante_a.md` |
| `scripts/tabla_cota_variante_c.py` | Compara c1 y c2 con la enumeración en 27 instancias × 4 valores de β × 3 valores de B (324 filas) | escribe `resultados/variantes/c_tabla_cota.csv` | `docs/modulos/tabla_cota_variante_c.md` |

### Módulos existentes que cambiaron

| Archivo | Cambio |
|---|---|
| `ejecutar.py` | Opción `--variante a\|b\|c1\|c2` y sus parámetros: `--modo-fallo`, `--prob-fallo`, `--semilla-fallos` y `--rondas` (b); `--beta` y `--limite-repartos` (c). Sin `--variante`, estas opciones no se usan |
| `red/entrada.py` | Campos opcionales del formato propio: `costo` por nodo, `presupuesto_costos` y `rondas`. En el formato de la profesora, `costo_participacion`, `presupuesto_costos_participacion_por_ronda` y `numero_rondas` ya se leían; ahora los usan las variantes |
| `red/ronda.py` | Con `variante="a"`, la Parte 2 pasa a ser el voraz modificado; el reparto no cambia |
| `red/verificacion.py` | Verificaciones nuevas: Σ c(S) ≤ L y costos > 0 (a); T ≥ 1, restante ≥ 0, cota por ronda y, en el modo permanente, candidatos que nunca aumentan (b); «la instancia trae grafo», «cada u_i es log» y la comparación con el exacto (c) |
| `red/traza.py` | La traza muestra Δ/c de cada candidato que cabe en (a) |
| `red/generador.py` | Parámetro opcional `presupuesto_costos` (L) en el generador de influencia |
| `scripts/experimentos.py` | Seis series nuevas, de la i a la m: `ic`, `im`, `j`, `k`, `l` y `m` (sección 11) |

### Por qué está organizado así

- **Un módulo por variante.** Cada variante cambia una sola pieza: (a) cambia la restricción de la Parte 2, (b) repite la ronda y (c) cambia la utilidad de la Parte 1. Un archivo por variante deja esa pieza aislada y permite leerla junto a su ficha.
- **Reutilizar en vez de copiar.** (b) llama a `seleccionar_nodos` y a `repartir_presupuesto` con V = candidatos y topes = restante. c1 llama a `repartir_presupuesto` con otras utilidades. (a) usa el mismo oráculo que la base. Un cambio en la base se refleja en las variantes sin tocarlas.
- **Los exactos son referencias y no entran a la ronda**, salvo el de cada ronda en (b), que se puede apagar. Todos usan el mismo límite de 200 000 (subconjuntos o repartos) y se niegan a correr, sin evaluar nada, si el tamaño lo pasa.
- **Pruebas.** Cada variante tiene su archivo de pruebas: `pruebas/test_variante_costos.py` (57 pruebas), `test_variante_rondas.py` (105) y `test_variante_vecinos.py` (133). En las tres hay una prueba de reducción: con costos 1 y L = k, con q = 0 y T = 1, o con β = 0, la variante da exactamente el resultado de la base.
