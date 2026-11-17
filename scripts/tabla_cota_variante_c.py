"""Genera resultados/variantes/c_tabla_cota.csv: los voraces de la variante (c) contra el exacto por enumeración.

Uso, desde la raíz del repositorio:  python scripts/tabla_cota_variante_c.py
Batería (decisión 46): instancias de influencia de generar_instancia_influencia con N ∈ {8, 10, 12}, k = 4,
densidad ∈ {0.3, 0.6, 1.0} y semillas 1, 2, 3 (27 instancias); S es el del voraz de la Parte 2 base; por
cada instancia, β ∈ {0.2, 0.5, 1.0, 2.0} y B ∈ {3, 6, 10} (324 filas). Por fila: U del voraz y del exacto
en c1 (deben coincidir) y en c2 (razón U/OPT contra la cota 1 − (1 − 1/B)^B).
No escribe en resultados/profesora/ ni toca la ronda.
"""

import csv
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from red.entrada import instancia_desde_diccionario  # noqa: E402
from red.generador import generar_instancia_influencia  # noqa: E402
from red.seleccion import seleccionar_nodos  # noqa: E402
from red.variante_vecinos import (contar_repartos, cota_c2, repartir_c1, repartir_c2,  # noqa: E402
                                  repartir_exacto, utilidad_c1, utilidad_c2, vecinos_en_S)

SALIDA = RAIZ / "resultados" / "variantes" / "c_tabla_cota.csv"
TOLERANCIA = 1e-9
COLUMNAS = ["caso", "N", "k", "densidad", "semilla", "beta", "B", "S", "aristas_en_S", "repartos",
            "U_c1_voraz", "U_c1_exacto", "c1_coincide",
            "x_c2_voraz", "x_c2_exacto", "U_c2_voraz", "U_c2_exacto", "razon_c2", "cota_c2", "cumple"]

# Batería (decisión 46): 3 tamaños x 3 densidades x 3 semillas = 27 instancias; x 4 β x 3 B = 324 filas.
TAMANOS = (8, 10, 12)
DENSIDADES = (0.3, 0.6, 1.0)
SEMILLAS = (1, 2, 3)
K = 4                          # |S| = 4: con B = 10 hay C(14, 4) = 1001 repartos por enumeración
BETAS = (0.2, 0.5, 1.0, 2.0)   # de «se mueven un poco» a un acople fuerte
PRESUPUESTOS = (3, 6, 10)      # B pequeño para que la enumeración quepa; el tope del generador es B


def _texto_x(S, x):
    """x como texto «id:valor» en el orden de S, para el CSV."""
    return " ".join(f"{i}:{x[i]}" for i in S)


def fila_de_una_instancia(inst, nombre, beta):
    """c1 y c2 sobre el S del voraz base: voraz y exacto de cada modelo, razón y cota.

    Costo: la selección base O(k·(N + A)), los dos voraces O(B·(|S| + A_S)) y dos enumeraciones de
    R = contar_repartos repartos, cada uno a O(|S| + A_S) (ver docs/modulos/variante_vecinos.md).
    """
    S, _ = seleccionar_nodos(inst.crear_oraculo(), inst.ids(), inst.k)
    coef = {nodo.id: nodo.utilidad.a for nodo in inst.nodos}
    topes, B = inst.topes(), inst.B
    grafo_S = vecinos_en_S(S, inst.vecinos)

    c1, a_prima = repartir_c1(S, B, coef, inst.vecinos, beta, topes)
    _, opt_c1, _ = repartir_exacto(S, B, lambda x: utilidad_c1(x, a_prima), topes)
    c2 = repartir_c2(S, B, coef, inst.vecinos, beta, topes)
    x_opt, opt_c2, _ = repartir_exacto(S, B, lambda x: utilidad_c2(x, coef, grafo_S, beta), topes)

    razon = c2.utilidad / opt_c2 if opt_c2 > 0 else 1.0
    cota = cota_c2(B)
    coincide = abs(c1.utilidad - opt_c1) <= TOLERANCIA * max(1.0, abs(opt_c1))
    cumple = coincide and razon <= 1 + TOLERANCIA and razon >= cota - TOLERANCIA
    return {
        "caso": nombre, "N": inst.N, "k": inst.k, "densidad": "", "semilla": "", "beta": beta, "B": B,
        "S": " ".join(S), "aristas_en_S": sum(len(l) for l in grafo_S.values()) // 2,
        "repartos": contar_repartos(S, B, topes),
        "U_c1_voraz": round(c1.utilidad, 9), "U_c1_exacto": round(opt_c1, 9), "c1_coincide": coincide,
        "x_c2_voraz": _texto_x(S, c2.x), "x_c2_exacto": _texto_x(S, x_opt),
        "U_c2_voraz": round(c2.utilidad, 9), "U_c2_exacto": round(opt_c2, 9),
        "razon_c2": round(razon, 9), "cota_c2": round(cota, 6), "cumple": cumple,
    }


def bateria(tamanos=TAMANOS, densidades=DENSIDADES, semillas=SEMILLAS, betas=BETAS, presupuestos=PRESUPUESTOS):
    """Las filas de la batería, en memoria. Recorre N, densidad, semilla, B y β en ese orden.

    Cada instancia sale de generar_instancia_influencia (tope de cada nodo = B) y pasa por
    instancia_desde_diccionario, el camino de entrada del formato de la profesora.
    """
    filas = []
    for n in tamanos:
        for densidad in densidades:
            for semilla in semillas:
                for B in presupuestos:
                    nombre = f"aleatorio_N{n}_d{densidad}_s{semilla}_B{B}"
                    inst = instancia_desde_diccionario(generar_instancia_influencia(n, K, B, densidad, semilla),
                                                       nombre)
                    for beta in betas:
                        fila = fila_de_una_instancia(inst, nombre, beta)
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
    filas = bateria()
    escribir_csv(SALIDA, COLUMNAS, filas)
    peor = min(filas, key=lambda f: f["razon_c2"])
    print(f"{len(filas)} filas escritas en {SALIDA}")
    print(f"c1: voraz = exacto en {sum(f['c1_coincide'] for f in filas)} de {len(filas)}")
    print(f"c2: filas con razón < 1: {sum(f['razon_c2'] < 1 - TOLERANCIA for f in filas)}; "
          f"razón mínima {peor['razon_c2']} ({peor['caso']}, beta = {peor['beta']}, cota {peor['cota_c2']})")
    print("todas cumplen:", all(f["cumple"] for f in filas))
    return 0 if all(f["cumple"] for f in filas) else 1


if __name__ == "__main__":
    sys.exit(main())
