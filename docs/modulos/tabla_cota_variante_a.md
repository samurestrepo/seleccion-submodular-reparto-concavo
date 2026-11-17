# Ficha: `scripts/tabla_cota_variante_a.py`

## Para qué existe
Genera `resultados/variantes/a_tabla_cota.csv`: los tres aproximados de la variante (a) (voraz por cociente, voraz modificado y enumeración parcial) contra el OPT exacto de `seleccionar_exacto_costos`, en el caso de la docente (N = 15, L = 24) y en una batería aleatoria de influencia (decisión 38). Uso, desde la raíz: `python scripts/tabla_cota_variante_a.py` (unos 2 a 3 s); `--help` o `-h` imprime la ayuda y sale sin calcular ni escribir el CSV. No escribe en `resultados/profesora/` ni en `resultados/cota/`.

## Funciones públicas
| Función | Recibe | Devuelve | Complejidad |
|---|---|---|---|
| `fila_de_una_instancia(inst, nombre)` | instancia ya leída (con costos y L) | dict con las columnas del CSV | F evaluaciones (fuerza bruta) + O(N²) (cociente; el modificado no agrega) + O(N⁵) (enumeración) |
| `fila_de_la_profesora()` | nada | la fila del caso oficial con L = 24 | igual, con N = 15 |
| `bateria_aleatoria(tamanos, densidades, semillas, L)` | por omisión N ∈ {10, 12, 14, 16}, densidad ∈ {0.3, 0.6, 1.0}, semillas 1, 2, 3, L = 12 | 36 filas en memoria | 36 × lo anterior |
| `escribir_csv(ruta, columnas, filas)` | ruta, columnas, filas | escribe el CSV | O(filas) |
| `leer_argumentos(argumentos=None)` | lista de textos (None = `sys.argv[1:]`) | `Namespace` vacío; con `--help`/`-h` imprime la ayuda y sale con `SystemExit(0)`; otro argumento, `SystemExit(2)` | O(1) |
| `main(argumentos=None)` | lo mismo | lee los argumentos primero; sin ellos, escribe el CSV e imprime las razones mínimas; 0 si todas cumplen | suma de las anteriores |

Columnas: caso, N, L, densidad, semilla, OPT, costo_OPT, f_cociente, razon_cociente, f_modificado, razon_modificado, origen_modificado, f_enumeracion, razon_enumeracion, eval_exacto, eval_cociente, eval_modificado, eval_enumeracion, cota_modificado (0,405), cota_enumeracion (1 − 1/e), cumple.

## Cómo funciona
Cada instancia pasa por los cuatro algoritmos con un oráculo nuevo cada vez. `razon = f/OPT` (1 si OPT = 0). `cumple` = las tres razones ≤ 1, razon_modificado ≥ 0,405 y razon_enumeracion ≥ 1 − 1/e (tolerancia 1e-9). La batería usa `generar_instancia_influencia(..., presupuesto_costos=L)` y `instancia_desde_diccionario`, el camino de entrada del formato de la docente; los costos son los enteros en [1, 5] del generador. k = 5 y B = 100 solo llenan el formato (L reemplaza a k, decisión 35). N ≤ 16 mantiene 2^N ≤ 65536, bajo el límite de la fuerza bruta.

## Resultados (2026-11-16)
Docente: OPT = 146,27141 (costo 23); cociente y modificado 145,9911 (razón 0,998084, origen cociente, 74 evaluaciones); enumeración 146,27141 (razón 1,0, 13117 evaluaciones); fuerza bruta 4502 evaluaciones (subconjuntos factibles de 32768). Batería: razón mínima del cociente y del modificado 0,946839, media 0,987267, 25 de 36 con razón < 1; la enumeración alcanzó el OPT en las 36 (razón 1,0); el mejor nodo solo nunca ganó (`origen_modificado` = cociente en las 37 filas). Ninguna fila incumple las cotas.

## Por qué así
`--help` con `argparse` (P-5, decisión 59): `main` llama a `leer_argumentos` antes de calcular nada, así que la ayuda no cuesta la batería ni toca el CSV. El texto de la ayuda no reutiliza el docstring del módulo porque lleva ∈ y −, que no existen en cp1252 (la consola de Windows); se escribe aparte con caracteres de cp1252. Sin argumentos el comportamiento es el de antes (mismo CSV, byte a byte).
L = 12 con costos de promedio 3 deja entrar unos 4 nodos: ni trivial (todo cabe) ni vacío. Los parámetros de `bateria_aleatoria` permiten una batería corta en las pruebas; la reproducibilidad se comprueba con un subconjunto. La enumeración y la fuerza bruta solo son viables por el tamaño (N ≤ 16): el script muestra el costo exponencial y O(N⁵) con sus contadores.

## Cómo modificarlo
Otros tamaños o L: las constantes `TAMANOS`, `DENSIDADES`, `SEMILLAS`, `L_ALEATORIA`. Con N ≥ 18 la fuerza bruta se niega (2^N > 200000).

## Pruebas
`pruebas/test_variante_costos.py`: fila de la docente (OPT, costo, razones, cumple), batería de 36 filas con las cotas, reproducible, columnas del CSV y coincidencia del CSV del repositorio con lo que genera el script. `pruebas/test_tablas_cota_ayuda.py`: `--help` y `-h` salen con 0 por consola cp1252 y el CSV no cambia (bytes y fecha); `main(["--help"])` no llama a la escritura ni a la batería; un argumento desconocido da código 2.

## Preguntas probables en la sustentación
- **¿Qué muestra la tabla?** Que el modificado queda muy por encima de 0,405 (mínimo 0,947) y la enumeración alcanza el OPT en estas instancias; y el precio: 74 evaluaciones contra 13117 y 4502.

_Última actualización: 2026-11-17 · `--help` con argparse (P-5)_
