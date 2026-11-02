"""Generador de instancias sintéticas en el formato provisional (informe 6.5).

Uso desde la terminal (desde la raíz del repositorio):
    python -m red.generador --N 50 --k 5 --B 100 --semilla 1 --salida casos/propios/sintetico_N50.json

Con la misma semilla se obtiene exactamente la misma instancia (reproducible).
"""

import argparse
import json
import random


def generar_instancia(N, k, B, tam_universo=None, max_cubre=None, semilla=0):
    """Crea una instancia aleatoria y la devuelve como diccionario listo para JSON.

    Recibe: N nodos, k, B; tamaño del universo (por omisión 2N); máximo de elementos
    por nodo (por omisión 5); semilla. Cada nodo cubre entre 1 y max_cubre elementos
    distintos, y su utilidad es "log" o "raiz" con a entre 1 y 10.
    Tiempo O(N · max_cubre).
    """
    if not 1 <= k < N:
        raise ValueError(f"se necesita 1 ≤ k < N; llegó k = {k}, N = {N}")
    if B < 0:
        raise ValueError("B debe ser ≥ 0")
    tam_universo = tam_universo or 2 * N
    max_cubre = min(max_cubre or 5, tam_universo)

    azar = random.Random(semilla)
    universo = [f"e{j}" for j in range(1, tam_universo + 1)]
    nodos = []
    for i in range(1, N + 1):
        cantidad = azar.randint(1, max_cubre)
        cubre = sorted(azar.sample(universo, cantidad), key=lambda e: int(e[1:]))
        utilidad = {"tipo": azar.choice(["log", "raiz"]), "a": round(azar.uniform(1, 10), 2)}
        nodos.append({"id": i, "cubre": cubre, "utilidad": utilidad})
    return {"k": k, "B": B, "nodos": nodos}


def main(argumentos=None):
    """Lee los parámetros de la línea de comandos y escribe la instancia en --salida.

    El texto de ayuda evita símbolos como el de "menor o igual": en una consola
    Windows con cp1252 no se pueden imprimir y --help fallaría.
    """
    p = argparse.ArgumentParser(description="Genera una instancia sintética del Proyecto Red.")
    p.add_argument("--N", type=int, required=True, help="número de nodos candidatos")
    p.add_argument("--k", type=int, required=True, help="nodos a seleccionar (1 <= k < N)")
    p.add_argument("--B", type=int, required=True, help="unidades de presupuesto")
    p.add_argument("--universo", type=int, default=None, help="tamaño del universo (por omisión 2N)")
    p.add_argument("--max-cubre", type=int, default=None, help="máximo de elementos por nodo (por omisión 5)")
    p.add_argument("--semilla", type=int, default=0)
    p.add_argument("--salida", required=True, help="ruta del archivo JSON a escribir")
    a = p.parse_args(argumentos)
    datos = generar_instancia(a.N, a.k, a.B, a.universo, a.max_cubre, a.semilla)
    with open(a.salida, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)
    print(f"Instancia escrita en {a.salida} (N = {a.N}, k = {a.k}, B = {a.B}, semilla = {a.semilla})")


if __name__ == "__main__":
    main()
