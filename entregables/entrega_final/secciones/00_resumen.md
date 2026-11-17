# Resumen

**Conclusión.** El reparto del presupuesto (Parte 1) se resolvió de forma exacta y en tiempo polinomial. La selección de nodos (Parte 2) y la variante con costos son NP-difíciles y se resolvieron con algoritmos aproximados de garantía demostrada o citada. En las baterías aleatorias en que se calculó el óptimo, todos los aproximados quedaron por encima del 93 % del óptimo, muy por encima de sus cotas. Los tiempos medidos crecieron como predicen las funciones de eficiencia deducidas, con una excepción explicada abajo.

**Qué se resolvió de forma exacta.**
- **Parte 1:** el voraz con montículo es óptimo por un argumento de intercambio (§7.1.1) y cuesta Θ(N + B(1 + lg N)). La programación dinámica de §7.2 lo confirma.
- **Variante (c), modelo c1** (el efecto de los vecinos va aparte): se reduce a la Parte 1 con otros coeficientes y el mismo voraz sigue siendo exacto (§8.4.1); coincidió con la enumeración exacta en las 324 instancias de prueba.

**Qué no, y con qué garantía.**
- **Parte 2:** NP-difícil por reducción desde Cobertura Máxima (§6). El voraz hace k·N − k(k − 1)/2 evaluaciones de f y garantiza 1 − (1 − 1/k)ᵏ ≥ 1 − 1/e ≈ 0,632 del óptimo (Nemhauser, Wolsey y Fisher, 1978). Peor razón medida: 0,937 en 45 instancias aleatorias (§10.2.1).
- **Variante (a), costos de participación:** NP-difícil, porque contiene a la Parte 2 (§6.9). El voraz modificado garantiza 0,405 del óptimo (Tang et al., 2021) con O(N²) evaluaciones; la enumeración parcial garantiza 1 − 1/e (Sviridenko, 2004) con O(N⁵). Peor razón medida del modificado: 0,947 en 36 instancias (§8.2.4).
- **Variante (b), T rondas con fallos:** cada ronda reutiliza los dos voraces sobre los nodos disponibles, con costo O(T·(k·(N + A) + B lg k)). La cota del voraz vale ronda por ronda, no sobre las T rondas juntas (§8.3).
- **Variante (c), modelo c2** (el presupuesto del vecino entra en la utilidad): la utilidad deja de separarse por nodo, el voraz deja de ser exacto (contraejemplo de 3 nodos) y conserva la cota 1 − (1 − 1/B)ᴮ ≥ 1 − 1/e (§8.4.3). Peor razón medida: 0,987 en 324 instancias.

**Qué confirmó el experimento.** Se midieron 14 series de al menos 5 tamaños, con semilla fija (§11). En 13, la pendiente log-log del tiempo contra la T(n) deducida quedó entre 0,94 y 1,09: Θ(k·N) en el voraz de la Parte 2, Θ(N²) en el voraz de la variante (a), Θ(N⁵) en la enumeración parcial, Θ(2ᴺ) en la fuerza bruta con presupuesto y crecimiento lineal en T y en B en las variantes (b) y c2. La excepción es el reparto con N creciente y B fijo (serie d): con T = N + B·lg N se espera una pendiente de 0,36 contra N y se midió 0,78 (`resultados/experimentos/d_reparto_varia_N.csv`). La causa principal es que los dos términos tienen constantes distintas: con las del ajuste a·N + b·B·lg N, el término en N cuesta unas 6 veces más por unidad y la pendiente esperada pasa a 0,71. Que la caché explique el resto es una hipótesis no comprobada (§11.3).

**Supuestos.** Donde el enunciado no fija un dato (cómo conviven k y L, cómo fallan los nodos, cómo influyen los vecinos), se tomó un supuesto explícito, marcado **Supuesto ❓** en §5 y reunido en §13.
