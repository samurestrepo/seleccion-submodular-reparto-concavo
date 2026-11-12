"""Generador de instancias sintéticas en el formato provisional (informe 6.5).

Uso desde la terminal (desde la raíz del repositorio):
    python -m red.generador --N 50 --k 5 --B 100 --semilla 1 --salida casos/propios/sintetico_N50.json

Con la misma semilla se obtiene exactamente la misma instancia (reproducible).
Con --formato influencia (y --densidad) se genera una instancia en el formato de la profesora.
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


def _identificador(i, N):
    """Id de texto "N01", "N02", …: relleno de ceros con al menos 2 dígitos y los que pida N."""
    return f"N{i:0{max(2, len(str(N)))}d}"


def generar_instancia_influencia(N, k, B, densidad, semilla=0):
    """Crea una instancia en el formato de la profesora (parametros, grafo, nodos) como diccionario.

    Recibe: N nodos (ids "N01"…), k, B, densidad en [0, 1] y semilla. El grafo NO es dirigido: cada
    par {i, j} con i < j tiene una arista con probabilidad `densidad` (densidad 1 da N(N−1)/2 aristas)
    y peso_influencia uniforme en [0,05; 0,70] con 2 decimales. Cada nodo: coeficiente_utilidad
    uniforme en [1; 10] (2 decimales), costo_participacion entero en [1; 5] y presupuesto_total_nodo = B
    (tope que nunca limita en una ronda). numero_rondas = 1. Tiempo O(N²) por recorrer todos los pares.
    """
    if not 1 <= k < N:
        raise ValueError(f"se necesita 1 ≤ k < N; llegó k = {k}, N = {N}")
    if B < 0:
        raise ValueError("B debe ser ≥ 0")
    if not 0 <= densidad <= 1:
        raise ValueError(f"densidad debe estar en [0, 1]; llegó {densidad}")

    azar = random.Random(semilla)
    ids = [_identificador(i, N) for i in range(1, N + 1)]
    nodos = []
    for id_nodo in ids:
        nodos.append({
            "id": id_nodo,
            "coeficiente_utilidad": round(azar.uniform(1, 10), 2),
            "presupuesto_total_nodo": B,
            "costo_participacion": azar.randint(1, 5),
        })
    grafo = []
    for a in range(N):
        for b in range(a + 1, N):
            # random() está en [0, 1): con densidad 1 siempre hay arista y con 0 nunca
            if azar.random() < densidad:
                grafo.append({"u": ids[a], "v": ids[b],
                              "peso_influencia": round(azar.uniform(0.05, 0.70), 2)})
    parametros = {
        "numero_nodos": N,
        "numero_rondas": 1,
        "cupo_participantes_por_ronda_k": k,
        "presupuesto_ruido_por_ronda_B": B,
        "presupuesto_costos_participacion_por_ronda": 5 * k,   # alcanza para cualquier k nodos (costo ≤ 5)
    }
    return {"parametros": parametros, "grafo": grafo, "nodos": nodos}


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
    p.add_argument("--formato", choices=["cobertura", "influencia"], default="cobertura",
                   help="cobertura (formato propio, por omisión) o influencia (formato de la profesora)")
    p.add_argument("--densidad", type=float, default=0.5,
                   help="solo con influencia: probabilidad de arista entre cada par, de 0 a 1 (por omisión 0.5)")
    p.add_argument("--semilla", type=int, default=0)
    p.add_argument("--salida", required=True, help="ruta del archivo JSON a escribir")
    a = p.parse_args(argumentos)
    if a.formato == "influencia":
        datos = generar_instancia_influencia(a.N, a.k, a.B, a.densidad, a.semilla)
    else:
        datos = generar_instancia(a.N, a.k, a.B, a.universo, a.max_cubre, a.semilla)
    with open(a.salida, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)
    print(f"Instancia escrita en {a.salida} (N = {a.N}, k = {a.k}, B = {a.B}, semilla = {a.semilla})")


if __name__ == "__main__":
    main()
