# Mapa del código

Qué hace cada archivo y dónde está su documentación. **Planeado** significa que el archivo todavía no existe.

## Código (`red/`)
| Archivo | Responsabilidad | Ficha | Estado |
|---|---|---|---|
| `red/entrada.py` | Leer y validar una instancia (JSON). Es el único archivo que conoce el formato. | `docs/modulos/entrada.md` | hecho |
| `red/cobertura.py` | Oráculo f de cobertura: f(S) y Δ(v \| S); cuenta las llamadas | `docs/modulos/cobertura.md` | hecho |
| `red/seleccion.py` | Parte 2: voraz de selección, Θ(N·k) llamadas a f | `docs/modulos/seleccion.md` | hecho |
| `red/utilidades.py` | Familias de u_i (log, raíz, tabla) y su ganancia marginal Δ_i(x) en O(1) | `docs/modulos/utilidades.md` | hecho |
| `red/reparto.py` | Parte 1: voraz con montículo (heapq), O(N + B lg N) | `docs/modulos/reparto.md` | hecho |
| `red/verificacion.py` | Comprobar las restricciones de entrada y de salida | `docs/modulos/verificacion.md` | hecho |
| `red/traza.py` | Registrar el paso a paso y escribirlo en texto y JSON | `docs/modulos/traza.md` | hecho |
| `red/ronda.py` | Orquestar una ronda: Parte 2, luego Parte 1, verificar y medir tiempos | `docs/modulos/ronda.md` | hecho |
| `red/generador.py` | Generar instancias sintéticas de tamaño creciente con semilla | `docs/modulos/generador.md` | hecho |
| `ejecutar.py` | Línea de comandos: correr un caso o una carpeta de casos | `docs/modulos/ejecutar.md` | hecho |
| `red/__init__.py` | Marca `red/` como paquete de Python | — | hecho |

## Otros
| Ruta | Contenido |
|---|---|
| `pruebas/` | Pruebas con pytest: `test_<módulo>.py` y `test_ronda.py` (integración y línea de comandos) |
| `pruebas/__init__.py` | Marca `pruebas/` como paquete (para importar `fuerza_bruta`) |
| `pruebas/fuerza_bruta.py` | Fuerza bruta **solo para pruebas** (comparar el reparto y la cota 1 − 1/e en instancias pequeñas) |
| `pytest.ini` | Le dice a pytest que las pruebas están en `pruebas/` |
| `requirements-dev.txt` | Única dependencia externa: `pytest`, solo para las pruebas |
| `casos/propios/` | `ejemplo_informe.json` (sección 6.5), `contraejemplo_seleccion.json`, `sintetico_N40_k5_B60.json` (semilla 1) |
| `casos/profesora/` | Casos oficiales (cuando lleguen); `LEEME.md` explica cómo correrlos |
| `resultados/` | Salidas, trazas y tiempos por caso (evidencias de la entrega); `resultados/propios/` con los casos propios |
| `docs/curso/` | Enunciado, guía de la entrega y enlace al informe |
| `docs/modulos/` | Una ficha por archivo de código |
| `docs/agente/` | Memoria del agente: bitácora, mapa, decisiones, guía de cambios, plantilla |
| `README.md` | Instalación y ejecución (entregable) |
| `MANUAL_TECNICO.md` | Algoritmos, estructura, formatos, ejecución y limitaciones (entregable) |
