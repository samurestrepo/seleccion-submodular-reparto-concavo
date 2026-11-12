"""Experimentos de tiempo: 8 series que contrastan lo medido con la T(n) teórica del informe.

Uso, desde la raíz del repositorio:
    python scripts/experimentos.py                 # las 8 series: CSV y gráficas en resultados/experimentos/
    python scripts/experimentos.py --series a d    # solo algunas
    python scripts/experimentos.py --sin-graficas  # solo CSV (no necesita matplotlib)

Se cronometra SOLO el algoritmo (decisión 8): la instancia y el oráculo se crean antes del reloj, y no
se lee ni se escribe ningún archivo dentro de la medición. Cada punto se repite 21 veces con
time.perf_counter; se guardan el mínimo (el de las gráficas, decisión 30) y la mediana.
"""

import argparse
import csv
import statistics
import sys
import time
from math import comb, log2
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from red.entrada import instancia_desde_diccionario      # noqa: E402
from red.exacto import seleccionar_exacto                # noqa: E402
from red.pd_reparto import repartir_pd                  # noqa: E402
from red.generador import generar_instancia, generar_instancia_influencia  # noqa: E402
from red.reparto import repartir_presupuesto             # noqa: E402
from red.seleccion import seleccionar_nodos              # noqa: E402

SALIDA = RAIZ / "resultados" / "experimentos"
SEMILLA = 1          # misma semilla en todas las series (decisión 32)
REPETICIONES = 21
COLUMNAS = ["n", "N", "k", "B", "densidad", "semilla", "t_min", "t_mediana",
            "conteo", "T_teorica", "cociente"]
COLUMNAS_H = COLUMNAS + ["repeticiones"]         # serie h: repeticiones realmente usadas (límite de 2 s)
LIMITE_UNA_REPETICION = 2.0                      # s; si una repetición lo pasa, la serie h usa REPETICIONES_LENTAS
REPETICIONES_LENTAS = 5
COLUMNAS_AJUSTADAS = COLUMNAS + ["t_ajustado"]   # series d y e: se agrega el tiempo del ajuste (decisión 32)


# ----------------------------------------------------------------- medición

def medir(preparar, repeticiones=REPETICIONES):
    """Mide un algoritmo `repeticiones` veces y devuelve (t_min, t_mediana, conteo).

    `preparar()` crea el estado fresco (oráculo nuevo) FUERA del reloj y devuelve (ejecutar, contar):
    `ejecutar()` es el algoritmo y es lo único que se cronometra; `contar()` lee el contador de
    operaciones básicas (se toma de la primera repetición). Tiempo: repeticiones · T(algoritmo).
    """
    return medir_con_limite(preparar, repeticiones)[:3]


def medir_con_limite(preparar, repeticiones=REPETICIONES, limite=None):
    """Como `medir`, pero devuelve (t_min, t_mediana, conteo, repeticiones_usadas).

    Si `limite` (segundos) no es None y la primera repetición lo pasa, se hacen solo
    min(repeticiones, REPETICIONES_LENTAS) repeticiones en total: así la serie h no se vuelve eterna.
    """
    tiempos = []
    conteo = None
    total = repeticiones
    repeticion = 0
    while repeticion < total:
        ejecutar, contar = preparar()
        inicio = time.perf_counter()
        ejecutar()
        tiempos.append(time.perf_counter() - inicio)
        if repeticion == 0:
            conteo = contar()
            if limite is not None and tiempos[0] > limite:
                total = min(total, REPETICIONES_LENTAS)
        repeticion += 1
    return min(tiempos), statistics.median(tiempos), conteo, total


# ------------------------------------------------- cómo se prepara cada algoritmo

def _preparar_seleccion(instancia):
    """Voraz de la Parte 2 sobre `instancia`. Conteo: llamadas a Δ (ganancia) del oráculo."""
    ids = instancia.ids()

    def preparar():
        oraculo = instancia.crear_oraculo()
        return (lambda: seleccionar_nodos(oraculo, ids, instancia.k),
                lambda: oraculo.llamadas_ganancia)
    return preparar


def _preparar_reparto(instancia):
    """Voraz de la Parte 1 con los N nodos. Conteo: extracciones + inserciones del montículo."""
    ids = instancia.ids()
    utilidades = instancia.utilidades()
    resultado = []

    def ejecutar():
        resultado.append(repartir_presupuesto(ids, instancia.B, utilidades))

    def preparar():
        resultado.clear()
        return ejecutar, lambda: resultado[0].extracciones + resultado[0].inserciones
    return preparar


def _preparar_pd(instancia):
    """PD de la Parte 1 con los N nodos y topes ≥ B (sin topes). Conteo: candidatos t evaluados."""
    ids = instancia.ids()
    utilidades = instancia.utilidades()
    resultado = []

    def ejecutar():
        resultado.append(repartir_pd(ids, instancia.B, utilidades))

    def preparar():
        resultado.clear()
        return ejecutar, lambda: resultado[0].candidatos
    return preparar


def _preparar_exacto(instancia):
    """Fuerza bruta de la Parte 2. Conteo: evaluaciones de f(S) (exactamente C(N, k))."""
    ids = instancia.ids()
    resultado = []

    def preparar():
        oraculo = instancia.crear_oraculo()
        resultado.clear()
        return (lambda: resultado.append(seleccionar_exacto(oraculo, ids, instancia.k)),
                lambda: resultado[0][2])
    return preparar


# ----------------------------------------------------------------- las 8 series
# Cada serie es (nombre, descripción, tamaños, construir(n) → (parámetros, preparar), T_teorica(parámetros)).
# `construir` genera la instancia FUERA del reloj, directo del generador (sin archivos).

K = 5


def _cobertura(n):
    inst = instancia_desde_diccionario(generar_instancia(n, K, 100, semilla=SEMILLA))
    return dict(N=n, k=K, B=100, densidad=""), _preparar_seleccion(inst)


def _influencia(densidad_de):
    def construir(n):
        d = densidad_de(n)
        inst = instancia_desde_diccionario(generar_instancia_influencia(n, K, 100, d, SEMILLA))
        return dict(N=n, k=K, B=100, densidad=d), _preparar_seleccion(inst)
    return construir


def _reparto_varia_n(n):
    inst = instancia_desde_diccionario(generar_instancia(n, K, 1000, semilla=SEMILLA))
    return dict(N=n, k=K, B=1000, densidad=""), _preparar_reparto(inst)


def _reparto_varia_b(b):
    inst = instancia_desde_diccionario(generar_instancia(100, K, b, semilla=SEMILLA))
    return dict(N=100, k=K, B=b, densidad=""), _preparar_reparto(inst)


def _pd_varia_b(b):
    inst = instancia_desde_diccionario(generar_instancia(10, K, b, semilla=SEMILLA))
    return dict(N=10, k=K, B=b, densidad=""), _preparar_pd(inst)


def _exacto(k_de):
    def construir(n):
        k = k_de(n)
        inst = instancia_desde_diccionario(generar_instancia_influencia(n, k, 100, 1, SEMILLA))
        return dict(N=n, k=k, B=100, densidad=1), _preparar_exacto(inst)
    return construir


SERIES = {
    "a": ("a_cobertura", "Voraz Parte 2, cobertura, k = 5", [20, 40, 80, 160, 320, 640],
          _cobertura, lambda p: p["k"] * p["N"], "k·N"),
    "b": ("b_influencia_completo", "Voraz Parte 2, influencia, grafo completo, k = 5", [25, 50, 100, 200, 400],
          _influencia(lambda n: 1), lambda p: p["k"] * p["N"] ** 2, "k·N²"),
    "c": ("c_influencia_grado5", "Voraz Parte 2, influencia, grado medio ~ 5, k = 5", [25, 50, 100, 200, 400],
          _influencia(lambda n: 5 / (n - 1)), lambda p: p["k"] * p["N"], "k·N"),
    "d": ("d_reparto_varia_N", "Reparto Parte 1, B = 1000, varía N", [1000, 2000, 4000, 8000, 16000],
          _reparto_varia_n, lambda p: p["N"] + p["B"] * log2(p["N"]), "N + B·lg N"),
    "e": ("e_reparto_varia_B", "Reparto Parte 1, N = 100, varía B", [1000, 2000, 4000, 8000, 16000],
          _reparto_varia_b, lambda p: p["N"] + p["B"] * log2(p["N"]), "N + B·lg N"),
    "f": ("f_exacto_k3", "Fuerza bruta, k = 3, grafo completo", [10, 15, 20, 25, 30],
          _exacto(lambda n: 3), lambda p: comb(p["N"], p["k"]) * p["k"] * p["N"], "C(N, k)·k·N"),
    "g": ("g_exacto_k_mitad", "Fuerza bruta, k = N/2, grafo completo", [8, 10, 12, 14, 16],
          _exacto(lambda n: n // 2), lambda p: comb(p["N"], p["k"]) * p["k"] * p["N"], "C(N, k)·k·N"),
    "h": ("h_pd_varia_B", "PD Parte 1, N = 10, varía B, sin topes", [25, 50, 100, 200, 400],
          _pd_varia_b, lambda p: p["N"] * p["B"] ** 2, "N·B²"),
}


def ejecutar_serie(clave, repeticiones=REPETICIONES):
    """Corre una serie y devuelve sus filas (diccionarios con COLUMNAS), una por tamaño.

    Para cada n: construye la instancia, mide con `medir_con_limite` y calcula cociente = t_min / T_teorica.
    """
    _, _, tamanos, construir, teorica, _ = SERIES[clave]
    limite = LIMITE_UNA_REPETICION if clave == "h" else None      # solo la PD puede ser lenta
    filas = []
    for n in tamanos:
        parametros, preparar = construir(n)
        t_min, t_mediana, conteo, usadas = medir_con_limite(preparar, repeticiones, limite)
        T = teorica(parametros)
        filas.append({"n": n, **parametros, "semilla": SEMILLA, "t_min": t_min, "t_mediana": t_mediana,
                      "conteo": conteo, "T_teorica": T, "cociente": t_min / T, "repeticiones": usadas})
    return filas


# ----------------------------------------------------------------- análisis

def pendiente(xs, ys):
    """Pendiente de la regresión lineal por mínimos cuadrados de ys contra xs. Con (log x, log y)
    es el exponente aparente del tiempo. Tiempo O(n)."""
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)


def pendiente_loglog(filas, variable="n"):
    """Pendiente de log t_min contra log de la `variable` ('n' o 'T_teorica')."""
    from math import log
    return pendiente([log(f[variable]) for f in filas], [log(f["t_min"]) for f in filas])


def ajustar_reparto(filas):
    """Ajusta t_min ≈ a·N + b·B·lg N por mínimos cuadrados (sin término independiente).

    `filas` son las de las series d y e juntas; usa el N y el B reales de cada fila (no la columna n).
    Ecuaciones normales 2x2 con u = N, v = B·lg N:  (Σu²)a + (Σuv)b = Σu·t  y  (Σuv)a + (Σv²)b = Σv·t.
    Agrega a cada fila "t_ajustado" = a·u + b·v y devuelve (a, b). Tiempo O(número de filas).
    """
    u = [f["N"] for f in filas]
    v = [f["B"] * log2(f["N"]) for f in filas]
    t = [f["t_min"] for f in filas]
    suu = sum(x * x for x in u)
    suv = sum(x * y for x, y in zip(u, v))
    svv = sum(y * y for y in v)
    sut = sum(x * y for x, y in zip(u, t))
    svt = sum(x * y for x, y in zip(v, t))
    det = suu * svv - suv * suv                       # regla de Cramer
    a = (sut * svv - suv * svt) / det
    b = (suu * svt - suv * sut) / det
    for fila, x, y in zip(filas, u, v):
        fila["t_ajustado"] = a * x + b * y
    return a, b


def error_relativo(fila):
    """(t_ajustado − t_min) / t_min de una fila ya ajustada."""
    return (fila["t_ajustado"] - fila["t_min"]) / fila["t_min"]


# ----------------------------------------------------------------- salida

def escribir_csv(nombre, filas, columnas=COLUMNAS):
    """Escribe resultados/experimentos/<nombre>.csv con las `columnas` dadas."""
    SALIDA.mkdir(parents=True, exist_ok=True)
    with open(SALIDA / f"{nombre}.csv", "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=columnas)
        escritor.writeheader()
        for fila in filas:
            escritor.writerow({c: (repr(fila[c]) if isinstance(fila[c], float) else fila[c]) for c in columnas})


def graficar_ajuste(filas, a, b):
    """PNG del tiempo medido contra el predicho por el ajuste, con la recta y = x (ajuste_reparto.png)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    figura, eje = plt.subplots(figsize=(5, 5))
    eje.loglog([f["t_ajustado"] for f in filas], [f["t_min"] for f in filas], "o", label="puntos (series d y e)")
    extremos = [min(f["t_min"] for f in filas), max(f["t_min"] for f in filas)]
    eje.loglog(extremos, extremos, "--", label="y = x")
    eje.set_xlabel("t predicho (s)")
    eje.set_ylabel("t_min medido (s)")
    eje.set_title(f"Reparto: t ≈ a·N + b·B·lg N\na = {a:.3e}, b = {b:.3e}")
    eje.legend()
    figura.tight_layout()
    figura.savefig(SALIDA / "ajuste_reparto.png", dpi=120)
    plt.close(figura)


def graficar(clave, filas):
    """Dos PNG: (1) t_min contra n con c·T_teorica (c ajustada en el n más grande) y (2) el cociente.

    En la serie g el eje y de las dos va en escala logarítmica (el tiempo es exponencial en N).
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    nombre, titulo, _, _, _, formula = SERIES[clave]
    ns = [f["n"] for f in filas]
    c = filas[-1]["t_min"] / filas[-1]["T_teorica"]
    etiqueta_n = "B" if clave in ("e", "h") else "N"

    figura, eje = plt.subplots(figsize=(6, 4))
    eje.plot(ns, [f["t_min"] for f in filas], "o-", label="t_min medido")
    eje.plot(ns, [c * f["T_teorica"] for f in filas], "--", label=f"c·T teórica, T = {formula}")
    eje.set_xlabel(etiqueta_n)
    eje.set_ylabel("tiempo (s)")
    eje.set_title(titulo)
    if clave == "g":
        eje.set_yscale("log")
    eje.legend()
    figura.tight_layout()
    figura.savefig(SALIDA / f"{nombre}_tiempo.png", dpi=120)
    plt.close(figura)

    figura, eje = plt.subplots(figsize=(6, 4))
    eje.plot(ns, [f["cociente"] for f in filas], "o-")
    eje.set_xlabel(etiqueta_n)
    eje.set_ylabel(f"t_min / ({formula})")
    eje.set_title(f"Cociente: {titulo}")
    if clave == "g":
        eje.set_yscale("log")
    figura.tight_layout()
    figura.savefig(SALIDA / f"{nombre}_cociente.png", dpi=120)
    plt.close(figura)


def imprimir(clave, filas):
    """Imprime la tabla de una serie y sus pendientes log-log."""
    nombre, titulo, _, _, _, formula = SERIES[clave]
    print(f"\n== Serie {clave}: {titulo} (T = {formula}) ==")
    print(f"{'n':>7} {'t_min (s)':>12} {'t_mediana (s)':>14} {'conteo':>10} {'T_teorica':>14} {'cociente':>12}")
    for f in filas:
        print(f"{f['n']:>7} {f['t_min']:>12.6f} {f['t_mediana']:>14.6f} {f['conteo']:>10} "
              f"{f['T_teorica']:>14.1f} {f['cociente']:>12.4e}")
    print(f"pendiente log-log de t_min contra n: {pendiente_loglog(filas):.3f}")
    if clave == "h":
        print(f"repeticiones usadas por tamaño: {[f['repeticiones'] for f in filas]}")
    if clave in ("f", "g"):
        print(f"pendiente log-log de t_min contra T_teorica: {pendiente_loglog(filas, 'T_teorica'):.3f}")


def imprimir_ajuste(filas, a, b):
    """Imprime a, b y el error relativo de cada punto del ajuste del reparto."""
    print("\n== Ajuste del reparto: t_min ≈ a·N + b·B·lg N ==")
    print(f"a = {a:.6e}")
    print(f"b = {b:.6e}")
    for f in filas:
        print(f"  N = {f['N']:>6}  B = {f['B']:>6}  t_min = {f['t_min']:.6f}  "
              f"t_ajustado = {f['t_ajustado']:.6f}  error relativo = {error_relativo(f):+.2%}")


def main(argumentos=None):
    """Corre las series pedidas (todas por omisión), escribe CSV y gráficas e imprime las tablas."""
    p = argparse.ArgumentParser(description="Experimentos de tiempo del Proyecto Red.")
    p.add_argument("--series", nargs="+", choices=sorted(SERIES), default=sorted(SERIES))
    p.add_argument("--sin-graficas", action="store_true", help="solo CSV (no usa matplotlib)")
    p.add_argument("--repeticiones", type=int, default=REPETICIONES)
    a = p.parse_args(argumentos)
    inicio = time.perf_counter()
    resultados = {clave: ejecutar_serie(clave, a.repeticiones) for clave in a.series}
    ajuste = None
    if "d" in resultados and "e" in resultados:       # el ajuste usa las dos series juntas
        ajuste = ajustar_reparto(resultados["d"] + resultados["e"])
    for clave, filas in resultados.items():
        columnas = COLUMNAS_AJUSTADAS if ajuste and clave in ("d", "e") else (COLUMNAS_H if clave == "h" else COLUMNAS)
        escribir_csv(SERIES[clave][0], filas, columnas)
        if not a.sin_graficas:
            graficar(clave, filas)
        imprimir(clave, filas)
    if ajuste:
        imprimir_ajuste(resultados["d"] + resultados["e"], *ajuste)
        if not a.sin_graficas:
            graficar_ajuste(resultados["d"] + resultados["e"], *ajuste)
    print(f"\nTiempo total: {time.perf_counter() - inicio:.1f} s (semilla {SEMILLA}, {a.repeticiones} repeticiones)")


if __name__ == "__main__":
    main()
