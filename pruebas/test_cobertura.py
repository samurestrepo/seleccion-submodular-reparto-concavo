from red.cobertura import OraculoCobertura

CONJUNTOS = {1: frozenset("abc"), 2: frozenset("cd"), 3: frozenset("de")}


def test_valores_del_informe():
    f = OraculoCobertura(CONJUNTOS)
    assert f.valor([]) == 0
    assert f.valor([1, 3]) == 5
    assert f.valor([1, 2]) == 4
    assert f.llamadas_valor == 3


def test_ganancia_es_lo_nuevo_que_aporta():
    # Tabla de la sección 5.6: Δ(3 | ∅) = 2 y Δ(3 | {2}) = 1
    f = OraculoCobertura(CONJUNTOS)
    assert f.ganancia(3, set()) == 2
    assert f.ganancia(3, set(CONJUNTOS[2])) == 1
    assert f.llamadas_ganancia == 2


def test_ganancia_coincide_con_la_resta_de_valores():
    f = OraculoCobertura(CONJUNTOS)
    for S in ([], [1], [2], [1, 2]):
        cubiertos = set().union(*(CONJUNTOS[v] for v in S))
        for v in (3,):
            assert f.ganancia(v, cubiertos) == f.valor(S + [v]) - f.valor(S)
