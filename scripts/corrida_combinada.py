"""Corrida combinada de las variantes (a) + (b) + (c) en el caso de la docente (P-4, fase 6).

Uso, desde la raíz del repositorio:  python scripts/corrida_combinada.py
Escribe resultados/variantes/combinada_c1/ y combinada_c2/ (salida.json y traza.txt).
Ficha: docs/modulos/corrida_combinada.md. Decisiones 56 y 57.

Cada ronda r = 1..T (variante b) hace, sin cambiar ninguna variante ni la base:
1. sorteo de fallos y candidatos (`sortear_fallos`, `candidatos_de_la_ronda` de variante_rondas.py);
2. selección con costos (variante a): `voraz_modificado` con V = candidatos y Σ c(S_r) ≤ L. **Supuesto ❓
   (decisión 56):** L reemplaza a k también aquí, como en la decisión 35; y OPT_r con
   `seleccionar_exacto_costos` sobre los candidatos (2^n_r ≤ 2^15 subconjuntos);
3. reparto con vecinos (variante c): `repartir_c1` o `repartir_c2` sobre S_r con topes = presupuesto restante;
4. se descuenta x del restante.
Sin pseudocódigo en el informe: solo compone funciones que ya tienen el suyo (fichas de cada variante).
"""

import json
import random
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from red.entrada import leer_instancia  # noqa: E402
from red.exacto import DemasiadasCombinaciones  # noqa: E402
from red.utilidades import UtilidadLog  # noqa: E402
from red.variante_costos import seleccionar_exacto_costos, voraz_modificado  # noqa: E402
from red.variante_rondas import (MODOS, PROBABILIDAD_FALLO, SEMILLA_FALLOS,  # noqa: E402
                                 candidatos_de_la_ronda, sortear_fallos)
from red.variante_vecinos import (BETA, LIMITE_REPARTOS, MODELOS, contar_repartos, cota_c2,  # noqa: E402
                                  repartir_c1, repartir_c2, repartir_exacto, utilidad_c2, vecinos_en_S)
from red.verificacion import (Verificacion, verificar_entrada, verificar_reparto, verificar_reparto_c2,  # noqa: E402
                              verificar_variante_a, verificar_variante_b, verificar_variante_c)

CASO = RAIZ / "casos" / "profesora" / "entrada_G2_red_15_nodos.json"
SALIDA = RAIZ / "resultados" / "variantes"
COTA_A = 0.405        # garantía del voraz modificado (Tang et al., 2021), la misma de la variante (a)
TOLERANCIA = 1e-9
SUPUESTOS = (
    "Supuesto ❓ (decisión 56): en cada ronda Σ c(S_r) ≤ L reemplaza a |S_r| ≤ k (como la decisión 35)",
    "Supuesto ❓ (decisión 56): los supuestos de (b) (decisión 39) y de (c) (decisión 43) valen tal cual",
    "Supuesto ❓ (decisión 57): el exacto del reparto de c2 solo corre si los repartos caben en el límite",
)


def _validar(instancia, modelo, modo, T):
    """Revisa la entrada y las tres variantes; lanza ValueError con los motivos si algo falla. Tiempo O(N + A)."""
    if modelo not in MODELOS:
        raise ValueError(f"modelo desconocido: {modelo!r}; los válidos son {MODELOS}")
    if modo not in MODOS:
        raise ValueError(f"modo de fallo desconocido: {modo!r}; los válidos son {MODOS}")
    verificaciones = (verificar_entrada(instancia) + verificar_variante_a(instancia)
                      + verificar_variante_b(T) + verificar_variante_c(instancia))
    fallas = [f"{v.nombre}: {v.detalle}" for v in verificaciones if not v.cumple]
    if fallas:
        raise ValueError("la instancia no admite la corrida combinada: " + "; ".join(fallas))


def _seleccion_con_costos(instancia, candidatos, costos, L, exacto):
    """Paso 2 de la ronda: voraz modificado sobre los candidatos y, si se pide, OPT_r por fuerza bruta.

    Devuelve un diccionario con S_r, f(S_r), costo, evaluaciones, origen, OPT_r y razón.
    Tiempo O(n_r·mín(n_r, L/c_mín)) evaluaciones de f; el exacto suma hasta 2^n_r evaluaciones.
    """
    oraculo = instancia.crear_oraculo()                # oráculo nuevo: contadores en cero
    r = voraz_modificado(oraculo, candidatos, costos, L)
    seleccion = {"S": r.S, "valor": r.valor, "costo": r.costo, "evaluaciones": r.evaluaciones,
                 "origen": r.origen, "OPT": None, "S_opt": None, "razon": None}
    if exacto:
        try:
            S_opt, OPT, evaluadas = seleccionar_exacto_costos(instancia.crear_oraculo(), candidatos, costos, L)
            seleccion.update({"OPT": OPT, "S_opt": S_opt, "evaluaciones_OPT": evaluadas,
                              "razon": r.valor / OPT if OPT > 0 else None})
        except DemasiadasCombinaciones as error:
            seleccion["motivo_sin_OPT"] = str(error)
    seleccion["verificaciones"] = _verificar_seleccion(instancia, candidatos, costos, L, seleccion)
    return seleccion


def _verificar_seleccion(instancia, candidatos, costos, L, sel):
    """S_r ⊆ candidatos, sin repetidos, Σ c(S_r) ≤ L, f(S_r) recalculada y f ≥ 0,405·OPT_r. Tiempo O(n_r) + valor(S_r)."""
    S = sel["S"]
    recalculado = instancia.crear_oraculo().valor(list(S))
    lista = [
        Verificacion("S_r ⊆ candidatos de la ronda", set(S) <= set(candidatos), f"S_r = {S}"),
        Verificacion("S_r sin repetidos", len(set(S)) == len(S), f"|S_r| = {len(S)}"),
        Verificacion("Σ c(S_r) ≤ L (reemplaza a |S_r| ≤ k; Supuesto ❓)", sum(costos[v] for v in S) <= L,
                     f"Σ c(S_r) = {sum(costos[v] for v in S)}, L = {L}"),
        Verificacion("f(S_r) acumulada = f(S_r) recalculada", abs(recalculado - sel["valor"]) <= TOLERANCIA,
                     f"acumulada = {sel['valor']}, recalculada = {recalculado}"),
    ]
    if sel["OPT"] is not None:
        lista.append(Verificacion("f(S_r) ≥ 0,405·OPT_r (voraz modificado)",
                                  sel["valor"] >= COTA_A * sel["OPT"] - TOLERANCIA,
                                  f"f(S_r) = {sel['valor']}, OPT_r = {sel['OPT']}"))
    return [v.a_diccionario() for v in lista]


def _reparto_con_vecinos(instancia, modelo, S, beta, topes_r, coef):
    """Paso 3 de la ronda: reparto c1 o c2 sobre S_r con topes = restante. Devuelve un diccionario.

    c1: O(|S| + Σ grado + B lg |S|), exacto por §7.1.1. c2: O(|S| + Σ grado + B·(|S| + A_S)), cota 1 − (1 − 1/B)^B;
    su exacto por enumeración solo corre si los repartos caben en LIMITE_REPARTOS (decisión 57).
    """
    B = instancia.B
    if not S:                                          # sin participantes: nada que repartir
        return {"x": {}, "U": 0.0, "verificaciones": [], "a_prima": None}
    if modelo == "c1":
        resultado, a_prima = repartir_c1(S, B, coef, instancia.vecinos, beta, topes_r)
        utilidades = {i: UtilidadLog(a_prima[i]) for i in S}
        lista = verificar_reparto(S, B, utilidades, resultado, topes_r)
        return {"x": resultado.x, "U": resultado.utilidad, "a_prima": a_prima,
                "verificaciones": [v.a_diccionario() for v in lista]}
    resultado = repartir_c2(S, B, coef, instancia.vecinos, beta, topes_r)
    grafo_S = vecinos_en_S(S, instancia.vecinos)
    valor_U = lambda x: utilidad_c2(x, coef, grafo_S, beta)   # noqa: E731  U(x) del modelo c2
    lista = verificar_reparto_c2(S, B, resultado, valor_U, topes_r)
    reparto = {"x": resultado.x, "U": resultado.utilidad, "a_prima": None, "pasos": resultado.pasos,
               "repartos": contar_repartos(S, B, topes_r), "cota": cota_c2(B), "OPT": None}
    if reparto["repartos"] <= LIMITE_REPARTOS:
        _, OPT, _ = repartir_exacto(S, B, valor_U, topes_r)
        reparto["OPT"] = OPT
    reparto["verificaciones"] = [v.a_diccionario() for v in lista]
    return reparto


def ejecutar_combinada(instancia, modelo="c1", modo="transitorio", prob_fallo=PROBABILIDAD_FALLO,
                       semilla=SEMILLA_FALLOS, rondas=None, beta=BETA, exacto=True):
    """Corre las T rondas combinadas: fallos (b), selección con costos y L (a), reparto con vecinos (c).

    Recibe la instancia (formato de la docente: costos, L y grafo), modelo "c1"|"c2", modo "transitorio"|
    "permanente", q, semilla, T (None: numero_rondas del caso, o 1), β y si se calcula OPT_r.
    Devuelve un diccionario con la entrada, las rondas (fallados, candidatos, selección, reparto, restante) y
    todas_cumplen. Tiempo por ronda: Θ(N) + O(n_r·mín(n_r, L/c_mín)·(1 + grado)) + el reparto + 2^n_r·O(N + A)
    del exacto. Espacio O(N + A) más el resultado.
    """
    T = rondas if rondas is not None else (instancia.numero_rondas() or 1)
    _validar(instancia, modelo, modo, T)
    ids, costos, L = instancia.ids(), instancia.costos(), instancia.presupuesto_costos
    coef = {nodo.id: nodo.utilidad.a for nodo in instancia.nodos}   # a_i de la familia log
    topes = instancia.topes()
    restante = {v: topes.get(v, instancia.B) for v in ids}           # el restante empieza en el tope
    azar = random.Random(semilla)
    caidos = set()
    lista_rondas = []
    for numero in range(1, T + 1):
        fallados = sortear_fallos(ids, prob_fallo, azar)              # (b) Θ(N)
        if modo == "permanente":
            caidos.update(fallados)
        fuera = caidos if modo == "permanente" else set(fallados)
        candidatos = candidatos_de_la_ronda(ids, fuera, restante)
        seleccion = _seleccion_con_costos(instancia, candidatos, costos, L, exacto)   # (a)
        topes_r = {v: restante[v] for v in seleccion["S"]}            # el tope de esta ronda es el restante
        reparto = _reparto_con_vecinos(instancia, modelo, seleccion["S"], beta, topes_r, coef)   # (c)
        for v, x_v in reparto["x"].items():
            restante[v] -= x_v                                        # x_v ≤ restante[v]: nunca negativo
        lista_rondas.append({"ronda": numero, "fallados": fallados, "candidatos": candidatos,
                             "seleccion": seleccion, "reparto": reparto, "restante": dict(restante),
                             "restante_total": sum(restante.values())})
    negativos = [v for v in ids if restante[v] < 0]
    globales = [Verificacion("presupuesto restante ≥ 0 en todos los nodos", not negativos,
                             "todos cumplen" if not negativos else f"negativos: {negativos}").a_diccionario()]
    todas = [v for r in lista_rondas for v in r["seleccion"]["verificaciones"] + r["reparto"]["verificaciones"]]
    return {"caso": instancia.nombre,
            "entrada": {"N": instancia.N, "k": instancia.k, "B": instancia.B, "L": L, "T": T, "modelo": modelo,
                        "beta": beta, "modo": modo, "prob_fallo": prob_fallo, "semilla": semilla},
            "supuestos": list(SUPUESTOS), "rondas": lista_rondas, "verificaciones_globales": globales,
            "resumen": {"suma_f": sum(r["seleccion"]["valor"] for r in lista_rondas),
                        "suma_U": sum(r["reparto"]["U"] for r in lista_rondas)},
            "todas_cumplen": all(v["cumple"] for v in todas + globales)}


def _texto_x(x):
    """x como «id:valor» en el orden de S."""
    return ", ".join(f"{i}:{v}" for i, v in x.items()) or "-"


def a_texto(resultado):
    """Traza legible de la corrida combinada: una cabecera y un bloque por ronda. Tiempo O(tamaño del resultado)."""
    e = resultado["entrada"]
    lineas = [f"Corrida combinada (a)+(b)+(c{e['modelo'][1]}) · caso {resultado['caso']}",
              f"N = {e['N']}, B = {e['B']}, L = {e['L']} (reemplaza a k = {e['k']}), T = {e['T']}, "
              f"modo = {e['modo']}, q = {e['prob_fallo']}, semilla = {e['semilla']}, β = {e['beta']}"]
    lineas += [f"  {s}" for s in resultado["supuestos"]]
    for r in resultado["rondas"]:
        s, p = r["seleccion"], r["reparto"]
        lineas.append(f"\nRonda {r['ronda']}")
        lineas.append(f"  fallados: {r['fallados'] or '-'}; candidatos ({len(r['candidatos'])}): {r['candidatos']}")
        lineas.append(f"  S_r = {s['S']} (origen: {s['origen']}), costo = {s['costo']} ≤ L, "
                      f"f(S_r) = {s['valor']:.6f}, evaluaciones = {s['evaluaciones']}")
        if s["OPT"] is not None:
            lineas.append(f"  OPT_r = {s['OPT']:.6f} con {s['S_opt']} ({s['evaluaciones_OPT']} subconjuntos factibles), razón = {s['razon']:.6f} (cota 0,405)")
        lineas.append(f"  x = {_texto_x(p['x'])}; U_r = {p['U']:.6f}")
        if p.get("a_prima"):
            lineas.append("  a'_i = " + ", ".join(f"{i}:{a:.4f}" for i, a in p["a_prima"].items()))
        if "repartos" in p:
            opt = f"OPT = {p['OPT']:.6f}" if p["OPT"] is not None else "exacto no corre (pasa del límite)"
            lineas.append(f"  c2: repartos = {p['repartos']}, {opt}, cota 1 − (1 − 1/B)^B = {p['cota']:.6f}")
        lineas.append(f"  restante total tras la ronda = {r['restante_total']}")
        malas = [v for v in s["verificaciones"] + p["verificaciones"] if not v["cumple"]]
        lineas.append("  verificaciones: todas cumplen" if not malas else f"  FALLAN: {malas}")
    lineas.append(f"\nΣ f = {resultado['resumen']['suma_f']:.6f}; Σ U = {resultado['resumen']['suma_U']:.6f}; "
                  f"todas cumplen: {resultado['todas_cumplen']}")
    return "\n".join(lineas) + "\n"


def _sin_verificaciones(resultado):
    """Las rondas sin las listas de verificaciones: para comparar dos corridas por sus decisiones."""
    return [{"fallados": r["fallados"], "candidatos": r["candidatos"], "S": r["seleccion"]["S"],
             "x": r["reparto"]["x"]} for r in resultado["rondas"]]


def main():
    instancia = leer_instancia(CASO)
    ok = True
    for modelo in MODELOS:
        resultado = ejecutar_combinada(instancia, modelo)
        permanente = ejecutar_combinada(instancia, modelo, modo="permanente")
        coincide = _sin_verificaciones(resultado) == _sin_verificaciones(permanente)
        resultado["modo_permanente"] = {"coincide_con_transitorio": coincide,
                                        "nota": "con la semilla 0 los fallados de cada ronda contienen a los de "
                                                "la anterior, así que los candidatos de los dos modos son iguales"}
        carpeta = SALIDA / f"combinada_{modelo}"
        carpeta.mkdir(parents=True, exist_ok=True)
        with open(carpeta / "salida.json", "w", encoding="utf-8") as archivo:
            json.dump(resultado, archivo, ensure_ascii=False, indent=2)
        texto = a_texto(resultado) + f"Modo permanente: coincide con el transitorio = {coincide}\n"
        (carpeta / "traza.txt").write_text(texto, encoding="utf-8")
        # La consola de Windows puede no tener β ni Σ: se imprime solo un resumen ASCII; la traza va al archivo
        print(f"{modelo}: suma f = {resultado['resumen']['suma_f']:.6f}, suma U = {resultado['resumen']['suma_U']:.6f}, "
              f"todas cumplen = {resultado['todas_cumplen']}, permanente coincide = {coincide} -> {carpeta}")
        ok = ok and resultado["todas_cumplen"] and permanente["todas_cumplen"]
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
