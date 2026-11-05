"""Pruebas de la línea de comandos: lotes con archivos malos, evidencias y resumen."""

import os
import csv
import json
from pathlib import Path

import pytest

from ejecutar import main

RAIZ = Path(__file__).resolve().parent.parent
EJEMPLO = RAIZ / "casos" / "propios" / "ejemplo_informe.json"
UTILIDAD_LOG = {"tipo": "log", "a": 1}
K_IGUAL_N = {"k": 2, "B": 2, "nodos": [
    {"id": 1, "cubre": ["a"], "utilidad": UTILIDAD_LOG},
    {"id": 2, "cubre": ["b"], "utilidad": UTILIDAD_LOG}]}


def escribir_caso(ruta, datos):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(datos), encoding="utf-8")


def leer_resumen(salida):
    with open(salida / "resumen.csv", encoding="utf-8", newline="") as archivo:
        return list(csv.DictReader(archivo))


@pytest.mark.parametrize("contenido", [
    b'{"k":1,"B":1,"nodos":[{"id":1,"cubre":[],"utilidad":5}]}',            # utilidad no es objeto
    b'{"k":1,"B":1,"nodos":[{"id":1,"cubre":[],"utilidad":null}]}',
    b'{"k":1,"B":1,"nodos":[5,6]}',                                         # nodo no es objeto
    b'{"k":1,"B":1,"nodos":["id cubre utilidad"]}',
    b'{"k":1,"B":1,"nodos":[{"id":1,"cubre":[["a"]],"utilidad":{"tipo":"log","a":1}}]}',  # no hashable
    b'{"k":1,"B":1,"nodos":[{"id":1,"cubre":[{"x":1}],"utilidad":{"tipo":"log","a":1}}]}',
    b"5",                                                                   # raíz no es objeto
    b"null",
    b'{"k":1,"B":1,"nodos":[{"id":1,"cubre":["\xf1"],"utilidad":{"tipo":"log","a":1}}]}',  # latin-1
    b"[" * 100000,                                                          # anidado sin fin
])
def test_archivo_malo_no_detiene_el_lote(tmp_path, contenido, capsys):
    # H1: el archivo del medio da [ERROR] y los otros dos corren; resumen.csv se escribe
    carpeta = tmp_path / "casos"
    carpeta.mkdir()
    (carpeta / "a_bueno.json").write_bytes(EJEMPLO.read_bytes())
    (carpeta / "m_malo.json").write_bytes(contenido)
    (carpeta / "z_bueno.json").write_bytes(EJEMPLO.read_bytes())
    salida = tmp_path / "salida"

    assert main([str(carpeta), "--salida", str(salida)]) == 1

    assert "[ERROR]" in capsys.readouterr().out
    assert (salida / "a_bueno" / "traza.txt").exists()
    assert (salida / "z_bueno" / "traza.txt").exists()
    filas = {fila["caso"]: fila["todas_cumplen"] for fila in leer_resumen(salida)}
    assert filas == {"a_bueno": "True", "m_malo": "False", "z_bueno": "True"}


def test_archivo_malo_deja_el_motivo_en_la_traza(tmp_path):
    malo = tmp_path / "malo.json"
    escribir_caso(malo, {"k": 1, "B": 1, "nodos": [{"id": 1, "cubre": [], "utilidad": 5}]})
    salida = tmp_path / "salida"
    main([str(malo), "--salida", str(salida)])
    traza_txt = (salida / "malo" / "traza.txt").read_text(encoding="utf-8")
    traza_json = json.loads((salida / "malo" / "traza.json").read_text(encoding="utf-8"))
    assert "debe ser un objeto" in traza_txt
    assert "debe ser un objeto" in traza_json["motivo_rechazo"][0]


def test_archivo_inexistente_da_error_y_no_escribe_evidencias(tmp_path, capsys):
    salida = tmp_path / "salida"
    assert main([str(tmp_path / "no_existe.json"), "--salida", str(salida)]) == 1
    assert "[ERROR]" in capsys.readouterr().out
    assert not (salida / "no_existe").exists()
    assert leer_resumen(salida)[0]["todas_cumplen"] == "False"


def test_entrada_invalida_escribe_traza_con_el_motivo_y_fila(tmp_path):
    # H2: antes solo quedaba salida.json y el caso no aparecía en el resumen
    caso = tmp_path / "k_igual_N.json"
    escribir_caso(caso, K_IGUAL_N)
    salida = tmp_path / "salida"
    assert main([str(caso), "--salida", str(salida)]) == 1

    carpeta = salida / "k_igual_N"
    traza_txt = (carpeta / "traza.txt").read_text(encoding="utf-8")
    traza_json = json.loads((carpeta / "traza.json").read_text(encoding="utf-8"))
    assert "k = 2, N = 2" in traza_txt
    assert "k = 2, N = 2" in traza_json["motivo_rechazo"][0]
    assert traza_json["pasos_seleccion"] == []
    fila = leer_resumen(salida)[0]
    assert (fila["caso"], fila["N"], fila["S"], fila["todas_cumplen"]) == ("k_igual_N", "2", "", "False")


@pytest.mark.parametrize("datos_malos", [
    K_IGUAL_N,                                                               # entrada inválida
    {"k": 1, "B": 1, "nodos": [{"id": 1, "cubre": [], "utilidad": {"tipo": "log", "a": -2}}]},  # forma
])
def test_no_queda_traza_vieja_que_contradiga_el_resultado(tmp_path, datos_malos):
    # H2: un caso válido que después se vuelve inválido no conserva "CUMPLEN"
    caso = tmp_path / "c.json"
    salida = tmp_path / "salida"
    caso.write_bytes(EJEMPLO.read_bytes())
    assert main([str(caso), "--salida", str(salida)]) == 0
    assert "CUMPLEN" in (salida / "c" / "traza.txt").read_text(encoding="utf-8")

    escribir_caso(caso, datos_malos)
    assert main([str(caso), "--salida", str(salida)]) == 1

    assert "CUMPLEN" not in (salida / "c" / "traza.txt").read_text(encoding="utf-8")
    traza_json = json.loads((salida / "c" / "traza.json").read_text(encoding="utf-8"))
    assert traza_json["unidades_reparto"] == [] and traza_json["motivo_rechazo"]
    salida_json = json.loads((salida / "c" / "salida.json").read_text(encoding="utf-8"))
    assert salida_json["todas_cumplen"] is False


def test_dos_archivos_con_el_mismo_caso_no_se_pisan(tmp_path, capsys):
    # H11: el segundo es un error; las evidencias siguen siendo las del primero
    (tmp_path / "d1").mkdir()
    (tmp_path / "d2").mkdir()
    (tmp_path / "d1" / "c.json").write_bytes(EJEMPLO.read_bytes())
    (tmp_path / "d2" / "C.json").write_bytes(
        (RAIZ / "casos" / "propios" / "contraejemplo_seleccion.json").read_bytes())
    salida = tmp_path / "salida"

    assert main([str(tmp_path / "d1"), str(tmp_path / "d2"), "--salida", str(salida)]) == 1

    assert "ya se corrió" in capsys.readouterr().out
    salida_json = json.loads((salida / "c" / "salida.json").read_text(encoding="utf-8"))
    assert salida_json["seleccion"]["S"] == [1, 3]   # el del primer archivo
    assert [fila["caso"] for fila in leer_resumen(salida)] == ["c"]


def test_resumen_refleja_solo_la_ultima_corrida_y_avisa(tmp_path, capsys):
    # H11: el reemplazo del resumen ya no es silencioso
    salida = tmp_path / "salida"
    main([str(RAIZ / "casos" / "propios"), "--salida", str(salida)])
    assert "Aviso" not in capsys.readouterr().out
    casos = [f for f in os.listdir(RAIZ / "casos" / "propios") if f.endswith(".json")]
    assert len(leer_resumen(salida)) == len(casos)

    main([str(EJEMPLO), "--salida", str(salida)])
    assert "Aviso: se reemplaza" in capsys.readouterr().out
    assert [fila["caso"] for fila in leer_resumen(salida)] == ["ejemplo_informe"]


def test_extension_sin_distinguir_mayusculas(tmp_path):
    # H12: c.JSON se encuentra en la carpeta y su caso se llama c
    carpeta = tmp_path / "casos"
    carpeta.mkdir()
    (carpeta / "c.JSON").write_bytes(EJEMPLO.read_bytes())
    salida = tmp_path / "salida"
    assert main([str(carpeta), "--salida", str(salida)]) == 0
    assert (salida / "c" / "salida.json").exists()


def test_archivo_con_bom_se_lee(tmp_path):
    # H12: un JSON válido guardado con BOM por un editor de Windows no es un error
    caso = tmp_path / "con_bom.json"
    caso.write_bytes(b"\xef\xbb\xbf" + EJEMPLO.read_bytes())
    assert main([str(caso), "--salida", str(tmp_path / "salida")]) == 0


def test_opcion_repeticiones_llega_a_las_evidencias(tmp_path):
    assert main([str(EJEMPLO), "--salida", str(tmp_path), "--repeticiones", "4"]) == 0
    salida = json.loads((tmp_path / "ejemplo_informe" / "salida.json").read_text(encoding="utf-8"))
    tiempos = salida["tiempos_segundos"]
    assert tiempos["repeticiones"] == 4
    assert set(tiempos["seleccion"]) == set(tiempos["reparto"]) == {"mediana", "minimo", "maximo"}
    fila = leer_resumen(tmp_path)[0]
    assert fila["repeticiones"] == "4"
    # El resumen usa la mediana
    assert fila["tiempo_seleccion_s"] == f"{tiempos['seleccion']['mediana']:.9f}"
    assert fila["tiempo_reparto_s"] == f"{tiempos['reparto']['mediana']:.9f}"


def test_el_resumen_trae_el_minimo_igual_al_de_salida_json_y_menor_o_igual_a_la_mediana(tmp_path):
    assert main([str(EJEMPLO), "--salida", str(tmp_path), "--repeticiones", "9"]) == 0
    tiempos = json.loads((tmp_path / "ejemplo_informe" / "salida.json").read_text(encoding="utf-8"))["tiempos_segundos"]
    fila = leer_resumen(tmp_path)[0]
    for parte in ("seleccion", "reparto"):
        minimo = float(fila[f"minimo_{parte}_s"])
        assert fila[f"minimo_{parte}_s"] == f"{tiempos[parte]['minimo']:.9f}"
        assert minimo <= float(fila[f"tiempo_{parte}_s"])
    assert list(fila)[7:11] == ["tiempo_seleccion_s", "tiempo_reparto_s", "minimo_seleccion_s", "minimo_reparto_s"]


def test_por_omision_el_resumen_trae_21_repeticiones(tmp_path):
    assert main([str(EJEMPLO), "--salida", str(tmp_path)]) == 0
    assert leer_resumen(tmp_path)[0]["repeticiones"] == "21"


def test_un_caso_rechazado_deja_vacia_la_columna_de_repeticiones(tmp_path):
    caso = tmp_path / "k_igual_N.json"
    escribir_caso(caso, K_IGUAL_N)
    assert main([str(caso), "--salida", str(tmp_path / "salida")]) == 1
    fila = leer_resumen(tmp_path / "salida")[0]
    assert fila["repeticiones"] == ""
    assert fila["minimo_seleccion_s"] == fila["minimo_reparto_s"] == ""
    assert fila["todas_cumplen"] == "False"


@pytest.mark.parametrize("valor", ["0", "-3", "dos", "1.5"])
def test_repeticiones_invalidas_las_rechaza_la_linea_de_comandos(tmp_path, valor):
    with pytest.raises(SystemExit):
        main([str(EJEMPLO), "--salida", str(tmp_path), f"--repeticiones={valor}"])


def test_un_caso_malo_de_la_profesora_no_detiene_el_lote(tmp_path, capsys):
    # La arista está repetida: el segundo caso del lote (por orden alfabético) igual corre
    entrada = tmp_path / "entrada"
    entrada.mkdir()
    escribir_caso(entrada / "a_malo.json", {
        "parametros": {"numero_nodos": 2, "numero_rondas": 1, "cupo_participantes_por_ronda_k": 1,
                       "presupuesto_ruido_por_ronda_B": 1, "presupuesto_costos_participacion_por_ronda": 1},
        "grafo": [{"u": "N1", "v": "N2", "peso_influencia": 0.5}, {"u": "N2", "v": "N1", "peso_influencia": 0.5}],
        "nodos": [{"id": i, "coeficiente_utilidad": 1, "presupuesto_total_nodo": 1, "costo_participacion": 1}
                  for i in ("N1", "N2")]})
    (entrada / "b_bueno.json").write_bytes(EJEMPLO.read_bytes())
    assert main([str(entrada), "--salida", str(tmp_path / "salida")]) == 1
    consola = capsys.readouterr().out
    assert "[ERROR]" in consola and "repetida" in consola
    assert "[OK] b_bueno" in consola
    assert "repetida" in (tmp_path / "salida" / "a_malo" / "traza.txt").read_text(encoding="utf-8")
