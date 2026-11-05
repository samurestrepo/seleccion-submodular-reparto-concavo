# seleccion-submodular-reparto-concavo

# Proyecto Red · Análisis y Diseño de Algoritmos 2026-2 — instrucciones para Claude

Este archivo se lee al abrir cualquier sesión sobre este repositorio.
Es la fuente de verdad sobre **cómo se trabaja aquí**. El estado del trabajo está en `docs/agente/`.

## 1. Antes de hacer cualquier cosa

0. `git pull` para traer lo último: GitHub es la única fuente de verdad.
1. Lee `docs/agente/BITACORA_TECNICA.md`: estado actual, último cambio y pendientes.
2. Lee `docs/agente/MAPA_DEL_CODIGO.md`: qué archivo hace qué y dónde está su documentación.
3. Si la tarea toca un módulo, lee su ficha en `docs/modulos/` **antes** de abrir el código.
4. Di en una línea en qué estado está el proyecto y qué vas a tocar. Después trabaja.

Para cualquier tarea de código usa el agente `ingeniero-red` (`.claude/agents/ingeniero-red.md`).

## 2. Qué es el proyecto (resumen)

Una red de N nodos entrena por rondas. En cada ronda:

- **Parte 2, selección:** elegir a lo sumo k nodos que maximicen una utilidad conjunta f, monótona y submodular. Es NP-difícil (reducción desde Cobertura Máxima). Se resuelve con un **voraz aproximado**: garantía ≥ (1 − 1/e) del óptimo y Θ(N·k) llamadas a f.
- **Parte 1, reparto:** repartir B unidades entre los nodos elegidos para maximizar Σ u_i(x_i), con u_i crecientes y cóncavas. Se resuelve con un **voraz óptimo con montículo**: O(N + B lg N).

El enunciado está en `docs/curso/enunciado_proyecto_final.md`; el informe, el manual en PDF y el anexo de cada entrega están en `entregables/`.
**Lo que importa es la eficiencia demostrada y explicada, no el volumen de código.**

## 3. Reglas no negociables

- **Python 3.11+, solo biblioteca estándar** para la lógica. `matplotlib` solo en la parte de gráficas.
- **Todo en español:** nombres de funciones, variables, comentarios y documentación (`seleccionar_nodos`, `repartir_presupuesto`).
- **Claridad antes que ingenio:** el código debe poder leerse y explicarse con su ficha al lado. Nada de trucos de una línea.
- **Fidelidad al informe:** cada algoritmo sigue el pseudocódigo del informe y lo cita con comentarios `# línea N del pseudocódigo`. Si el código se aparta del informe, se anota en `docs/agente/DECISIONES.md`.
- **Reproducible:** los casos entran por archivo, nunca escritos dentro del código. Los generadores usan semilla fija. Los empates se rompen por el menor índice.
- **Documentación:** cada archivo importante tiene su ficha en `docs/modulos/<archivo>.md`, con la plantilla de `docs/agente/PLANTILLA_FICHA.md`. **Un cambio de código sin actualizar su ficha está incompleto.**
- **Pruebas:** `python -m pytest` debe pasar antes de dar algo por terminado. Toda corrección de un error trae una prueba que lo reproduce.
- **Nada de dependencias, archivos ni carpetas nuevas** sin anotarlas en el MAPA.

## 4. Al terminar cualquier tarea

1. Actualiza la ficha de cada módulo tocado.
2. Agrega una entrada al registro de `docs/agente/BITACORA_TECNICA.md` (fecha, qué, por qué, archivos, pruebas).
3. Si tomaste una decisión de diseño, regístrala en `DECISIONES.md`.
4. Si un cambio introduce algo nuevo (una estructura, un costo, un supuesto), explícalo en la conversación en 3 o 4 líneas.
5. Con `python -m pytest` en verde y con permiso del autor, haz commit y `git push` a `main`. Lo que no está en GitHub no existe para otra sesión.

**Qué va dónde:** en este repo vive solo lo técnico: código, fichas, bitácora técnica y decisiones.

## 5. Uso de IA

El curso permite el uso de IA. En este proyecto se usa como apoyo en la parte operativa (código, pruebas, evidencias y documentación), con el agente `ingeniero-red`. El autor del proyecto revisa, entiende y responde por todo el contenido del repositorio.
