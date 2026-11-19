# Hito 1 · Guía de supervivencia del veinteañero

**Colección.** Reconstruimos 1.395 documentos a partir de 11 copias locales de legislación consolidada del BOE. Cada documento es un precepto, como un artículo o una disposición. Quitamos duplicaciones y notas editoriales, y conservamos las citas y el texto de las tablas. La unidad de indexación es el fragmento. Hay 2.315 fragmentos, con ventanas de hasta 300 palabras y 45 de solapamiento en documentos largos. Cada fragmento guarda sus dos IDs.

**Método.** Aplicamos a consultas y fragmentos la misma lematización con spaCy, el mismo filtrado gramatical y de palabras vacías, y un vocabulario obtenido solo de los fragmentos mediante frecuencia documental. Comparamos TF-IDF sublineal con coseno y BM25 Okapi de implementación propia, con IDF positiva de tipo Lucene, `k1=1.5` y `b=0.75`. Cada documento recibe la puntuación de su mejor fragmento. Se eliminan duplicados antes de medir Recall@K. MRR usa el ranking completo de documentos con puntuación positiva.

**Consultas.** Conservamos los 30 casos de una muestra histórica aleatoria de 50 fragmentos (semilla 42). El equipo dejó constancia de haber revisado 30 preguntas. Tras limpiar el corpus se comprobó que nueve fragmentos habían cambiado y conservaban el pasaje de respaldo, con un cambio de ID. Dos ajustes de redacción quedan pendientes de validación por el equipo. El historial y la evidencia están en [REVISION_CONSULTAS.md](REVISION_CONSULTAS.md).

| Método | Recall@5 | Recall@10 | MRR |
|---|---:|---:|---:|
| TF-IDF + coseno | 0,5667 | 0,6667 | 0,3459 |
| BM25 | 0,4667 | 0,6667 | 0,3608 |

**Resultados y siguiente paso.** Ambos métodos recuperan el documento etiquetado en 20 de 30 consultas en el top 10, y fallan conjuntamente en nueve. La pregunta sobre una embajada, por ejemplo, coincide poco con un fragmento que habla de «misiones diplomáticas». En la pregunta sobre alérgenos, ambos primeros resultados hablan de anualidades por alimentos. El [notebook](hito_1.ipynb) muestra la ejecución y el detalle. En el Hito 2 contrastaremos si los embeddings mejoran los casos de paráfrasis con la misma colección, fragmentos y protocolo.

**Uso de IA.** El equipo usó ChatGPT para los borradores de preguntas, el código y la redacción. El modelo exacto de generación y sus parámetros carecen de registro. Queda por validar con el profesor el alcance de la condición de pesos abiertos para esas preguntas. Codex ayudó a corregir la extracción, comprobar el respaldo, proponer dos ajustes y ejecutar y documentar la evaluación. Las métricas se obtienen con los baselines locales.
