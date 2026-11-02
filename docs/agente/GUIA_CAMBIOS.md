# Guía de cambios rápidos (modo sustentación)

Recetas para los cambios que es probable que pidan en vivo. Cada receta dice dónde tocar, qué pasa con la complejidad y qué prueba correr.
Los números de línea son los del 2026-11-02; si el archivo cambia, buscar el comentario `# línea N del pseudocódigo`.

| Cambio pedido | Dónde | Efecto en la complejidad | Verificar |
|---|---|---|---|
| Desempatar por el mayor índice | `seleccion.py` línea 34: `>` por `>=`. `reparto.py` líneas 42 y 53: guardar `(-ganancia, -i)`, y en la 48 deshacer el signo de i | Ninguno | `test_empate_gana_el_menor_indice` (cambiar lo esperado) |
| Mostrar cuántas llamadas a f se hicieron | Ya está: `llamadas_ganancia` en `salida.json`, en la traza y verificado contra la fórmula | Ninguno; confirma Θ(N·k) | Debe dar k·N − k(k−1)/2 |
| Contar las operaciones del montículo | Ya está: `extracciones` e `inserciones` en `reparto.py` | Ninguno | Deben valer B |
| Nueva familia de utilidad (por ejemplo, a·x/(1+x)) | `utilidades.py`: clase nueva + un `if` en `crear_utilidad` | Ninguno si Δ sigue siendo O(1) | Prueba de creciente y cóncava |
| Utilidad convexa (para mostrar que el voraz falla) | Usar `{"tipo": "tabla", "ganancias": [1, 10]}`; la verificación de entrada la marca como no cóncava | — | `test_contraejemplo_convexo` |
| Restricción "≤ B" en vez de "= B" con Δ negativas | `reparto.py`: justo después de la línea 50, `if delta < 0: break`; `verificacion.py`: `suma <= B` | Ninguno (a lo sumo B vueltas) | Caso con Δ negativas |
| Tope de presupuesto por nodo (x_i ≤ c_i) | `reparto.py` línea 53: no reinsertar si x[i] llegó a c_i; parar si H queda vacío | Ninguno | Caso con topes |
| Variante (a): costos de participación con presupuesto | `seleccion.py`: elegir por Δ/costo; nueva restricción | Cambia la cota: ya no es 1 − 1/e (cobertura con presupuesto) | Pendiente de diseño |
| Cambiar el formato de entrada | Solo `entrada.py` (`instancia_desde_diccionario`) | Ninguno | Pruebas de `entrada.py` |
| Medir varias veces y tomar el mínimo | `ronda.py`, bloque "1. Ejecución medida" dentro de un ciclo | Ninguno | `test_ronda.py` |
