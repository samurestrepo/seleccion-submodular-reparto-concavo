"""Línea de comandos: correr una ronda por cada caso y guardar las evidencias.

Uso (desde la raíz del repositorio):
    python ejecutar.py casos/propios/ejemplo_informe.json
    python ejecutar.py casos/profesora                  # todos los .json de la carpeta
    python ejecutar.py casos/propios --salida resultados/propios

Por cada caso escribe en <salida>/<nombre_del_caso>/:
    salida.json   resultado, tiempos y verificaciones
    traza.json    paso a paso de los dos voraces
    traza.txt     lo mismo, en texto legible
y además <salida>/resumen.csv con una fila por caso.
"""

import argparse
import csv
import os
import sys

from red.entrada import ErrorDeFormato, leer_instancia
from red.ronda import ejecutar_ronda
from red.traza import a_texto, escribir_json


def buscar_casos(rutas):
    """Expande las rutas: un archivo se toma tal cual; una carpeta aporta sus .json en orden."""
    casos = []
    for ruta in rutas:
        if os.path.isdir(ruta):
            for nombre in sorted(os.listdir(ruta)):
                if nombre.endswith(".json"):
                    casos.append(os.path.join(ruta, nombre))
        else:
            casos.append(ruta)
    return casos


def guardar_evidencias(resultado, carpeta):
    """Escribe salida.json, traza.json y traza.txt de un caso."""
    os.makedirs(carpeta, exist_ok=True)
    salida = {clave: valor for clave, valor in resultado.items() if clave != "traza"}
    escribir_json(os.path.join(carpeta, "salida.json"), salida)
    if "traza" in resultado:
        escribir_json(os.path.join(carpeta, "traza.json"), resultado["traza"])
        with open(os.path.join(carpeta, "traza.txt"), "w", encoding="utf-8") as archivo:
            archivo.write(a_texto(resultado))


def main(argumentos=None):
    p = argparse.ArgumentParser(description="Ejecuta la solución base del Proyecto Red.")
    p.add_argument("rutas", nargs="+", help="archivos .json o carpetas con casos")
    p.add_argument("--salida", default="resultados", help="carpeta de evidencias (por omisión: resultados)")
    a = p.parse_args(argumentos)

    casos = buscar_casos(a.rutas)
    if not casos:
        print("No se encontró ningún caso .json.")
        return 1

    filas = []
    hubo_fallas = False
    for ruta in casos:
        try:
            instancia = leer_instancia(ruta)
        except (ErrorDeFormato, OSError) as error:
            print(f"[ERROR] {ruta}: {error}")
            hubo_fallas = True
            continue
        resultado = ejecutar_ronda(instancia)
        guardar_evidencias(resultado, os.path.join(a.salida, instancia.nombre))
        if not resultado["todas_cumplen"]:
            hubo_fallas = True
        if "seleccion" in resultado:
            t = resultado["tiempos_segundos"]
            filas.append([instancia.nombre, instancia.N, instancia.k, instancia.B,
                          " ".join(map(str, resultado["seleccion"]["S"])), resultado["seleccion"]["valor"],
                          f"{resultado['reparto']['utilidad']:.6f}", f"{t['seleccion']:.9f}",
                          f"{t['reparto']:.9f}", resultado["todas_cumplen"]])
            print(f"[{'OK' if resultado['todas_cumplen'] else 'FALLA'}] {instancia.nombre}: "
                  f"S = {resultado['seleccion']['S']}, f(S) = {resultado['seleccion']['valor']}, "
                  f"utilidad = {resultado['reparto']['utilidad']:.4f}, "
                  f"tiempos = {t['seleccion']:.6f} s + {t['reparto']:.6f} s")
        else:
            print(f"[FALLA] {instancia.nombre}: la entrada no cumple sus restricciones (ver traza)")

    os.makedirs(a.salida, exist_ok=True)
    with open(os.path.join(a.salida, "resumen.csv"), "w", encoding="utf-8", newline="") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["caso", "N", "k", "B", "S", "f(S)", "utilidad_reparto",
                           "tiempo_seleccion_s", "tiempo_reparto_s", "todas_cumplen"])
        escritor.writerows(filas)
    print(f"Evidencias en {a.salida}/")
    return 1 if hubo_fallas else 0


if __name__ == "__main__":
    sys.exit(main())
