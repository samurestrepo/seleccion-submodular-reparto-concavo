# Mapa del código

Qué hace cada archivo y dónde está su documentación. **Planeado** significa que el archivo todavía no existe.

## Código (`red/`)
| Archivo | Responsabilidad | Ficha | Estado |
|---|---|---|---|
| `red/entrada.py` | Leer y validar una instancia (JSON), en el formato de la profesora o en el propio. Es el único archivo que conoce los formatos, y crea el oráculo que corresponde. | `docs/modulos/entrada.md` | hecho |
| `red/cobertura.py` | Oráculo f de cobertura (formato propio): estado, f(S) y Δ(v \| S); cuenta las llamadas | `docs/modulos/cobertura.md` | hecho |
| `red/influencia.py` | Oráculo f de cobertura por influencia (formato de la profesora), con la misma interfaz | `docs/modulos/influencia.md` | hecho |
| `red/seleccion.py` | Parte 2: voraz de selección, Θ(N·k) llamadas a f | `docs/modulos/seleccion.md` | hecho |
| `red/exacto.py` | Parte 2, referencia: óptimo exacto por fuerza bruta (C(N, k) evaluaciones, se niega si C(N, k) > 200000). No forma parte de la ronda | `docs/modulos/exacto.md` | hecho |
| `red/utilidades.py` | Familias de u_i (log, raíz, tabla) y su ganancia marginal Δ_i(x) en O(1) | `docs/modulos/utilidades.md` | hecho |
| `red/reparto.py` | Parte 1: voraz con montículo (heapq) y topes por nodo opcionales, peor caso O(N + B lg N) | `docs/modulos/reparto.md` | hecho |
| `red/verificacion.py` | Comprobar las restricciones de entrada y de salida | `docs/modulos/verificacion.md` | hecho |
| `red/traza.py` | Registrar el paso a paso y escribirlo en texto y JSON | `docs/modulos/traza.md` | hecho |
| `red/ronda.py` | Orquestar una ronda: Parte 2, luego Parte 1, verificar y medir tiempos (mediana de R repeticiones) | `docs/modulos/ronda.md` | hecho |
| `red/generador.py` | Generar instancias sintéticas de tamaño creciente con semilla, en el formato propio (cobertura) o en el de la profesora (influencia, `--formato`) | `docs/modulos/generador.md` | hecho |
| `red/pd_reparto.py` | Parte 1, referencia: reparto por programación dinámica (Θ(N·B²) candidatos, Θ(N·B) espacio), correcto aun con u_i no cóncavas. No forma parte de la ronda | `docs/modulos/pd_reparto.md` | hecho |
| `scripts/tabla_cota.py` | Genera `resultados/cota/tabla_cota.csv` (y `tabla_cota_aleatoria.csv`): voraz contra OPT exacto y las cotas 1 − (1 − 1/k)^k y 1 − 1/e | `docs/modulos/tabla_cota.md` | hecho |
| `scripts/experimentos.py` | Mide el tiempo y el conteo de las 8 series (voraz Parte 2, reparto Parte 1 voraz y PD, fuerza bruta) y escribe CSV y gráficas en `resultados/experimentos/` | `docs/modulos/experimentos.md` | hecho |
| `ejecutar.py` | Línea de comandos: correr un caso o una carpeta de casos | `docs/modulos/ejecutar.md` | hecho |
| `red/__init__.py` | Marca `red/` como paquete de Python | — | hecho |

## Otros
| Ruta | Contenido |
|---|---|
| `CLAUDE.md` | Reglas de trabajo del repositorio; se lee al abrir cualquier sesión |
| `.claude/agents/ingeniero-red.md` | Definición del agente `ingeniero-red` |
| `.gitignore` | Lo que git no versiona: `__pycache__/`, `*.pyc`, `.pytest_cache/`, `.venv/` |
| `pruebas/` | Pruebas con pytest: `test_<módulo>.py`, más `test_ronda.py` (integración) y `test_ejecutar.py` (línea de comandos). Pasan desde la raíz y desde `pruebas/`, y escriben solo en `tmp_path` |
| `pruebas/test_verificacion.py` | Ramas de fallo de las verificaciones y revisión de la concavidad, con su costo medido sin reloj |
| `pruebas/test_traza.py` | Lo que anota la traza y el reporte de un caso válido o rechazado |
| `pruebas/test_ejecutar.py` | Lotes con archivos malos, evidencias de casos rechazados, colisiones de nombres y `resumen.csv` |
| `pruebas/test_generador.py` | Ayuda imprimible en cp1252, instancia guardada reproducible y a > 0 |
| `pruebas/test_influencia.py` | Oráculo de influencia: Δ = resta de valores, monotonía y submodularidad por fuerza bruta, cobertura como caso particular, costo sin reloj y cota (1 − 1/e) |
| `pruebas/test_bateria.py` | Toda la carpeta `casos/`: los válidos cumplen y dan lo esperado, los inválidos se rechazan, y la regresión del caso de la profesora. Esa regresión y `test_entrada.py` leen `casos/profesora/entrada_G2_red_15_nodos.json` |
| `pruebas/__init__.py` | Marca `pruebas/` como paquete (para importar `fuerza_bruta`) |
| `pruebas/test_exacto.py` | Conteo C(N, k) de `exacto.py`, cota del voraz contra OPT en los casos con N <= 20 y en el de la profesora, contraejemplo (OPT = 6, S* = {2, 3}), empate y negativa por tamaño |
| `resultados/cota/` | `tabla_cota.csv` y `tabla_cota_aleatoria.csv` (45 instancias aleatorias), generados por `scripts/tabla_cota.py` (nada en `resultados/profesora/`) |
| `pruebas/test_tabla_cota.py` | Batería aleatoria de la cota: 45 filas, reproducible, f_voraz <= OPT, razón en (0, 1], cumplen y columnas del CSV |
| `pruebas/fuerza_bruta.py` | Fuerza bruta **solo para pruebas** (comparar el reparto, con y sin topes, y la cota 1 − 1/e en instancias pequeñas) Aclaración: no es el exacto que se entrega (ese es `red/exacto.py`, con oráculo y conteo de evaluaciones); esta calcula f por unión directa, sin oráculo, como verificación cruzada independiente |
| `pytest.ini` | Le dice a pytest que las pruebas están en `pruebas/` |
| `requirements-dev.txt` | Dependencias externas, ambas fuera de la lógica: `pytest` (pruebas) y `matplotlib` (solo las gráficas de `scripts/experimentos.py`) |
| `pruebas/test_experimentos.py` | `medir`, conteos de las series contra las fórmulas del informe, columnas del CSV y la pendiente log-log, con tamaños mínimos |
| `pruebas/test_pd_reparto.py` | La PD iguala al voraz en los casos propios y en 200 instancias cóncavas, lo supera con una u convexa, bordes y el conteo exacto N·(B+1)(B+2)/2 |
| `resultados/experimentos/` | 8 CSV y 16 PNG (tiempo y cociente por serie) más `ajuste_reparto.png`, generados por `scripts/experimentos.py` (decisión 32) |
| `casos/CATALOGO.md` | Tabla de la batería: qué comprueba cada caso, esperado y obtenido |
| `casos/propios/` | Batería de casos válidos: ejemplos del informe, contraejemplo, bordes, empates, `tope_activo` y 5 sintéticos (N = 20 a 320, semilla 1) |
| `casos/invalidos/` | Casos que deben rechazarse: utilidad convexa, k = N, ids repetidos |
| `casos/profesora/` | Caso oficial `entrada_G2_red_15_nodos.json`; `LEEME.md` explica qué es, el comando y los supuestos |
| `resultados/` | Salidas, trazas y tiempos por caso (evidencias de la entrega); `resultados/propios/`, `resultados/invalidos/` y `resultados/profesora/` |
| `docs/curso/` | Enunciado, guía de la entrega y enlace al informe |
| `docs/modulos/` | Una ficha por archivo de código |
| `docs/agente/` | Memoria del agente: bitácora, mapa, decisiones, guía de cambios, plantilla |
| `entregables/primera_entrega/` | Archivos de la primera entrega: informe (PDF), manual técnico (PDF, exportado desde Google Docs tras importar `MANUAL_TECNICO.md`), anexo de Samuel (PDF) y `LEEME.md` |
| `README.md` | Instalación y ejecución (entregable), con la sección "Primera entrega" |
| `MANUAL_TECNICO.md` | Algoritmos, estructura, formatos, ejecución y limitaciones (entregable) |
