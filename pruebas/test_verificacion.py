"""Pruebas de verificacion.py: complejidad sin reloj (H3), bordes de la concavidad (H10) y ramas de fallo."""

import pytest

from red.cobertura import OraculoCobertura
from red.entrada import Instancia, Nodo
from red.influencia import OraculoInfluencia
from red.reparto import ResultadoReparto
from red.ronda import ejecutar_ronda
from red.utilidades import UtilidadLog, UtilidadRaiz, UtilidadTabla
from red.verificacion import (verificar_conteo_llamadas, verificar_entrada, verificar_reparto,
                              verificar_seleccion)

ENORME = 10**12  # con un recorrido de las B unidades, estas pruebas no terminarían


def concavidad(utilidad, B):
    """La verificación "creciente y cóncava" de una instancia con esa utilidad y otro nodo normal."""
    instancia = Instancia(1, B, [Nodo(1, [], utilidad), Nodo(2, [], UtilidadLog(1.0))])
    return verificar_entrada(instancia)[3]


class IdContado(int):
    """Un id que cuenta cuántas veces se compara con ==."""
    comparaciones = 0
    __hash__ = int.__hash__

    def __eq__(self, otro):
        IdContado.comparaciones += 1
        return int.__eq__(self, otro)


def test_ids_repetidos_sin_comparar_todos_contra_todos():
    # H3: ids.count hacía del orden de N² comparaciones
    IdContado.comparaciones = 0
    N = 500
    nodos = [Nodo(IdContado(i), [], UtilidadLog(1.0)) for i in range(N)]
    verificar_entrada(Instancia(1, 0, nodos))
    assert IdContado.comparaciones <= N


def test_ids_repetidos_se_reportan():
    nodos = [Nodo(i, [], UtilidadLog(1.0)) for i in (3, 1, 3, 2, 1)]
    ids_unicos = verificar_entrada(Instancia(1, 0, nodos))[2]
    assert not ids_unicos.cumple
    assert ids_unicos.detalle == "repetidos: [1, 3]"


@pytest.mark.parametrize("familia", [UtilidadLog, UtilidadRaiz])
@pytest.mark.parametrize("a", [1.0, 1e6, 1e9])
def test_log_y_raiz_se_revisan_sin_recorrer_B(familia, a):
    # H3 y H17: es O(1), y por eso el ruido flotante (x ≥ 1e8, a grande) ya no da un falso "no cóncava"
    class SinRecorrer(familia):
        def ganancia(self, x):
            raise AssertionError("verificar_entrada no debe recorrer las unidades de log ni raíz")

    assert concavidad(SinRecorrer(a), ENORME).cumple


def test_tabla_se_revisa_en_el_largo_de_su_lista():
    # H3: O(L) aunque B sea enorme
    class Contada(UtilidadTabla):
        llamadas = 0

        def ganancia(self, x):
            Contada.llamadas += 1
            assert Contada.llamadas <= 40, "la revisión recorre más que la lista"
            return super().ganancia(x)

    assert concavidad(Contada([5, 4, 3, 2, 1]), ENORME).cumple


@pytest.mark.parametrize("ganancias, B", [
    ([3, 2, 5], 2),    # Δ(2) = 5 no se entrega nunca: u es cóncava en {0, 1, 2}
    ([1, -1], 1),      # Δ(1) < 0 no se entrega nunca: u es creciente en {0, 1}
    ([-1], 0),         # sin presupuesto no se entrega ninguna unidad
    ([1, 10], 1),
])
def test_solo_importan_las_unidades_que_se_entregan(ganancias, B):
    # H10: antes se rechazaban por mirar una posición de más
    assert concavidad(UtilidadTabla(ganancias), B).cumple


@pytest.mark.parametrize("ganancias, B, motivo", [
    ([3, 2, 5], 3, "Δ(2) > Δ(1) (no es cóncava)"),
    ([1, 10], 2, "Δ(1) > Δ(0) (no es cóncava)"),
    ([1, -1], 2, "Δ(1) < 0 (no es creciente)"),
    ([-1, -2], 1, "Δ(0) < 0 (no es creciente)"),
])
def test_tabla_mala_dentro_del_presupuesto_se_rechaza(ganancias, B, motivo):
    revision = concavidad(UtilidadTabla(ganancias), B)
    assert not revision.cumple
    assert motivo in revision.detalle


@pytest.mark.parametrize("ganancias", [[], [5], [4, 1]])
def test_tabla_corta_sigue_siendo_valida(ganancias):
    # Después de la lista cada unidad aporta 0
    assert concavidad(UtilidadTabla(ganancias), 50).cumple


@pytest.mark.parametrize("familia", [UtilidadLog, UtilidadRaiz])
@pytest.mark.parametrize("a", [0.0, -2.0, float("nan"), float("inf")])
def test_coeficiente_malo_creado_directamente_se_rechaza(familia, a):
    assert not concavidad(familia(a), 3).cumple


def resultado_seleccion(S, valorS, k=2):
    instancia = Instancia(k, 0, [Nodo(i, [f"e{i}"], UtilidadLog(1.0)) for i in (1, 2, 3)])
    verificaciones = verificar_seleccion(instancia, OraculoCobertura(instancia.conjuntos()), S, valorS)
    return {v.nombre: v.cumple for v in verificaciones}


def test_seleccion_correcta_cumple_todo():
    assert all(resultado_seleccion([1, 2], 2).values())


@pytest.mark.parametrize("S, valorS, falla", [
    ([1, 9], 1, "S ⊆ V"),
    ([1, 1], 1, "S sin repetidos"),
    ([1, 2, 3], 3, "|S| ≤ k"),
    ([1, 2], 7, "valor acumulado = f(S) recalculada"),
])
def test_seleccion_mala_se_detecta(S, valorS, falla):
    assert [nombre for nombre, cumple in resultado_seleccion(S, valorS).items() if not cumple][-1] == falla


def test_conteo_de_llamadas():
    assert verificar_conteo_llamadas(3, 2, 5)[0].cumple
    falla = verificar_conteo_llamadas(3, 2, 6)[0]
    assert not falla.cumple
    assert falla.detalle == "contadas = 6, fórmula = 5"


UTILIDADES = {1: UtilidadTabla([3, 2]), 2: UtilidadTabla([1])}
CONTEO_REPARTO = "extracciones = Σ x_i e inserciones = Σ x_i − nodos en su tope"


def fallas_del_reparto(x, utilidad, extracciones=3, inserciones=3):
    r = ResultadoReparto(x, utilidad, extracciones, inserciones)
    return [v.nombre for v in verificar_reparto([1, 2], 3, UTILIDADES, r) if not v.cumple]


def test_reparto_correcto_cumple_todo():
    assert fallas_del_reparto({1: 2, 2: 1}, 6) == []


@pytest.mark.parametrize("x, utilidad, extracciones, inserciones, falla", [
    ({1: 4, 2: -1}, 5, 3, 3, "cada x_i entero con 0 ≤ x_i ≤ B"),
    ({1: 1.5, 2: 1.5}, 0, 3, 3, "cada x_i entero con 0 ≤ x_i ≤ B"),
    ({1: 1, 2: 1}, 4, 3, 3, "Σ x_i = mín(B, Σ c_i)"),
    ({1: 2, 2: 1}, 99, 3, 3, "utilidad acumulada = Σ u_i(x_i) recalculada"),
    ({1: 2, 2: 1}, 6, 2, 3, CONTEO_REPARTO),
    ({1: 2, 2: 1}, 6, 3, 2, CONTEO_REPARTO),
])
def test_reparto_malo_se_detecta(x, utilidad, extracciones, inserciones, falla):
    # Debe reportarse sin lanzar excepciones, aunque un x_i no se pueda evaluar en la tabla
    assert falla in fallas_del_reparto(x, utilidad, extracciones, inserciones)


def test_utilidad_infinita_no_pasa_como_correcta():
    # a enorme pero finita: los valores se desbordan a inf
    utilidades = {1: UtilidadLog(1e308), 2: UtilidadLog(1e308)}
    infinita = sum(utilidades[i].valor(2) for i in (1, 2))
    r = ResultadoReparto({1: 2, 2: 2}, infinita, 4, 4)
    fallas = [v.nombre for v in verificar_reparto([1, 2], 4, utilidades, r) if not v.cumple]
    assert fallas == ["utilidad acumulada = Σ u_i(x_i) recalculada"]


# ---- Topes por nodo ----

U_TOPES = {1: UtilidadLog(10.0), 2: UtilidadLog(1.0)}


def fallas_con_topes(x, extracciones, inserciones, B=5, topes=None):
    """Nombres de lo que falla, con la utilidad correcta para ese x."""
    utilidad = sum(U_TOPES[i].valor(x[i]) for i in x)
    r = ResultadoReparto(x, utilidad, extracciones, inserciones)
    return [v.nombre for v in verificar_reparto([1, 2], B, U_TOPES, r, topes) if not v.cumple]


def test_reparto_con_tope_activo_cumple_todo():
    # x = 2 y 3, con 5 extracciones y 4 inserciones: el nodo 1 no vuelve al montículo
    assert fallas_con_topes({1: 2, 2: 3}, 5, 4, topes={1: 2}) == []


def test_topes_que_no_alcanzan_B_no_son_una_falla():
    # Σ c_i = 2 < B = 9: se exige gastar mín(B, Σ c_i) = 2, no B
    assert fallas_con_topes({1: 2, 2: 0}, 2, 1, B=9, topes={1: 2, 2: 0}) == []


def test_el_nodo_con_tope_cero_no_se_descuenta_de_las_inserciones():
    # El nodo 2 nunca entró al montículo: su x_i = c_i = 0 no significa que dejó de reinsertarse
    assert fallas_con_topes({1: 3, 2: 0}, 3, 3, B=3, topes={2: 0}) == []


@pytest.mark.parametrize("x, extracciones, inserciones, B, topes, falla", [
    ({1: 3, 2: 2}, 5, 5, 5, {1: 2}, "cada x_i ≤ c_i"),
    ({1: 2, 2: 2}, 4, 3, 5, {1: 2}, "Σ x_i = mín(B, Σ c_i)"),      # gastó 4 pudiendo gastar 5
    ({1: 1, 2: 0}, 1, 0, 9, {1: 2, 2: 0}, "Σ x_i = mín(B, Σ c_i)"),  # debía llegar a Σ c_i = 2
    ({1: 2, 2: 3}, 5, 5, 5, {1: 2}, CONTEO_REPARTO),                # el que llegó a su tope se reinsertó
    ({1: 2, 2: 3}, 4, 4, 5, {1: 2}, CONTEO_REPARTO),
])
def test_reparto_con_topes_malo_se_detecta(x, extracciones, inserciones, B, topes, falla):
    assert falla in fallas_con_topes(x, extracciones, inserciones, B, topes)


def test_la_linea_del_tope_solo_aparece_si_hay_topes():
    r = ResultadoReparto({1: 2, 2: 3}, U_TOPES[1].valor(2) + U_TOPES[2].valor(3), 5, 5)
    assert "cada x_i ≤ c_i" not in [v.nombre for v in verificar_reparto([1, 2], 5, U_TOPES, r)]
    r_tope = ResultadoReparto({1: 2, 2: 3}, r.utilidad, 5, 4)
    assert "cada x_i ≤ c_i" in [v.nombre for v in verificar_reparto([1, 2], 5, U_TOPES, r_tope, {1: 2})]


def test_x_fuera_de_rango_con_topes_no_lanza_excepcion():
    r = ResultadoReparto({1: -1, 2: 1.5}, 0, 0, 0)
    assert "cada x_i entero con 0 ≤ x_i ≤ B" in [
        v.nombre for v in verificar_reparto([1, 2], 5, U_TOPES, r, {1: 2}) if not v.cumple]


# ---- Oráculo de influencia ----

NOMBRE_PESOS = "cada peso de influencia en [0, 1]"


def instancia_con_peso(peso):
    """Tres nodos y dos aristas; la primera tiene el peso pedido."""
    nodos = [Nodo(i, [], UtilidadLog(1.0), costo_participacion=1) for i in ("N1", "N2", "N3")]
    vecinos = {"N1": {"N2": peso}, "N2": {"N1": peso, "N3": 0.5}, "N3": {"N2": 0.5}}
    return Instancia(1, 2, nodos, "con_grafo", vecinos, {"numero_rondas": 1,
                                                         "presupuesto_costos_participacion_por_ronda": 1})


@pytest.mark.parametrize("peso", [0, 0.0, 0.5, 1, 1.0])
def test_peso_dentro_del_rango_cumple(peso):
    verificaciones = {v.nombre: v.cumple for v in verificar_entrada(instancia_con_peso(peso))}
    assert verificaciones[NOMBRE_PESOS]


@pytest.mark.parametrize("peso", [-0.1, 1.5, float("nan"), float("inf")])
def test_peso_fuera_del_rango_falla_y_el_caso_no_corre(peso):
    instancia = instancia_con_peso(peso)
    falla = [v for v in verificar_entrada(instancia) if v.nombre == NOMBRE_PESOS][0]
    assert not falla.cumple
    assert falla.detalle == f"{{N1, N2}}: {peso}"   # la arista se reporta una sola vez
    r = ejecutar_ronda(instancia)
    assert not r["todas_cumplen"]
    assert "seleccion" not in r
    assert NOMBRE_PESOS in r["traza"]["motivo_rechazo"][0]


def test_el_formato_propio_no_tiene_verificacion_de_pesos():
    instancia = Instancia(1, 2, [Nodo(1, ["a"], UtilidadLog(1.0)), Nodo(2, ["b"], UtilidadLog(1.0))])
    assert NOMBRE_PESOS not in [v.nombre for v in verificar_entrada(instancia)]


def falla_del_valor(valorS):
    instancia = instancia_con_peso(0.5)
    verificaciones = verificar_seleccion(instancia, instancia.crear_oraculo(), ["N1"], valorS)
    return {v.nombre: v.cumple for v in verificaciones}["valor acumulado = f(S) recalculada"]


def test_el_valor_real_se_compara_con_tolerancia():
    # f({N1}) = 1 + 0.5 = 1.5: el redondeo se tolera; una diferencia de verdad, no
    assert falla_del_valor(1.5)
    assert falla_del_valor(1.5 + 1e-12)
    assert not falla_del_valor(1.5 + 1e-3)


def test_el_redondeo_de_verdad_pasa_con_tolerancia_y_no_con_igualdad():
    # Sumar Δ uno a uno y recalcular desde cero no da el mismo float: por eso no sirve ==
    coeficientes = {i: 0.1 * (i + 1) for i in range(12)}
    vecinos = {i: {j: 0.3 for j in range(12) if j != i} for i in range(12)}
    oraculo = OraculoInfluencia(coeficientes, vecinos)
    q = oraculo.estado_inicial()
    acumulado = 0.0
    S = list(range(8))
    for v in S:
        acumulado += oraculo.ganancia(v, q)
        oraculo.agregar(q, v)
    recalculado = oraculo.valor(S)
    assert acumulado != recalculado
    instancia = Instancia(8, 0, [Nodo(i, [], UtilidadLog(1.0)) for i in range(12)], "redondeo", vecinos)
    nombres = {v.nombre: v.cumple for v in verificar_seleccion(instancia, oraculo, S, acumulado)}
    assert nombres["valor acumulado = f(S) recalculada"]
