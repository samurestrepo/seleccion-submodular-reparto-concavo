# Ficha: `scripts/serie_d_fuera_de_muestra.py`

## Para qué existe
Hace reproducible la **prueba fuera de muestra de la serie d** que cita el informe final (sección 11.3, punto 2, y sección 13). La serie d (reparto con B = 1000, N = 1000 a 16000) no ajusta a su T = N + B·lg N con una sola constante. Esta prueba pregunta cuánto de eso explica que los dos términos tengan constantes distintas: estima las constantes **solo con la serie e** y con ellas predice la serie d, que no se usó para estimar nada. No mide nada: lee dos CSV que ya existen.

Uso, desde la raíz: `python scripts/serie_d_fuera_de_muestra.py` (menos de 1 s). `--help` o `-h` imprime la ayuda y sale sin leer ni escribir nada.

## Funciones públicas
| Función | Recibe | Devuelve | Complejidad |
|---|---|---|---|
| `leer_serie(ruta)` | un CSV de `experimentos.py` | `[{'N', 'B', 't_min'}]`; no usa `t_ajustado` | O(filas) |
| `recta(xs, ys)` | datos | (α, β) de y = α + β·x por mínimos cuadrados; β es `pendiente` de `experimentos.py` | O(n) |
| `constantes_desde_e(filas_e)` | filas de la serie e (un solo N) | (a, b, α, β) con a = α/N y b = β/lg N; `ValueError` si hay más de un N | O(filas) |
| `predecir(filas_d, a, b)` | filas de la serie d y las constantes | por punto: N, B, t_min_medido, t_predicho = a·N + b·B·lg N y error_relativo = (predicho − medido)/medido | O(filas) |
| `pendientes(puntos)` | los puntos predichos | (pendiente log-log predicha, medida) contra N | O(filas) |
| `calcular(ruta_e, ruta_d)` | rutas (por omisión los CSV del repositorio) | `{'puntos': [...], 'resumen': {...}}` | O(filas) |
| `escribir_csv(ruta, resultado)`, `imprimir(resultado)` | el resultado | el CSV y la tabla por consola | O(filas) |
| `leer_argumentos(argumentos=None)`, `main(argumentos=None)` | lista de textos | `--help`/`-h`: ayuda y `SystemExit(0)`; otro argumento: `SystemExit(2)`; sin argumentos escribe el CSV y devuelve 0 | O(filas) |

## Cómo funciona
1. **Serie e** (`resultados/experimentos/e_reparto_varia_B.csv`, N = 100 fijo, B = 1000 a 16000): recta t_min = α + β·B **con** término independiente. Con N fijo, el modelo t ≈ a·N + b·B·lg N es exactamente esa recta, con α = a·100 y β = b·lg 100; se despeja a = α/100 y b = β/lg 100 (lg = log₂, el de `experimentos.py`).
2. **Serie d** (`d_reparto_varia_N.csv`, B = 1000): t predicho = a·N + b·1000·lg N con el N y el B de cada fila.
3. Error por punto y **pendiente log-log** de lo predicho y de lo medido contra N, con la misma regresión (`pendiente` de `experimentos.py` sobre logaritmos naturales; la base no cambia la pendiente).

Salida: `resultados/experimentos/d_fuera_de_muestra.csv`, columnas `tipo, N, B, t_min_medido, t_predicho, error_relativo, nombre, valor`. Hay dos tipos de fila:
- `punto` (una por N de la serie d): llena N a `error_relativo`; `nombre` y `valor` van vacías.
- `resumen` (seis filas): `nombre` ∈ {`alfa_s`, `beta_s_por_unidad`, `a_s`, `b_s`, `pendiente_predicha`, `pendiente_medida`} y su `valor`; las demás van vacías. Las constantes están en segundos (β en segundos por unidad de B).

## Resultados (CSV del repositorio, semilla 1, 2026-11-12)
α = 7,984·10⁻⁵ s, β = 1,320·10⁻⁶ s por unidad → **a = 7,98·10⁻⁷ s y b = 1,99·10⁻⁷ s**.

| N | t_min medido (s) | t predicho (s) | error |
|---|---|---|---|
| 1 000 | 0,002784 | 0,002778 | −0,2 % |
| 2 000 | 0,003710 | 0,003775 | +1,8 % |
| 4 000 | 0,005892 | 0,005570 | −5,5 % |
| 8 000 | 0,010960 | 0,008963 | −18,2 % |
| 16 000 | 0,024249 | 0,015548 | −35,9 % |

Pendiente log-log: **predicha 0,62, medida 0,78** (con una sola constante se esperaba 0,36). Lectura: la diferencia de constantes explica todo hasta N = 4000 y una parte de la pendiente (de 0,36 a 0,62); lo que aparece desde N = 8000 no lo explica (la caché es una hipótesis no comprobada).

## Por qué así
- **Fuera de muestra** (decisión 60): el ajuste conjunto de d y e de `experimentos.py` (`t_ajustado`, decisión 32) usa los mismos puntos de d que luego «predice», así que es descriptivo. Aquí las constantes salen solo de e; la evidencia que se cita es esta.
- **Recta con término independiente**, no el ajuste sin término independiente de `ajustar_reparto`: con N fijo el término a·N es justamente el independiente de la recta en B.
- **Reutiliza `pendiente`** de `experimentos.py` para que las pendientes sean comparables con las demás series. Importarlo no ejecuta nada (solo carga los módulos de `red/`).
- **No mide nada ni toca otros CSV:** solo lee d y e y escribe su propio CSV.
- `--help` con `argparse` y ayuda en cp1252, como las tablas de cota (decisión 59).

## Cómo modificarlo
Otra serie de entrenamiento o de prueba: pasar otras rutas a `calcular`. Si se vuelven a medir d o e, correr el script de nuevo y actualizar esta ficha, el informe y los valores esperados de la prueba.

## Pruebas
`pruebas/test_serie_d_fuera_de_muestra.py` (10 pruebas): a y b, el error de cada punto (tolerancia de 0,05 puntos porcentuales) y las dos pendientes contra los valores del informe, leyendo los CSV del repositorio; con datos exactos del modelo recupera a y b con error 0; una serie e con dos N se rechaza; el CSV del repositorio es igual, línea por línea (sin depender de LF o CRLF), a lo que escribe el script; `--help` y `-h` salen con 0 en consola cp1252 sin cambiar el CSV (bytes y fecha); `main(["--help"])` no lee ni escribe; un argumento desconocido da código 2.

## Preguntas probables en la sustentación
- **¿Por qué no basta el ajuste conjunto?** Porque sus constantes se calculan en parte con los puntos de d: que «ajuste» no prueba nada. Fuera de muestra, d no influye en a ni en b.
- **¿Qué dice el −35,9 % en N = 16000?** Que con las constantes de N = 100 el reparto en N grande es más lento de lo predicho: el costo por operación crece con N, cosa que ninguna constante fija capta.
- **¿Contradice O(N + B(1 + lg N))?** No: la cota es asintótica y no fija constantes.

_Última actualización: 2026-11-17 · creación (P-6 fase 1)_
