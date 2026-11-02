import math

import pytest

from red.utilidades import UtilidadLog, UtilidadRaiz, UtilidadTabla, crear_utilidad


def test_log_valor_y_ganancia():
    u = UtilidadLog(9.0)
    assert u.valor(0) == 0
    assert math.isclose(u.ganancia(0), 9 * math.log(2))
    assert math.isclose(u.ganancia(3), u.valor(4) - u.valor(3))


def test_raiz_valor_y_ganancia():
    u = UtilidadRaiz(7.0)
    assert u.valor(0) == 0
    assert math.isclose(u.valor(4), 14.0)
    assert math.isclose(u.ganancia(0), 7.0)


@pytest.mark.parametrize("u", [UtilidadLog(3.0), UtilidadRaiz(5.0)])
def test_familias_crecientes_y_concavas(u):
    ganancias = [u.ganancia(x) for x in range(50)]
    assert all(g >= 0 for g in ganancias)
    assert all(ganancias[x + 1] <= ganancias[x] for x in range(49))


def test_tabla_acumula_y_se_acaba_en_cero():
    u = UtilidadTabla([9, 5, 2, 1])
    assert [u.valor(x) for x in range(5)] == [0, 9, 14, 16, 17]
    assert u.ganancia(4) == 0
    assert u.valor(10) == 17


def test_crear_utilidad_desconocida():
    with pytest.raises(ValueError):
        crear_utilidad({"tipo": "exponencial", "a": 1})
