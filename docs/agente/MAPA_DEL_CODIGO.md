# Mapa del código

Qué hace cada archivo y dónde está su documentación. **Planeado** significa que el archivo todavía no existe.

## Código (`red/`)
| Archivo | Responsabilidad | Ficha | Estado |
|---|---|---|---|
| `red/entrada.py` | Leer y validar una instancia (JSON). Es el único archivo que conoce el formato. | `docs/modulos/entrada.md` | planeado |
| `red/cobertura.py` | Oráculo f de cobertura: f(S) y Δ(v \| S); cuenta las llamadas | `docs/modulos/cobertura.md` | planeado |
| `red/seleccion.py` | Parte 2: voraz de selección, Θ(N·k) llamadas a f | `docs/modulos/seleccion.md` | planeado |
| `red/utilidades.py` | Familias de u_i (log, raíz) y su ganancia marginal Δ_i(x) en O(1) | `docs/modulos/utilidades.md` | planeado |
| `red/reparto.py` | Parte 1: voraz con montículo (heapq), O(N + B lg N) | `docs/modulos/reparto.md` | planeado |
| `red/verificacion.py` | Comprobar las restricciones de entrada y de salida | `docs/modulos/verificacion.md` | planeado |
| `red/traza.py` | Registrar el paso a paso y escribirlo en texto y JSON | `docs/modulos/traza.md` | planeado |
| `red/ronda.py` | Orquestar una ronda: Parte 2, luego Parte 1, verificar y medir tiempos | `docs/modulos/ronda.md` | planeado |
| `red/generador.py` | Generar instancias sintéticas de tamaño creciente con semilla | `docs/modulos/generador.md` | planeado |
| `ejecutar.py` | Línea de comandos: correr un caso o una carpeta de casos | `docs/modulos/ejecutar.md` | planeado |

## Otros
| Ruta | Contenido |
|---|---|
| `pruebas/` | Pruebas con pytest; una por módulo más los ejemplos del informe |
| `casos/propios/` | Instancias de ejemplo en el formato provisional |
| `casos/profesora/` | Casos oficiales (cuando lleguen) |
| `resultados/` | Salidas, trazas y tiempos por caso (evidencias de la entrega) |
| `docs/curso/` | Enunciado, guía de la entrega y enlace al informe |
| `docs/modulos/` | Una ficha por archivo de código |
| `docs/agente/` | Memoria del agente: bitácora, mapa, decisiones, guía de cambios, plantilla |
| `README.md` | Instalación y ejecución (entregable) |
| `MANUAL_TECNICO.md` | Algoritmos, estructura, formatos, ejecución y limitaciones (entregable) |
