"""Prueba fuera de muestra de la serie d (informe final, sección 11.3, punto 2; decisión 60).

Uso, desde la raíz del repositorio:  python scripts/serie_d_fuera_de_muestra.py
No mide nada: solo lee dos CSV que ya existen en resultados/experimentos/.
  1. Serie e (N = 100 fijo): recta t_min = α + β·B por mínimos cuadrados. Como el modelo del reparto
     es t ≈ a·N + b·B·lg N, con N = 100 queda α = a·100 y β = b·lg 100, así que a = α/100 y
     b = β/lg 100 (lg = log₂, el mismo de experimentos.py).
  2. Con esas a y b se predice la serie d (B = 1000): t = a·N + b·1000·lg N. La serie d no se usó
     para estimar nada: por eso es «fuera de muestra».
  3. Error por punto (predicho − medido)/medido y pendiente log-log de lo predicho y de lo medido
     contra N (la misma regresión `pendiente` de experimentos.py, con logaritmo natural).
Escribe resultados/experimentos/d_fuera_de_muestra.csv. Tiempo O(puntos de d + puntos de e).
"""

import argparse
import csv
import sys
from math import log, log2
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

from experimentos import pendiente  # noqa: E402  (misma regresión que las demás series)

CARPETA = RAIZ / "resultados" / "experimentos"
ENTRADA_E = CARPETA / "e_reparto_varia_B.csv"
ENTRADA_D = CARPETA / "d_reparto_varia_N.csv"
SALIDA = CARPETA / "d_fuera_de_muestra.csv"
COLUMNAS = ["tipo", "N", "B", "t_min_medido", "t_predicho", "error_relativo", "nombre", "valor"]


def leer_serie(ruta):
    """Lee un CSV de experimentos.py y devuelve [{'N', 'B', 't_min'}] (N y B enteros, t_min en s).

    Solo usa las columnas N, B y t_min; no toca t_ajustado (el ajuste conjunto de d y e). O(filas).
    """
    with open(ruta, newline="", encoding="utf-8") as archivo:
        return [{"N": int(f["N"]), "B": int(f["B"]), "t_min": float(f["t_min"])}
                for f in csv.DictReader(archivo)]


def recta(xs, ys):
    """Recta y = α + β·x por mínimos cuadrados (con término independiente).

    β es la `pendiente` de experimentos.py y α = media(y) − β·media(x). Devuelve (α, β). O(n).
    """
    beta = pendiente(xs, ys)
    alfa = sum(ys) / len(ys) - beta * sum(xs) / len(xs)
    return alfa, beta


def constantes_desde_e(filas_e):
    """Estima a y b del modelo t ≈ a·N + b·B·lg N solo con la serie e (N fijo).

    Exige un único N en las filas. Con N fijo, t = (a·N) + (b·lg N)·B es una recta en B:
    a = α/N y b = β/lg N. Devuelve (a, b, α, β). O(filas).
    """
    valores_N = {f["N"] for f in filas_e}
    if len(valores_N) != 1:
        raise ValueError(f"la serie e debe tener un solo N y tiene {sorted(valores_N)}")
    N = valores_N.pop()
    alfa, beta = recta([f["B"] for f in filas_e], [f["t_min"] for f in filas_e])
    return alfa / N, beta / log2(N), alfa, beta


def predecir(filas_d, a, b):
    """Predice cada punto de la serie d con t = a·N + b·B·lg N y su error (predicho − medido)/medido.

    Devuelve una fila nueva por punto con N, B, t_min_medido, t_predicho y error_relativo. O(filas).
    """
    puntos = []
    for f in filas_d:
        t_predicho = a * f["N"] + b * f["B"] * log2(f["N"])
        puntos.append({"N": f["N"], "B": f["B"], "t_min_medido": f["t_min"], "t_predicho": t_predicho,
                       "error_relativo": (t_predicho - f["t_min"]) / f["t_min"]})
    return puntos


def pendientes(puntos):
    """Pendientes log-log contra N de lo predicho y de lo medido: (predicha, medida). O(puntos)."""
    log_N = [log(p["N"]) for p in puntos]
    return (pendiente(log_N, [log(p["t_predicho"]) for p in puntos]),
            pendiente(log_N, [log(p["t_min_medido"]) for p in puntos]))


def calcular(ruta_e=ENTRADA_E, ruta_d=ENTRADA_D):
    """Hace la prueba completa y devuelve {'puntos': [...], 'resumen': {nombre: valor}}. O(filas)."""
    a, b, alfa, beta = constantes_desde_e(leer_serie(ruta_e))
    puntos = predecir(leer_serie(ruta_d), a, b)
    predicha, medida = pendientes(puntos)
    resumen = {"alfa_s": alfa, "beta_s_por_unidad": beta, "a_s": a, "b_s": b,
               "pendiente_predicha": predicha, "pendiente_medida": medida}
    return {"puntos": puntos, "resumen": resumen}


def escribir_csv(ruta, resultado):
    """Escribe el CSV: una fila 'punto' por N de la serie d y una fila 'resumen' por constante.

    Las filas 'punto' llenan N..error_relativo y dejan vacías nombre y valor; las 'resumen', al revés.
    Los flotantes van con repr, como en experimentos.py. O(filas).
    """
    def texto(x):
        return repr(x) if isinstance(x, float) else x
    with open(ruta, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=COLUMNAS, restval="")
        escritor.writeheader()
        for p in resultado["puntos"]:
            escritor.writerow({"tipo": "punto", **{c: texto(v) for c, v in p.items()}})
        for nombre, valor in resultado["resumen"].items():
            escritor.writerow({"tipo": "resumen", "nombre": nombre, "valor": texto(valor)})


def imprimir(resultado):
    """Imprime a, b, el error de cada punto y las dos pendientes."""
    r = resultado["resumen"]
    print(f"Serie e (N = 100): t_min = {r['alfa_s']:.6e} + {r['beta_s_por_unidad']:.6e}·B")
    print(f"a = {r['a_s']:.3e} s   b = {r['b_s']:.3e} s")
    for p in resultado["puntos"]:
        print(f"  N = {p['N']:>6}  medido = {p['t_min_medido']:.6f}  predicho = {p['t_predicho']:.6f}"
              f"  error = {p['error_relativo']:+.1%}")
    print(f"pendiente log-log: predicha {r['pendiente_predicha']:.2f}, medida {r['pendiente_medida']:.2f}")


def leer_argumentos(argumentos=None):
    """Lee la línea de comandos. El script no tiene opciones: solo existe para atender --help (y -h).

    argumentos: lista de textos (None = sys.argv[1:]). Con --help, argparse imprime la ayuda y sale
    con SystemExit(0) antes de leer o escribir nada. La ayuda va solo en caracteres de cp1252
    (la consola de Windows), por eso no usa __doc__, que lleva α, β y ₂. O(1).
    """
    p = argparse.ArgumentParser(
        description=(
            'Prueba fuera de muestra de la serie d (informe final, seccion 11.3, punto 2).\n'
            'Estima a y b solo con resultados/experimentos/e_reparto_varia_B.csv (N = 100 fijo,\n'
            'recta t_min = alfa + beta*B; a = alfa/100, b = beta/lg 100, lg = log en base 2) y con\n'
            'ellas predice la serie d (d_reparto_varia_N.csv): t = a*N + b*B*lg N.'
        ),
        epilog=(
            'No mide nada y no recibe opciones: sin argumentos escribe\n'
            'resultados/experimentos/d_fuera_de_muestra.csv (error por punto, a, b y las pendientes\n'
            'log-log predicha y medida) e imprime los mismos valores.\n'
            'Uso, desde la raíz del repositorio:  python scripts/serie_d_fuera_de_muestra.py'
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter)
    return p.parse_args(argumentos)


def main(argumentos=None):
    leer_argumentos(argumentos)       # con --help sale aquí, sin leer ni escribir nada
    resultado = calcular()
    escribir_csv(SALIDA, resultado)
    imprimir(resultado)
    print(f"Escrito: {SALIDA}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
