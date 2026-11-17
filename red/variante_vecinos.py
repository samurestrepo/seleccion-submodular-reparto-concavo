"""Variante (c): los vecinos alteran la utilidad del reparto (Parte 1). Ficha: docs/modulos/variante_vecinos.md.

La Parte 2 no cambia: S sale del voraz de la solución base. Lo que cambia es la utilidad del reparto de B.
w_ij es el peso de la arista {i, j} del grafo de la instancia (formato de la docente) y β ≥ 0 es un
parámetro (0,2 por omisión). Las u_i de la docente son a_i·ln(1 + x_i) (familia log).

**Supuesto ❓ (decisión 43):** solo cuentan los vecinos que están en S, porque la utilidad de la ronda es
la de los participantes. Sin grafo (formato propio) la variante se rechaza.

Dos modelos:
- **c1, el efecto va aparte.** Lo que gasta i le suma β·w_ij·ln(1 + x_i) a cada vecino j ∈ S. Al reagrupar,
  U(x) = Σ_{i∈S} a'_i·ln(1 + x_i) con a'_i = a_i + β·Σ_{j∈S vecino de i} w_ij. Es la Parte 1 con otros
  coeficientes: valen H1 a H4 y el voraz de reparto.py es exacto (§7.1.1). Se reutiliza tal cual.
- **c2, el efecto va dentro.** U(x) = Σ_{j∈S} a_j·ln(1 + z_j), con z_j = x_j + β·Σ_{i∈S vecino de j} w_ij·x_i.
  U es cóncava pero no se separa por nodo (falla H1): ni §7.1.1 ni la PD de §7.2 aplican. Se resuelve con
  un voraz unidad por unidad (aproximado, cota 1 − (1 − 1/B)^B, ver la ficha) y se compara con un exacto
  por enumeración de todos los repartos enteros.

Este módulo no tiene pseudocódigo en el informe: los comentarios «línea N» citan el pseudocódigo de la ficha.
"""

import math
import time

from red.reparto import repartir_presupuesto
from red.ronda import _resultado_rechazado, _resumen_tiempos
from red.seleccion import seleccionar_nodos
from red.traza import Traza, _numero
from red.utilidades import UtilidadLog
from red.verificacion import (Verificacion, verificar_conteo_llamadas, verificar_entrada, verificar_reparto,
                              verificar_reparto_c2, verificar_reparto_contra_exacto, verificar_seleccion,
                              verificar_variante_c)

MODELOS = ("c1", "c2")
BETA = 0.2                  # por omisión: las utilidades «se mueven un poco»
LIMITE_REPARTOS = 200000    # mismo límite que exacto.py: por encima, la enumeración se niega a correr
SUPUESTO_C = "Supuesto ❓: solo cuentan los vecinos que están en S (decisión 43)"


class DemasiadosRepartos(Exception):
    """El número de repartos supera el límite: la enumeración no se ejecuta."""


class ResultadoVecinos:
    """Lo que devuelve el voraz de c2: x, U(x) y sus contadores."""

    def __init__(self, x, utilidad, pasos, ganancias_recalculadas, revisados):
        self.x = x                                            # id → unidades asignadas
        self.utilidad = utilidad                              # U(x) del modelo c2
        self.pasos = pasos                                    # unidades entregadas (= Σ x_i)
        self.ganancias_recalculadas = ganancias_recalculadas  # llamadas a ganancia_c2 (las iniciales incluidas)
        self.revisados = revisados                            # nodos mirados por el barrido lineal


# ---------------------------------------------------------------- piezas comunes

def vecinos_en_S(S, vecinos):
    """El grafo restringido a S: id → lista de (j, w_ij) con j ∈ S, en el orden del grafo de entrada.

    Recibe S (ids) y el grafo completo id → {vecino: peso}. Mira todos los vecinos de cada i ∈ S
    (no solo los de S: el grafo no los separa). No se ordena: el orden del archivo ya es reproducible.
    Tiempo O(|S| + Σ_{i∈S} grado(i)); espacio O(|S| + A_S), con A_S = aristas dentro de S.
    """
    en_S = set(S)
    return {i: [(j, w) for j, w in vecinos[i].items() if j in en_S] for i in S}


def _subida(a, z, d):
    """a·ln(1 + z + d) − a·ln(1 + z): lo que gana el término a·ln(1 + z) si z sube d. Tiempo O(1).

    Se escribe como resta de dos valores (no a·(ln − ln)) para dar el mismo número que
    UtilidadLog.ganancia cuando d = 1 y z es entero: así con β = 0 los empates son los de la base.
    """
    return a * math.log(1 + z + d) - a * math.log(1 + z)


# ---------------------------------------------------------------- modelo c1

def coeficientes_c1(S, coeficientes, grafo_S, beta):
    """a'_i = a_i + β·Σ_{j∈S vecino de i} w_ij para cada i ∈ S. Recibe el grafo ya restringido a S.

    Tiempo O(|S| + A_S): cada arista dentro de S se mira desde sus dos puntas. Espacio O(|S|).
    """
    return {i: coeficientes[i] + beta * sum(w for _, w in grafo_S[i]) for i in S}


def repartir_c1(S, B, coeficientes, vecinos, beta, topes=None, traza=None):
    """Modelo c1: el reparto de la Parte 1 con u_i(x) = a'_i·ln(1 + x). Devuelve (ResultadoReparto, a').

    Recibe S, B, coeficientes (id → a_i), el grafo completo, β ≥ 0, topes (id → c_i) y traza opcionales.
    Exacto por §7.1.1 (H1 a H4 se cumplen). Tiempo O(|S| + Σ_{i∈S} grado(i)) para restringir el grafo y
    calcular a' más el reparto O(|S| + B lg |S|). Espacio O(|S| + A_S).
    """
    a_prima = coeficientes_c1(S, coeficientes, vecinos_en_S(S, vecinos), beta)
    utilidades = {i: UtilidadLog(a_prima[i]) for i in S}
    return repartir_presupuesto(S, B, utilidades, traza, topes), a_prima


def utilidad_c1(x, a_prima):
    """U(x) = Σ_i a'_i·ln(1 + x_i) del modelo c1. Tiempo O(|S|)."""
    return sum(a_prima[i] * math.log(1 + x[i]) for i in x)


# ---------------------------------------------------------------- modelo c2

def utilidad_c2(x, coeficientes, grafo_S, beta):
    """U(x) = Σ_{j∈S} a_j·ln(1 + z_j), con z_j = x_j + β·Σ_{i∈S vecino de j} w_ij·x_i.

    Recibe x (id → unidades de cada i ∈ S), los coeficientes, el grafo restringido a S y β.
    Tiempo O(|S| + A_S). U(0) = 0.
    """
    total = 0.0
    for j in x:
        z_j = x[j] + beta * sum(w * x[i] for i, w in grafo_S[j])
        total += coeficientes[j] * math.log(1 + z_j)
    return total


def ganancia_c2(l, z, coeficientes, grafo_S, beta):
    """U(x + e_l) − U(x) con z el estado actual: sube z_l en 1 y z_j en β·w_lj para cada vecino j ∈ S.

    Tiempo O(1 + grado_S(l)). Es la operación básica del voraz de c2 (se cuenta afuera).
    """
    delta = _subida(coeficientes[l], z[l], 1)
    for j, w in grafo_S[l]:
        delta += _subida(coeficientes[j], z[j], beta * w)
    return delta


def _afectados(i, grafo_S):
    """Los nodos cuya ganancia cambia cuando i recibe una unidad: {i} ∪ N_S(i) ∪ N_S(N_S(i)).

    Cambian z_i y z_j (j vecino de i); la ganancia de l depende de z_l y de los z de sus vecinos,
    así que cambia para todo l a distancia ≤ 2 de i dentro de S. Tiempo O(Σ_{j∈{i}∪N_S(i)} (1 + grado_S(j))).
    """
    afectados = {i}
    for j, _ in grafo_S[i]:
        afectados.add(j)
        for l, _ in grafo_S[j]:
            afectados.add(l)
    return afectados


def repartir_c2(S, B, coeficientes, vecinos, beta, topes=None, traza=None):
    """Modelo c2: voraz unidad por unidad. Cada unidad va al nodo activo de mayor U(x + e_i) − U(x).

    Recibe S, B, coeficientes (id → a_i), el grafo completo, β ≥ 0, topes y traza opcionales.
    Barrido lineal en orden creciente de id con '>' estricto: el empate lo gana el menor id.
    Devuelve ResultadoVecinos. Tiempo O(|S| + Σ_{i∈S} grado(i)) + O(B·(|S| + A_S)); espacio O(|S| + A_S).
    No es exacto (falla H1); cota U ≥ (1 − (1 − 1/B)^B)·OPT (ficha, Nemhauser, Wolsey y Fisher).
    """
    if B > 0 and len(S) == 0:
        raise ValueError("no hay nodos a quienes repartir el presupuesto")
    topes = topes or {}
    grafo_S = vecinos_en_S(S, vecinos)
    orden = sorted(S)                                         # el barrido va por id: desempate por el menor
    x = {i: 0 for i in S}                                     # línea 1 del pseudocódigo
    z = {i: 0.0 for i in S}                                   # línea 1: z_j = x_j + β·Σ w_ij·x_i
    activos = {i for i in S if topes.get(i, B) > 0}           # línea 2: los que no están en su tope
    ganancia = {}
    recalculadas = 0
    for i in orden:                                           # línea 2: ganancias iniciales
        if i in activos:
            ganancia[i] = ganancia_c2(i, z, coeficientes, grafo_S, beta)
            recalculadas += 1
    revisados = 0
    pasos = 0
    for unidad in range(1, B + 1):                            # línea 3 del pseudocódigo
        if not activos:                                       # línea 4: todos en su tope, sobra presupuesto
            break
        elegido = None
        for i in orden:                                       # línea 5: barrido lineal, O(|S|)
            if i in activos:
                revisados += 1
                if elegido is None or ganancia[i] > ganancia[elegido]:
                    elegido = i
        delta = ganancia[elegido]
        x[elegido] += 1                                       # línea 6: la unidad va a elegido
        z[elegido] += 1
        for j, w in grafo_S[elegido]:                         # línea 6: los vecinos en S suben β·w
            z[j] += beta * w
        pasos += 1
        if x[elegido] >= topes.get(elegido, B):               # línea 7: llegó a su tope
            activos.discard(elegido)
        for l in _afectados(elegido, grafo_S):                # línea 8: solo las ganancias que cambian
            if l in activos:
                ganancia[l] = ganancia_c2(l, z, coeficientes, grafo_S, beta)
                recalculadas += 1
        if traza is not None:
            traza.unidad_reparto(unidad, elegido, delta)
    utilidad = utilidad_c2(x, coeficientes, grafo_S, beta)   # línea 9: U(x) recalculada desde x
    return ResultadoVecinos(x, utilidad, pasos, recalculadas, revisados)


# ---------------------------------------------------------------- exacto por enumeración

def contar_repartos(S, B, topes=None):
    """Cuántos vectores enteros x tienen Σ x_i ≤ B y 0 ≤ x_i ≤ c_i (sin tope, c_i = B).

    Sin topes es C(B + |S|, |S|). Cuenta por programación dinámica con sumas prefijas:
    formas[b] = repartos de los nodos vistos que suman exactamente b. Tiempo O(|S|·B), espacio O(B).
    """
    topes = topes or {}
    formas = [1] + [0] * B
    for i in S:
        c = min(topes.get(i, B), B)
        prefija = [0]
        for valor in formas:
            prefija.append(prefija[-1] + valor)
        # nuevo[b] = formas[b] + formas[b − 1] + … + formas[b − c]
        formas = [prefija[b + 1] - prefija[max(0, b - c)] for b in range(B + 1)]
    return sum(formas)


def repartir_exacto(S, B, valor_U, topes=None, limite=LIMITE_REPARTOS):
    """Óptimo por enumeración de todos los repartos enteros con Σ x_i ≤ B y x_i ≤ c_i.

    valor_U(x) evalúa la utilidad (c1 o c2) de un diccionario id → x_i. Recorre los repartos en orden
    lexicográfico de (x_{i1}, x_{i2}, …) con i1 < i2 < … y reemplaza solo con '>': gana el primero.
    Devuelve (x*, OPT, evaluados). Lanza DemasiadosRepartos, sin evaluar nada, si hay más de `limite`.
    Tiempo R·O(costo de valor_U) con R = contar_repartos (C(B + |S|, |S|) sin topes); espacio O(|S|).
    """
    topes = topes or {}
    total = contar_repartos(S, B, topes)
    if total > limite:
        raise DemasiadosRepartos(f"hay {total} repartos con Σ x_i ≤ {B}; supera el límite de {limite}: "
                                 "la enumeración no se ejecuta")
    orden = sorted(S)
    x = [0] * len(orden)
    mejor = {"x": None, "valor": float("-inf"), "evaluados": 0}

    def recorrer(posicion, restante):
        """Fija x de la posición y sigue con la próxima; en la última evalúa U. Profundidad |S|."""
        if posicion == len(orden):
            valor = valor_U(dict(zip(orden, x)))
            mejor["evaluados"] += 1
            if valor > mejor["valor"]:                        # '>' estricto: el empate lo gana el primero
                mejor["x"], mejor["valor"] = dict(zip(orden, x)), valor
            return
        for t in range(min(topes.get(orden[posicion], B), restante) + 1):
            x[posicion] = t
            recorrer(posicion + 1, restante - t)
        x[posicion] = 0

    recorrer(0, B)
    return mejor["x"], mejor["valor"], mejor["evaluados"]


def cota_c2(B):
    """1 − (1 − 1/B)^B: la cota del voraz de c2 con a lo sumo B copias (0 si B = 0). Tiempo O(1)."""
    return 1 - (1 - 1 / B) ** B if B >= 1 else 0.0


# ---------------------------------------------------------------- la ronda con la variante

def _coeficientes(instancia):
    """id → a_i de la familia log (verificar_variante_c ya revisó que todas sean log). Tiempo O(N)."""
    return {nodo.id: nodo.utilidad.a for nodo in instancia.nodos}


def _reparto_del_modelo(modelo, S, instancia, beta, traza=None):
    """El reparto del modelo pedido sobre S. Devuelve (resultado, a' o None). Mismo costo que el modelo."""
    coef = _coeficientes(instancia)
    if modelo == "c1":
        return repartir_c1(S, instancia.B, coef, instancia.vecinos, beta, instancia.topes(), traza)
    return repartir_c2(S, instancia.B, coef, instancia.vecinos, beta, instancia.topes(), traza), None


def _valor_del_modelo(modelo, S, instancia, beta, a_prima):
    """La función x ↦ U(x) del modelo, para la enumeración y para evaluar el reparto base. O(|S| + A_S) por llamada."""
    if modelo == "c1":
        return lambda x: utilidad_c1(x, a_prima)
    grafo_S = vecinos_en_S(S, instancia.vecinos)
    coef = _coeficientes(instancia)
    return lambda x: utilidad_c2(x, coef, grafo_S, beta)


def _ejecucion_medida(instancia, modelo, beta, repeticiones):
    """R veces la Parte 2 base y el reparto del modelo, sin traza y con el reloj alrededor de cada parte.

    Cada repetición usa un oráculo nuevo, creado fuera del reloj. Devuelve (corridas, tiempos_sel, tiempos_rep).
    """
    corridas, tiempos_seleccion, tiempos_reparto = [], [], []
    for _ in range(repeticiones):
        oraculo = instancia.crear_oraculo()
        inicio = time.perf_counter()
        S, valorS = seleccionar_nodos(oraculo, instancia.ids(), instancia.k)
        tiempos_seleccion.append(time.perf_counter() - inicio)
        inicio = time.perf_counter()
        reparto, a_prima = _reparto_del_modelo(modelo, S, instancia, beta)
        tiempos_reparto.append(time.perf_counter() - inicio)
        corridas.append((oraculo, S, valorS, reparto, a_prima))
    return corridas, tiempos_seleccion, tiempos_reparto


def _exacto(modelo, S, instancia, beta, a_prima, limite):
    """La enumeración como referencia (una sola vez, fuera de la medición), o el motivo si no cabe."""
    total = contar_repartos(S, instancia.B, instancia.topes())
    try:
        inicio = time.perf_counter()
        x, opt, evaluados = repartir_exacto(S, instancia.B, _valor_del_modelo(modelo, S, instancia, beta, a_prima),
                                            instancia.topes(), limite)
        segundos = time.perf_counter() - inicio
    except DemasiadosRepartos as error:
        return {"disponible": False, "repartos": total, "limite": limite, "motivo": str(error)}
    return {"disponible": True, "repartos": total, "limite": limite, "x": {str(i): x[i] for i in S},
            "OPT": opt, "evaluados": evaluados, "tiempo_segundos": segundos}


def _verificaciones_de_ejecucion(corridas, S_traza, reparto_traza):
    """Todas las repeticiones y la ejecución con traza dan el mismo S y el mismo x. Tiempo O(R·k)."""
    _, S, _, reparto, _ = corridas[0]
    distintas = [n for n, (_, otro_S, _, otro, _) in enumerate(corridas, start=1)
                 if otro_S != S or otro.x != reparto.x]
    iguales = S == S_traza and reparto.x == reparto_traza.x
    return [Verificacion("todas las repeticiones dan el mismo S y el mismo reparto", not distintas,
                         f"R = {len(corridas)}" if not distintas else f"difieren las repeticiones {distintas}"),
            Verificacion("ejecución con traza = ejecución medida", iguales,
                         "mismo S y mismo reparto" if iguales else "difieren")]


def _validar_parametros(modelo, beta, repeticiones, limite):
    """Lanza ValueError si un parámetro de la línea de comandos no sirve. Tiempo O(1)."""
    if modelo not in MODELOS:
        raise ValueError(f"modelo desconocido: {modelo!r}; los válidos son {MODELOS}")
    if isinstance(beta, bool) or not isinstance(beta, (int, float)) or not math.isfinite(beta) or beta < 0:
        raise ValueError(f"β debe ser un número finito ≥ 0; llegó {beta!r}")
    if repeticiones < 1:
        raise ValueError(f"se necesita al menos una repetición; llegó {repeticiones}")
    if limite < 0:
        raise ValueError(f"el límite de repartos debe ser ≥ 0; llegó {limite}")


def ejecutar_variante_c(instancia, modelo="c1", beta=BETA, repeticiones=1, limite=LIMITE_REPARTOS):
    """Una ronda con la variante (c): la Parte 2 base y el reparto del modelo c1 o c2, con su exacto de referencia.

    Recibe la instancia (con grafo), el modelo, β ≥ 0, R ≥ 1 y el límite de la enumeración.
    Devuelve un diccionario con las claves de una ronda base (seleccion, reparto, tiempos, verificaciones,
    traza) más `variante_c`, `exacto` y `reparto_base`. Si la entrada no cumple, el rechazo de ronda.py.
    Tiempo: R·(selección base + reparto del modelo) + la enumeración (ficha, sección T(n)).
    """
    _validar_parametros(modelo, beta, repeticiones, limite)
    entrada = {"N": instancia.N, "k": instancia.k, "B": instancia.B, "modelo": modelo, "beta": beta}
    verificaciones_entrada = [v.a_diccionario() for v in verificar_entrada(instancia) + verificar_variante_c(instancia)]
    if not all(v["cumple"] for v in verificaciones_entrada):
        return _resultado_rechazado(instancia.nombre, entrada, verificaciones_entrada)

    corridas, tiempos_seleccion, tiempos_reparto = _ejecucion_medida(instancia, modelo, beta, repeticiones)
    oraculo, S, valorS, reparto, a_prima = corridas[0]

    traza = Traza()
    S_traza, _ = seleccionar_nodos(instancia.crear_oraculo(), instancia.ids(), instancia.k, traza)
    reparto_traza, _ = _reparto_del_modelo(modelo, S_traza, instancia, beta, traza)

    exacto = _exacto(modelo, S, instancia, beta, a_prima, limite)
    valor_U = _valor_del_modelo(modelo, S, instancia, beta, a_prima)
    base = repartir_presupuesto(S, instancia.B, instancia.utilidades(), topes=instancia.topes())

    v_seleccion = verificar_seleccion(instancia, instancia.crear_oraculo(), S, valorS)
    v_seleccion += verificar_conteo_llamadas(instancia.N, instancia.k, oraculo.llamadas_ganancia)
    if modelo == "c1":
        utilidades_c1 = {i: UtilidadLog(a_prima[i]) for i in S}
        v_reparto = verificar_reparto(S, instancia.B, utilidades_c1, reparto, instancia.topes())
    else:
        v_reparto = verificar_reparto_c2(S, instancia.B, reparto, valor_U, instancia.topes())
    if exacto["disponible"]:
        cota = cota_c2(instancia.B) if modelo == "c2" else 1.0
        v_reparto += verificar_reparto_contra_exacto(modelo, reparto.utilidad, exacto["OPT"], cota)

    resultado = {
        "caso": instancia.nombre,
        "entrada": entrada,
        "variante_c": {"modelo": modelo, "beta": beta, "supuesto": SUPUESTO_C,
                       "aristas_en_S": sum(len(l) for l in vecinos_en_S(S, instancia.vecinos).values()) // 2},
        "verificaciones": {"entrada": verificaciones_entrada},
        "seleccion": {"S": S, "valor": valorS, "llamadas_ganancia": oraculo.llamadas_ganancia,
                      "llamadas_valor": oraculo.llamadas_valor},
        "reparto": {"x": {str(i): reparto.x[i] for i in S}, "utilidad": reparto.utilidad},
        "exacto": exacto,
        "reparto_base": {"x": {str(i): base.x[i] for i in S}, "utilidad_base": base.utilidad,
                         "utilidad_con_vecinos": valor_U(base.x)},
        "tiempos_segundos": {"repeticiones": repeticiones, "seleccion": _resumen_tiempos(tiempos_seleccion),
                             "reparto": _resumen_tiempos(tiempos_reparto)},
    }
    if modelo == "c1":
        resultado["variante_c"]["a_prima"] = {str(i): a_prima[i] for i in S}
        resultado["reparto"].update({"extracciones": reparto.extracciones, "inserciones": reparto.inserciones})
    else:
        resultado["reparto"].update({"pasos": reparto.pasos, "ganancias_recalculadas": reparto.ganancias_recalculadas,
                                     "revisados": reparto.revisados})
    if exacto["disponible"]:
        resultado["exacto"]["razon"] = reparto.utilidad / exacto["OPT"] if exacto["OPT"] > 0 else 1.0
        resultado["exacto"]["cota"] = cota
    resultado["verificaciones"]["seleccion"] = [v.a_diccionario() for v in v_seleccion]
    resultado["verificaciones"]["reparto"] = [v.a_diccionario() for v in v_reparto]
    resultado["verificaciones"]["ejecucion"] = [v.a_diccionario() for v in
                                                _verificaciones_de_ejecucion(corridas, S_traza, reparto_traza)]
    resultado["traza"] = traza.a_diccionario()
    resultado["todas_cumplen"] = all(v["cumple"] for lista in resultado["verificaciones"].values() for v in lista)
    return resultado


# ---------------------------------------------------------------- reporte de texto

def _lineas_verificaciones(lineas, titulo, verificaciones):
    """Agrega un bloque de verificaciones con [OK] o [FALLA]."""
    lineas.append(f"== Verificación: {titulo} ==")
    for v in verificaciones:
        lineas.append(f"  [{'OK' if v['cumple'] else 'FALLA'}] {v['nombre']}: {v['detalle']}")
    lineas.append("")


def a_texto_vecinos(resultado):
    """El reporte traza.txt de la variante (c): selección base, a' (c1), unidades, x, U, exacto y verificaciones.

    Tiempo O(tamaño del resultado).
    """
    e, vc = resultado["entrada"], resultado["variante_c"]
    titulo = ("c1: el efecto va aparte, a'_i = a_i + β·Σ w_ij; voraz con montículo (exacto)" if vc["modelo"] == "c1"
              else "c2: el efecto va dentro, u_j = a_j·ln(1 + x_j + β·Σ w_ij·x_i); voraz unidad por unidad")
    lineas = [f"CASO: {resultado['caso']}", f"N = {e['N']}, k = {e['k']}, B = {e['B']}",
              f"VARIANTE ({titulo}), β = {vc['beta']}. {vc['supuesto']}", ""]
    _lineas_verificaciones(lineas, "entrada", resultado["verificaciones"]["entrada"])

    s = resultado["seleccion"]
    lineas.append("== Parte 2: selección de nodos (voraz de la solución base, sin cambios) ==")
    for p in resultado["traza"]["pasos_seleccion"]:
        lineas.append(f"  Paso {p['paso']}: elige {p['elegido']} (Δ = {_numero(p['ganancia_elegido'])}); "
                      f"f(S) = {_numero(p['valor_despues'])}")
    lineas.append(f"  Resultado: S = {s['S']}, f(S) = {_numero(s['valor'])}; "
                  f"aristas dentro de S = {vc['aristas_en_S']}")
    lineas.append("")

    if vc["modelo"] == "c1":
        lineas.append("== Coeficientes nuevos a'_i ==")
        lineas.append("  " + ", ".join(f"a'_{i} = {_numero(a)}" for i, a in vc["a_prima"].items()))
        lineas.append("")
    lineas.append(f"== Parte 1: reparto ({vc['modelo']}) ==")
    for u in resultado["traza"]["unidades_reparto"]:
        lineas.append(f"  Unidad {u['unidad']}: al nodo {u['nodo']} (Δ = {_numero(u['ganancia'])})")
    r = resultado["reparto"]
    lineas.append(f"  Resultado: {', '.join(f'x_{i} = {x}' for i, x in r['x'].items())}; U = {r['utilidad']:.6f}")
    if vc["modelo"] == "c2":
        lineas.append(f"  Contadores: pasos = {r['pasos']}, ganancias recalculadas = {r['ganancias_recalculadas']}, "
                      f"revisados en el barrido = {r['revisados']}")
    base = resultado["reparto_base"]
    lineas.append(f"  Reparto base (sin vecinos): {', '.join(f'x_{i} = {x}' for i, x in base['x'].items())}; "
                  f"U con vecinos = {base['utilidad_con_vecinos']:.6f}")
    lineas.append("")

    ex = resultado["exacto"]
    lineas.append("== Referencia: exacto por enumeración ==")
    if ex["disponible"]:
        lineas.append(f"  {ex['repartos']} repartos evaluados; x* = "
                      f"{', '.join(f'x_{i} = {x}' for i, x in ex['x'].items())}; OPT = {ex['OPT']:.6f}; "
                      f"razón U/OPT = {ex['razon']:.6f} (cota {ex['cota']:.6f})")
    else:
        lineas.append(f"  No disponible: {ex['motivo']}")
    lineas.append("")

    for parte, nombre in (("seleccion", "Parte 2"), ("reparto", "Parte 1"), ("ejecucion", "Ejecución")):
        _lineas_verificaciones(lineas, nombre, resultado["verificaciones"][parte])
    t = resultado["tiempos_segundos"]
    lineas.append(f"== Tiempos: mediana de {t['repeticiones']} repeticiones (sin el exacto) ==")
    lineas.append(f"  Parte 2 (selección): {t['seleccion']['mediana']:.9f} s")
    lineas.append(f"  Parte 1 (reparto):   {t['reparto']['mediana']:.9f} s")
    lineas.append("")
    lineas.append(f"TODAS LAS VERIFICACIONES: {'CUMPLEN' if resultado['todas_cumplen'] else 'HAY FALLAS'}")
    return "\n".join(lineas) + "\n"
