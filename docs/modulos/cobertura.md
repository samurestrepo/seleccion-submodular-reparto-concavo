# Ficha: `red/cobertura.py`

## Para qué existe
Es el **oráculo f** de la Parte 2: dado un equipo S, dice cuántos elementos distintos cubren sus nodos. También calcula la ganancia Δ(v | S) y **cuenta las llamadas**, porque el costo de la Parte 2 se mide en llamadas a f.

## Funciones públicas
| Función | Recibe | Devuelve | Complejidad (tiempo · espacio) |
|---|---|---|---|
| `OraculoCobertura(conjuntos)` | diccionario id → C_v | el oráculo | O(1) · guarda la entrada |
| `.valor(S)` | lista de ids | f(S) = \|⋃ C_v\| | O(Σ_{v∈S} \|C_v\|) · O(\|U\|) |
| `.estado_inicial()` | — | el estado del equipo vacío: un `set` vacío, nuevo | O(1) |
| `.ganancia(v, estado)` | id y cub(S) ya calculado | Δ(v \| S) = \|C_v ∖ cub(S)\| | O(\|C_v\|) · O(1) |
| `.agregar(estado, v)` | estado e id que entra | el mismo `set`, actualizado en su lugar (`estado \|= C_v`); no cuenta | O(\|C_v\|) · O(\|C_v\|) |

## Cómo funciona
- `valor` une los conjuntos desde cero. Se usa para f(∅) y para la verificación (comparar con el valor acumulado).
- `ganancia` recorre los elementos de C_v una sola vez y cuenta los que no están en el estado. Es la **línea 5** de SELECCIONAR-NODOS.
- `agregar` suma C_v al estado cuando v entra al equipo. Es parte de la **línea 8**. Cuesta lo mismo que la línea que reemplazó.
- Dos contadores separados: `llamadas_ganancia` (la operación básica del voraz) y `llamadas_valor`.

## Por qué así
- La ganancia se calcula directamente como "lo nuevo que trae v" (informe 5.6) en lugar de f(S ∪ {v}) − f(S): da el mismo número sin recalcular la unión. La prueba `test_ganancia_coincide_con_la_resta_de_valores` lo comprueba.
- Es un oráculo y no una tabla porque una tabla tendría 2ᴺ filas (informe 5.5).
- **Estado explícito:** el voraz guarda un "estado" que no sabe interpretar, y se lo pasa al oráculo. Aquí es cub(S); en `red/influencia.py` son los q_w. Así el voraz sirve para cualquier f con esta interfaz. El antiguo método `conjunto(v)` desapareció, porque solo tenía sentido en cobertura.

## Cómo modificarlo
- **Otra función submodular:** escribir otra clase con los mismos métodos (`estado_inicial`, `ganancia`, `agregar`, `valor`) y los mismos contadores, y devolverla desde `Instancia.crear_oraculo`. `seleccion.py` no cambia. `red/influencia.py` es el ejemplo.
- **Imprimir cuántas llamadas se hicieron:** ya está en `salida.json` y en la traza (`llamadas_ganancia`).

## Pruebas
`pruebas/test_cobertura.py`: los valores del informe (f({1,3}) = 5, f({1,2}) = 4), la tabla de submodularidad de la sección 5.6 (Δ(3 \| ∅) = 2, Δ(3 \| {2}) = 1) que la ganancia coincide con la resta de valores en todos los pares (S, v) de ese ejemplo, y que `agregar` actualiza en su lugar sin contar una llamada ni tocar el dato de entrada.

## Preguntas probables en la sustentación
- **¿Qué cuenta como "llamada a f"?** Cada evaluación de Δ(v \| S) en el voraz. Se cuentan con `llamadas_ganancia`.
- **¿Cuánto cuesta una llamada con cobertura?** O(\|C_v\|), porque cada pregunta "¿ya está cubierto?" es O(1) esperado en un `set`.

_Última actualización: 2026-11-04 · interfaz con estado explícito: `estado_inicial` y `agregar` reemplazan a `conjunto`_
