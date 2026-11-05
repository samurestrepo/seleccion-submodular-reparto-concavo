# Primera entrega

Versión: etiqueta `primera-entrega` del repositorio <https://github.com/samurestrepo/seleccion-submodular-reparto-concavo>.

| Archivo | Qué es |
|---|---|
| `1_Informe_Primera_Entrega_G2.pdf` | El informe: formalización, NP-dureza, algoritmos y su eficiencia, y el caso de la docente (sección 6.9) |
| `2_Manual_Tecnico_G2.pdf` | El manual técnico, en PDF |
| `3_Anexo_notas_de_trabajo_Samuel.pdf` | Anexo: notas de trabajo de Samuel. Es el original (21 MB, 13 páginas) |

El manual en PDF se genera de `MANUAL_TECNICO.md` de esta misma versión: se convierte a HTML con el paquete `markdown` (extensiones `tables` y `fenced_code`, más una hoja de estilo simple) y se imprime a PDF con Edge o Chrome en modo headless (`--print-to-pdf`). `markdown` se instala solo en el entorno de quien genera el PDF: **no es una dependencia del proyecto** y no está en `requirements-dev.txt`.

Para reproducir el caso de la docente: `python ejecutar.py casos/profesora --salida resultados/profesora` (ver `README.md`).
