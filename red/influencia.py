"""Oráculo f de la Parte 2 para el formato de la profesora: cobertura por influencia.

f(S) = Σ_w a_w · (1 − Π_{v ∈ S} (1 − p_vw)), con a_w el coeficiente de utilidad de w,
p_vw el peso de la arista {v, w} (0 si no hay arista) y p_ww = 1 (decisión 24).

En palabras: q_w = Π_{v ∈ S} (1 − p_vw) es la probabilidad de que la información de w
siga sin entrar al equipo, y a_w · (1 − q_w) es lo que w aporta en promedio.

Tiene la misma interfaz que OraculoCobertura, así que seleccion.py no distingue entre los dos.
"""


class OraculoInfluencia:
    """Guarda los coeficientes y el grafo, y cuenta cuántas veces se le consulta."""

    def __init__(self, coeficientes, vecinos):
        """coeficientes: id → a_w. vecinos: id → {vecino: peso}; cada arista aparece en sus dos puntas."""
        self.coeficientes = coeficientes
        self.vecinos = vecinos
        self.llamadas_ganancia = 0   # evaluaciones de Δ(v | S): la operación básica del voraz
        self.llamadas_valor = 0      # evaluaciones de f(S) desde cero

    def estado_inicial(self):
        """El estado del equipo vacío: q_w = 1 para todo w (producto sin factores). Tiempo O(N)."""
        return {w: 1.0 for w in self.coeficientes}

    def ganancia(self, v, q):
        """Δ(v | S) = a_v·q_v + Σ_{w vecino de v} a_w·p_vw·q_w, con q el estado de S.

        Cada q_w baja a q_w·(1 − p_vw), así que w aporta a_w·q_w·p_vw más que antes (p_vv = 1).
        Tiempo O(1 + grado(v)). No modifica q. Precondición: v no está en S (el voraz nunca lo pide).
        Es una llamada al oráculo (línea 5 del pseudocódigo de SELECCIONAR-NODOS).
        """
        self.llamadas_ganancia += 1
        delta = self.coeficientes[v] * q[v]
        for w, peso in self.vecinos[v].items():
            delta += self.coeficientes[w] * peso * q[w]
        return delta

    def agregar(self, q, v):
        """Actualiza q EN SU LUGAR cuando v entra al equipo y lo devuelve. No cuenta como llamada.

        q_v ← 0 (porque p_vv = 1) y q_w ← q_w·(1 − p_vw) para cada vecino w.
        Tiempo O(1 + grado(v)). Precondición: v no está todavía en el equipo.
        """
        q[v] = 0.0
        for w, peso in self.vecinos[v].items():
            q[w] = q[w] * (1 - peso)
        return q

    def valor(self, S):
        """f(S) calculada desde cero. S: lista de ids sin repetir.

        Tiempo O(N + Σ_{v ∈ S} (1 + grado(v))). Se usa en f(∅) y en la verificación.
        """
        self.llamadas_valor += 1
        q = self.estado_inicial()
        for v in S:
            self.agregar(q, v)
        total = 0.0
        for w, a_w in self.coeficientes.items():
            total += a_w * (1 - q[w])
        return total
