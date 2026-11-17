"""Línea de comandos: correr una ronda por cada caso y guardar las evidencias.

Uso (desde la raíz del repositorio):
    python ejecutar.py casos/propios/ejemplo_informe.json
    python ejecutar.py casos/profesora                  # todos los .json de la carpeta
    python ejecutar.py casos/propios --salida resultados/propios
    python ejecutar.py casos/propios --repeticiones 5   # por omisión, 21
    python ejecutar.py casos/profesora --variante a --salida resultados/variantes/a_profesora
                                                        # variante (a): costos de participación
    python ejecutar.py casos/profesora --variante b --modo-fallo permanente --prob-fallo 0.2 \
        --semilla-fallos 0 --salida resultados/variantes/b_profesora_permanente
                                                        # variante (b): T rondas con nodos que fallan
    python ejecutar.py casos/profesora --variante c2 --beta 0.2 --limite-repartos 302792         --salida resultados/variantes/c2_profesora   # variante (c): vecinos que alteran la utilidad (c1 o c2)

Por cada caso escribe en <salida>/<nombre_del_caso>/:
    salida.json   resultado, tiempos (mediana, mínimo, máximo y R) y verificaciones
    traza.json    paso a paso de los dos voraces (o el motivo, si el caso se rechazó)
    traza.txt     lo mismo, en texto legible
y además <salida>/resumen.csv con una fila por caso de ESTA corrida (con --variante b, una fila
por ronda de cada caso): no acumula corridas anteriores. Si ya existía, se reemplaza y se avisa.
"""

import argparse
import csv
import math
import os
import sys

from red.entrada import ErrorDeFormato, leer_instancia, nombre_del_caso
from red.ronda import REPETICIONES, ejecutar_ronda, resultado_de_error
from red.traza import a_texto, escribir_json
from red.variante_rondas import MODOS, PROBABILIDAD_FALLO, SEMILLA_FALLOS, a_texto_rondas, ejecutar_rondas
from red.variante_vecinos import BETA, LIMITE_REPARTOS, MODELOS, a_texto_vecinos, ejecutar_variante_c

# Columnas de resumen.csv: una fila por caso (base y variante a) o una por ronda (variante b)
ENCABEZADO = ["caso", "N", "k", "B", "S", "f(S)", "utilidad_reparto",
              "tiempo_seleccion_s", "tiempo_reparto_s", "minimo_seleccion_s", "minimo_reparto_s",
              "repeticiones", "todas_cumplen"]
ENCABEZADO_RONDAS = ["caso", "modo", "prob_fallo", "semilla", "T", "ronda", "N", "k", "B", "fallados",
                     "candidatos", "k_ronda", "S_r", "f(S_r)", "OPT_r", "razon", "utilidad_reparto",
                     "presupuesto_restante_total", "tiempo_seleccion_s", "tiempo_reparto_s",
                     "repeticiones", "todas_cumplen"]


def _entero_positivo(texto):
    """Convierte el valor de --repeticiones o --rondas. Si no es un entero ≥ 1, argparse muestra el error."""
    try:
        valor = int(texto)
    except ValueError:
        raise argparse.ArgumentTypeError(f"debe ser un entero; llegó {texto!r}") from None
    if valor < 1:
        raise argparse.ArgumentTypeError(f"debe ser al menos 1; llegó {valor}")
    return valor


def _probabilidad(texto):
    """Convierte el valor de --prob-fallo: un número en [0, 1]. Si no, argparse muestra el error."""
    try:
        valor = float(texto)
    except ValueError:
        raise argparse.ArgumentTypeError(f"debe ser un número; llegó {texto!r}") from None
    if not 0 <= valor <= 1:
        raise argparse.ArgumentTypeError(f"debe estar en [0, 1]; llegó {valor}")
    return valor


def _beta(texto):
    """Convierte el valor de --beta: un número finito ≥ 0. Si no, argparse muestra el error."""
    try:
        valor = float(texto)
    except ValueError:
        raise argparse.ArgumentTypeError(f"debe ser un número; llegó {texto!r}") from None
    if not math.isfinite(valor) or valor < 0:
        raise argparse.ArgumentTypeError(f"debe ser un número finito >= 0; llegó {valor}")
    return valor


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
    if "rondas" in resultado:              # variante (b)
        texto = a_texto_rondas(resultado)
    elif "variante_c" in resultado:        # variante (c)
        texto = a_texto_vecinos(resultado)
    else:
        texto = a_texto(resultado)
    with open(os.path.join(carpeta, "traza.txt"), "w", encoding="utf-8") as archivo:
        archivo.write(texto)


def _imprimir_rondas(nombre, resultado):
    """Una línea por ronda de la variante (b): candidatos, fallados, S_r, f(S_r), OPT_r, razón y U_r."""
    estado = "OK" if resultado["todas_cumplen"] else "FALLA"
    e = resultado["entrada"]
    print(f"[{estado}] {nombre}: variante (b), modo = {e['modo']}, q = {e['prob_fallo']}, T = {e['T']} rondas")
    for r in resultado["rondas"]:
        opt = f"{r['exacto']['OPT']}" if r["exacto"]["disponible"] else "no disponible"
        razon = "-" if r["razon"] is None else f"{r['razon']:.6f}"
        print(f"    ronda {r['ronda']}: candidatos = {len(r['candidatos'])}, fallados = {r['fallados']}, "
              f"S_r = {r['seleccion']['S']}, f(S_r) = {r['seleccion']['valor']}, OPT_r = {opt}, "
              f"razon = {razon}, U_r = {r['reparto']['utilidad']:.4f}")


def correr_caso(ruta, salida, repeticiones=REPETICIONES, variante=None, fallos=None, vecinos=None):
    """Lee un caso, corre su ronda (o sus T rondas), guarda sus evidencias e imprime. Devuelve el resultado.

    repeticiones es R, las veces que se repite la ejecución medida; variante es None (base), "a", "b", "c1" o "c2".
    fallos son los parámetros de la variante (b): diccionario con modo, prob_fallo, semilla y rondas.
    vecinos son los de la variante (c): diccionario con beta y limite (de la enumeración).
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

    if variante == "b":
        resultado = ejecutar_rondas(instancia, repeticiones=repeticiones, **(fallos or {}))
    elif variante in MODELOS:
        resultado = ejecutar_variante_c(instancia, variante, repeticiones=repeticiones, **(vecinos or {}))
    else:
        resultado = ejecutar_ronda(instancia, repeticiones, variante)
    guardar_evidencias(resultado, os.path.join(salida, nombre))
    if "rondas" in resultado:
        _imprimir_rondas(nombre, resultado)
        return resultado
    if "seleccion" not in resultado:
        print(f"[FALLA] {nombre}: la entrada no cumple sus restricciones (ver traza)")
        return resultado
    t = resultado["tiempos_segundos"]
    costo = ""
    if "variante" in resultado:   # variante (a): se muestra el costo de S frente a L
        costo = f"costo(S) = {resultado['seleccion']['costo']} <= L = {resultado['variante']['L']}, "
    if "variante_c" in resultado:   # variante (c): el modelo, beta y el exacto si cupo
        ex = resultado["exacto"]
        opt = f"OPT = {ex['OPT']:.4f}, razon = {ex['razon']:.6f}" if ex["disponible"] else "OPT no disponible"
        costo = f"modelo {resultado['variante_c']['modelo']}, beta = {resultado['variante_c']['beta']}, {opt}, "
    print(f"[{'OK' if resultado['todas_cumplen'] else 'FALLA'}] {nombre}: "
          f"S = {resultado['seleccion']['S']}, f(S) = {resultado['seleccion']['valor']}, {costo}"
          f"utilidad = {resultado['reparto']['utilidad']:.4f}, "
          f"tiempos (mediana de {t['repeticiones']}) = "
          f"{t['seleccion']['mediana']:.6f} s + {t['reparto']['mediana']:.6f} s")
    return resultado


def fila_resumen(resultado):
    """La fila de resumen.csv de un caso: las medianas y los mínimos de las R repeticiones.

    Para la gráfica de T(n) se usa el mínimo (decisión 30). Un caso rechazado deja vacíos
    S, f(S), utilidad, tiempos y repeticiones.
    """
    e = resultado["entrada"]
    if "seleccion" not in resultado:
        return [resultado["caso"], e["N"], e["k"], e["B"], "", "", "", "", "", "", "", "", False]
    t = resultado["tiempos_segundos"]
    return [resultado["caso"], e["N"], e["k"], e["B"],
            " ".join(map(str, resultado["seleccion"]["S"])), resultado["seleccion"]["valor"],
            f"{resultado['reparto']['utilidad']:.6f}", f"{t['seleccion']['mediana']:.9f}",
            f"{t['reparto']['mediana']:.9f}", f"{t['seleccion']['minimo']:.9f}",
            f"{t['reparto']['minimo']:.9f}", t["repeticiones"], resultado["todas_cumplen"]]


def filas_resumen_rondas(resultado):
    """Las filas de resumen.csv de un caso con la variante (b): una por ronda (`ENCABEZADO_RONDAS`).

    Un caso rechazado deja una sola fila con lo que se conoce y las demás columnas vacías.
    Tiempo O(T·N) por la suma del presupuesto restante de cada ronda.
    """
    e = resultado["entrada"]
    if "rondas" not in resultado:
        return [[resultado["caso"], e.get("modo", ""), e.get("prob_fallo", ""), e.get("semilla", ""),
                 e.get("T", ""), "", e["N"], e["k"], e["B"]] + [""] * 12 + [False]]
    filas = []
    for r in resultado["rondas"]:
        t = r["tiempos_segundos"]
        opt = r["exacto"]["OPT"] if r["exacto"]["disponible"] else ""
        razon = "" if r["razon"] is None else f"{r['razon']:.6f}"
        filas.append([resultado["caso"], e["modo"], e["prob_fallo"], e["semilla"], e["T"], r["ronda"],
                      e["N"], e["k"], e["B"], " ".join(map(str, r["fallados"])), len(r["candidatos"]),
                      r["k_ronda"], " ".join(map(str, r["seleccion"]["S"])), r["seleccion"]["valor"], opt, razon,
                      f"{r['reparto']['utilidad']:.6f}", sum(r["presupuesto_restante"].values()),
                      f"{t['seleccion']['mediana']:.9f}", f"{t['reparto']['mediana']:.9f}", t["repeticiones"],
                      r["todas_cumplen"]])
    return filas


def escribir_resumen(filas, salida, encabezado=ENCABEZADO):
    """Escribe <salida>/resumen.csv con las filas de esta corrida. Avisa si reemplaza uno anterior."""
    os.makedirs(salida, exist_ok=True)
    ruta = os.path.join(salida, "resumen.csv")
    if os.path.exists(ruta):
        print(f"Aviso: se reemplaza {ruta}; el resumen solo refleja esta corrida.")
    with open(ruta, "w", encoding="utf-8", newline="") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(encabezado)
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
    p.add_argument("--repeticiones", type=_entero_positivo, default=REPETICIONES,
                   help=f"veces que se repite la ejecución medida; se reporta la mediana (por omisión: {REPETICIONES})")
    p.add_argument("--variante", choices=["a", "b"] + list(MODELOS), default=None,
                   help="a = costos de participacion: la Parte 2 maximiza f con suma de costos <= L "
                        "en lugar de |S| <= k; b = T rondas con nodos que fallan y presupuesto por nodo "
                        "que se descuenta; c1 / c2 = los vecinos en S alteran la utilidad del reparto "
                        "(c1 efecto aparte, c2 efecto dentro; solo con grafo) (por omision: ninguna, solucion base)")
    p.add_argument("--modo-fallo", choices=list(MODOS), default=MODOS[0],
                   help="variante b: transitorio = el nodo falla solo esa ronda; permanente = no vuelve "
                        f"(por omision: {MODOS[0]})")
    p.add_argument("--prob-fallo", type=_probabilidad, default=PROBABILIDAD_FALLO,
                   help=f"variante b: probabilidad q de que cada nodo falle antes de una ronda (por omision: {PROBABILIDAD_FALLO})")
    p.add_argument("--semilla-fallos", type=int, default=SEMILLA_FALLOS,
                   help=f"variante b: semilla del sorteo de fallos (por omision: {SEMILLA_FALLOS})")
    p.add_argument("--rondas", type=_entero_positivo, default=None,
                   help="variante b: T, el numero de rondas; por omision el numero_rondas (o rondas) del caso, o 1")
    p.add_argument("--beta", type=_beta, default=BETA,
                   help=f"variantes c1 y c2: intensidad beta >= 0 del efecto de los vecinos (por omision: {BETA})")
    p.add_argument("--limite-repartos", type=_entero_positivo, default=LIMITE_REPARTOS,
                   help="variantes c1 y c2: maximo de repartos que enumera el exacto de referencia; si hay "
                        f"mas, no corre (por omision: {LIMITE_REPARTOS})")
    a = p.parse_args(argumentos)
    vecinos = {"beta": a.beta, "limite": a.limite_repartos}
    fallos = {"modo": a.modo_fallo, "prob_fallo": a.prob_fallo, "semilla": a.semilla_fallos, "rondas": a.rondas}
    encabezado = ENCABEZADO_RONDAS if a.variante == "b" else ENCABEZADO

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
        resultado = correr_caso(ruta, a.salida, a.repeticiones, a.variante, fallos, vecinos)
        if a.variante == "b":
            filas += filas_resumen_rondas(resultado)
        else:
            filas.append(fila_resumen(resultado))
        if not resultado["todas_cumplen"]:
            hubo_fallas = True

    escribir_resumen(filas, a.salida, encabezado)
    print(f"Evidencias en {a.salida}/")
    return 1 if hubo_fallas else 0


if __name__ == "__main__":
    sys.exit(main())
