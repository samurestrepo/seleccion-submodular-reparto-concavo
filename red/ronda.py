"""Una ronda completa (informe 6.1): Parte 2, luego Parte 1 sobre los elegidos, verificar y medir.

Cada algoritmo se ejecuta DOS veces:
1. Una vez sin traza, con el reloj alrededor: es el tiempo que se reporta
   (así el tiempo corresponde a la T(n) deducida y no incluye escribir la traza).
2. Otra vez con traza, para la evidencia. Como los algoritmos son deterministas,
   las dos ejecuciones deben dar lo mismo; eso también se verifica.
"""

import time

from red.cobertura import OraculoCobertura
from red.reparto import repartir_presupuesto
from red.seleccion import seleccionar_nodos
from red.traza import Traza
from red.verificacion import (Verificacion, verificar_conteo_llamadas, verificar_entrada,
                              verificar_reparto, verificar_seleccion)


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


def ejecutar_ronda(instancia):
    """Corre una ronda sobre la instancia y devuelve un diccionario con todo el resultado.

    Si la entrada no cumple sus restricciones, no corre los algoritmos: devuelve
    las verificaciones de entrada y una traza con el motivo.
    Tiempo de los algoritmos: O(k·(N + M) + B(1 + lg k)), con M = Σ |C_v|.
    """
    entrada = {"N": instancia.N, "k": instancia.k, "B": instancia.B}
    verificaciones_entrada = [v.a_diccionario() for v in verificar_entrada(instancia)]
    if not all(v["cumple"] for v in verificaciones_entrada):
        return _resultado_rechazado(instancia.nombre, entrada, verificaciones_entrada)

    resultado = {
        "caso": instancia.nombre,
        "entrada": entrada,
        "verificaciones": {"entrada": verificaciones_entrada},
    }

    V = instancia.ids()
    utilidades = instancia.utilidades()

    # 1. Ejecución medida (sin traza)
    oraculo = OraculoCobertura(instancia.conjuntos())
    inicio = time.perf_counter()
    S, valorS = seleccionar_nodos(oraculo, V, instancia.k)
    tiempo_seleccion = time.perf_counter() - inicio

    inicio = time.perf_counter()
    reparto = repartir_presupuesto(S, instancia.B, utilidades)
    tiempo_reparto = time.perf_counter() - inicio

    # 2. Ejecución con traza (evidencia)
    traza = Traza()
    oraculo_traza = OraculoCobertura(instancia.conjuntos())
    S_traza, valor_traza = seleccionar_nodos(oraculo_traza, V, instancia.k, traza)
    reparto_traza = repartir_presupuesto(S_traza, instancia.B, utilidades, traza)

    # 3. Verificaciones de la salida (con un oráculo aparte, para no tocar el conteo)
    oraculo_verificacion = OraculoCobertura(instancia.conjuntos())
    v_seleccion = verificar_seleccion(instancia, oraculo_verificacion, S, valorS)
    v_seleccion += verificar_conteo_llamadas(instancia.N, instancia.k, oraculo.llamadas_ganancia)
    v_reparto = verificar_reparto(S, instancia.B, utilidades, reparto)
    iguales = (S == S_traza and valorS == valor_traza and reparto.x == reparto_traza.x)
    v_ejecucion = [Verificacion("ejecución con traza = ejecución medida", iguales,
                                "mismo S y mismo reparto" if iguales else "difieren")]

    resultado["seleccion"] = {
        "S": S,
        "valor": valorS,
        "llamadas_ganancia": oraculo.llamadas_ganancia,
        "llamadas_valor": oraculo.llamadas_valor,
    }
    resultado["reparto"] = {
        "x": {str(i): reparto.x[i] for i in S},
        "utilidad": reparto.utilidad,
        "extracciones": reparto.extracciones,
        "inserciones": reparto.inserciones,
    }
    resultado["tiempos_segundos"] = {"seleccion": tiempo_seleccion, "reparto": tiempo_reparto}
    resultado["verificaciones"]["seleccion"] = [v.a_diccionario() for v in v_seleccion]
    resultado["verificaciones"]["reparto"] = [v.a_diccionario() for v in v_reparto]
    resultado["verificaciones"]["ejecucion"] = [v.a_diccionario() for v in v_ejecucion]
    resultado["traza"] = traza.a_diccionario()
    resultado["todas_cumplen"] = all(
        v["cumple"] for lista in resultado["verificaciones"].values() for v in lista)
    return resultado
