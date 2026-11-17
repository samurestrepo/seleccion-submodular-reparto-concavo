"""Variante (b): T rondas con nodos que fallan y presupuesto por nodo que se descuenta.

La red entrena T rondas (`numero_rondas` en el formato de la profesora, 3 en el caso oficial; el campo
opcional `rondas` en el propio; 1 si no viene). Antes de cada ronda, cada nodo falla de forma
independiente con probabilidad q, con `random.Random(semilla)`. Dos modos:
- "transitorio": el nodo falla solo esa ronda y puede volver en la siguiente;
- "permanente": el nodo que falla no vuelve.

**Supuestos ❓ (decisión 39):** la docente no ha dicho cómo fallan los nodos ni cómo se gasta
`presupuesto_total_nodo` entre rondas. Aquí:
1. El tope de cada nodo es su presupuesto restante: empieza en `presupuesto_total_nodo` (o `tope`;
   si no hay tope, B) y se le descuenta lo que recibe en cada ronda. Nunca queda negativo.
2. Candidatos de la ronda r: los nodos que no fallaron y tienen presupuesto restante > 0. El voraz
   recibe esa lista como V, con k_r = mín(k, |candidatos|): si son k o menos, participan todos. El
   oráculo es el de la instancia completa (f se mide sobre todo el grafo), solo cambia quién se puede elegir.
3. Cada ronda se optimiza sola, con el mismo k y el mismo B, sin mirar las siguientes. Optimizar las T
   rondas juntas es otro problema (planeación con incertidumbre) y queda como limitación.
4. En cada ronda se sortea el fallo de los N nodos, también de los ya caídos en modo permanente, para que
   con la misma semilla los fallos de los dos modos coincidan: los caídos del permanente en la ronda r son
   la unión de los fallados transitorios de las rondas 1 a r.

Por ronda corren la Parte 2 (`seleccionar_nodos`) y la Parte 1 (`repartir_presupuesto` con topes = restante),
y como referencia la fuerza bruta de `exacto.py` sobre los candidatos (OPT_r). La cota vale ronda por ronda:
f(S_r) ≥ (1 − (1 − 1/k_r)^k_r)·OPT_r; no es una cota sobre las T rondas juntas.

T(n) (ficha `docs/modulos/variante_rondas.md`): T rondas por el costo de una ronda más el sorteo,
O(T·(k·(N + A) + B lg k)) con influencia (sin el exacto), más O(T·C(N, k)·(N + A)) si corre el exacto.
"""

import random
import time

from red.exacto import DemasiadasCombinaciones, seleccionar_exacto
from red.reparto import ResultadoReparto, repartir_presupuesto
from red.ronda import _resultado_rechazado, _resumen_tiempos
from red.seleccion import seleccionar_nodos
from red.traza import Traza, _numero
from red.verificacion import (Verificacion, verificar_conteo_llamadas, verificar_cota_ronda, verificar_entrada,
                              verificar_reparto, verificar_seleccion_ronda, verificar_variante_b)

MODOS = ("transitorio", "permanente")
PROBABILIDAD_FALLO = 0.2   # q por omisión (Supuesto ❓)
SEMILLA_FALLOS = 0         # semilla por omisión del sorteo
SUPUESTOS = (
    "Supuesto ❓: el tope de cada nodo es su presupuesto restante (empieza en presupuesto_total_nodo o tope; "
    "sin tope, B) y se descuenta lo gastado en cada ronda",
    "Supuesto ❓: candidatos = nodos que no fallaron y con presupuesto restante > 0; si son k o menos, "
    "participan todos (k_r = mín(k, |candidatos|))",
    "Supuesto ❓: cada ronda se optimiza sola con el mismo k y el mismo B; no se planean las T rondas juntas",
    "Supuesto ❓: cada nodo falla antes de cada ronda con probabilidad q, de forma independiente "
    "(random.Random(semilla)); transitorio = solo esa ronda, permanente = no vuelve",
)


def sortear_fallos(ids, prob_fallo, azar):
    """Sortea qué nodos fallan antes de una ronda. Devuelve la lista de fallados, en orden creciente.

    Recibe los ids en orden creciente, q en [0, 1] y el generador `random.Random` ya sembrado.
    Cada nodo falla de forma independiente: `azar.random() < q` (con q = 0 nadie falla, porque
    random() está en [0, 1); con q = 1 fallan todos). Tiempo Θ(N), un número aleatorio por nodo.
    """
    return [v for v in ids if azar.random() < prob_fallo]


def candidatos_de_la_ronda(ids, fuera, restante):
    """Los nodos que pueden participar: no están fuera (fallados o caídos) y les queda presupuesto > 0.

    Recibe los ids en orden creciente, el conjunto `fuera` y el diccionario id → presupuesto restante.
    Devuelve la lista en orden creciente (el orden que recorre el voraz). Tiempo Θ(N).
    """
    return [v for v in ids if v not in fuera and restante[v] > 0]


def _reparto_vacio():
    """El reparto de una ronda sin participantes: nada que repartir, ningún movimiento del montículo."""
    return ResultadoReparto({}, 0.0, 0, 0)


def _correr_ronda(instancia, candidatos, k_r, topes_r, traza=None):
    """Parte 2 y Parte 1 de una ronda sobre los candidatos, con un oráculo nuevo y reloj alrededor de cada una.

    Devuelve (oraculo, S, valorS, reparto, t_seleccion, t_reparto). Con k_r = 0 (sin candidatos) no corre
    nada: S = [], f = 0 y reparto vacío. Tiempo O(k_r·(N + A)) con influencia más O(k_r + B lg k_r).
    """
    utilidades = instancia.utilidades()
    oraculo = instancia.crear_oraculo()
    if k_r == 0:
        return oraculo, [], 0.0, _reparto_vacio(), 0.0, 0.0
    inicio = time.perf_counter()
    S, valorS = seleccionar_nodos(oraculo, candidatos, k_r, traza)   # V = candidatos, k = k_r
    t_seleccion = time.perf_counter() - inicio
    inicio = time.perf_counter()
    reparto = repartir_presupuesto(S, instancia.B, utilidades, traza, topes_r)   # topes = restante
    t_reparto = time.perf_counter() - inicio
    return oraculo, S, valorS, reparto, t_seleccion, t_reparto


def _exacto_de_la_ronda(instancia, candidatos, k_r):
    """OPT_r por fuerza bruta sobre los candidatos (referencia). Devuelve un diccionario.

    Con k_r = 0, OPT = 0 sin evaluar nada. Si C(|candidatos|, k_r) supera el límite de `exacto.py`,
    devuelve disponible = False con el motivo. Tiempo C(n_r, k_r) evaluaciones de f, cada una O(N + A).
    """
    if k_r == 0:
        return {"disponible": True, "S": [], "OPT": 0.0, "evaluaciones": 0}
    try:
        S_opt, OPT, evaluaciones = seleccionar_exacto(instancia.crear_oraculo(), candidatos, k_r)
    except DemasiadasCombinaciones as error:
        return {"disponible": False, "motivo": str(error)}
    return {"disponible": True, "S": S_opt, "OPT": OPT, "evaluaciones": evaluaciones}


def _ejecutar_una_ronda(instancia, numero, candidatos, topes_r, repeticiones, exacto):
    """Una ronda completa sobre los candidatos: R ejecuciones medidas, una con traza, exacto y verificaciones.

    Devuelve (diccionario de la ronda, traza de la ronda, reparto). k_r = mín(k, |candidatos|).
    Tiempo: R veces el costo de los algoritmos, más el exacto (si se pide) y las verificaciones.
    """
    k_r = min(instancia.k, len(candidatos))
    utilidades = instancia.utilidades()

    # 1. R ejecuciones medidas, sin traza (decisión 11); se reporta la primera
    corridas = [_correr_ronda(instancia, candidatos, k_r, topes_r) for _ in range(repeticiones)]
    oraculo, S, valorS, reparto, _, _ = corridas[0]
    tiempos_seleccion = [c[4] for c in corridas]
    tiempos_reparto = [c[5] for c in corridas]

    # 2. Ejecución con traza (evidencia)
    traza = Traza()
    _, S_traza, valor_traza, reparto_traza, _, _ = _correr_ronda(instancia, candidatos, k_r, topes_r, traza)

    # 3. Referencia: OPT_r por fuerza bruta sobre los candidatos
    referencia = _exacto_de_la_ronda(instancia, candidatos, k_r) if exacto else {"disponible": False,
                                                                                 "motivo": "no se pidió"}
    razon = None
    if referencia["disponible"] and referencia["OPT"] > 0:
        razon = valorS / referencia["OPT"]
    cota = 1 - (1 - 1 / k_r) ** k_r if k_r >= 1 else None

    # 4. Verificaciones de la ronda
    v_seleccion = verificar_seleccion_ronda(candidatos, k_r, instancia.crear_oraculo(), S, valorS)
    v_seleccion += verificar_conteo_llamadas(len(candidatos), k_r, oraculo.llamadas_ganancia)
    if referencia["disponible"]:
        v_seleccion += verificar_cota_ronda(valorS, referencia["OPT"], k_r)
    v_reparto = verificar_reparto(S, instancia.B, utilidades, reparto, topes_r)
    distintas = [i for i, c in enumerate(corridas, start=1) if c[1] != S or c[3].x != reparto.x]
    iguales = S == S_traza and valorS == valor_traza and reparto.x == reparto_traza.x
    v_ejecucion = [
        Verificacion("todas las repeticiones dan el mismo S y el mismo reparto", not distintas,
                     f"R = {repeticiones}" if not distintas else f"difieren las repeticiones {distintas}"),
        Verificacion("ejecución con traza = ejecución medida", iguales,
                     "mismo S y mismo reparto" if iguales else "difieren"),
    ]
    verificaciones = {"seleccion": [v.a_diccionario() for v in v_seleccion],
                      "reparto": [v.a_diccionario() for v in v_reparto],
                      "ejecucion": [v.a_diccionario() for v in v_ejecucion]}
    ronda = {
        "ronda": numero,
        "candidatos": list(candidatos),
        "k_ronda": k_r,
        "seleccion": {"S": S, "valor": valorS, "llamadas_ganancia": oraculo.llamadas_ganancia,
                      "llamadas_valor": oraculo.llamadas_valor},
        "exacto": referencia,
        "razon": razon,
        "cota": cota,
        "reparto": {"x": {str(i): reparto.x[i] for i in S}, "utilidad": reparto.utilidad,
                    "extracciones": reparto.extracciones, "inserciones": reparto.inserciones},
        "tiempos_segundos": {"repeticiones": repeticiones, "seleccion": _resumen_tiempos(tiempos_seleccion),
                             "reparto": _resumen_tiempos(tiempos_reparto)},
        "verificaciones": verificaciones,
        "todas_cumplen": all(v["cumple"] for lista in verificaciones.values() for v in lista),
    }
    return ronda, traza.a_diccionario(), reparto


def _verificaciones_globales(modo, historial_candidatos, restante):
    """Lo que debe cumplirse entre rondas: el restante nunca negativo y, en permanente, candidatos que no crecen."""
    negativos = sorted(str(v) for v, r in restante.items() if r < 0)
    resultado = [Verificacion("presupuesto restante ≥ 0 en todos los nodos tras las T rondas", not negativos,
                              "todos cumplen" if not negativos else f"negativos: {negativos}")]
    if modo == "permanente":
        crecen = [r + 1 for r in range(len(historial_candidatos) - 1)
                  if not set(historial_candidatos[r + 1]) <= set(historial_candidatos[r])]
        resultado.append(Verificacion("modo permanente: los candidatos nunca aumentan (cada ronda ⊆ la anterior)",
                                      not crecen, "cumple" if not crecen else f"crecen en las rondas {crecen}"))
    return resultado


def ejecutar_rondas(instancia, modo="transitorio", prob_fallo=PROBABILIDAD_FALLO, semilla=SEMILLA_FALLOS,
                    rondas=None, repeticiones=1, exacto=True):
    """Corre las T rondas de la variante (b) sobre la instancia y devuelve un diccionario con todo.

    Recibe: la instancia; modo ("transitorio" o "permanente"); q = prob_fallo en [0, 1]; la semilla del
    sorteo; rondas = T (si es None, el `numero_rondas`/`rondas` de la instancia, y si tampoco viene, 1);
    R = repeticiones de la ejecución medida por ronda; exacto = si se calcula OPT_r por fuerza bruta.
    Devuelve: caso, entrada (N, k, B, T, modo, q, semilla), variante (supuestos), rondas (una entrada por
    ronda: fallados, caídos, candidatos, k_r, selección, exacto, razón, cota, reparto, presupuesto restante
    después, tiempos, verificaciones), resumen (sumas de f y U), verificaciones globales, traza y todas_cumplen.
    Si la entrada no cumple sus restricciones (o T < 1), no corre nada y devuelve el rechazo con el motivo.
    Con q = 0 y T = 1 el resultado es el de la solución base (mismo S, f(S), reparto y U).
    Tiempo, sin el exacto: O(T·(k·(N + A) + B lg k))·R con influencia (O(T·(k·(N + M) + B lg k))·R con
    cobertura); el exacto suma O(T·C(N, k)·(N + A)). Espacio: O(N + A) del oráculo y O(N) del restante,
    más O(T·(k·N + B)) del resultado con sus trazas.
    """
    if modo not in MODOS:
        raise ValueError(f"modo de fallo desconocido: {modo!r}; los válidos son {MODOS}")
    if not 0 <= prob_fallo <= 1:
        raise ValueError(f"la probabilidad de fallo debe estar en [0, 1]; llegó {prob_fallo}")
    if repeticiones < 1:
        raise ValueError(f"se necesita al menos una repetición; llegó {repeticiones}")
    T = rondas if rondas is not None else instancia.numero_rondas()
    if T is None:
        T = 1
    entrada = {"N": instancia.N, "k": instancia.k, "B": instancia.B, "T": T, "modo": modo,
               "prob_fallo": prob_fallo, "semilla": semilla}
    verificaciones_entrada = [v.a_diccionario() for v in verificar_entrada(instancia)]
    verificaciones_entrada += [v.a_diccionario() for v in verificar_variante_b(T)]
    if not all(v["cumple"] for v in verificaciones_entrada):
        return _resultado_rechazado(instancia.nombre, entrada, verificaciones_entrada)

    ids = instancia.ids()
    topes = instancia.topes()
    restante = {v: topes.get(v, instancia.B) for v in ids}   # Supuesto ❓ 1: sin tope, B
    azar = random.Random(semilla)
    caidos = set()                                           # solo crece en modo permanente
    rondas_resultado = []
    trazas = []
    historial_candidatos = []
    for numero in range(1, T + 1):
        fallados = sortear_fallos(ids, prob_fallo, azar)      # Θ(N) por ronda
        if modo == "permanente":
            caidos.update(fallados)
        fuera = caidos if modo == "permanente" else set(fallados)
        candidatos = candidatos_de_la_ronda(ids, fuera, restante)
        topes_r = {v: restante[v] for v in candidatos}        # el tope de esta ronda es el restante
        ronda, traza, reparto = _ejecutar_una_ronda(instancia, numero, candidatos, topes_r, repeticiones, exacto)
        for v in ronda["seleccion"]["S"]:                     # se descuenta lo gastado; x_v ≤ restante[v]
            restante[v] -= reparto.x[v]
        ronda["fallados"] = fallados
        ronda["caidos"] = sorted(caidos) if modo == "permanente" else fallados
        ronda["presupuesto_restante"] = {str(v): restante[v] for v in ids}
        rondas_resultado.append(ronda)
        trazas.append({"ronda": numero, "fallados": fallados, "candidatos": list(candidatos), **traza})
        historial_candidatos.append(candidatos)

    globales = [v.a_diccionario() for v in _verificaciones_globales(modo, historial_candidatos, restante)]
    return {
        "caso": instancia.nombre,
        "entrada": entrada,
        "variante": {"nombre": "b", "modo": modo, "prob_fallo": prob_fallo, "semilla": semilla, "T": T,
                     "supuestos": list(SUPUESTOS)},
        "verificaciones": {"entrada": verificaciones_entrada, "globales": globales},
        "rondas": rondas_resultado,
        "resumen": {"suma_valores": sum(r["seleccion"]["valor"] for r in rondas_resultado),
                    "suma_utilidades": sum(r["reparto"]["utilidad"] for r in rondas_resultado),
                    "rondas_sin_participantes": sum(1 for r in rondas_resultado if r["k_ronda"] == 0)},
        "traza": {"rondas": trazas},
        "todas_cumplen": all(v["cumple"] for v in verificaciones_entrada + globales)
        and all(r["todas_cumplen"] for r in rondas_resultado),
    }


def _lineas_verificaciones(lineas, titulo, verificaciones, sangria="  "):
    """Agrega al reporte una sección de verificaciones con [OK]/[FALLA]."""
    lineas.append(f"{sangria}== Verificación: {titulo} ==")
    for v in verificaciones:
        lineas.append(f"{sangria}  [{'OK' if v['cumple'] else 'FALLA'}] {v['nombre']}: {v['detalle']}")


def _lineas_ronda(ronda, traza, modo):
    """Las líneas del reporte de una ronda: fallos, candidatos, paso a paso, resultado, referencia y reparto."""
    s, r, e = ronda["seleccion"], ronda["reparto"], ronda["exacto"]
    lineas = [f"== Ronda {ronda['ronda']} ==",
              f"  Fallan en esta ronda: {ronda['fallados'] or 'ninguno'}"]
    if modo == "permanente":
        lineas.append(f"  Caídos acumulados: {ronda['caidos'] or 'ninguno'}")
    lineas.append(f"  Candidatos ({len(ronda['candidatos'])}): {ronda['candidatos'] or 'ninguno'}; "
                  f"k_r = {ronda['k_ronda']}"
                  + (" (participan todos)" if 0 < ronda["k_ronda"] == len(ronda["candidatos"]) else ""))
    lineas.append("  -- Parte 2: selección de nodos (voraz sobre los candidatos) --")
    for p in traza["pasos_seleccion"]:
        aportes = ", ".join(f"Δ({a['nodo']}) = {_numero(a['ganancia'])}" for a in p["aportes"])
        lineas.append(f"    Paso {p['paso']}: {aportes}")
        lineas.append(f"      → elige el nodo {p['elegido']} (Δ = {_numero(p['ganancia_elegido'])}); "
                      f"f(S) = {_numero(p['valor_despues'])}")
    lineas.append(f"    Resultado: S_r = {s['S']}, f(S_r) = {_numero(s['valor'])}, llamadas a Δ = {s['llamadas_ganancia']}")
    if e["disponible"]:
        razon = "—" if ronda["razon"] is None else f"{ronda['razon']:.6f}"
        cota = "—" if ronda["cota"] is None else f"{ronda['cota']:.6f}"
        lineas.append(f"    Referencia (fuerza bruta sobre los candidatos): S* = {e['S']}, OPT_r = {_numero(e['OPT'])}, "
                      f"evaluaciones = {e['evaluaciones']}; razón f(S_r)/OPT_r = {razon}; cota 1 − (1 − 1/k_r)^k_r = {cota}")
    else:
        lineas.append(f"    Referencia: OPT_r no disponible ({e['motivo']})")
    lineas.append("  -- Parte 1: reparto del presupuesto (topes = presupuesto restante) --")
    for u in traza["unidades_reparto"]:
        lineas.append(f"    Unidad {u['unidad']}: al nodo {u['nodo']} (Δ = {_numero(u['ganancia'])})")
    reparto = ", ".join(f"x_{i} = {x}" for i, x in r["x"].items()) or "sin participantes"
    lineas.append(f"    Resultado: {reparto}; U_r = {r['utilidad']:.6f}")
    restante = ", ".join(f"{v}: {x}" for v, x in ronda["presupuesto_restante"].items())
    lineas.append(f"  Presupuesto restante tras la ronda: {restante}")
    for parte, titulo in (("seleccion", "Parte 2"), ("reparto", "Parte 1"), ("ejecucion", "Ejecución")):
        _lineas_verificaciones(lineas, titulo, ronda["verificaciones"][parte])
    t = ronda["tiempos_segundos"]
    lineas.append(f"  Tiempos (mediana de {t['repeticiones']}): selección {t['seleccion']['mediana']:.9f} s, "
                  f"reparto {t['reparto']['mediana']:.9f} s")
    lineas.append("")
    return lineas


def a_texto_rondas(resultado):
    """Convierte el resultado de `ejecutar_rondas` en un reporte de texto. Tiempo O(tamaño del resultado).

    Para un caso rechazado (sin "rondas") usar `traza.a_texto`, que ya sabe mostrar el motivo.
    """
    e, va = resultado["entrada"], resultado["variante"]
    lineas = [f"CASO: {resultado['caso']}",
              f"N = {e['N']}, k = {e['k']}, B = {e['B']}, T = {e['T']} rondas",
              f"VARIANTE (b): nodos que fallan; modo = {va['modo']}, q = {va['prob_fallo']}, semilla = {va['semilla']}"]
    lineas += [f"  {supuesto}" for supuesto in va["supuestos"]]
    lineas.append("")
    _lineas_verificaciones(lineas, "entrada", resultado["verificaciones"]["entrada"], sangria="")
    lineas.append("")
    for ronda, traza in zip(resultado["rondas"], resultado["traza"]["rondas"]):
        lineas += _lineas_ronda(ronda, traza, va["modo"])
    res = resultado["resumen"]
    lineas.append(f"== Resumen de las {e['T']} rondas ==")
    lineas.append(f"  Σ f(S_r) = {_numero(res['suma_valores'])}; Σ U_r = {res['suma_utilidades']:.6f}; "
                  f"rondas sin participantes = {res['rondas_sin_participantes']}")
    lineas.append("  La cota 1 − (1 − 1/k_r)^k_r vale ronda por ronda, no sobre las T rondas juntas.")
    _lineas_verificaciones(lineas, "entre rondas", resultado["verificaciones"]["globales"], sangria="")
    lineas.append("")
    lineas.append(f"TODAS LAS VERIFICACIONES: {'CUMPLEN' if resultado['todas_cumplen'] else 'HAY FALLAS'}")
    return "\n".join(lineas) + "\n"
