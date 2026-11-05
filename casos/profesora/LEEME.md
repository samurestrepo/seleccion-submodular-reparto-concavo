# Casos de la profesora

## Qué es el archivo
`entrada_G2_red_15_nodos.json` es el caso oficial de G2: 15 nodos, k = 5, B = 30, 3 rondas y un grafo completo no dirigido de 105 aristas con pesos de influencia. Cada nodo trae su coeficiente de utilidad, su presupuesto total y su costo de participación. **No trae "cubre".** El archivo no se edita.

## Cómo correrlo
Desde la raíz del repositorio:

    python ejecutar.py casos/profesora --salida resultados/profesora

Las evidencias quedan en `resultados/profesora/`: `resumen.csv` y, por caso, `salida.json`, `traza.json` y `traza.txt`. El formato de la entrada y de la salida está en `MANUAL_TECNICO.md`, sección 3.

## Supuestos de modelado adoptados
El archivo trae los datos, pero no dice cómo se usan. La docente no responde esta semana, así que se tomaron como válidos estos supuestos, que el informe declara como tales (`docs/agente/DECISIONES.md`, decisiones 24 a 26 y 28):

1. **Utilidad conjunta (Parte 2):** cobertura por influencia. f(S) = Σ_w a_w · (1 − Π_{v∈S} (1 − p_vw)), con a_w = `coeficiente_utilidad` de w, p_vw = `peso_influencia` de la arista {v, w} (0 si no hay arista) y p_ww = 1.
2. **Utilidad de cada nodo (Parte 1):** u_i(x) = `coeficiente_utilidad` · ln(1 + x).
3. **Alcance:** la solución base corre **una** ronda con k y B. `numero_rondas`, `costo_participacion` y `presupuesto_costos_participacion_por_ronda` son de las variantes (b) y (a): se leen y se reportan en la sección "informativo", pero no se aplican.
4. **Tope por nodo (decisión 28):** `presupuesto_total_nodo` es el tope c_i de x_i ≤ c_i. Es lo que le queda al nodo para todo el proyecto, y en una ronda lo puede gastar completo. En la variante (b) se descontará ronda a ronda. En este caso todos valen 18 y el mayor reparto es 7, así que el tope no cambia el resultado.

## Resultado esperado
S = N11, N14, N09, N15, N13 (en orden de elección); f(S) ≈ 145.5795; 65 llamadas a Δ; reparto N11 = 5, N14 = 7, N09 = 7, N15 = 6, N13 = 5; U ≈ 88.5640; 30 extracciones y 30 inserciones. Σ costos de S = 23 frente a 24 (informativo). Lo comprueba `pruebas/test_bateria.py::test_regresion_caso_de_la_profesora`.
