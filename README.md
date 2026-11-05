# seleccion-submodular-reparto-concavo

Proyecto Red · Análisis y Diseño de Algoritmos (59G8F) · Universidad de Caldas, 2026-2 · Grupo G2.
Autor: Samuel Restrepo Ramírez.

En cada ronda, una red de N nodos:
1. **Parte 2, selección:** elige k nodos que maximicen una utilidad conjunta f monótona y submodular (cobertura en el formato propio; cobertura por influencia en el de la profesora). El problema es NP-difícil; se usa un **voraz aproximado** con garantía ≥ (1 − 1/e)·OPT y Θ(N·k) llamadas a f.
2. **Parte 1, reparto:** reparte B unidades entre los elegidos para maximizar Σ u_i(x_i), con u_i crecientes y cóncavas. Se usa un **voraz óptimo con montículo**, O(N + B lg N).

- Informe de la primera entrega (versión oficial): [`entregables/primera_entrega/1_Informe_Primera_Entrega_G2.pdf`](entregables/primera_entrega/1_Informe_Primera_Entrega_G2.pdf). Versión de consulta en Google Docs, que puede tener cambios posteriores a la etiqueta: <https://docs.google.com/document/d/1Z7U0C04y9HhB1FRQQxCu9ldMJjMfnfyggFd_Ma2NNhE/edit>
- Manual técnico: [`MANUAL_TECNICO.md`](MANUAL_TECNICO.md)

## Primera entrega
Versión: etiqueta `primera-entrega` del repositorio. Para reproducir el caso de la docente, desde la raíz:

```
python ejecutar.py casos/profesora --salida resultados/profesora
```

Sus evidencias quedan en `resultados/profesora/` (`resumen.csv` y, en `entrada_G2_red_15_nodos/`, `salida.json`, `traza.json` y `traza.txt`). El informe y el anexo (PDF) están en `entregables/primera_entrega/` (ver su `LEEME.md`). El manual técnico es [`MANUAL_TECNICO.md`](MANUAL_TECNICO.md), en la raíz (https://github.com/samurestrepo/seleccion-submodular-reparto-concavo/blob/primera-entrega/MANUAL_TECNICO.md, en la etiqueta `primera-entrega`).

## Uso de inteligencia artificial
El curso permite el uso de IA. En este proyecto se usó Claude, con un agente configurado para el repositorio (`.claude/agents/ingeniero-red.md` y `CLAUDE.md`), en la parte operativa: implementación, pruebas, evidencias y documentación. El planteamiento del problema, las demostraciones y la sustentación son responsabilidad del autor.

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
python ejecutar.py casos/invalidos --salida resultados/invalidos   # deben rechazarse
python ejecutar.py casos/profesora --salida resultados/profesora

# Cambiar las repeticiones de la medición (por omisión, 21)
python ejecutar.py casos/profesora --repeticiones 5 --salida resultados/prueba
```

Un caso rechazado (archivo con forma inválida o entrada que no cumple las restricciones) no detiene a los demás: los algoritmos no corren y sus tres archivos traen el motivo. Dos archivos con el mismo nombre de caso son un error: corre solo el primero. El programa termina con código 0 si todas las verificaciones cumplen.

## Formatos de entrada
`red/entrada.py` reconoce dos. Si el objeto tiene `"parametros"`, es el de la profesora; si no, es el propio. El detalle de cada campo está en `MANUAL_TECNICO.md`, sección 3.

**Formato de la profesora** (`casos/profesora/`):
```json
{
  "parametros": {
    "numero_nodos": 2, "numero_rondas": 3,
    "cupo_participantes_por_ronda_k": 1, "presupuesto_ruido_por_ronda_B": 30,
    "presupuesto_costos_participacion_por_ronda": 24
  },
  "grafo": [{"u": "N01", "v": "N02", "peso_influencia": 0.25}],
  "nodos": [
    {"id": "N01", "coeficiente_utilidad": 8.5, "presupuesto_total_nodo": 18, "costo_participacion": 3},
    {"id": "N02", "coeficiente_utilidad": 10.2, "presupuesto_total_nodo": 18, "costo_participacion": 5}
  ]
}
```
El archivo no dice cómo usar los datos, así que se adoptaron estos **supuestos de modelado** (decisiones 24 a 26; ver `casos/profesora/LEEME.md`):
- f(S) = Σ_w a_w · (1 − Π_{v∈S} (1 − p_vw)), con a_w = `coeficiente_utilidad`, p_vw = `peso_influencia` (0 si no hay arista) y p_ww = 1.
- u_i(x) = `coeficiente_utilidad` · ln(1 + x).
- La solución base corre **una** ronda con k y B. `numero_rondas`, `costo_participacion` y `presupuesto_costos_participacion_por_ronda` solo se reportan.
- `presupuesto_total_nodo` es el tope x_i ≤ c_i (decisión 28): lo que le queda al nodo para todo el proyecto, que en una ronda puede gastar completo.

**Formato propio** (`casos/propios/`, provisional, informe 6.5): `{"k": 2, "B": 4, "nodos": [{"id": 1, "cubre": ["a", "b"], "utilidad": {"tipo": "log", "a": 9.0}, "tope": 3}, ...]}`. El campo `tope` es opcional.

Si los topes de los elegidos suman menos que B, el sobrante queda sin gastar, y eso no es una falla.

## Formato de salida
Por cada caso se crea `<salida>/<caso>/` con tres archivos, y `<salida>/` tiene además `resumen.csv`.

**`salida.json`**
| Campo | Contenido |
|---|---|
| `caso` | nombre del archivo, sin `.json` |
| `entrada` | `N`, `k`, `B` |
| `seleccion` | `S` (en orden de elección), `valor` = f(S), `llamadas_ganancia`, `llamadas_valor` |
| `reparto` | `x` (id → unidades), `utilidad` = Σ u_i(x_i), `extracciones`, `inserciones` |
| `tiempos_segundos` | `repeticiones` (R), y para `seleccion` y `reparto`: `mediana`, `minimo` y `maximo` de las R repeticiones. Solo el algoritmo |
| `verificaciones` | listas `entrada`, `seleccion`, `reparto` y `ejecucion`, cada una con `nombre`, `cumple` y `detalle` |
| `todas_cumplen` | `true` si todas las verificaciones cumplen |
| `informativo` | solo en el formato de la profesora: datos de las variantes (a) y (b), con el texto "no se aplica en la solución base". No es una verificación ni entra en `todas_cumplen` |

**`traza.txt`** es el reporte legible, por secciones: la entrada y sus verificaciones; la Parte 2 (Δ de cada candidato, elegido y f(S) por paso); la Parte 1 (a qué nodo va cada unidad y su Δ); las verificaciones de cada parte; `Informativo` (solo en el formato de la profesora); la mediana de los tiempos; y una línea final con `CUMPLEN` o `HAY FALLAS`. Si el caso se rechazó, trae solo la entrada, sus verificaciones y el motivo.

**`traza.json`** trae los mismos pasos para un programa: `pasos_seleccion` y `unidades_reparto` (y `motivo_rechazo` si el caso se rechazó).

**`resumen.csv`** tiene una fila por caso **de la última corrida**: no acumula, y si ya existía se reemplaza con un aviso por consola. Columnas: `caso, N, k, B, S, f(S), utilidad_reparto, tiempo_seleccion_s, tiempo_reparto_s, minimo_seleccion_s, minimo_reparto_s, repeticiones, todas_cumplen`. Los tiempos son las medianas; los `minimo_*` son los mínimos de las R repeticiones y son los que se usan para la gráfica de T(n) (decisión 30). S va separado por espacios, y un caso rechazado deja vacíos S, f(S), utilidad, tiempos, mínimos y repeticiones.

## Generar instancias sintéticas
```
python -m red.generador --N 50 --k 5 --B 100 --semilla 1 --salida casos/propios/sintetico_N50.json
```

## Pruebas
```
python -m pytest
```
Incluyen los ejemplos del informe, los dos contraejemplos, el conteo exacto de llamadas k·N − k(k−1)/2, la comparación del reparto contra fuerza bruta, la cota (1 − 1/e) en instancias pequeñas, archivos y entradas inválidos, las ramas de fallo de las verificaciones, la monotonía y submodularidad de f por fuerza bruta y la regresión del caso de la profesora. Pasan desde la raíz y desde `pruebas/`, y no escriben en `resultados/`.

## Estructura
```
ejecutar.py          línea de comandos
red/                 la solución (un archivo por responsabilidad)
pruebas/             pruebas con pytest
casos/propios/       batería de casos válidos (ver casos/CATALOGO.md)
casos/invalidos/     casos que deben rechazarse
casos/profesora/     caso oficial y sus supuestos (LEEME.md)
resultados/          evidencias de ejecución
docs/modulos/        una ficha por archivo de código
docs/agente/         bitácora técnica, mapa, decisiones y guía de cambios
docs/curso/          enunciado y guía de la entrega
```
