# Ficha: `red/cobertura.py`

## Para qué existe
Es el **oráculo f** de la Parte 2: dado un equipo S, dice cuántos elementos distintos cubren sus nodos. También calcula la ganancia Δ(v | S) y **cuenta las llamadas**, porque el costo de la Parte 2 se mide en llamadas a f.

## Funciones públicas
| Función | Recibe | Devuelve | Complejidad (tiempo · espacio) |
|---|---|---|---|
| `OraculoCobertura(conjuntos)` | diccionario id → C_v | el oráculo | O(1) · guarda la entrada |
| `.valor(S)` | lista de ids | f(S) = \|⋃ C_v\| | O(Σ_{v∈S} \|C_v\|) · O(\|U\|) |
| `.ganancia(v, cubiertos)` | id y cub(S) ya calculado | Δ(v \| S) = \|C_v ∖ cub(S)\| | O(\|C_v\|) · O(1) |
| `.conjunto(v)` | id | C_v | O(1), no cuenta |

## Cómo funciona
- `valor` une los conjuntos desde cero. Se usa para f(∅) y para la verificación (comparar con el valor acumulado).
- `ganancia` recorre los elementos de C_v una sola vez y cuenta los que no están en `cubiertos`. Es la **línea 5** de SELECCIONAR-NODOS.
- Dos contadores separados: `llamadas_ganancia` (la operación básica del voraz) y `llamadas_valor`.

## Por qué así
- La ganancia se calcula directamente como "lo nuevo que trae v" (informe 5.6) en lugar de f(S ∪ {v}) − f(S): da el mismo número sin recalcular la unión. La prueba `test_ganancia_coincide_con_la_resta_de_valores` lo comprueba.
- Es un oráculo y no una tabla porque una tabla tendría 2ᴺ filas (informe 5.5).

## Cómo modificarlo
- **Otra función submodular:** escribir otra clase con los mismos métodos (`valor`, `ganancia`, `conjunto`) y los mismos contadores. `seleccion.py` no cambia.
- **Imprimir cuántas llamadas se hicieron:** ya está en `salida.json` y en la traza (`llamadas_ganancia`).

## Pruebas
`pruebas/test_cobertura.py`: los valores del informe (f({1,3}) = 5, f({1,2}) = 4), la tabla de submodularidad de la sección 5.6 (Δ(3 \| ∅) = 2, Δ(3 \| {2}) = 1) y que la ganancia coincide con la resta de valores en todos los pares (S, v) de ese ejemplo.

## Preguntas probables en la sustentación
- **¿Qué cuenta como "llamada a f"?** Cada evaluación de Δ(v \| S) en el voraz. Se cuentan con `llamadas_ganancia`.
- **¿Cuánto cuesta una llamada con cobertura?** O(\|C_v\|), porque cada pregunta "¿ya está cubierto?" es O(1) esperado en un `set`.

_Última actualización: 2026-11-02 · la prueba de la resta cubre todos los pares; el código no cambió_
