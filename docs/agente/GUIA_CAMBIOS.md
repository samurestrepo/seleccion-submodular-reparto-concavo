# Guía de cambios rápidos (modo sustentación)

Recetas para los cambios que es probable que pidan en vivo. Cada receta dice dónde tocar, qué pasa con la complejidad y qué prueba correr.
_Las rutas exactas de las líneas se completan cuando exista el código._

| Cambio pedido | Dónde | Efecto en la complejidad | Verificar |
|---|---|---|---|
| Desempatar por el mayor índice | `seleccion.py` (la comparación) y `reparto.py` (la clave del montículo) | Ninguno | Pruebas de desempate |
| Mostrar cuántas llamadas a f se hicieron | Contador en `cobertura.py`, impreso en la traza | Ninguno; confirma Θ(N·k) en la práctica | Debe dar k·N − k(k−1)/2 |
| Contar las operaciones del montículo | Contador en `reparto.py` | Ninguno | ≈ B veces el costo de extraer e insertar |
| Nueva familia de utilidad (por ejemplo, a·x/(1+x)) | `utilidades.py` | Ninguno si Δ sigue siendo O(1) | Verificar que sea creciente y cóncava |
| Utilidad convexa (para mostrar que el voraz falla) | `utilidades.py` + caso en `casos/propios/` | — | Contraejemplo convexo del informe |
| Restricción "≤ B" en vez de "= B" con Δ negativas | `reparto.py`: parar cuando la mayor Δ sea < 0 | Ninguno | Caso con Δ negativas |
| Tope de presupuesto por nodo (x_i ≤ c_i) | `reparto.py`: no reinsertar el nodo que llega a su tope | Ninguno | Caso con topes |
| Variante (a): costos de participación con presupuesto | `seleccion.py`: elegir por Δ/costo; nueva restricción | Cambia la cota: ya no es 1 − 1/e (cobertura con presupuesto) | Pendiente de diseño |
| Cambiar el formato de entrada | Solo `entrada.py` | Ninguno | Pruebas de `entrada.py` |
