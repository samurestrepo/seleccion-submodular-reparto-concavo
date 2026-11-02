# Decisiones de diseño

Cada decisión lleva su porqué, para no reabrirla sin motivo.

| # | Fecha | Decisión | Por qué | Quién |
|---|---|---|---|---|
| 1 | 2026-11-01 | Python 3.11+, solo biblioteca estándar en la lógica | Se lee casi como el pseudocódigo; trae `heapq` y `time.perf_counter` | Samuel |
| 2 | 2026-11-01 | Nombres, comentarios y documentación en español | Coinciden con el informe y facilitan sustentar sin notas | Samuel |
| 3 | 2026-11-01 | Repositorio privado en GitHub | La guía pide repositorio; privado evita copias | Samuel |
| 4 | 2026-11-01 | El agente funciona igual en el PC y en la nube | Toda la memoria vive en el repo; sin rutas absolutas | Samuel |
| 5 | 2026-11-01 | f de la Parte 2 = cobertura; u_i de la Parte 1 = familias log y raíz con coeficiente a | Es el caso que conecta con la reducción; Δ en O(1) (informe 6.5) | Claude (informe) |
| 6 | 2026-11-01 | Empates por el menor índice | Ejecuciones reproducibles (informe 6.3 y 6.4) | Claude (informe) |
| 7 | 2026-11-01 | Montículo de máximos con `heapq` y claves `(-ganancia, indice)` | `heapq` solo ofrece montículo de mínimos | Claude |
| 8 | 2026-11-01 | El tiempo se mide solo alrededor de cada algoritmo, sin lectura ni escritura | Así el tiempo medido corresponde a la T(n) deducida | Claude (informe 6.6) |
| 9 | 2026-11-01 | Nombre del proyecto y del repo: `seleccion-submodular-reparto-concavo` | Dice qué resuelve cada parte y con qué propiedad; pensado para hacerlo público después | Samuel |
| 10 | 2026-11-02 | Familia extra de utilidad `"tabla"` (lista de ganancias por unidad). Agregada al informe 6.5 el 2026-11-02 | Permite probar tal cual los ejemplos del informe (P: 9, 5, 2, 1) y el contraejemplo convexo; no cambia los algoritmos | Claude |
| 11 | 2026-11-02 | Cada algoritmo se corre dos veces: una medida sin traza y otra con traza; se verifica que coinciden | El informe pide medir solo el algoritmo; anotar la traza también cuesta tiempo. Descrito en el informe 6.6 el 2026-11-02 | Claude |
| 12 | 2026-11-02 | Se verifica además que las llamadas a Δ sean k·N − k(k−1)/2 y que extracciones = inserciones = B. Agregado a la tabla 6.6 del informe el 2026-11-02 | Es evidencia directa de las funciones de eficiencia en cada caso | Claude |
| 13 | 2026-11-02 | `heappop` + `heappush` separados en lugar de `heapreplace` | Se leen como las líneas 4 y 6 del pseudocódigo; misma complejidad | Claude |
| 14 | 2026-11-02 | Si la entrada no cumple sus restricciones, la ronda no ejecuta los algoritmos | El voraz de la Parte 1 solo es correcto con u_i cóncavas; se reporta en la traza en vez de dar un resultado sin garantía. Descrito en el informe 6.6 el 2026-11-02 | Claude |
