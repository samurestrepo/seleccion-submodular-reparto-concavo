## 1.2 Qué contiene este informe y dónde está cada exigencia del enunciado

La tabla relaciona lo que exige el enunciado del proyecto (sus secciones 2, 4 y 5) con la sección del informe que lo responde.

**Sección 2 del enunciado: qué significa «eficiente».**

| Lo que se exige demostrar | Dónde |
|---|---|
| Definición precisa del tamaño de la entrada n | Partes 1 y 2: fila «Tamaño de la entrada» de las tablas de formalización (§3 y §4). Variantes: §5.1, §5.2 y §5.3. |
| T(n) del algoritmo exacto, contando operaciones paso a paso | Parte 1: voraz exacto, §7.1.2; programación dinámica, §7.2. Parte 2: fuerza bruta, §7.3. Variante (a): fuerza bruta con presupuesto, §7.4. Variante (c): c1 en §8.4.1 y enumeración exacta en §8.4.4. |
| T(n) de cada aproximado y su garantía, demostrada o citada | Parte 2: §8.1 (Nemhauser, Wolsey y Fisher, 1978). Variante (a): §8.2 (voraz por cociente, voraz modificado y enumeración parcial; Khuller, Moss y Naor, 1999; Sviridenko, 2004; Tang et al., 2021). Variante (b): §8.3 (cota ronda por ronda). Variante (c): §8.4.2 y §8.4.3 (cota del voraz de c2, demostrada por reducción a copias). |
| Validación experimental: tiempos para n creciente, gráficas y contraste con T(n) | Secciones 11 a 13 (tiempos medidos contra T(n)). Las razones contra el óptimo: §8.2.4, §8.3.3 y §8.4.4, y las baterías y contraejemplos de §10.2. |

**Sección 4 del enunciado: el problema.**

| Lo que pide | Dónde |
|---|---|
| 4.2 Parte 1: formalización y tamaño de la entrada N | §3 |
| 4.2 Parte 1: optimalidad del voraz por argumento de intercambio | §7.1.1 (hipótesis H1 a H4, definidas en §2.1) |
| 4.2 Parte 1: T(N, B) con montículo, O(B log N) | §7.1.2: Θ(N + B(1 + lg N)) sin topes |
| 4.3 Parte 2: formalización y tamaño (N, k) | §4 |
| 4.3 Parte 2: NP-dureza por reducción desde Cobertura Máxima | Sección 6 (6.1 a 6.8; la variante (a), en 6.9) |
| 4.3 Parte 2: voraz, cota (1 − 1/e) citada y verificada en los datos propios | §8.1; verificación en la batería de §10.2.1 |
| 4.3 Parte 2: T(N, k) = O(N·k) del voraz | §8.1: k·N − k(k − 1)/2 evaluaciones |
| 4.4 Variante (a): costos de participación; la cota «cambia de forma» y debe citarse en su versión con presupuesto | Formalización §5.1; NP-dureza §6.9; exacto §7.4; aproximados y cotas §8.2 |
| 4.4 Variante (b): T rondas con nodos que fallan | Formalización §5.2; algoritmo, T y cota por ronda §8.3 |
| 4.4 Variante (c): el presupuesto de un nodo afecta a sus vecinos | Formalización §5.3 (modelos c1 y c2); algoritmos y cota §8.4 |
| Por qué cada parte usa la técnica que usa (voraz, PD, fuerza bruta, aproximación) | Sección 9 |
| Las variantes con el caso de la docente | §10.1 |

**Sección 5 del enunciado: entregables.**

| Lo que pide | Dónde |
|---|---|
| Informe técnico con definición de n, T(n) del exacto, NP-dureza, aproximado con cota y validación experimental | Este informe: §3 a §5, sección 6, §7, §8 y secciones 11 a 13 |
| Implementación reproducible, instancias sintéticas, al menos 5 tamaños de n, medición de tiempos y gráfica de tiempo contra n | Sección 10 (implementación y casos), secciones 11 a 13 (experimentos) y el manual técnico. Cada serie del experimento tiene al menos 5 tamaños y semilla fija; los datos y las gráficas están en `resultados/experimentos/` del repositorio. |
| Sustentación: defender la reducción y la deducción de T(n) del exacto sin notas | Sección 6 (reducción) y §7 (deducciones paso a paso) |

**Términos.** Los términos nuevos de esta entrega se definen en §2.1, antes de usarlos. Los supuestos que el enunciado no fija se marcan **Supuesto ❓** donde aparecen.
