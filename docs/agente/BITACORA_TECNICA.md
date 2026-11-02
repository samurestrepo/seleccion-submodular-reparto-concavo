# Bitácora técnica del agente

Memoria de trabajo del agente `ingeniero-red`. Se lee al empezar y se actualiza al terminar.
Se escribe para alguien que no recuerda nada: frases completas, sin "lo de ayer".

## Estado actual
- **Fase:** solución base **completa** (2026-11-02). Los 10 módulos del mapa existen, tienen ficha y pruebas; `python -m pytest` pasa con 36 pruebas.
- **Próximo entregable:** primera entrega, el viernes 6 de noviembre de 2026. Incluye la solución base de los dos voraces con traza y tiempos, README, manual técnico y la ejecución de los casos de la profesora.
- **Bloqueante:** los casos de la profesora y su formato no han llegado. Mientras tanto se usa el formato provisional (informe, sección 6.5). Si llegan en otro formato, solo se cambia `red/entrada.py`.

## Pendientes (en orden)
1. [x] Esqueleto del repositorio según `MAPA_DEL_CODIGO.md`.
2. [x] `entrada.py` y su validación.
3. [x] `cobertura.py` (oráculo f) y `seleccion.py` (voraz de la Parte 2), con sus pruebas.
4. [x] `utilidades.py` y `reparto.py` (voraz de la Parte 1 con montículo), con sus pruebas.
5. [x] `verificacion.py`, `traza.py` y `ronda.py`; la interfaz de línea de comandos `ejecutar.py`.
6. [x] `generador.py` de instancias sintéticas.
7. [x] README y MANUAL_TECNICO.
8. [ ] Correr los casos de la profesora cuando lleguen y guardar las evidencias en `resultados/profesora/`: `python ejecutar.py casos/profesora --salida resultados/profesora`.
9. [ ] Que Samuel lea y explique la deuda de estudio (abajo), empezando por `reparto.py`.

## Deuda de estudio (lo que Samuel aún no sabría rehacer solo)
Todo el código lo escribió Claude el 2026-11-02. Orden sugerido de estudio, de lo que más se pregunta en la sustentación a lo que menos:
1. **`red/reparto.py`:** por qué se guarda `(-ganancia, indice)` en `heapq`; cómo eso desempata por el menor índice; de dónde sale O(N + B lg N) (heapify O(N) + B vueltas de pop y push). Ficha: `docs/modulos/reparto.md`.
2. **`red/seleccion.py`:** recorrido de V en orden creciente con `>` estricto (desempate); por qué hay exactamente k·N − k(k−1)/2 llamadas. Ficha: `docs/modulos/seleccion.md`.
3. **`red/cobertura.py`:** Δ(v | S) = |C_v ∖ cub(S)| sin recalcular la unión; qué cuenta como llamada.
4. **`red/ronda.py`:** por qué se ejecuta dos veces (medida sin traza y con traza) y qué incluye el tiempo.
5. `red/verificacion.py`, `red/utilidades.py` (familia tabla), `red/entrada.py`, `red/traza.py`, `red/generador.py`, `ejecutar.py`: de lectura, menos probables en la sustentación.
6. Las pruebas de fuerza bruta (`pruebas/fuerza_bruta.py`): qué comprueban.

## Registro de cambios
| Fecha | Qué | Por qué | Archivos | Pruebas |
|---|---|---|---|---|
| 2026-11-01 | Se crea el agente y su memoria | Samuel pidió un agente que documente todo y resuelva cambios rápido | CLAUDE.md, .claude/agents/ingeniero-red.md, docs/agente/* | — |
| 2026-11-02 | Solución base completa: los dos voraces, oráculo, utilidades, entrada, verificación, traza, ronda, generador y CLI; 3 casos propios; fichas, README y manual técnico | Pendientes 1 a 7, para la primera entrega del 6 de noviembre. Samuel dio la orden de escribir el código | red/*, ejecutar.py, pruebas/*, casos/*, resultados/propios/*, docs/modulos/*, README.md, MANUAL_TECNICO.md, pytest.ini, requirements-dev.txt; DECISIONES (10 a 14), MAPA, GUIA_CAMBIOS | 36 pruebas en verde: ejemplos del informe (27; {1, 3} con 5), los dos contraejemplos (4 vs 11; 5 vs 6), conteo k·N − k(k−1)/2, reparto = fuerza bruta en 150 instancias, cota 1 − 1/e en 200, entrada, ronda y CLI |
| 2026-11-02 | Se sube la solución base a `main` y se alinea el informe con el código: familia «tabla» (6.5); 1 ≤ k < N, conteo k·N − k(k−1)/2, B extracciones y B inserciones, doble ejecución medida/con traza y entrada inválida sin ejecutar (6.6) | Samuel pidió que el informe y el código dijeran lo mismo | Informe (Google Doc); DECISIONES (10 a 14) | Sin cambios de código; 36 pruebas en verde |
| 2026-11-02 | `red/utilidades.py` apareció movido a `resultados/propios/contraejemplo_seleccion/` en el PC de Samuel (arrastre accidental en VS Code) y por eso fallaba la ejecución; se devolvió a `red/` sin cambios. Se agrega a CLAUDE.md la regla de sincronización (pull al empezar, push al terminar) | Trabajar desde VS Code y desde el chat sin pisarse | CLAUDE.md, BITACORA_TECNICA.md | Caso del informe en OK en el PC |
