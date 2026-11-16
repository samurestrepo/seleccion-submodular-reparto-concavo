"""Genera resultados/variantes/a_tabla_cota.csv: los tres aproximados de la variante (a) contra el OPT exacto.

Uso, desde la raíz del repositorio:  python scripts/tabla_cota_variante_a.py
Filas: el caso de la profesora (N = 15, L = 24) y una batería aleatoria de influencia (decisión 38):
N ∈ {10, 12, 14, 16}, densidad ∈ {0.3, 0.6, 1.0}, semillas 1, 2, 3, costos enteros en [1, 5] del generador
y L = 12. Por fila: f de la fuerza bruta (OPT), del voraz por cociente, del voraz modificado y de la
enumeración parcial, sus razones contra OPT, las evaluaciones de cada uno y si se cumplen las cotas
0,405 (modificado; Tang et al., 2021) y 1 − 1/e (enumeración; Sviridenko, 2004).
No escribe en resultados/profesora/ ni toca la ronda.
"""

import csv
import sys
from math import e
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from red.entrada import instancia_desde_diccionario, leer_instancia  # noqa: E402
from red.generador import generar_instancia_influencia  # noqa: E402
from red.variante_costos import (enumeracion_parcial, seleccionar_exacto_costos,  # noqa: E402
                                 voraz_modificado, voraz_por_cociente)

SALIDA = RAIZ / "resultados" / "variantes" / "a_tabla_cota.csv"
PROFESORA = RAIZ / "casos" / "profesora" / "entrada_G2_red_15_nodos.json"
TOLERANCIA = 1e-9
COTA_MODIFICADO = 0.405           # Tang et al. (2021), f monótona y submodular con mochila
COTA_ENUMERACION = 1 - 1 / e      # Sviridenko (2004)
COLUMNAS = ["caso", "N", "L", "densidad", "semilla", "OPT", "costo_OPT",
            "f_cociente", "razon_cociente", "f_modificado", "razon_modificado", "origen_modificado",
            "f_enumeracion", "razon_enumeracion",
            "eval_exacto", "eval_cociente", "eval_modificado", "eval_enumeracion",
            "cota_modificado", "cota_enumeracion", "cumple"]

# Batería aleatoria (decisión 38): 4 tamaños x 3 densidades x 3 semillas = 36 instancias.
TAMANOS = (10, 12, 14, 16)
DENSIDADES = (0.3, 0.6, 1.0)
SEMILLAS = (1, 2, 3)
K_ALEATORIA = 5     # no se usa en la variante (L reemplaza a k); solo llena el campo del formato
B_ALEATORIA = 100   # no influye en f ni en la selección
L_ALEATORIA = 12    # con costos en [1, 5] (promedio 3), caben unos 4 nodos: ni trivial ni todo


def fila_de_una_instancia(inst, nombre):
    """Los cuatro algoritmos sobre una instancia ya leída, cada uno con un oráculo nuevo. Con OPT = 0 la razón es 1.

    Costo: F evaluaciones de la fuerza bruta (F = subconjuntos factibles, ≤ 2^N) + O(N²) del cociente
    (el modificado no agrega ninguna) + O(N⁵) de la enumeración; ver docs/modulos/variante_costos.md.
    """
    ids = inst.ids()
    costos = inst.costos()
    L = inst.presupuesto_costos
    S_opt, opt, eval_exacto = seleccionar_exacto_costos(inst.crear_oraculo(), ids, costos, L)
    cociente = voraz_por_cociente(inst.crear_oraculo(), ids, costos, L)
    modificado = voraz_modificado(inst.crear_oraculo(), ids, costos, L)
    enumeracion = enumeracion_parcial(inst.crear_oraculo(), ids, costos, L)

    def razon(valor):
        return valor / opt if opt > 0 else 1.0

    razones = (razon(cociente.valor), razon(modificado.valor), razon(enumeracion.valor))
    cumple = (all(r <= 1 + TOLERANCIA for r in razones)
              and razones[1] >= COTA_MODIFICADO - TOLERANCIA
              and razones[2] >= COTA_ENUMERACION - TOLERANCIA)
    return {
        "caso": nombre, "N": inst.N, "L": L, "densidad": "", "semilla": "",
        "OPT": round(opt, 6), "costo_OPT": sum(costos[v] for v in S_opt),
        "f_cociente": round(cociente.valor, 6), "razon_cociente": round(razones[0], 6),
        "f_modificado": round(modificado.valor, 6), "razon_modificado": round(razones[1], 6),
        "origen_modificado": modificado.origen,
        "f_enumeracion": round(enumeracion.valor, 6), "razon_enumeracion": round(razones[2], 6),
        "eval_exacto": eval_exacto, "eval_cociente": cociente.evaluaciones,
        "eval_modificado": modificado.evaluaciones, "eval_enumeracion": enumeracion.evaluaciones,
        "cota_modificado": COTA_MODIFICADO, "cota_enumeracion": round(COTA_ENUMERACION, 6),
        "cumple": cumple,
    }


def fila_de_la_profesora():
    """La fila del caso oficial, con su L = 24 (presupuesto_costos_participacion_por_ronda)."""
    return fila_de_una_instancia(leer_instancia(PROFESORA), PROFESORA.stem)


def bateria_aleatoria(tamanos=TAMANOS, densidades=DENSIDADES, semillas=SEMILLAS, L=L_ALEATORIA):
    """Las filas de la batería aleatoria, en memoria (sin archivos de entrada).

    Recorre N, densidad y semilla en ese orden; cada instancia sale de generar_instancia_influencia con
    presupuesto_costos = L y pasa por instancia_desde_diccionario, el camino de entrada del formato de
    la profesora. Los parámetros permiten una batería más corta en las pruebas.
    """
    filas = []
    for n in tamanos:
        for densidad in densidades:
            for semilla in semillas:
                nombre = f"aleatorio_N{n}_L{L}_d{densidad}_s{semilla}"
                datos = generar_instancia_influencia(n, K_ALEATORIA, B_ALEATORIA, densidad, semilla,
                                                     presupuesto_costos=L)
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
    filas = [fila_de_la_profesora()] + bateria_aleatoria()
    escribir_csv(SALIDA, COLUMNAS, filas)
    minimos = {nombre: min(f[nombre] for f in filas)
               for nombre in ("razon_cociente", "razon_modificado", "razon_enumeracion")}
    print(f"{len(filas)} filas escritas en {SALIDA}")
    print("razones mínimas contra OPT:", minimos)
    print("todas cumplen las cotas:", all(f["cumple"] for f in filas))
    return 0 if all(f["cumple"] for f in filas) else 1


if __name__ == "__main__":
    sys.exit(main())
