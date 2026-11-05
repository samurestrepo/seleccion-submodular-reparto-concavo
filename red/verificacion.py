"""Comprobación de las restricciones de entrada y de salida (informe 6.6).

Cada función devuelve una lista de Verificacion; ninguna lanza excepciones,
para que TODAS las comprobaciones queden en la traza aunque alguna falle.
"""

import math

TOLERANCIA = 1e-9  # para comparar números con decimales (sumas de logaritmos y raíces)


class Verificacion:
    """Una comprobación: su nombre, si se cumple y un detalle legible."""

    def __init__(self, nombre, cumple, detalle):
        self.nombre = nombre
        self.cumple = cumple
        self.detalle = detalle

    def a_diccionario(self):
        """La comprobación como diccionario, listo para escribirlo en JSON."""
        return {"nombre": self.nombre, "cumple": self.cumple, "detalle": self.detalle}


def _iguales(a, b):
    """True si a y b coinciden salvo el error de redondeo de los decimales."""
    return math.isclose(a, b, rel_tol=TOLERANCIA, abs_tol=TOLERANCIA)


def _ids_repetidos(ids):
    """Los ids que aparecen más de una vez, en orden. Tiempo O(N) esperado (usa un set)."""
    vistos = set()
    repetidos = set()
    for i in ids:
        if i in vistos:
            repetidos.add(i)
        vistos.add(i)
    return sorted(repetidos)


def verificar_entrada(instancia):
    """Restricciones de la entrada: k < N, B ≥ 0, ids únicos, cada u_i creciente y cóncava.

    Cada familia revisa su forma en {0, …, B}: log y raíz en O(1) mirando a > 0; tabla
    recorriendo su lista (Δ(x) ≥ 0 si x < B; Δ(x + 1) ≤ Δ(x) si x + 1 < B).
    Tiempo O(N + Σ_i min(L_i, B)) esperado, con L_i = largo de la tabla del nodo i
    (0 en log y raíz). NO se incluye en los tiempos medidos.
    """
    resultado = []
    N, k, B = instancia.N, instancia.k, instancia.B

    resultado.append(Verificacion("1 ≤ k < N", 1 <= k < N, f"k = {k}, N = {N}"))
    resultado.append(Verificacion("B ≥ 0", B >= 0, f"B = {B}"))

    repetidos = _ids_repetidos(instancia.ids())
    resultado.append(Verificacion("ids únicos", not repetidos,
                                  "sin repetidos" if not repetidos else f"repetidos: {repetidos}"))

    malos = []
    for nodo in instancia.nodos:
        problema = nodo.utilidad.revisar_forma(B, TOLERANCIA)
        if problema is not None:
            malos.append(f"nodo {nodo.id}: {problema}")
    resultado.append(Verificacion("cada u_i creciente y cóncava en {0, …, B}", not malos,
                                  "todas cumplen" if not malos else "; ".join(malos)))

    if instancia.vecinos is not None:   # solo el oráculo de influencia tiene pesos
        resultado.append(_verificar_pesos(instancia.vecinos))
    return resultado


def _verificar_pesos(vecinos):
    """Cada peso de influencia en [0, 1]; fuera de ahí f deja de ser monótona y submodular.

    Recibe id → {vecino: peso}. Cada arista está en sus dos puntas: se reporta una sola vez.
    Tiempo O(N + A), con A = número de aristas.
    """
    malos = []
    for v, adyacentes in vecinos.items():
        for w, peso in adyacentes.items():
            if v < w and not 0 <= peso <= 1:
                malos.append(f"{{{v}, {w}}}: {peso}")
    return Verificacion("cada peso de influencia en [0, 1]", not malos,
                        "todos cumplen" if not malos else "; ".join(malos))


def verificar_seleccion(instancia, oraculo, S, valorS):
    """Parte 2: S ⊆ V, sin repetidos, |S| ≤ k, y valorS = f(S) recalculada desde cero.

    valorS se compara con tolerancia: con influencia f es real y lleva error de redondeo.
    """
    resultado = []
    V = set(instancia.ids())
    resultado.append(Verificacion("S ⊆ V", set(S) <= V, f"S = {S}"))
    resultado.append(Verificacion("S sin repetidos", len(set(S)) == len(S), f"|S| = {len(S)}"))
    resultado.append(Verificacion("|S| ≤ k", len(S) <= instancia.k, f"|S| = {len(S)}, k = {instancia.k}"))
    recalculado = oraculo.valor([v for v in S if v in V])   # un id ajeno ya falló arriba; no debe lanzar KeyError
    resultado.append(Verificacion("valor acumulado = f(S) recalculada", _iguales(recalculado, valorS),
                                  f"acumulado = {valorS}, recalculado = {recalculado}"))
    return resultado


def verificar_conteo_llamadas(N, k, llamadas):
    """Las llamadas a Δ deben ser exactamente k·N − k(k−1)/2 (informe 6.3)."""
    esperado = k * N - k * (k - 1) // 2
    return [Verificacion("llamadas a Δ = k·N − k(k−1)/2", llamadas == esperado,
                         f"contadas = {llamadas}, fórmula = {esperado}")]


def verificar_reparto(S, B, utilidades, resultado_reparto, topes=None):
    """Parte 1: x_i entero en [0, B] y ≤ c_i, Σ x_i = mín(B, Σ c_i), y la utilidad coincide con Σ u_i(x_i).

    topes: id → c_i; un nodo que no aparece no tiene tope (y entonces mín(B, Σ c_i) = B).
    Las extracciones deben ser Σ x_i; las inserciones, Σ x_i menos los nodos que llegaron a su tope,
    porque esos no vuelven al montículo. Un nodo con tope 0 nunca entró, así que no se descuenta.
    La línea "x_i ≤ c_i" solo aparece si la instancia tiene topes. Tiempo O(|S|).
    """
    topes = topes or {}
    resultado = []
    x = resultado_reparto.x
    fuera = [i for i in S if not (isinstance(x[i], int) and 0 <= x[i] <= B)]
    resultado.append(Verificacion("cada x_i entero con 0 ≤ x_i ≤ B", not fuera,
                                  "todos cumplen" if not fuera else f"fallan: {fuera}"))
    if topes:
        pasados = [i for i in S if i in topes and x[i] > topes[i]]
        topes_de_S = {str(i): topes[i] for i in S if i in topes}
        resultado.append(Verificacion("cada x_i ≤ c_i", not pasados,
                                      f"c = {topes_de_S}" if not pasados else f"fallan: {pasados}"))
    suma = sum(x[i] for i in S)
    esperado = min(B, sum(topes.get(i, B) for i in S))
    resultado.append(Verificacion("Σ x_i = mín(B, Σ c_i)", suma == esperado,
                                  f"Σ x_i = {suma}, mín(B, Σ c_i) = {esperado}, B = {B}"))
    # Un x_i fuera de rango ya falló arriba; evaluar u_i con él no tendría sentido o lanzaría una excepción
    recalculada = sum(utilidades[i].valor(x[i]) for i in S if i not in fuera)
    resultado.append(Verificacion("utilidad acumulada = Σ u_i(x_i) recalculada",
                                  math.isfinite(recalculada) and _iguales(recalculada, resultado_reparto.utilidad),
                                  f"acumulada = {resultado_reparto.utilidad:.6f}, recalculada = {recalculada:.6f}"))
    en_su_tope = sum(1 for i in S if i in topes and 0 < topes[i] == x[i])
    resultado.append(Verificacion("extracciones = Σ x_i e inserciones = Σ x_i − nodos en su tope",
                                  resultado_reparto.extracciones == suma
                                  and resultado_reparto.inserciones == suma - en_su_tope,
                                  f"extracciones = {resultado_reparto.extracciones}, "
                                  f"inserciones = {resultado_reparto.inserciones}, "
                                  f"Σ x_i = {suma}, nodos en su tope = {en_su_tope}"))
    return resultado
