# Ficha: `ejecutar.py`

## Para qué existe
Es la línea de comandos: corre una ronda por cada caso y guarda las evidencias que pide la entrega (resultado, tiempo y traza por caso).

## Funciones públicas
| Función | Recibe | Devuelve |
|---|---|---|
| `main(argumentos)` | rutas de archivos o carpetas, `--salida` | código 0 si todo cumple, 1 si algo falla o no hay casos |
| `buscar_casos(rutas)` | rutas | lista de casos (una carpeta aporta sus `.json`, sin distinguir mayúsculas, en orden alfabético) |
| `correr_caso(ruta, salida)` | ruta de un caso y carpeta de salida | el resultado; escribe evidencias e imprime una línea |
| `guardar_evidencias(resultado, carpeta)` | resultado de la ronda | escribe siempre salida.json, traza.json y traza.txt |
| `fila_resumen(resultado)` | resultado | la fila de `resumen.csv` |
| `escribir_resumen(filas, salida)` | filas y carpeta | escribe `resumen.csv`; avisa si reemplaza uno anterior |

## Cómo funciona
Para cada caso: `leer_instancia` → `ejecutar_ronda` → `guardar_evidencias` en `<salida>/<caso>/`. Al final escribe `<salida>/resumen.csv` con una fila por caso (S, f(S), utilidad, tiempos, si cumple) e imprime una línea por caso.

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
```

## Por qué así
- La guía exige que sea reproducible **sin editar la lógica**: los casos entran por archivo y la salida va a una carpeta. Un archivo con formato inválido se reporta como `[ERROR]` y no detiene a los demás.
- **Siempre se escriben los tres archivos** (decisión 22): así un caso rechazado reemplaza la traza de una corrida anterior y no queda una con "CUMPLEN" que lo contradiga. Por eso no hace falta borrar nada aparte.
- **`resumen.csv` refleja solo la última corrida** (decisión 18): no acumula. Si ya existe, se reemplaza y se avisa por consola. Las carpetas de casos de corridas anteriores no se tocan. Para tener el resumen completo, correr la carpeta entera.
- **Colisión de nombres** (decisión 18): el nombre del caso es el del archivo. Dos archivos con el mismo nombre, en distintas carpetas, usarían la misma carpeta de evidencias: corre el primero y el segundo es un error. Se compara sin distinguir mayúsculas porque en Windows `c` y `C` serían la misma carpeta.

## Cómo modificarlo
- **Otra columna en el resumen:** agregarla en `fila_resumen` (también en la fila del caso rechazado) y en el encabezado de `escribir_resumen`.

## Pruebas
`pruebas/test_ejecutar.py`: un archivo malo en medio del lote (10 formas), el motivo en la traza, archivo inexistente, entrada inválida con traza y fila, traza vieja reemplazada, colisión de nombres, resumen de la última corrida con aviso, extensión `.JSON` y BOM. `test_ronda.py::test_ejecutar_escribe_las_evidencias`: el caso normal.

## Preguntas probables en la sustentación
- **¿Cómo se corre un caso nuevo?** Se pone el .json en una carpeta y se pasa la ruta; no se toca el código.
- **¿Qué pasa si un caso está mal?** No detiene a los demás: da `[ERROR]` o `[FALLA]`, deja el motivo en la traza y el programa termina con código 1.

_Última actualización: 2026-11-02 · lote robusto, evidencias de casos rechazados, colisiones y aviso del resumen_
