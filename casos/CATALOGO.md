# Catálogo de casos de prueba

Batería propia de la primera entrega. El caso oficial de la docente está en `casos/profesora/`, con sus supuestos en `casos/profesora/LEEME.md` y sus evidencias en `resultados/profesora/`.
Las evidencias de cada caso (salida, traza y tiempos) están en `resultados/propios/` y `resultados/invalidos/`, con un `resumen.csv` por carpeta.

```
python ejecutar.py casos/propios   --salida resultados/propios
python ejecutar.py casos/invalidos --salida resultados/invalidos
```

## Casos válidos (`casos/propios/`)
| Caso | Qué comprueba | Esperado | Obtenido |
|---|---|---|---|
| `ejemplo_informe` | El ejemplo del formato (informe 6.5) y la selección del informe 6.3 | S = [1, 3], f(S) = 5 (Δ: 3, 2, 2 y luego 1, 2) | ✅ S = [1, 3], f(S) = 5; x₁ = 3, x₃ = 1 |
| `reparto_P_Q_informe` | El reparto del informe 6.4 (P: 9, 5, 2, 1; Q: 7, 6, 1, 0; B = 4) | P, Q, Q, P; utilidad 27 | ✅ x_P = 2, x_Q = 2; utilidad 27 |
| `contraejemplo_seleccion` | El voraz de la Parte 2 no es exacto | Voraz 5; el óptimo ({2, 3}) es 6 | ✅ S = [1, 2], f(S) = 5 |
| `borde_B_cero` | Presupuesto vacío | Nadie recibe unidades; utilidad 0 | ✅ |
| `borde_k_uno` | Se elige un solo nodo | El de mayor cobertura (nodo 2); recibe las 5 unidades | ✅ S = [2]; x₂ = 5 |
| `borde_k_N_menos_uno` | k en su valor máximo permitido (N − 1) | 3 nodos elegidos; k·N − k(k−1)/2 = 9 llamadas | ✅ S = [1, 3, 2], f(S) = 4 |
| `borde_nodo_sin_cobertura` | Un nodo que no cubre nada (aunque tenga la mejor utilidad) | Nunca se elige; S = [2, 3] | ✅ |
| `empates` | Desempate por el menor índice en las dos partes | S = [1, 2]; las unidades alternan 1, 2, 1, 2 | ✅ |
| `tope_activo` | El tope x_i ≤ c_i cambia el reparto: nodos log con a = 10 (tope 2) y a = 1, B = 5. El nodo 3 no cubre nada y nunca se elige; existe porque se exige k < N | S = [1, 2]; x = 2 y 3; 5 extracciones y 4 inserciones (sin el tope sería x = 5 y 0) | ✅ S = [1, 2], f(S) = 3; x₁ = 2, x₂ = 3; utilidad 12.372417; 5 extracciones y 4 inserciones |
| `sintetico_N020_k5` … `sintetico_N320_k5` | 5 tamaños crecientes de N (20, 40, 80, 160, 320), k = 5, B = 2N, semilla 1 | Todas las verificaciones en OK | ✅ (el tiempo mínimo (`minimo_*` de `resumen.csv`, el que se usa para T(n)) crece más o menos al doble cuando N se duplica; la mediana de una corrida se puede salir por una ráfaga de ruido: en la evidencia actual, N = 80 da 657 µs de mediana y 183 µs de mínimo, ver las decisiones 29 y 30) |

## Casos inválidos (`casos/invalidos/`): deben rechazarse sin ejecutar los algoritmos
| Caso | Qué comprueba | Esperado | Obtenido |
|---|---|---|---|
| `convexa_rechazada` | El contraejemplo convexo del informe 6.4 (P: 1, 10) | FALLA "no es cóncava" en el nodo 1 | ✅ |
| `k_igual_a_N` | Violación de k < N | FALLA "1 ≤ k < N" | ✅ |
| `ids_repetidos` | Dos nodos con el mismo id | FALLA "ids únicos" | ✅ |

## Caso oficial (`casos/profesora/`)
| Caso | Qué comprueba | Esperado | Obtenido |
|---|---|---|---|
| `entrada_G2_red_15_nodos` | El caso de la docente: N = 15, k = 5, B = 30, grafo completo de 105 aristas | S = N11, N14, N09, N15, N13; f(S) ≈ 145.5795; 65 llamadas; x = 5, 7, 7, 6, 5; U ≈ 88.5640; 30 extracciones y 30 inserciones | ✅ f(S) = 145.57952; U = 88.563953; Σ costos de S = 23 frente a 24 (informativo). El tope no cambia nada: todos los `presupuesto_total_nodo` valen 18 y el mayor x_i es 7 |

Todos se comprueban automáticamente en `pruebas/test_bateria.py`.
