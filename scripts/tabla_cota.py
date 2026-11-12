"""Genera resultados/cota/tabla_cota.csv: voraz contra óptimo exacto (fuerza bruta) y las dos cotas.

Uso, desde la raíz del repositorio:  python scripts/tabla_cota.py
Casos: el de la profesora y los válidos de casos/propios con N <= 20. No escribe en resultados/profesora/.
"""

import csv
import os
import sys
from math import e
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from red.entrada import leer_instancia      # noqa: E402
from red.exacto import seleccionar_exacto   # noqa: E402
from red.seleccion import seleccionar_nodos  # noqa: E402

SALIDA = RAIZ / "resultados" / "cota" / "tabla_cota.csv"
TOLERANCIA = 1e-9
COLUMNAS = ["caso", "N", "k", "f_voraz", "OPT", "razon", "cota_k", "cota_e", "cumple"]


def rutas_de_los_casos():
    """Los casos propios con N <= 20 (orden alfabético) y, al final, el de la profesora."""
    propios = sorted(f for f in os.listdir(RAIZ / "casos" / "propios") if f.endswith(".json"))
    rutas = [RAIZ / "casos" / "propios" / f for f in propios]
    rutas = [r for r in rutas if leer_instancia(r).N <= 20]
    return rutas + [RAIZ / "casos" / "profesora" / "entrada_G2_red_15_nodos.json"]


def fila_de_un_caso(ruta):
    """Corre el voraz y el exacto sobre un caso y devuelve su fila. Con OPT = 0 la razón es 1."""
    inst = leer_instancia(ruta)
    ids = inst.ids()
    _, f_voraz = seleccionar_nodos(inst.crear_oraculo(), ids, inst.k)
    _, opt, _ = seleccionar_exacto(inst.crear_oraculo(), ids, inst.k)
    razon = f_voraz / opt if opt > 0 else 1.0
    cota_k = 1 - (1 - 1 / inst.k) ** inst.k
    cumple = f_voraz <= opt + TOLERANCIA and razon >= cota_k - TOLERANCIA
    return {
        "caso": ruta.stem, "N": inst.N, "k": inst.k,
        "f_voraz": round(f_voraz, 6), "OPT": round(opt, 6), "razon": round(razon, 6),
        "cota_k": round(cota_k, 6), "cota_e": round(1 - 1 / e, 6), "cumple": cumple,
    }


def main():
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    filas = [fila_de_un_caso(r) for r in rutas_de_los_casos()]
    with open(SALIDA, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=COLUMNAS)
        escritor.writeheader()
        escritor.writerows(filas)
    print(f"{len(filas)} casos escritos en {SALIDA}")
    return 0 if all(f["cumple"] for f in filas) else 1


if __name__ == "__main__":
    sys.exit(main())
