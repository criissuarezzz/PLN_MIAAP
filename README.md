# Guía de supervivencia del veinteañero

Hito 1 de Procesamiento del Lenguaje Natural (UC3M). El proyecto compara dos
buscadores léxicos sobre una colección normativa. Cada resultado de la evaluación
corresponde a un documento del corpus.

## Reproducir la ejecución

Usa Python 3.13.9, la versión con la que se comprobó el proyecto. Desde la raíz
del repositorio, en PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest test_corpus
.\.venv\Scripts\python.exe descargar_corpus.py --comprobar
$env:JUPYTER_PATH = Join-Path $PWD '.venv/share/jupyter'
$env:JUPYTER_RUNTIME_DIR = Join-Path $PWD '.venv'
.\.venv\Scripts\python.exe -m ipykernel install --sys-prefix --name hito1
.\.venv\Scripts\python.exe -m nbconvert --to notebook --execute --inplace --ExecutePreprocessor.kernel_name=hito1 --ExecutePreprocessor.timeout=300 hito_1.ipynb
```

En Windows, si el comando `python` no encuentra tu instalación, usa la ruta de tu
intérprete o `py -3.13` para crear el entorno. En macOS y Linux sustituye
`.venv/Scripts/python.exe` por `.venv/bin/python` y define
`export JUPYTER_PATH="$PWD/.venv/share/jupyter"`. El primer paso de instalación
descarga el modelo español `es_core_news_sm 3.8.0` para spaCy 3.8.11.
La reconstrucción y la evaluación usan los archivos locales.

## Colección congelada

- `data/raw/boe/` contiene las 11 copias de legislación consolidada. La fecha
  de descarga registrada por el proyecto original es el **13 de noviembre de 2026**.
  La reconstrucción de este hito se realizó el **19 de noviembre de 2026** a partir
  de esas copias.
- `descargar_corpus.py` toma la última versión disponible de cada precepto en la
  copia local. Extrae párrafos, citas y celdas en orden, una sola vez. Excluye las
  clases editoriales `nota_pie` y `nota_pie_2`, las referencias `refPost` y los
  avisos editoriales identificados dentro de citas. Conserva el texto de las tablas
  en orden de lectura y las citas que forman parte del precepto. La extracción
  aplana el formato de las tablas y se limita al texto del XML.
- `data/corpus.jsonl` contiene **1.395 documentos**. Un documento es un
  precepto de al menos 15 palabras de texto extraído, como un artículo, una
  disposición o un anexo. Solo se incluyen las normas BOE de la lista del script.
  Los tres archivos de EUR-Lex estaban vacíos y se retiraron.
- `data/chunks.jsonl` contiene **2.315 fragmentos** y es el índice de referencia
  para el Hito 2. Los documentos de hasta 300 palabras quedan completos. Los
  largos se cortan en ventanas de 300, con 45 de solapamiento (15 %) y una última
  ventana que puede ser más corta. Cada fragmento guarda ambos IDs y los límites
  de palabra, con inicio inclusivo y fin exclusivo.
- `python descargar_corpus.py` vuelve a escribir los dos JSONL de corpus y
  fragmentos a partir de los XML. Usa `--comprobar` para contrastar el contenido
  guardado con el reconstruido. Una copia ausente, vacía o inválida detiene el
  proceso. Los XML quedan fuera de la ruta de escritura.

## Consultas y evaluación

- `data/muestra_consultas.jsonl` conserva el muestreo histórico de 50 fragmentos
  con semilla 42. `data/respuestas_llm.jsonl` conserva las preguntas revisadas
  históricas. `data/queries.jsonl` contiene las 30 preguntas evaluadas y los
  fragmentos de referencia actuales. La [revisión](REVISION_CONSULTAS.md) explica
  los cambios, su respaldo y la procedencia declarada de ChatGPT.
- [hito_1.ipynb](hito_1.ipynb) aplica el mismo preprocesado a consultas y
  fragmentos. Aprende el vocabulario únicamente de los fragmentos, con
  `min_df=2` y `max_df=0.95`. Conserva negaciones, números y unidades de plazo
  como excepciones al filtrado gramatical y de palabras vacías.
- TF-IDF usa frecuencia sublineal, IDF suavizada y coseno. BM25 usa
  normalización Okapi, IDF positiva de tipo Lucene, `k1=1.5` y `b=0.75`.
  Ambos estiman IDF por fragmento. BM25 calcula su longitud media con los
  tokens que superan el filtrado.
- El documento toma la puntuación de su mejor fragmento antes del corte K.
  Se desempata por `chunk_id` y se recuperan resultados de puntuación positiva.
  Recall@5, Recall@10 y MRR se calculan sobre documentos únicos. MRR usa el ranking
  positivo completo. La tasa de acierto del fragmento se muestra aparte.
- [MILESTONE_1.md](MILESTONE_1.md) resume el trabajo y las métricas. El
  notebook conserva las salidas y el análisis de fallos compartidos.
