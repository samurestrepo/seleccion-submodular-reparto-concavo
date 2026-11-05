import json
from pathlib import Path

import pytest

from red.cobertura import OraculoCobertura
from red.entrada import ErrorDeFormato, instancia_desde_diccionario, leer_instancia, nombre_del_caso
from red.influencia import OraculoInfluencia

RAIZ = Path(__file__).resolve().parent.parent


def test_lee_el_ejemplo_del_informe():
    inst = leer_instancia(RAIZ / "casos" / "propios" / "ejemplo_informe.json")
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


def caso_con_utilidad(utilidad, cubre=()):
    return {"k": 1, "B": 1, "nodos": [{"id": 1, "cubre": list(cubre), "utilidad": utilidad}]}


@pytest.mark.parametrize("datos", [
    5,                                                                 # raíz que no es objeto
    None,
    [1, 2],
    "k B nodos",
    {"k": 1, "B": 1, "nodos": [5]},                                    # nodo que no es objeto
    {"k": 1, "B": 1, "nodos": [None]},
    {"k": 1, "B": 1, "nodos": ["id cubre utilidad"]},
    caso_con_utilidad(5),                                              # utilidad que no es objeto
    caso_con_utilidad(None),
    caso_con_utilidad("log"),
    caso_con_utilidad({"tipo": "log", "a": 1}, cubre=[["a"]]),         # elementos no hashables
    caso_con_utilidad({"tipo": "log", "a": 1}, cubre=[{"x": 1}]),
    caso_con_utilidad({"tipo": "log"}),                                # falta a
    caso_con_utilidad({"tipo": "tabla"}),                              # falta ganancias
])
def test_formas_que_antes_tumbaban_el_programa(datos):
    # H1: estos casos lanzaban TypeError o AttributeError en vez de ErrorDeFormato
    with pytest.raises(ErrorDeFormato):
        instancia_desde_diccionario(datos)


@pytest.mark.parametrize("tipo", ["log", "raiz"])
@pytest.mark.parametrize("a", [0, 0.0, -1, -0.5, True, False, "3", None, [1], float("nan"),
                               float("inf"), float("-inf"), 10**400])
def test_coeficiente_debe_ser_finito_y_positivo(tipo, a):
    # H9: antes a = Infinity salía en [OK] y a = "3" se convertía sin avisar
    with pytest.raises(ErrorDeFormato):
        instancia_desde_diccionario(caso_con_utilidad({"tipo": tipo, "a": a}))


@pytest.mark.parametrize("texto", ["NaN", "Infinity", "-Infinity", "1e999"])
def test_coeficiente_no_finito_escrito_en_el_json(tmp_path, texto):
    ruta = tmp_path / "caso.json"
    ruta.write_text('{"k":1,"B":1,"nodos":[{"id":1,"cubre":[],"utilidad":{"tipo":"log","a":%s}}]}' % texto,
                    encoding="utf-8")
    with pytest.raises(ErrorDeFormato):
        leer_instancia(ruta)


@pytest.mark.parametrize("a", [1, 0.5, 9.0, 1e-3])
def test_coeficiente_valido_se_acepta(a):
    inst = instancia_desde_diccionario(caso_con_utilidad({"tipo": "raiz", "a": a}))
    assert inst.utilidades()[1].a == a


@pytest.mark.parametrize("ganancias", [5, "abc", {}, {"a": 1}, None, [1, None], [1, "2"], [True],
                                       [float("nan")], [float("inf")], [10**400]])
def test_ganancias_deben_ser_una_lista_de_numeros_finitos(ganancias):
    with pytest.raises(ErrorDeFormato):
        instancia_desde_diccionario(caso_con_utilidad({"tipo": "tabla", "ganancias": ganancias}))


def test_tabla_negativa_no_es_error_de_forma():
    # La forma no juzga la concavidad: eso lo revisa verificacion.py y queda en la traza
    inst = instancia_desde_diccionario(caso_con_utilidad({"tipo": "tabla", "ganancias": [1, 10, -3]}))
    assert inst.utilidades()[1].ganancias == [1, 10, -3]


@pytest.mark.parametrize("contenido", [
    b"{k:",                                       # JSON mal escrito
    b"",                                          # vacío
    b'{"k":1,"B":1,"nodos":[{"id":1,"cubre":["\xf1"],"utilidad":{"tipo":"log","a":1}}]}',  # latin-1
    b"[" * 100000,                                # anidado sin fin
    b'{"k":1' + b"0" * 5000 + b"}",               # entero más largo de lo que Python convierte
])
def test_archivos_que_no_se_pueden_interpretar(tmp_path, contenido):
    ruta = tmp_path / "caso.json"
    ruta.write_bytes(contenido)
    with pytest.raises(ErrorDeFormato):
        leer_instancia(ruta)


def test_lee_utf8_con_bom(tmp_path):
    # H12: el BOM es la marca invisible que agregan algunos editores de Windows
    ruta = tmp_path / "caso.json"
    datos = caso_con_utilidad({"tipo": "log", "a": 1}, cubre=["ñ"])
    ruta.write_bytes(b"\xef\xbb\xbf" + json.dumps(datos, ensure_ascii=False).encode("utf-8"))
    assert leer_instancia(ruta).conjuntos()[1] == frozenset({"ñ"})


@pytest.mark.parametrize("ruta, nombre", [
    ("casos/c.json", "c"),
    ("casos\\c.json", "c"),
    ("c.JSON", "c"),
    ("c.Json", "c"),
    ("sin_extension", "sin_extension"),
    ("otro.txt", "otro.txt"),
])
def test_nombre_del_caso(ruta, nombre):
    assert nombre_del_caso(ruta) == nombre


# ---- Formato de la profesora ----

CASO_PROFESORA = RAIZ / "casos" / "profesora" / "entrada_G2_red_15_nodos.json"


def caso_profesora():
    """Un caso mínimo y válido del formato de la profesora. Cada prueba le daña una parte."""
    return {
        "parametros": {
            "numero_nodos": 3,
            "numero_rondas": 2,
            "cupo_participantes_por_ronda_k": 1,
            "presupuesto_ruido_por_ronda_B": 4,
            "presupuesto_costos_participacion_por_ronda": 9,
        },
        "grafo": [
            {"u": "N01", "v": "N02", "peso_influencia": 0.5},
            {"u": "N02", "v": "N03", "peso_influencia": 0.25},
        ],
        "nodos": [
            {"id": "N02", "coeficiente_utilidad": 2.0, "presupuesto_total_nodo": 18, "costo_participacion": 3},
            {"id": "N01", "coeficiente_utilidad": 1.5, "presupuesto_total_nodo": 18, "costo_participacion": 4},
            {"id": "N03", "coeficiente_utilidad": 3.0, "presupuesto_total_nodo": 17, "costo_participacion": 5},
        ],
    }


def test_lee_el_archivo_de_la_profesora():
    inst = leer_instancia(CASO_PROFESORA)
    assert (inst.N, inst.k, inst.B) == (15, 5, 30)
    assert inst.numero_aristas() == 105
    assert inst.ids() == [f"N{i:02d}" for i in range(1, 16)]
    assert inst.utilidades()["N01"].describir() == {"tipo": "log", "a": 8.5}
    assert inst.variantes == {"numero_rondas": 3, "presupuesto_costos_participacion_por_ronda": 24}
    assert inst.nodos[0].presupuesto_total == 18
    assert inst.nodos[0].costo_participacion == 3
    assert inst.vecinos["N01"]["N02"] == inst.vecinos["N02"]["N01"] == 0.25


def test_el_formato_de_la_profesora_conserva_los_ids_como_texto_y_ordena():
    inst = instancia_desde_diccionario(caso_profesora())
    assert inst.ids() == ["N01", "N02", "N03"]
    assert inst.conjuntos() == {"N01": frozenset(), "N02": frozenset(), "N03": frozenset()}


def test_sin_ceros_a_la_izquierda_manda_el_orden_de_texto():
    # Limitación anotada en la ficha: "N10" va antes que "N2"; con ceros a la izquierda no pasa
    datos = caso_profesora()
    datos["grafo"] = []
    for nodo, nuevo in zip(datos["nodos"], ("N2", "N10", "N3")):
        nodo["id"] = nuevo
    assert instancia_desde_diccionario(datos).ids() == ["N10", "N2", "N3"]


def test_crear_oraculo_da_el_tipo_del_formato_y_uno_nuevo_cada_vez():
    profesora = instancia_desde_diccionario(caso_profesora())
    assert isinstance(profesora.crear_oraculo(), OraculoInfluencia)
    assert profesora.crear_oraculo() is not profesora.crear_oraculo()
    usado = profesora.crear_oraculo()
    usado.ganancia("N01", usado.estado_inicial())
    assert profesora.crear_oraculo().llamadas_ganancia == 0

    propio = leer_instancia(RAIZ / "casos" / "propios" / "ejemplo_informe.json")
    assert isinstance(propio.crear_oraculo(), OraculoCobertura)
    assert propio.crear_oraculo() is not propio.crear_oraculo()
    assert propio.vecinos is None
    assert propio.variantes is None


@pytest.mark.parametrize("campo", ["parametros", "grafo", "nodos"])
def test_profesora_falta_un_campo_de_la_raiz(campo):
    datos = caso_profesora()
    del datos[campo]
    if campo == "parametros":
        # Sin "parametros" ya no se reconoce como de la profesora; igual es un error de forma
        with pytest.raises(ErrorDeFormato, match="falta el campo 'k'"):
            instancia_desde_diccionario(datos)
    else:
        with pytest.raises(ErrorDeFormato, match=campo):
            instancia_desde_diccionario(datos)


@pytest.mark.parametrize("campo", list(caso_profesora()["parametros"]))
def test_profesora_falta_un_parametro(campo):
    datos = caso_profesora()
    del datos["parametros"][campo]
    with pytest.raises(ErrorDeFormato, match=campo):
        instancia_desde_diccionario(datos)


@pytest.mark.parametrize("campo", ["u", "v", "peso_influencia"])
def test_profesora_falta_un_campo_de_la_arista(campo):
    datos = caso_profesora()
    del datos["grafo"][1][campo]
    with pytest.raises(ErrorDeFormato, match=campo):
        instancia_desde_diccionario(datos)


@pytest.mark.parametrize("campo", ["id", "coeficiente_utilidad", "presupuesto_total_nodo", "costo_participacion"])
def test_profesora_falta_un_campo_del_nodo(campo):
    datos = caso_profesora()
    del datos["nodos"][2][campo]
    with pytest.raises(ErrorDeFormato, match=campo):
        instancia_desde_diccionario(datos)


@pytest.mark.parametrize("numero_nodos", [2, 4, 0])
def test_profesora_numero_de_nodos_no_coincide(numero_nodos):
    datos = caso_profesora()
    datos["parametros"]["numero_nodos"] = numero_nodos
    with pytest.raises(ErrorDeFormato, match="numero_nodos"):
        instancia_desde_diccionario(datos)


@pytest.mark.parametrize("u, v", [
    ("N01", "N99"),     # el segundo extremo no existe
    ("N99", "N01"),     # el primero tampoco
    ("n01", "N02"),     # el texto debe ser idéntico
    (1, "N02"),         # un número no nombra ningún nodo
    (["N01"], "N02"),   # una lista no debe tumbar el programa
    (None, "N02"),
])
def test_profesora_arista_con_nodo_inexistente(u, v):
    datos = caso_profesora()
    datos["grafo"].append({"u": u, "v": v, "peso_influencia": 0.5})
    with pytest.raises(ErrorDeFormato, match="inexistente"):
        instancia_desde_diccionario(datos)


def test_profesora_arista_lazo():
    datos = caso_profesora()
    datos["grafo"].append({"u": "N01", "v": "N01", "peso_influencia": 0.5})
    with pytest.raises(ErrorDeFormato, match="lazo"):
        instancia_desde_diccionario(datos)


@pytest.mark.parametrize("u, v", [("N01", "N02"), ("N02", "N01")])
def test_profesora_arista_repetida_en_cualquier_sentido(u, v):
    # El grafo no es dirigido: {N01, N02} y {N02, N01} son la misma arista
    datos = caso_profesora()
    datos["grafo"].append({"u": u, "v": v, "peso_influencia": 0.1})
    with pytest.raises(ErrorDeFormato, match="repetida"):
        instancia_desde_diccionario(datos)


@pytest.mark.parametrize("malo", ["3", None, True, [1], {"a": 1}, float("nan"), float("inf"), 10**400])
@pytest.mark.parametrize("ubicar", [
    lambda d, x: d["grafo"][0].__setitem__("peso_influencia", x),
    lambda d, x: d["nodos"][0].__setitem__("coeficiente_utilidad", x),
    lambda d, x: d["nodos"][0].__setitem__("presupuesto_total_nodo", x),
    lambda d, x: d["nodos"][0].__setitem__("costo_participacion", x),
    lambda d, x: d["parametros"].__setitem__("presupuesto_costos_participacion_por_ronda", x),
], ids=["peso", "coeficiente", "presupuesto_total", "costo", "presupuesto_costos"])
def test_profesora_valor_no_numerico(ubicar, malo):
    datos = caso_profesora()
    ubicar(datos, malo)
    with pytest.raises(ErrorDeFormato):
        instancia_desde_diccionario(datos)


@pytest.mark.parametrize("campo", ["numero_nodos", "numero_rondas", "cupo_participantes_por_ronda_k",
                                   "presupuesto_ruido_por_ronda_B"])
@pytest.mark.parametrize("malo", ["3", None, True, 3.5, [1]])
def test_profesora_parametro_entero_no_es_entero(campo, malo):
    datos = caso_profesora()
    datos["parametros"][campo] = malo
    with pytest.raises(ErrorDeFormato, match=campo):
        instancia_desde_diccionario(datos)


@pytest.mark.parametrize("coeficiente", [0, -1.5])
def test_profesora_coeficiente_no_positivo(coeficiente):
    # Igual que en el formato propio (decisión 17): sin a > 0 no hay utilidad creciente
    datos = caso_profesora()
    datos["nodos"][0]["coeficiente_utilidad"] = coeficiente
    with pytest.raises(ErrorDeFormato, match="a > 0"):
        instancia_desde_diccionario(datos)


@pytest.mark.parametrize("daño", [
    lambda d: d.__setitem__("parametros", 5),
    lambda d: d.__setitem__("parametros", None),
    lambda d: d.__setitem__("grafo", {"u": "N01"}),
    lambda d: d.__setitem__("nodos", "N01"),
    lambda d: d["grafo"].__setitem__(0, 5),
    lambda d: d["nodos"].__setitem__(0, ["N01"]),
    lambda d: d["nodos"][0].__setitem__("id", 1),
    lambda d: d["nodos"][0].__setitem__("id", ["N01"]),
], ids=["parametros_numero", "parametros_nulo", "grafo_objeto", "nodos_texto", "arista_numero",
        "nodo_lista", "id_numero", "id_lista"])
def test_profesora_tipos_que_no_deben_tumbar_el_programa(daño):
    datos = caso_profesora()
    daño(datos)
    with pytest.raises(ErrorDeFormato):
        instancia_desde_diccionario(datos)


# ---- Topes por nodo ----

def caso_propio_con_topes(*topes):
    """Formato propio: un nodo por tope; None significa que el nodo no trae el campo."""
    nodos = []
    for i, tope in enumerate(topes, start=1):
        nodo = {"id": i, "cubre": [f"e{i}"], "utilidad": {"tipo": "log", "a": 1}}
        if tope is not None:
            nodo["tope"] = tope
        nodos.append(nodo)
    return {"k": 1, "B": 1, "nodos": nodos}


def test_el_tope_propio_es_opcional():
    inst = instancia_desde_diccionario(caso_propio_con_topes(2, None, 0))
    assert inst.topes() == {1: 2, 3: 0}
    assert inst.nodos[1].tope is None


def test_sin_campo_tope_no_hay_topes():
    assert leer_instancia(RAIZ / "casos" / "propios" / "ejemplo_informe.json").topes() == {}


@pytest.mark.parametrize("malo", [-1, 1.5, 2.0, "3", True, None, [1], float("nan")])
def test_tope_propio_invalido(malo):
    datos = caso_propio_con_topes(1)
    datos["nodos"][0]["tope"] = malo
    with pytest.raises(ErrorDeFormato, match="tope"):
        instancia_desde_diccionario(datos)


def test_en_la_profesora_el_tope_es_presupuesto_total_nodo():
    inst = instancia_desde_diccionario(caso_profesora())
    assert inst.topes() == {"N01": 18, "N02": 18, "N03": 17}
    assert inst.nodos[2].presupuesto_total == inst.nodos[2].tope == 17


def test_en_la_profesora_el_campo_tope_no_se_lee():
    datos = caso_profesora()
    datos["nodos"][0]["tope"] = 1
    assert instancia_desde_diccionario(datos).topes()["N02"] == 18


def test_en_la_profesora_un_presupuesto_total_cero_es_valido():
    datos = caso_profesora()
    datos["nodos"][0]["presupuesto_total_nodo"] = 0
    assert instancia_desde_diccionario(datos).topes()["N02"] == 0


@pytest.mark.parametrize("malo", [-1, 18.5, 18.0])
def test_en_la_profesora_presupuesto_total_debe_ser_entero_no_negativo(malo):
    # Con 18.5, x_i < 18.5 dejaría llegar a x_i = 19, por encima del presupuesto
    datos = caso_profesora()
    datos["nodos"][0]["presupuesto_total_nodo"] = malo
    with pytest.raises(ErrorDeFormato, match="presupuesto_total_nodo"):
        instancia_desde_diccionario(datos)


def test_profesora_un_peso_fuera_de_rango_no_es_error_de_forma():
    # Es una restricción: la revisa verificacion.py para que quede escrita en la traza
    datos = caso_profesora()
    datos["grafo"][0]["peso_influencia"] = 1.5
    assert instancia_desde_diccionario(datos).vecinos["N01"]["N02"] == 1.5
