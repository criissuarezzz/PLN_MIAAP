# Hito 1 — Guía de supervivencia del veinteañero

## Colección, fragmentación y baselines

La colección contiene **1.409 documentos**, correspondientes a artículos y disposiciones de 11 normas del BOE. Cada artículo o disposición tiene un `doc_id` propio y es la unidad que se considera relevante en la evaluación.

La **unidad de indexación es el fragmento**. Los documentos de hasta 300 palabras se conservan completos. Los más largos se dividen en ventanas de 300 palabras con un solapamiento de 45 palabras (15 %). El último fragmento puede ser más corto. El resultado son **2.757 fragmentos**, cada uno con su propio `chunk_id` y el `doc_id` del documento de origen.

Comparamos **TF-IDF con similitud coseno** (scikit-learn) y una implementación propia de **Okapi BM25** en Python, con `k1 = 1.5` y `b = 0.75`. Aplicamos el mismo preprocesado a los fragmentos y a las consultas: lematización con spaCy, filtrado por categoría gramatical, eliminación de palabras vacías y filtrado por frecuencia documental. Calculamos el IDF de ambos métodos y la longitud media de BM25 sobre los fragmentos, no sobre los documentos completos.

## Consultas de prueba y evaluación

Seleccionamos al azar **50 fragmentos candidatos** con semilla 42. Pedimos a ChatGPT que redactara preguntas naturales para encontrar la información del fragmento sin copiar sus palabras ni expresiones distintivas. El conjunto final contiene **30 consultas de tipo *known-item***. Revisamos manualmente las 30 para comprobar que eran concretas, que el fragmento permitía responderlas y que no reproducían expresiones distintivas. Reformulamos 11 de ellas. El detalle se recoge en [REVISION_CONSULTAS.md](REVISION_CONSULTAS.md).

Cada línea de [`data/queries.jsonl`](data/queries.jsonl) contiene `qid`, `query`, `relevant_ids` (el documento de origen) y `source_chunk` (el fragmento de origen).

La evaluación principal se realiza **a nivel de documento**. Primero recuperamos fragmentos y los ordenamos por puntuación. Después asignamos a cada documento la puntuación de su mejor fragmento y eliminamos los documentos repetidos **antes de aplicar el corte en K**. Sobre esa lista calculamos Recall@5, Recall@10 y MRR.

## Resultados y análisis de errores

| Método | Recall@5 | Recall@10 | MRR |
|---|---:|---:|---:|
| TF-IDF + coseno | 0,4667 | 0,6333 | 0,2919 |
| BM25 | 0,5333 | 0,6000 | 0,3605 |

BM25 obtiene un mayor Recall@5 y MRR, mientras que TF-IDF recupera el documento relevante en una consulta más en el top 10 (19 frente a 18 de 30). Con 30 consultas, estas diferencias no bastan para afirmar que un método sea mejor en general.

Ambos métodos fallan en nueve consultas en el top 10. Un problema recurrente es la diferencia entre el vocabulario cotidiano y el jurídico. Por ejemplo, una consulta usa «embajada», mientras que el fragmento relevante dice «misiones diplomáticas». También se recuperan artículos cercanos o con contenido parecido que no cuentan como acierto porque la evaluación etiqueta como relevante únicamente el documento de origen. La ejecución y el análisis detallado están en [hito_1.ipynb](hito_1.ipynb).

## Siguiente paso

En el Hito 2 probaremos la recuperación densa con embeddings para comprobar si mejora en las consultas que usan sinónimos o paráfrasis. Mantendremos la misma colección, los mismos fragmentos, las mismas consultas y el mismo protocolo de evaluación para comparar los resultados con los baselines.

## Uso de IA generativa

Utilizamos ChatGPT para generar el borrador inicial de las consultas, como apoyo para revisar y mejorar el código del notebook y para redactar este resumen. Revisamos manualmente las 30 consultas finales y reformulamos 11. El notebook utiliza las consultas guardadas y no llama a un LLM para ejecutar los baselines ni calcular las métricas.