# Ficha: `red/entrada.py`

## Para qué existe
Lee un caso desde un archivo JSON y lo convierte en una `Instancia`. Es el **único** archivo que conoce el formato: si cambia el formato de los casos de la profesora, solo se toca este.

## Funciones públicas
| Función | Recibe | Devuelve | Complejidad (tiempo · espacio) |
|---|---|---|---|
| `leer_instancia(ruta)` | ruta de un .json (UTF-8, con o sin BOM) | `Instancia` (nombre = nombre del archivo) | O(N + M + ΣL) · O(N + M + ΣL) |
| `instancia_desde_diccionario(datos, nombre)` | contenido ya leído | `Instancia` | O(N + M + ΣL) · O(N + M + ΣL) |
| `nombre_del_caso(ruta)` | ruta | nombre del archivo sin `.json` (en mayúsculas o minúsculas) | O(largo de la ruta) |
| `Instancia.ids()`, `.conjuntos()`, `.utilidades()`, `.N` | — | ids en orden, id → C_v, id → u_i, número de nodos | O(N) |

M = total de elementos listados en los "cubre". L = largo de cada tabla de ganancias.

## Cómo funciona
1. Revisa que la raíz sea un objeto, que existan `k`, `B` y `nodos`, y que k y B sean enteros.
2. `_leer_nodo` revisa cada nodo: que sea un objeto, que traiga `id`, `cubre` (lista, sin listas ni objetos adentro) y `utilidad` (objeto), y construye la utilidad con `crear_utilidad`, que exige `a` finito y > 0 y ganancias finitas.
3. Ordena los nodos por id: ese es el "orden creciente de índice" que recorre el voraz.

Si algo no cuadra lanza `ErrorDeFormato` con un mensaje que dice qué campo falla. Eso incluye un archivo que no es UTF-8, que no es JSON, o que trae un entero o un anidamiento que Python no puede interpretar. Si el archivo no se puede abrir, sale `OSError`, que atiende `ejecutar.py`.

## Por qué así
- Revisa la **forma** y que los números de las utilidades sirvan. Las restricciones del problema (k < N, concavidad, ids únicos) las revisa `verificacion.py`, para que queden escritas en la traza.
- **`a` inválido es error de forma** (decisión 17), aunque "a > 0" sea también una condición del problema: un `a` que no es un número finito positivo ni siquiera define una utilidad de la familia. El motivo igual queda en la traza (decisión 22).
- **BOM:** es la marca invisible que algunos editores de Windows agregan al inicio de un archivo UTF-8. Se lee con `utf-8-sig`, que la acepta si está y no exige que esté.
- El formato es **provisional** (informe 6.5) mientras llegan los casos de la profesora.

## Formato provisional
```json
{"k": 2, "B": 4, "nodos": [
  {"id": 1, "cubre": ["a", "b", "c"], "utilidad": {"tipo": "log", "a": 9.0}},
  {"id": 2, "cubre": ["c", "d"], "utilidad": {"tipo": "raiz", "a": 7.0}},
  {"id": 3, "cubre": ["d", "e"], "utilidad": {"tipo": "tabla", "ganancias": [6, 3, 1]}}]}
```

## Cómo modificarlo
- **Llega otro formato:** reescribir `instancia_desde_diccionario` y `_leer_nodo` (y `leer_instancia` si no es JSON) para producir la misma `Instancia`. Agregar un caso de ejemplo y una prueba en `test_entrada.py`. Nada más cambia.
- **Un campo opcional por nodo (por ejemplo, un tope):** leerlo en `_leer_nodo` y guardarlo en `Nodo`. Receta 3 de `docs/agente/GUIA_CAMBIOS.md`.

## Pruebas
`pruebas/test_entrada.py`: lee el ejemplo del informe y ordena por id; rechaza formatos inválidos, incluidos los que antes tumbaban el programa (raíz, nodo o utilidad que no son objetos, `cubre` con listas); coeficientes y ganancias inválidos; archivos en latin-1, mal escritos, vacíos o con anidamiento sin fin; acepta BOM; nombre del caso con `.json` y `.JSON`. `pruebas/test_ejecutar.py` comprueba el efecto en un lote completo.

## Preguntas probables en la sustentación
- **¿Qué hay que cambiar si el formato es otro?** Solo este archivo; los algoritmos reciben ids, conjuntos y utilidades, no el JSON.
- **¿Qué pasa con un archivo malo?** Lanza `ErrorDeFormato`; `ejecutar.py` lo reporta como `[ERROR]` y sigue con los demás.

_Última actualización: 2026-11-02 · validación completa de la forma, a finito y > 0, UTF-8 con BOM, `nombre_del_caso`_
