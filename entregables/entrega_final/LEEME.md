# Entrega final

Versión: etiqueta `entrega-final` del repositorio <https://github.com/samurestrepo/seleccion-submodular-reparto-concavo>.

| Archivo | Qué es |
|---|---|
| `1_Informe_final_G2.pdf` | El informe final (87 páginas): formalización de las Partes 1 y 2 y de las variantes (a), (b) y (c), NP-dureza, algoritmos exactos y aproximados con su eficiencia, el caso de la docente, la validación experimental (sección 11), el resumen de eficiencia y los supuestos y limitaciones (sección 13) |
| `2_Manual_Tecnico_G2.pdf` | El manual técnico, en PDF (17 páginas) |
| `secciones/` | Borradores en Markdown de las secciones nuevas del informe, previos a la auditoría final. No son el texto entregado |

**El texto final es el PDF del informe.** Los archivos de `secciones/` son los borradores con que se armó en Google Docs, antes de la auditoría final; donde difieran, manda el PDF.

La fuente del manual es `MANUAL_TECNICO.md`, en la raíz del repositorio (https://github.com/samurestrepo/seleccion-submodular-reparto-concavo/blob/entrega-final/MANUAL_TECNICO.md, en la etiqueta `entrega-final`). El manual en PDF se obtiene importando `MANUAL_TECNICO.md` en Google Docs y exportándolo a PDF.

Para reproducir, ver el manual: la sección 4 (ejecución paso a paso, con el caso de la docente y sus variantes), la sección 8 (experimentos de tiempo), la sección 9 (variantes) y la sección 10 (tablas de la cota). El caso de la docente de la solución base sigue siendo `python ejecutar.py casos/profesora --salida resultados/profesora` (ver `README.md`); la prueba fuera de muestra de la serie d (informe, sección 11.3) se reproduce con `python scripts/serie_d_fuera_de_muestra.py`.
