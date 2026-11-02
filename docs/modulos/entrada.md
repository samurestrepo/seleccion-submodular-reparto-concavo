# Ficha: `red/entrada.py`

## Para qué existe
Lee un caso desde un archivo JSON y lo convierte en una `Instancia`. Es el **único** archivo que conoce el formato: si cambia el formato de los casos de la profesora, solo se toca este.

## Funciones públicas
| Función | Recibe | Devuelve | Complejidad (tiempo · espacio) |
|---|---|---|---|
| `leer_instancia(ruta)` | ruta de un .json | `Instancia` (nombre = nombre del archivo) | O(N + M) · O(N + M) |
| `instancia_desde_diccionario(datos, nombre)` | diccionario ya leído | `Instancia` | O(N + M) · O(N + M) |
| `Instancia.ids()`, `.conjuntos()`, `.utilidades()`, `.N` | — | ids en orden, id → C_v, id → u_i, número de nodos | O(N) |

M = total de elementos listados en los "cubre".

## Cómo funciona
1. Revisa que existan `k`, `B` y `nodos`, y que k y B sean enteros.
2. Por cada nodo revisa `id`, `cubre` (lista) y `utilidad`, y construye la utilidad con `crear_utilidad`.
3. Ordena los nodos por id: ese es el "orden creciente de índice" que recorre el voraz.
Si algo no cuadra lanza `ErrorDeFormato` con un mensaje que dice qué campo falla.

## Por qué así
- Solo revisa la **forma**. Las restricciones del problema (k < N, concavidad, ids únicos) las revisa `verificacion.py`, para que queden escritas en la traza.
- El formato es **provisional** (informe 6.5) mientras llegan los casos de la profesora.

## Formato provisional
```json
{"k": 2, "B": 4, "nodos": [
  {"id": 1, "cubre": ["a", "b", "c"], "utilidad": {"tipo": "log", "a": 9.0}},
  {"id": 2, "cubre": ["c", "d"], "utilidad": {"tipo": "raiz", "a": 7.0}},
  {"id": 3, "cubre": ["d", "e"], "utilidad": {"tipo": "tabla", "ganancias": [6, 3, 1]}}]}
```

## Cómo modificarlo
- **Llega otro formato:** reescribir `instancia_desde_diccionario` (y `leer_instancia` si no es JSON) para producir la misma `Instancia`. Agregar un caso de ejemplo y una prueba en `test_entrada.py`. Nada más cambia.

## Pruebas
`pruebas/test_entrada.py`: lee el ejemplo del informe, ordena por id y rechaza 5 formatos inválidos.

## Preguntas probables en la sustentación
- **¿Qué hay que cambiar si el formato es otro?** Solo este archivo; los algoritmos reciben ids, conjuntos y utilidades, no el JSON.

_Última actualización: 2026-11-02 · creación_
