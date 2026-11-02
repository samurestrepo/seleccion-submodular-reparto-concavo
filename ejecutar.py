"""Línea de comandos: correr una ronda por cada caso y guardar las evidencias.

Uso (desde la raíz del repositorio):
    python ejecutar.py casos/propios/ejemplo_informe.json
    python ejecutar.py casos/profesora                  # todos los .json de la carpeta
    python ejecutar.py casos/propios --salida resultados/propios

Por cada caso escribe en <salida>/<nombre_del_caso>/:
    salida.json   resultado, tiempos y verificaciones
    traza.json    paso a paso de los dos voraces (o el motivo, si el caso se rechazó)
    traza.txt     lo mismo, en texto legible
y además <salida>/resumen.csv con una fila por caso de ESTA corrida: no acumula corridas
anteriores. Si ya existía, se reemplaza y se avisa por consola.
"""

import argparse
import csv
import os
import sys

from red.entrada import ErrorDeFormato, leer_instancia, nombre_del_caso
from red.ronda import ejecutar_ronda, resultado_de_error
from red.traza import a_texto, escribir_json


def buscar_casos(rutas):
    """Expande las rutas: un archivo se toma tal cual; una carpeta aporta sus .json en orden.

    La extensión se reconoce sin distinguir mayúsculas (.json, .JSON).
    """
    casos = []
    for ruta in rutas:
        if os.path.isdir(ruta):
            for nombre in sorted(os.listdir(ruta)):
                if nombre.lower().endswith(".json"):
                    casos.append(os.path.join(ruta, nombre))
        else:
            casos.append(ruta)
    return casos


def guardar_evidencias(resultado, carpeta):
    """Escribe salida.json, traza.json y traza.txt de un caso.

    Siempre escribe los tres, también si el caso se rechazó: así reemplazan a los de
    una corrida anterior y no queda una traza vieja que contradiga el resultado.
    """
    os.makedirs(carpeta, exist_ok=True)
    salida = {clave: valor for clave, valor in resultado.items() if clave != "traza"}
    escribir_json(os.path.join(carpeta, "salida.json"), salida)
    escribir_json(os.path.join(carpeta, "traza.json"), resultado["traza"])
    with open(os.path.join(carpeta, "traza.txt"), "w", encoding="utf-8") as archivo:
        archivo.write(a_texto(resultado))


def correr_caso(ruta, salida):
    """Lee un caso, corre su ronda, guarda sus evidencias e imprime una línea. Devuelve el resultado.

    Un archivo malo no detiene el lote: devuelve un resultado rechazado. Si no se pudo
    ni abrir, no escribe evidencias, porque no hay caso del cual dejar constancia.
    """
    nombre = nombre_del_caso(ruta)
    try:
        instancia = leer_instancia(ruta)
    except OSError as error:
        print(f"[ERROR] {ruta}: {error}")
        return resultado_de_error(nombre, str(error))
    except ErrorDeFormato as error:
        print(f"[ERROR] {ruta}: {error}")
        resultado = resultado_de_error(nombre, str(error))
        guardar_evidencias(resultado, os.path.join(salida, nombre))
        return resultado

    resultado = ejecutar_ronda(instancia)
    guardar_evidencias(resultado, os.path.join(salida, nombre))
    if "seleccion" not in resultado:
        print(f"[FALLA] {nombre}: la entrada no cumple sus restricciones (ver traza)")
        return resultado
    t = resultado["tiempos_segundos"]
    print(f"[{'OK' if resultado['todas_cumplen'] else 'FALLA'}] {nombre}: "
          f"S = {resultado['seleccion']['S']}, f(S) = {resultado['seleccion']['valor']}, "
          f"utilidad = {resultado['reparto']['utilidad']:.4f}, "
          f"tiempos = {t['seleccion']:.6f} s + {t['reparto']:.6f} s")
    return resultado


def fila_resumen(resultado):
    """La fila de resumen.csv de un caso. Un caso rechazado deja vacíos S, f(S), utilidad y tiempos."""
    e = resultado["entrada"]
    if "seleccion" not in resultado:
        return [resultado["caso"], e["N"], e["k"], e["B"], "", "", "", "", "", False]
    t = resultado["tiempos_segundos"]
    return [resultado["caso"], e["N"], e["k"], e["B"],
            " ".join(map(str, resultado["seleccion"]["S"])), resultado["seleccion"]["valor"],
            f"{resultado['reparto']['utilidad']:.6f}", f"{t['seleccion']:.9f}",
            f"{t['reparto']:.9f}", resultado["todas_cumplen"]]


def escribir_resumen(filas, salida):
    """Escribe <salida>/resumen.csv con las filas de esta corrida. Avisa si reemplaza uno anterior."""
    os.makedirs(salida, exist_ok=True)
    ruta = os.path.join(salida, "resumen.csv")
    if os.path.exists(ruta):
        print(f"Aviso: se reemplaza {ruta}; el resumen solo refleja esta corrida.")
    with open(ruta, "w", encoding="utf-8", newline="") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["caso", "N", "k", "B", "S", "f(S)", "utilidad_reparto",
                           "tiempo_seleccion_s", "tiempo_reparto_s", "todas_cumplen"])
        escritor.writerows(filas)


def main(argumentos=None):
    """Corre todos los casos pedidos y escribe el resumen.

    Recibe las rutas y --salida. Dos archivos con el mismo nombre de caso son un error:
    el segundo no se ejecuta, para no pisar las evidencias del primero (los nombres
    se comparan sin distinguir mayúsculas, porque en Windows serían la misma carpeta).
    Devuelve 0 si todo cumple, 1 si algo falla o no hay casos.
    """
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
    primera_ruta = {}   # nombre del caso (sin distinguir mayúsculas) → ruta que lo usó primero
    for ruta in casos:
        clave = nombre_del_caso(ruta).casefold()
        if clave in primera_ruta:
            print(f"[ERROR] {ruta}: el caso '{nombre_del_caso(ruta)}' ya se corrió con "
                  f"{primera_ruta[clave]}; no se ejecuta para no pisar sus evidencias")
            hubo_fallas = True
            continue
        primera_ruta[clave] = ruta
        resultado = correr_caso(ruta, a.salida)
        filas.append(fila_resumen(resultado))
        if not resultado["todas_cumplen"]:
            hubo_fallas = True

    escribir_resumen(filas, a.salida)
    print(f"Evidencias en {a.salida}/")
    return 1 if hubo_fallas else 0


if __name__ == "__main__":
    sys.exit(main())
