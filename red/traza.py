"""Traza de una ronda: el paso a paso de los dos voraces, en texto y en JSON.

Los algoritmos llaman a paso_seleccion y unidad_reparto (línea 9 de
SELECCIONAR-NODOS y línea 7 de REPARTIR-PRESUPUESTO). Lo demás lo agrega ronda.py.
Si un caso se rechaza, los algoritmos no corren y la traza guarda el motivo.
"""

import json


def _numero(valor):
    """Formato corto para la traza: enteros sin decimales, el resto con 4."""
    if isinstance(valor, int) or float(valor).is_integer():
        return str(int(valor))
    return f"{valor:.4f}"


class Traza:
    """Guarda los pasos de la Parte 2, las unidades de la Parte 1 y el motivo de un rechazo."""

    def __init__(self):
        self.pasos_seleccion = []
        self.unidades_reparto = []
        self.motivo_rechazo = None   # lista de textos si el caso se rechazó; None si corrió

    def paso_seleccion(self, paso, aportes, elegido, ganancia, valor):
        """Un paso del voraz de selección: Δ de cada candidato, el elegido y f(S) después."""
        self.pasos_seleccion.append({
            "paso": paso,
            "aportes": [{"nodo": v, "ganancia": d} for v, d in aportes],
            "elegido": elegido,
            "ganancia_elegido": ganancia,
            "valor_despues": valor,
        })

    def unidad_reparto(self, unidad, nodo, ganancia):
        """Una unidad del reparto: qué nodo la recibe y cuánto aporta."""
        self.unidades_reparto.append({"unidad": unidad, "nodo": nodo, "ganancia": ganancia})

    def entrada_rechazada(self, motivos):
        """Anota por qué el caso no se ejecutó. motivos: lista de textos."""
        self.motivo_rechazo = motivos

    def a_diccionario(self):
        """La traza como diccionario para JSON. "motivo_rechazo" solo aparece si hubo rechazo."""
        datos = {"pasos_seleccion": self.pasos_seleccion, "unidades_reparto": self.unidades_reparto}
        if self.motivo_rechazo is not None:
            datos["motivo_rechazo"] = self.motivo_rechazo
        return datos


def escribir_json(ruta, datos):
    """Escribe cualquier diccionario como JSON legible (UTF-8, con sangría)."""
    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)


def a_texto(resultado):
    """Convierte el resultado de una ronda (ver ronda.py) en un reporte de texto.

    Sirve también para un caso rechazado: ese reporte trae la entrada y el motivo.
    Tiempo O(tamaño del resultado).
    """
    lineas = []
    e = resultado["entrada"]
    lineas.append(f"CASO: {resultado['caso']}")
    if e["N"] is None:
        lineas.append("N, k y B: no se pudieron leer del archivo")
    else:
        lineas.append(f"N = {e['N']}, k = {e['k']}, B = {e['B']}")
    lineas.append("")

    lineas.append("== Verificación de la entrada ==")
    for v in resultado["verificaciones"]["entrada"]:
        lineas.append(f"  [{'OK' if v['cumple'] else 'FALLA'}] {v['nombre']}: {v['detalle']}")
    lineas.append("")

    if "seleccion" not in resultado:
        lineas.append("== Caso rechazado: los algoritmos no se ejecutaron ==")
        for motivo in resultado["traza"]["motivo_rechazo"]:
            lineas.append(f"  Motivo: {motivo}")
        lineas.append("")
        lineas.append("TODAS LAS VERIFICACIONES: HAY FALLAS")
        return "\n".join(lineas) + "\n"

    lineas.append("== Parte 2: selección de nodos (voraz) ==")
    for p in resultado["traza"]["pasos_seleccion"]:
        aportes = ", ".join(f"Δ({a['nodo']}) = {_numero(a['ganancia'])}" for a in p["aportes"])
        lineas.append(f"  Paso {p['paso']}: {aportes}")
        lineas.append(f"    → elige el nodo {p['elegido']} (Δ = {_numero(p['ganancia_elegido'])}); "
                      f"f(S) = {_numero(p['valor_despues'])}")
    s = resultado["seleccion"]
    lineas.append(f"  Resultado: S = {s['S']}, f(S) = {_numero(s['valor'])}, "
                  f"llamadas a Δ = {s['llamadas_ganancia']}")
    lineas.append("")

    lineas.append("== Parte 1: reparto del presupuesto (voraz con montículo) ==")
    for u in resultado["traza"]["unidades_reparto"]:
        lineas.append(f"  Unidad {u['unidad']}: al nodo {u['nodo']} (Δ = {_numero(u['ganancia'])})")
    r = resultado["reparto"]
    reparto = ", ".join(f"x_{i} = {x}" for i, x in r["x"].items())
    lineas.append(f"  Resultado: {reparto}; utilidad total = {r['utilidad']:.6f}")
    lineas.append("")

    for parte, titulo in (("seleccion", "Parte 2"), ("reparto", "Parte 1"), ("ejecucion", "Ejecución")):
        lineas.append(f"== Verificación: {titulo} ==")
        for v in resultado["verificaciones"][parte]:
            lineas.append(f"  [{'OK' if v['cumple'] else 'FALLA'}] {v['nombre']}: {v['detalle']}")
        lineas.append("")

    t = resultado["tiempos_segundos"]
    lineas.append("== Tiempos (solo los algoritmos, sin lectura ni escritura) ==")
    lineas.append(f"  Parte 2 (selección): {t['seleccion']:.9f} s")
    lineas.append(f"  Parte 1 (reparto):   {t['reparto']:.9f} s")
    lineas.append("")
    lineas.append(f"TODAS LAS VERIFICACIONES: {'CUMPLEN' if resultado['todas_cumplen'] else 'HAY FALLAS'}")
    return "\n".join(lineas) + "\n"
