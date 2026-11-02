# Catálogo de casos de prueba

Batería propia de la primera entrega. Los casos oficiales de la docente no se habían recibido al 2026-11-02; cuando lleguen van en `casos/profesora/`.
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
| `sintetico_N020_k5` … `sintetico_N320_k5` | 5 tamaños crecientes de N (20, 40, 80, 160, 320), k = 5, B = 2N, semilla 1 | Todas las verificaciones en OK | ✅ (el tiempo crece más o menos al doble cuando N se duplica) |

## Casos inválidos (`casos/invalidos/`): deben rechazarse sin ejecutar los algoritmos
| Caso | Qué comprueba | Esperado | Obtenido |
|---|---|---|---|
| `convexa_rechazada` | El contraejemplo convexo del informe 6.4 (P: 1, 10) | FALLA "no es cóncava" en el nodo 1 | ✅ |
| `k_igual_a_N` | Violación de k < N | FALLA "1 ≤ k < N" | ✅ |
| `ids_repetidos` | Dos nodos con el mismo id | FALLA "ids únicos" | ✅ |

Todos se comprueban automáticamente en `pruebas/test_bateria.py`.
