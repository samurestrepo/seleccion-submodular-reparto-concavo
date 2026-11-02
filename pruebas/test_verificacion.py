"""Pruebas de verificacion.py: complejidad sin reloj (H3), bordes de la concavidad (H10) y ramas de fallo."""

import pytest

from red.cobertura import OraculoCobertura
from red.entrada import Instancia, Nodo
from red.reparto import ResultadoReparto
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


def fallas_del_reparto(x, utilidad, extracciones=3, inserciones=3):
    r = ResultadoReparto(x, utilidad, extracciones, inserciones)
    return [v.nombre for v in verificar_reparto([1, 2], 3, UTILIDADES, r) if not v.cumple]


def test_reparto_correcto_cumple_todo():
    assert fallas_del_reparto({1: 2, 2: 1}, 6) == []


@pytest.mark.parametrize("x, utilidad, extracciones, inserciones, falla", [
    ({1: 4, 2: -1}, 5, 3, 3, "cada x_i entero con 0 ≤ x_i ≤ B"),
    ({1: 1.5, 2: 1.5}, 0, 3, 3, "cada x_i entero con 0 ≤ x_i ≤ B"),
    ({1: 1, 2: 1}, 4, 3, 3, "Σ x_i = B"),
    ({1: 2, 2: 1}, 99, 3, 3, "utilidad acumulada = Σ u_i(x_i) recalculada"),
    ({1: 2, 2: 1}, 6, 2, 3, "extracciones = inserciones = B"),
    ({1: 2, 2: 1}, 6, 3, 2, "extracciones = inserciones = B"),
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
