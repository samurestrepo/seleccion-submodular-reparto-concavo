"""Genera resultados/cota/tabla_cota.csv: voraz contra óptimo exacto (fuerza bruta) y las dos cotas.

Uso, desde la raíz del repositorio:  python scripts/tabla_cota.py
Casos: el de la profesora y los válidos de casos/propios con N <= 20. No escribe en resultados/profesora/.
También genera resultados/cota/tabla_cota_aleatoria.csv: 45 instancias de influencia aleatorias (en memoria).
"""

import csv
import os
import sys
from math import e
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from red.entrada import leer_instancia      # noqa: E402
from red.entrada import instancia_desde_diccionario  # noqa: E402
from red.exacto import seleccionar_exacto   # noqa: E402
from red.generador import generar_instancia_influencia  # noqa: E402
from red.seleccion import seleccionar_nodos  # noqa: E402

SALIDA = RAIZ / "resultados" / "cota" / "tabla_cota.csv"
TOLERANCIA = 1e-9
COLUMNAS = ["caso", "N", "k", "f_voraz", "OPT", "razon", "cota_k", "cota_e", "cumple"]

# Batería aleatoria (decisión 34): 5 tamaños x 3 densidades x 3 semillas = 45 instancias.
SALIDA_ALEATORIA = RAIZ / "resultados" / "cota" / "tabla_cota_aleatoria.csv"
TAMANOS = (12, 14, 16, 18, 20)
K_ALEATORIA = 5
DENSIDADES = (0.3, 0.6, 1.0)
SEMILLAS = (1, 2, 3)
B_ALEATORIA = 100   # no influye en f ni en la selección; solo llena el campo del formato
COLUMNAS_ALEATORIA = ["caso", "N", "k", "densidad", "semilla", "f_voraz", "OPT", "razon",
                      "cota_k", "cota_e", "cumple"]


def rutas_de_los_casos():
    """Los casos propios con N <= 20 (orden alfabético) y, al final, el de la profesora."""
    propios = sorted(f for f in os.listdir(RAIZ / "casos" / "propios") if f.endswith(".json"))
    rutas = [RAIZ / "casos" / "propios" / f for f in propios]
    rutas = [r for r in rutas if leer_instancia(r).N <= 20]
    return rutas + [RAIZ / "casos" / "profesora" / "entrada_G2_red_15_nodos.json"]


def fila_de_un_caso(ruta):
    """Corre el voraz y el exacto sobre un caso y devuelve su fila. Con OPT = 0 la razón es 1."""
    return fila_de_una_instancia(leer_instancia(ruta), ruta.stem)


def fila_de_una_instancia(inst, nombre):
    """Voraz contra exacto sobre una instancia ya leída. Costo: Θ(N·k) llamadas a Δ + C(N, k) evaluaciones."""
    ids = inst.ids()
    _, f_voraz = seleccionar_nodos(inst.crear_oraculo(), ids, inst.k)
    _, opt, _ = seleccionar_exacto(inst.crear_oraculo(), ids, inst.k)
    razon = f_voraz / opt if opt > 0 else 1.0
    cota_k = 1 - (1 - 1 / inst.k) ** inst.k
    cumple = f_voraz <= opt + TOLERANCIA and razon >= cota_k - TOLERANCIA
    return {
        "caso": nombre, "N": inst.N, "k": inst.k,
        "f_voraz": round(f_voraz, 6), "OPT": round(opt, 6), "razon": round(razon, 6),
        "cota_k": round(cota_k, 6), "cota_e": round(1 - 1 / e, 6), "cumple": cumple,
    }


def bateria_aleatoria():
    """Las 45 filas de la batería aleatoria, en memoria (sin archivos de entrada).

    Recorre N, densidad y semilla en ese orden con k = 5 y B = 100; cada instancia sale de
    generar_instancia_influencia y pasa por instancia_desde_diccionario, el mismo camino de entrada
    que el formato de la profesora. Costo: 45 veces (voraz + C(N, 5) evaluaciones de f).
    """
    filas = []
    for n in TAMANOS:
        for densidad in DENSIDADES:
            for semilla in SEMILLAS:
                nombre = f"aleatorio_N{n}_d{densidad}_s{semilla}"
                datos = generar_instancia_influencia(n, K_ALEATORIA, B_ALEATORIA, densidad, semilla)
                fila = fila_de_una_instancia(instancia_desde_diccionario(datos, nombre), nombre)
                fila.update({"densidad": densidad, "semilla": semilla})
                filas.append(fila)
    return filas


def escribir_csv(ruta, columnas, filas):
    """Escribe las filas (dicts) en un CSV con las columnas dadas, creando la carpeta si falta."""
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with open(ruta, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=columnas)
        escritor.writeheader()
        escritor.writerows(filas)


def main():
    filas = [fila_de_un_caso(r) for r in rutas_de_los_casos()]
    escribir_csv(SALIDA, COLUMNAS, filas)
    print(f"{len(filas)} casos escritos en {SALIDA}")
    aleatorias = bateria_aleatoria()
    escribir_csv(SALIDA_ALEATORIA, COLUMNAS_ALEATORIA, aleatorias)
    print(f"{len(aleatorias)} casos escritos en {SALIDA_ALEATORIA}")
    return 0 if all(f["cumple"] for f in filas + aleatorias) else 1


if __name__ == "__main__":
    sys.exit(main())
