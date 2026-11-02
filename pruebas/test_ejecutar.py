"""Pruebas de la línea de comandos: lotes con archivos malos, evidencias y resumen."""

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
    assert len(leer_resumen(salida)) == 3

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
