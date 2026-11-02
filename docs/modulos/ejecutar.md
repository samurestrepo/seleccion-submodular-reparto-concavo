# Ficha: `ejecutar.py`

## Para qué existe
Es la línea de comandos: corre una ronda por cada caso y guarda las evidencias que pide la entrega (resultado, tiempo y traza por caso).

## Funciones públicas
| Función | Recibe | Devuelve |
|---|---|---|
| `main(argumentos)` | rutas de archivos o carpetas, `--salida` | código 0 si todo cumple, 1 si algo falla |
| `buscar_casos(rutas)` | rutas | lista de .json (una carpeta aporta los suyos en orden alfabético) |
| `guardar_evidencias(resultado, carpeta)` | resultado de la ronda | escribe salida.json, traza.json y traza.txt |

## Cómo funciona
Para cada caso: `leer_instancia` → `ejecutar_ronda` → `guardar_evidencias` en `<salida>/<caso>/`. Al final escribe `<salida>/resumen.csv` con una fila por caso (S, f(S), utilidad, tiempos, si cumple) e imprime una línea por caso.

Ejemplos:
```
python ejecutar.py casos/propios/ejemplo_informe.json
python ejecutar.py casos/profesora --salida resultados/profesora
```

## Por qué así
La guía exige que sea reproducible **sin editar la lógica**: los casos entran por archivo y la salida va a una carpeta. Un archivo con formato inválido se reporta como `[ERROR]` y no detiene a los demás.

## Cómo modificarlo
- **Otra columna en el resumen:** agregarla en `filas.append(...)` y en el encabezado del CSV.

## Pruebas
`test_ronda.py::test_ejecutar_escribe_las_evidencias`.

## Preguntas probables en la sustentación
- **¿Cómo se corre un caso nuevo?** Se pone el .json en una carpeta y se pasa la ruta; no se toca el código.

_Última actualización: 2026-11-02 · creación_
