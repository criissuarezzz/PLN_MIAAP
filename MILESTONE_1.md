# Hito 1 · Guía de supervivencia del veinteañero

Queríamos comprobar si una pregunta escrita con palabras cotidianas lleva al artículo o disposición que la responde. Partimos de 11 normas del BOE guardadas en el repositorio. Al limpiar los XML quitamos el texto duplicado y los avisos editoriales. Obtuvimos 1.395 documentos y 2.315 fragmentos. Dejamos enteros los textos de hasta 300 palabras y dividimos los más largos en ventanas de 300 con 45 palabras compartidas. Cada fragmento lleva su ID y el del documento al que pertenece.

Usamos spaCy para lematizar y filtrar los textos por categoría gramatical y palabras vacías. Aplicamos los mismos pasos a las preguntas y usamos el vocabulario que sale de los fragmentos tras el filtro de frecuencia. Comparamos TF-IDF sublineal con coseno y nuestra implementación de BM25 Okapi con IDF positiva de tipo Lucene (`k1=1.5`, `b=0.75`). Nos quedamos con el mejor fragmento de cada documento antes de contar los aciertos. Para MRR usamos todos los documentos con puntuación positiva.

Para la evaluación usamos 30 preguntas de una muestra aleatoria de 50 fragmentos (semilla 42). Pedimos que se redactaran en lenguaje cotidiano y evitando expresiones distintivas del BOE. Durante la preparación revisamos manualmente 30 preguntas para comprobar que fueran concretas y que el texto permitiera responderlas. El notebook comprueba la correspondencia entre las consultas evaluadas, los fragmentos y sus documentos de origen. Dejamos los criterios y ejemplos en [REVISION_CONSULTAS.md](REVISION_CONSULTAS.md).

| Método | Recall@5 | Recall@10 | MRR |
|---|---:|---:|---:|
| TF-IDF + coseno | 0,5667 | 0,6667 | 0,3459 |
| BM25 | 0,4667 | 0,6667 | 0,3608 |

TF-IDF encontró el documento esperado en 17 preguntas entre los cinco primeros resultados, frente a 14 de BM25. En el top 10 ambos acertaron 20 y fallaron juntos en nueve. En la pregunta sobre una embajada, por ejemplo, el texto usa «misiones diplomáticas». En otra, sobre alérgenos, los primeros resultados hablan de anualidades por alimentos. En el Hito 2 queremos probar si los embeddings ayudan en preguntas así. Usaremos la misma colección, los mismos fragmentos y el mismo protocolo.

**Uso de IA.** Usamos ChatGPT para preparar los borradores de las preguntas. También usamos un asistente de programación de OpenAI para revisar el código y la documentación. Las métricas las calculan TF-IDF y BM25 en el [notebook](hito_1.ipynb).
