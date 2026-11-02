import pytest

from red.entrada import ErrorDeFormato, instancia_desde_diccionario, leer_instancia


def test_lee_el_ejemplo_del_informe():
    inst = leer_instancia("casos/propios/ejemplo_informe.json")
    assert inst.nombre == "ejemplo_informe"
    assert (inst.N, inst.k, inst.B) == (3, 2, 4)
    assert inst.ids() == [1, 2, 3]
    assert inst.conjuntos()[1] == frozenset({"a", "b", "c"})
    assert inst.utilidades()[2].tipo == "raiz"


def test_ordena_los_nodos_por_id():
    datos = {"k": 1, "B": 0, "nodos": [
        {"id": 5, "cubre": [], "utilidad": {"tipo": "log", "a": 1}},
        {"id": 2, "cubre": [], "utilidad": {"tipo": "log", "a": 1}}]}
    assert instancia_desde_diccionario(datos).ids() == [2, 5]


@pytest.mark.parametrize("datos", [
    {"B": 1, "nodos": []},                                                   # falta k
    {"k": "2", "B": 1, "nodos": []},                                         # k no entero
    {"k": 1, "B": 1, "nodos": [{"id": 1, "cubre": []}]},                     # falta utilidad
    {"k": 1, "B": 1, "nodos": [{"id": 1, "cubre": "ab", "utilidad": {"tipo": "log", "a": 1}}]},
    {"k": 1, "B": 1, "nodos": [{"id": 1, "cubre": [], "utilidad": {"tipo": "otra"}}]},
])
def test_formatos_invalidos(datos):
    with pytest.raises(ErrorDeFormato):
        instancia_desde_diccionario(datos)
