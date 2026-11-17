## 5.3 Variante (c): los vecinos alteran la utilidad del reparto

Ahora los nodos se relacionan: el presupuesto que recibe un nodo también le sirve a sus vecinos, y sus utilidades «se mueven un poco». La selección (Parte 2) no cambia: S es el conjunto que elige el voraz de la solución base. Cambia la utilidad con la que se reparten las B unidades entre los nodos de S. El enunciado no fija cómo se mueven las utilidades, así que se estudian dos modelos: en **c1** el efecto del vecino es un término aparte; en **c2** el presupuesto del vecino entra dentro de la utilidad del nodo.

| Componente | Definición |
|---|---|
| Entrada | El conjunto S de nodos seleccionados, con m = \|S\| ≤ k; B ∈ ℕ; para cada i ∈ S un coeficiente aᵢ > 0 (uᵢ(x) = aᵢ·ln(1 + x), la familia del caso de la docente) y un tope cᵢ ∈ ℕ; el grafo no dirigido de la instancia con pesos w_ij = w_ji ∈ [0, 1]; y un parámetro β ≥ 0 que mide cuánto influye un vecino. |
| Variables | x = (xᵢ)_{i∈S}: unidades asignadas a cada nodo. |
| Restricciones | Las de la Parte 1: xᵢ ∈ ℤ, 0 ≤ xᵢ ≤ mín(B, cᵢ) y Σᵢ xᵢ = mín(B, Σᵢ cᵢ). |
| Objetivo (c1, el efecto va aparte) | Maximizar U₁(x) = Σ_{j∈S} [ a_j·ln(1 + x_j) + Σ_{i∈N_S(j)} β·w_ij·ln(1 + xᵢ) ]: lo que gasta i le suma β·w_ij·ln(1 + xᵢ) a cada vecino j que está en S. |
| Objetivo (c2, el efecto va dentro) | Maximizar U₂(x) = Σ_{j∈S} a_j·ln(1 + z_j), con z_j = x_j + β·Σ_{i∈N_S(j)} w_ij·xᵢ, la «entrada efectiva» de j: el presupuesto de los vecinos cuenta como presupuesto propio, rebajado por β·w_ij. |
| Salida | Un reparto x que cumple las restricciones, junto con U(x) del modelo. |
| Tamaño de la entrada | El par (m, B) de la Parte 1, más la parte del grafo que toca a S: d(S) = Σ_{i∈S} grado(i) para encontrar los vecinos dentro de S, y A_S, las aristas con los dos extremos en S. Con S completo, A_S = m(m − 1)/2. |

**Supuestos ❓** (el enunciado no dice cómo influyen los vecinos en la utilidad):

1. **Solo cuentan los vecinos que están en S**, porque la utilidad de la ronda es la de los participantes.
2. w_ij es el `peso_influencia` de la arista {i, j} del grafo de la docente. El formato propio no trae grafo, y en él la variante se rechaza en lugar de inventar un campo nuevo; también se rechaza si alguna uᵢ no es de la familia ln.
3. β es un parámetro de la corrida, 0,2 por omisión. El modelo pide β > 0, pero se acepta β = 0 porque reproduce exactamente el reparto base: sirve para comprobar que la variante extiende la solución base sin cambiarla.

**Observación: la diferencia entre los dos modelos.** En c1, al reagrupar los términos por el nodo que gasta, U₁ vuelve a ser una suma de funciones de un solo xᵢ (§8.4.1); en c2, z_j mezcla los x de varios nodos y U₂ ya no se separa por nodo. Esa diferencia decide si el problema sigue teniendo solución exacta por un voraz.

**Relación con el escenario.** Los nodos vecinos comparten datos parecidos: menos ruido en la actualización de un nodo también mejora lo que aportan sus vecinos. En el caso de la docente el grafo es completo, así que S = {N11, N14, N09, N15, N13} tiene A_S = 10 aristas y d(S) = 5·14 = 70 (`resultados/variantes/c1_profesora/`).
