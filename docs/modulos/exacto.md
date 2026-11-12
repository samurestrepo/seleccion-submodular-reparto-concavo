# Ficha: `red/exacto.py`

## Para qué existe
Da el óptimo real de la **Parte 2** por fuerza bruta, para comparar al voraz (razón f(voraz)/OPT) y mostrar el costo exponencial. No se usa en la ronda ni en `ejecutar.py`.

## Funciones públicas
| Función | Recibe | Devuelve | Complejidad (tiempo · espacio) |
|---|---|---|---|
| `seleccionar_exacto(oraculo, V, k)` | oráculo con `valor(S)`, ids en orden creciente, k | `(S*, OPT, evaluaciones)`: S* como lista, OPT = f(S*), evaluaciones = C(N, k) | C(N, k) evaluaciones de f, cada una con el costo de `valor(S)` (ver cada oráculo) · O(k) más lo del oráculo |

También `DemasiadasCombinaciones` (excepción) y `LIMITE_COMBINACIONES = 200000`.

## Cómo funciona
1. Calcula C(N, k) con `math.comb`; si pasa de 200000 lanza `DemasiadasCombinaciones` con un mensaje, sin evaluar nada.
2. Recorre `itertools.combinations(V, k)`: con V ordenado, salen en orden lexicográfico de ids.
3. Por cada subconjunto llama `oraculo.valor(list(S))` (desde cero, sin estado incremental) y cuenta una evaluación.
4. Reemplaza al mejor solo si el valor es **estrictamente mayor**.

## Por qué así
- **Mismo oráculo que el voraz** (`Instancia.crear_oraculo()`): OPT y voraz miden la misma f.
- **`>` estricto:** gana el primero en orden lexicográfico (decisión 31, coherente con la 6).
- **Tope de 200000:** C(20, 10) = 184756 cabe; C(40, 20) no. Evita colgar la máquina.
- `valor(S)` también incrementa `llamadas_valor` del oráculo, por eso se usa un oráculo nuevo, no el de la ronda.

## Cómo modificarlo
- Cambiar el límite: `LIMITE_COMBINACIONES`. Desempatar por el último: cambiar `>` por `>=`. Correr `pruebas/test_exacto.py`.

## Pruebas
`pruebas/test_exacto.py`: evaluaciones = C(N, k) (y `llamadas_valor`); en los casos válidos con N <= 20 y en el de la profesora, f(voraz) <= OPT y f(voraz)/OPT >= 1 − (1 − 1/k)^k (tolerancia 1e-9); contraejemplo con OPT = 6 y S* = {2, 3}; empate al primero lexicográfico; negativa con C(40, 20) sin evaluar f.

## Preguntas probables en la sustentación
- **¿Por qué no usar esto en la ronda?** Θ(C(N, k)) evaluaciones: exponencial en k (el problema es NP-difícil).
- **¿Por qué 1 − (1 − 1/k)^k?** Es la cota del voraz de Nemhauser et al. para k pasos; siempre es ≥ 1 − 1/e.

_Última actualización: 2026-11-09 · archivo nuevo_
