# Ficha: `red/influencia.py`

## Para qué existe
Es el **oráculo f** de la Parte 2 para el formato de la profesora, que no trae "cubre" sino un grafo con pesos de influencia. Tiene la misma interfaz que `OraculoCobertura`, así que `seleccion.py` no distingue entre los dos. Es un **supuesto de modelado adoptado** (decisión 24).

## Funciones públicas
| Función | Recibe | Devuelve | Complejidad (tiempo · espacio) |
|---|---|---|---|
| `OraculoInfluencia(coeficientes, vecinos)` | id → a_w; id → {vecino: peso}, con cada arista en sus dos puntas | el oráculo | O(1) · guarda la entrada |
| `.estado_inicial()` | — | q con q_w = 1 para todo w | O(N) · O(N) |
| `.ganancia(v, q)` | id que no está en S y estado de S | Δ(v \| S); cuenta una llamada | O(1 + grado(v)) · O(1) |
| `.agregar(q, v)` | estado e id que entra | el mismo q, actualizado en su lugar; no cuenta | O(1 + grado(v)) · O(1) |
| `.valor(S)` | lista de ids sin repetir | f(S) desde cero; cuenta en `llamadas_valor` | O(N + Σ_{v∈S} (1 + grado(v))) · O(N) |

## Cómo funciona
**La función:** f(S) = Σ_w a_w · (1 − Π_{v∈S} (1 − p_vw)), con a_w = `coeficiente_utilidad` de w, p_vw = peso de la arista {v, w} (0 si no hay arista) y p_ww = 1.

**En palabras:** cada nodo w tiene información que vale a_w. Cada v del equipo la trae con probabilidad p_vw, de forma independiente, y un nodo del equipo siempre trae la suya (p_ww = 1). El estado q_w = Π_{v∈S} (1 − p_vw) es la probabilidad de que la información de w **siga sin entrar**. Entonces a_w · (1 − q_w) es lo que w aporta en promedio, y f(S) es la suma de esos aportes.

**Δ sin recalcular todo:** cuando v entra, q_v pasa de q_v a 0 y cada vecino w pasa de q_w a q_w·(1 − p_vw). Lo que sube f es exactamente:

Δ(v | S) = a_v·q_v + Σ_{w vecino de v} a_w·p_vw·q_w

Por eso `ganancia` (**línea 5** de SELECCIONAR-NODOS) y `agregar` (**línea 8**) solo tocan a v y a sus vecinos.

## Por qué f es monótona
Agregar v solo multiplica cada q_w por (1 − p_vw), que es un número entre 0 y 1.
Entonces ningún q_w puede subir cuando entra un nodo.
Como a_w > 0, cada aporte a_w·(1 − q_w) se queda igual o sube.
Por tanto f(S ∪ {v}) ≥ f(S). Esto necesita los pesos en [0, 1]: por eso `verificar_entrada` los exige.

## Por qué f es submodular
La ganancia se puede escribir como Δ(v | S) = Σ_w a_w·p_vw·q_w(S), con v ∉ S.
Los a_w y los p_vw no dependen de S, y son mayores o iguales que 0; lo único que depende de S es q_w(S).
Si A ⊆ B, B tiene más factores entre 0 y 1 en cada producto, así que q_w(B) ≤ q_w(A).
Término a término, Δ(v | B) ≤ Δ(v | A): el mismo nodo aporta menos a un equipo más grande.

## Por qué así
- **Mantener q cuesta mucho menos que recalcular:** con q, una llamada cuesta O(1 + grado(v)). Con f(S ∪ {v}) − f(S) desde cero costaría recorrer todos los nodos y aristas de S.
- **Tiempo de la selección:** cada paso evalúa a lo sumo todos los nodos: Σ_v (1 + grado(v)) = N + 2A. Más el `agregar` y el recorrido de V, cada paso es O(N + A), y en total **O(k·(N + A))**. Las llamadas siguen siendo k·N − k(k−1)/2. Con el grafo completo del caso de la profesora, A = N(N−1)/2.
- **Espacio:** O(N) para q.
- **f(∅) = 0:** con S vacío, todo q_w = 1 y cada aporte vale 0. Junto con monotonía y submodularidad, es lo que pide la cota (1 − 1/e).
- **`valor` usa `agregar`:** las pruebas no se fían de eso; comparan `valor` con la fórmula escrita tal cual en la prueba.

**Cobertura como caso particular:** si todos los pesos son 0 o 1 y a_w = 1, entonces q_w solo vale 0 o 1, y f(S) = |⋃_{v∈S} C_v| con C_v = {v} ∪ {w : p_vw = 1}. Con a_w distintos es cobertura ponderada. Ojo: como el grafo no es dirigido, estos C_v son vecindades cerradas, no conjuntos arbitrarios; la reducción desde Cobertura Máxima del informe sigue siendo sobre la f general.

**Precisión:** `ganancia` exige v ∉ S. Para v ∈ S la resta valor(S ∪ {v}) − valor(S) es 0, pero la fórmula no lo daría, porque los vecinos ya fueron multiplicados. El voraz nunca lo pide (línea 4 salta a los de S). `agregar` y `valor` tampoco admiten repetidos: `verificar_seleccion` los reporta.

**Empates con números reales:** f es real, así que un empate exacto en teoría puede romperse por el redondeo, y entonces no ganaría el menor índice. En el caso de la profesora no pasa: con aritmética exacta (fracciones), la menor brecha entre el primero y el segundo de cada paso es 0.1037.

## Cómo modificarlo
- **Otra forma de combinar influencias:** cambiar `ganancia`, `agregar` y `valor` a la vez, y correr `pruebas/test_influencia.py`: la resta de valores, la monotonía y la submodularidad se comprueban por fuerza bruta.
- **Grafo dirigido:** `_leer_grafo` (en `entrada.py`) guardaría cada arista una sola vez y `vecinos[v]` serían los que v influye. La fórmula no cambia. La revisión de aristas repetidas también cambiaría.
- **Variante (c), presupuesto que afecta a vecinos:** no es este oráculo; afecta a la Parte 1. Pendiente de diseño.

## Pruebas
`pruebas/test_influencia.py`, con un ejemplo de 4 nodos que no es un grafo completo:
- f(∅) = 0, dos valores a mano y la fórmula de la decisión 24 escrita aparte.
- Ganancia = valor(S ∪ {v}) − valor(S) para todo S y todo v ∉ S.
- Monotonía y submodularidad por fuerza bruta (todos los A ⊆ B y v ∉ B).
- Con pesos 0 o 1 y a_w = 1, los mismos valores y el mismo S que `OraculoCobertura`.
- `agregar` actualiza en su lugar y no cuenta; `ganancia` cuenta una y no toca el estado.
- Costo sin reloj: se cuentan las posiciones del estado que se tocan (1 + grado).
- 150 instancias al azar con semilla: conteo de llamadas, acumulado = f(S) y cota (1 − 1/e) contra fuerza bruta.

## Preguntas probables en la sustentación
- **¿Qué significa q_w?** La probabilidad de que la información de w siga sin entrar al equipo.
- **¿Por qué es submodular?** Porque Δ(v | S) es una suma, con coeficientes fijos, de los q_w(S), y cada q_w solo baja cuando S crece.
- **¿Cuánto cuesta una llamada?** O(1 + grado(v)). Con el grafo completo es O(N), así que la selección es O(k·N²) en tiempo, aunque siga haciendo Θ(N·k) llamadas.
- **¿Es un dato del enunciado?** No. El archivo no dice cómo combinar los pesos: es un supuesto de modelado (decisión 24) y en el informe se declara como tal.

_Última actualización: 2026-11-04 · creación, con el caso oficial de la profesora_
