"""Una ronda completa (informe 6.1): Parte 2, luego Parte 1 sobre los elegidos, verificar y medir.

Cada algoritmo se ejecuta en dos momentos:
1. R veces sin traza, con el reloj alrededor: se reporta la mediana de cada parte
   (así el tiempo corresponde a la T(n) deducida, no incluye escribir la traza
   y una repetición lenta no lo arrastra; decisión 29).
2. Una vez más con traza, para la evidencia. Como los algoritmos son deterministas,
   todas las ejecuciones deben dar lo mismo; eso también se verifica.
"""

import statistics
import time

from red.reparto import repartir_presupuesto
from red.seleccion import seleccionar_nodos
from red.traza import Traza
from red.variante_costos import voraz_modificado
from red.verificacion import (Verificacion, verificar_conteo_evaluaciones_costos, verificar_conteo_llamadas,
                              verificar_entrada, verificar_reparto, verificar_seleccion,
                              verificar_seleccion_costos, verificar_variante_a)

NO_SE_APLICA = "no se aplica en la solución base"
SE_APLICA_A = "se aplica en esta corrida (variante a): Σ c(S) ≤ L es una verificación"
REPETICIONES = 21   # cuántas veces se repite la ejecución medida (decisión 29)
VARIANTES = (None, "a")   # None = solución base; "a" = costos de participación (decisión 35)
ALGORITMO_A = "voraz modificado (Khuller, Moss y Naor, 1999; cota 0,405 de Tang et al., 2021)"


def _resultado_rechazado(nombre, entrada, verificaciones):
    """Resultado de un caso que no se ejecuta: la entrada, sus verificaciones y el motivo en la traza."""
    traza = Traza()
    traza.entrada_rechazada([f"{v['nombre']}: {v['detalle']}" for v in verificaciones if not v["cumple"]])
    return {
        "caso": nombre,
        "entrada": entrada,
        "verificaciones": {"entrada": verificaciones},
        "traza": traza.a_diccionario(),
        "todas_cumplen": False,
    }


def resultado_de_error(nombre, mensaje):
    """Resultado de un caso cuyo archivo no se pudo leer o no tiene la forma esperada.

    Recibe el nombre del caso y el mensaje del error. N, k y B quedan en None porque no se conocen.
    """
    verificacion = Verificacion("archivo legible y con la forma esperada", False, mensaje)
    return _resultado_rechazado(nombre, {"N": None, "k": None, "B": None}, [verificacion.a_diccionario()])


def _informativo(instancia, S, variante=None):
    """Los datos de las variantes (a) y (b) para el reporte (decisión 26). Tiempo O(N).

    NO es una Verificacion ni entra en todas_cumplen: la solución base no los aplica.
    Con variante = "a", la nota de la variante (a) dice que sí se aplicó (la verificación está en "seleccion").
    """
    costos = {nodo.id: nodo.costo_participacion for nodo in instancia.nodos}
    return {
        "variante_a": {
            "suma_costos_de_S": sum(costos[v] for v in S),
            "presupuesto_costos_participacion_por_ronda":
                instancia.variantes["presupuesto_costos_participacion_por_ronda"],
            "nota": SE_APLICA_A if variante == "a" else NO_SE_APLICA,
        },
        "variante_b": {
            "numero_rondas": instancia.variantes["numero_rondas"],
            "nota": NO_SE_APLICA,
        },
    }


def _seleccionar(instancia, oraculo, variante, traza=None):
    """La Parte 2 que corresponde: el voraz base con k, o el voraz modificado con costos y L (variante a).

    Devuelve (S, valorS, extra): extra es None en la base y, en la variante (a), el ResultadoCostos
    (costo, evaluaciones y origen). Mismo costo que el algoritmo que llama.
    """
    if variante == "a":
        r = voraz_modificado(oraculo, instancia.ids(), instancia.costos(), instancia.presupuesto_costos, traza)
        return r.S, r.valor, r
    S, valorS = seleccionar_nodos(oraculo, instancia.ids(), instancia.k, traza)
    return S, valorS, None


def _ejecucion_medida(instancia, repeticiones, variante=None):
    """Corre los dos algoritmos R veces, sin traza y midiendo cada uno.

    Cada repetición usa un oráculo nuevo, creado fuera del reloj, para que sus contadores empiecen en cero.
    Devuelve: lista de corridas (oraculo, S, valorS, reparto, extra), tiempos de la selección y del reparto.
    Tiempo: R veces el costo de los algoritmos.
    """
    utilidades = instancia.utilidades()
    topes = instancia.topes()
    corridas = []
    tiempos_seleccion = []
    tiempos_reparto = []
    for _ in range(repeticiones):
        oraculo = instancia.crear_oraculo()
        inicio = time.perf_counter()
        S, valorS, extra = _seleccionar(instancia, oraculo, variante)
        tiempos_seleccion.append(time.perf_counter() - inicio)

        inicio = time.perf_counter()
        reparto = repartir_presupuesto(S, instancia.B, utilidades, topes=topes)
        tiempos_reparto.append(time.perf_counter() - inicio)
        corridas.append((oraculo, S, valorS, reparto, extra))
    return corridas, tiempos_seleccion, tiempos_reparto


def _resumen_tiempos(tiempos):
    """Mediana, mínimo y máximo de una lista de tiempos. Tiempo O(R lg R)."""
    return {"mediana": statistics.median(tiempos), "minimo": min(tiempos), "maximo": max(tiempos)}


def _verificar_repeticiones(corridas):
    """Todas las repeticiones deben dar el mismo S y el mismo reparto que la primera. Tiempo O(R·k)."""
    _, S, _, reparto, _ = corridas[0]
    distintas = [numero for numero, (_, otro_S, _, otro_reparto, _) in enumerate(corridas, start=1)
                 if otro_S != S or otro_reparto.x != reparto.x]
    return Verificacion("todas las repeticiones dan el mismo S y el mismo reparto", not distintas,
                        f"R = {len(corridas)}" if not distintas else f"difieren las repeticiones {distintas}")


def ejecutar_ronda(instancia, repeticiones=REPETICIONES, variante=None):
    """Corre una ronda sobre la instancia y devuelve un diccionario con todo el resultado.

    repeticiones (R ≥ 1) es cuántas veces se repite la ejecución medida. variante: None (solución base)
    o "a" (costos de participación: la Parte 2 es el voraz modificado con Σ c(S) ≤ L en lugar de |S| ≤ k,
    Supuesto ❓ de la decisión 35; el reparto no cambia). Con variante = "a" el resultado trae además
    "variante" y, en "seleccion", costo, evaluaciones y origen; con None nada cambia.
    Si la entrada no cumple sus restricciones, no corre los algoritmos: devuelve
    las verificaciones de entrada y una traza con el motivo.
    Tiempo de los algoritmos, por repetición: O(k·(N + M) + B(1 + lg k)) con cobertura
    (M = Σ |C_v|) y O(k·(N + A) + B(1 + lg k)) con influencia (A = aristas). Con la variante (a),
    la selección cuesta O(|S|·(N + A)) con influencia (ver docs/modulos/variante_costos.md).
    """
    if repeticiones < 1:
        raise ValueError(f"se necesita al menos una repetición; llegó {repeticiones}")
    if variante not in VARIANTES:
        raise ValueError(f"variante desconocida: {variante!r}; las válidas son {VARIANTES}")
    entrada = {"N": instancia.N, "k": instancia.k, "B": instancia.B}
    if variante == "a":
        entrada["L"] = instancia.presupuesto_costos
    verificaciones_entrada = [v.a_diccionario() for v in verificar_entrada(instancia)]
    if variante == "a":
        verificaciones_entrada += [v.a_diccionario() for v in verificar_variante_a(instancia)]
    if not all(v["cumple"] for v in verificaciones_entrada):
        return _resultado_rechazado(instancia.nombre, entrada, verificaciones_entrada)

    resultado = {
        "caso": instancia.nombre,
        "entrada": entrada,
        "verificaciones": {"entrada": verificaciones_entrada},
    }

    utilidades = instancia.utilidades()
    topes = instancia.topes()

    # 1. Ejecución medida (sin traza), R veces; lo que se reporta es la primera, y se comprueba que todas coinciden
    corridas, tiempos_seleccion, tiempos_reparto = _ejecucion_medida(instancia, repeticiones, variante)
    oraculo, S, valorS, reparto, extra = corridas[0]

    # 2. Ejecución con traza (evidencia)
    traza = Traza()
    oraculo_traza = instancia.crear_oraculo()
    S_traza, valor_traza, _ = _seleccionar(instancia, oraculo_traza, variante, traza)
    reparto_traza = repartir_presupuesto(S_traza, instancia.B, utilidades, traza, topes)

    # 3. Verificaciones de la salida (con un oráculo aparte, para no tocar el conteo)
    oraculo_verificacion = instancia.crear_oraculo()
    if variante == "a":
        v_seleccion = verificar_seleccion_costos(instancia, oraculo_verificacion, S, valorS,
                                                 instancia.costos(), instancia.presupuesto_costos)
        v_seleccion += verificar_conteo_evaluaciones_costos(
            instancia.N, S, extra.origen, extra.evaluaciones, oraculo.llamadas_ganancia + oraculo.llamadas_valor)
    else:
        v_seleccion = verificar_seleccion(instancia, oraculo_verificacion, S, valorS)
        v_seleccion += verificar_conteo_llamadas(instancia.N, instancia.k, oraculo.llamadas_ganancia)
    v_reparto = verificar_reparto(S, instancia.B, utilidades, reparto, topes)
    iguales = (S == S_traza and valorS == valor_traza and reparto.x == reparto_traza.x)
    v_ejecucion = [_verificar_repeticiones(corridas),
                   Verificacion("ejecución con traza = ejecución medida", iguales,
                                "mismo S y mismo reparto" if iguales else "difieren")]

    resultado["seleccion"] = {
        "S": S,
        "valor": valorS,
        "llamadas_ganancia": oraculo.llamadas_ganancia,
        "llamadas_valor": oraculo.llamadas_valor,
    }
    if variante == "a":
        resultado["seleccion"].update({"costo": extra.costo, "evaluaciones": extra.evaluaciones,
                                       "origen": extra.origen})
        resultado["variante"] = {"nombre": "a", "L": instancia.presupuesto_costos, "algoritmo": ALGORITMO_A,
                                 "supuesto": "Supuesto ❓: Σ c(S) ≤ L reemplaza a |S| ≤ k (decisión 35)"}
    resultado["reparto"] = {
        "x": {str(i): reparto.x[i] for i in S},
        "utilidad": reparto.utilidad,
        "extracciones": reparto.extracciones,
        "inserciones": reparto.inserciones,
    }
    resultado["tiempos_segundos"] = {
        "repeticiones": repeticiones,
        "seleccion": _resumen_tiempos(tiempos_seleccion),
        "reparto": _resumen_tiempos(tiempos_reparto),
    }
    resultado["verificaciones"]["seleccion"] = [v.a_diccionario() for v in v_seleccion]
    resultado["verificaciones"]["reparto"] = [v.a_diccionario() for v in v_reparto]
    resultado["verificaciones"]["ejecucion"] = [v.a_diccionario() for v in v_ejecucion]
    resultado["traza"] = traza.a_diccionario()
    resultado["todas_cumplen"] = all(
        v["cumple"] for lista in resultado["verificaciones"].values() for v in lista)
    if instancia.variantes is not None:   # solo el formato de la profesora
        resultado["informativo"] = _informativo(instancia, S, variante)
    return resultado
