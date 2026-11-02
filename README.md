# seleccion-submodular-reparto-concavo

Proyecto Red · Análisis y Diseño de Algoritmos (59G8F) · Universidad de Caldas, 2026-2 · Grupo G2.
Autor: Samuel Restrepo Ramírez.

En cada ronda, una red de N nodos:
1. **Parte 2, selección:** elige k nodos que maximicen una utilidad conjunta f monótona y submodular (aquí, cobertura). El problema es NP-difícil; se usa un **voraz aproximado** con garantía ≥ (1 − 1/e)·OPT y Θ(N·k) llamadas a f.
2. **Parte 1, reparto:** reparte B unidades entre los elegidos para maximizar Σ u_i(x_i), con u_i crecientes y cóncavas. Se usa un **voraz óptimo con montículo**, O(N + B lg N).

- Informe de la primera entrega: <https://docs.google.com/document/d/1Z7U0C04y9HhB1FRQQxCu9ldMJjMfnfyggFd_Ma2NNhE/edit>
- Manual técnico: [`MANUAL_TECNICO.md`](MANUAL_TECNICO.md)

## Requisitos
- **Python 3.11 o superior.** La solución usa solo la biblioteca estándar (`heapq`, `json`, `time`, `argparse`, `random`, `csv`).
- Para correr las pruebas: `pytest` (`requirements-dev.txt`).

```
python -m pip install -r requirements-dev.txt
```

## Ejecutar
Desde la raíz del repositorio:

```
# Un caso
python ejecutar.py casos/propios/ejemplo_informe.json

# Todos los casos de una carpeta, con las evidencias en otra
python ejecutar.py casos/propios --salida resultados/propios
python ejecutar.py casos/profesora --salida resultados/profesora
```

Por cada caso se crea `<salida>/<caso>/` con:
- `salida.json`: selección, reparto, tiempos y verificaciones;
- `traza.txt` y `traza.json`: ganancias marginales de cada paso de la selección, cada unidad del reparto y el resultado de cada verificación.

Además `<salida>/resumen.csv` tiene una fila por caso. El programa termina con código 0 si todas las verificaciones cumplen.

## Generar instancias sintéticas
```
python -m red.generador --N 50 --k 5 --B 100 --semilla 1 --salida casos/propios/sintetico_N50.json
```

## Pruebas
```
python -m pytest
```
Incluyen los ejemplos del informe, los dos contraejemplos, el conteo exacto de llamadas k·N − k(k−1)/2, la comparación del reparto contra fuerza bruta y la cota (1 − 1/e) en instancias pequeñas.

## Formato de entrada (provisional)
Mientras llegan los casos de la docente se usa el formato del informe (sección 6.5); ver `MANUAL_TECNICO.md`, sección 3.

## Estructura
```
ejecutar.py          línea de comandos
red/                 la solución (un archivo por responsabilidad)
pruebas/             pruebas con pytest
casos/propios/       instancias de ejemplo
casos/profesora/     casos oficiales (pendientes)
resultados/          evidencias de ejecución
docs/modulos/        una ficha por archivo de código
docs/agente/         bitácora técnica, mapa, decisiones y guía de cambios
docs/curso/          enunciado y guía de la entrega
```
