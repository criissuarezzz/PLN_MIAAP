"""
Descarga y prepara el corpus del chatbot "Guía de supervivencia del veinteañero".

Ejecutar UNA vez (descarga offline, como exige el proyecto):
    pip install requests beautifulsoup4 lxml pymupdf
    python descargar_corpus.py

Salida:
    data/raw/...           copias originales (XML, HTML, PDF)
    data/corpus.jsonl      un documento por línea (artículo de ley o sección de guía)

Formato de cada línea de corpus.jsonl:
    {"doc_id", "tema", "fuente", "titulo", "seccion", "url", "fecha_descarga", "texto"}
"""

import json
import re
import sys
import time
from datetime import date
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# ----------------------------------------------------------------------------
# 1. FUENTES
# ----------------------------------------------------------------------------

# Legislación consolidada del BOE (API oficial de datos abiertos).
# Cada artículo/disposición se guarda como un documento.
BOE_NORMAS = [
    # Primer trabajo y prácticas
    {"id": "BOE-A-2015-11430", "tema": "trabajo",
     "titulo": "Estatuto de los Trabajadores (RDL 2/2015)"},
    {"id": "BOE-A-2014-8138", "tema": "trabajo",
     "titulo": "Prácticas académicas externas universitarias (RD 592/2014)"},
    # Entender la nómina y primera declaración de la renta
    {"id": "BOE-A-2006-20764", "tema": "renta",
     "titulo": "Ley del IRPF (Ley 35/2006)"},
    {"id": "BOE-A-2007-6820", "tema": "nomina",
     "titulo": "Reglamento del IRPF, retenciones (RD 439/2007)"},
    # Becas
    {"id": "BOE-A-2008-821", "tema": "becas",
     "titulo": "Régimen de becas y ayudas al estudio (RD 1721/2007)"},
    # Transporte y ocio
    {"id": "BOE-A-2026-10885", "tema": "ocio",
     "titulo": "Bono Cultural Joven (RD 401/2026)"},
    # Compras online y suscripciones
    {"id": "BOE-A-2007-20555", "tema": "consumo",
     "titulo": "Ley General para la Defensa de los Consumidores (RDL 1/2007)"},
    {"id": "BOE-A-2002-13758", "tema": "consumo",
     "titulo": "Ley de Servicios de la Sociedad de la Información y Comercio Electrónico (Ley 34/2002)"},
    # Carnet de conducir
    {"id": "BOE-A-2015-11722", "tema": "conducir",
     "titulo": "Ley de Tráfico y Seguridad Vial (RDL 6/2015)"},
    {"id": "BOE-A-2003-23514", "tema": "conducir",
     "titulo": "Reglamento General de Circulación (RD 1428/2003)"},
    {"id": "BOE-A-2009-9481", "tema": "conducir",
     "titulo": "Reglamento General de Conductores (RD 818/2009)"},
]

# Documentos del BOE que NO son legislación consolidada (convocatorias, órdenes...).
# Busca el identificador en boe.es (formato BOE-A-AAAA-NNNNN) y añádelo aquí.
BOE_DIARIO = [
    # {"id": "BOE-A-2026-XXXXX", "tema": "becas",
    #  "titulo": "Convocatoria de becas generales curso 2026-2027"},
]

# Reglamentos europeos (EUR-Lex, versión en español). Un documento por artículo.
EURLEX = [
    {"celex": "32004R0261", "tema": "viajes",
     "titulo": "Reglamento (CE) 261/2004, derechos de pasajeros aéreos"},
    {"celex": "32021R0782", "tema": "viajes",
     "titulo": "Reglamento (UE) 2021/782, derechos de viajeros de ferrocarril"},
    {"celex": "32011R0181", "tema": "viajes",
     "titulo": "Reglamento (UE) 181/2011, derechos de viajeros de autobús"},
]

# Guías en PDF o HTML con URL directa. Rellenad las que encontréis (ver README).
WEB = [
    # {"url": "https://.../manual-renta.pdf", "tema": "renta",
    #  "titulo": "Manual práctico de Renta (AEAT)"},
]

# Carpeta para documentos descargados a mano: data/manual/<tema>/<archivo>.pdf|html|txt
MANUAL_DIR = Path("data/manual")

# ----------------------------------------------------------------------------
# 2. CONFIGURACIÓN
# ----------------------------------------------------------------------------

RAW_DIR = Path("data/raw")
CORPUS_PATH = Path("data/corpus.jsonl")
PAUSA = 1.0                # segundos entre peticiones, para no saturar los servidores
PALABRAS_POR_SECCION = 400  # tamaño aproximado de cada documento al trocear guías
MIN_PALABRAS = 15           # descarta bloques vacíos o "(Derogado)"

HEADERS = {"User-Agent": "UC3M-NLP-course-project/1.0 (uso académico)"}
HOY = date.today().isoformat()


# ----------------------------------------------------------------------------
# 3. UTILIDADES
# ----------------------------------------------------------------------------

def limpiar(texto: str) -> str:
    texto = texto.replace("\xa0", " ")
    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r"\n\s*\n+", "\n\n", texto)
    return texto.strip()


def n_palabras(texto: str) -> int:
    return len(texto.split())


def descargar(url: str, destino: Path, accept: str | None = None) -> bytes | None:
    """Descarga con caché: si el archivo ya existe en data/raw, no vuelve a pedirlo."""
    if destino.exists():
        return destino.read_bytes()
    headers = dict(HEADERS)
    if accept:
        headers["Accept"] = accept
    try:
        r = requests.get(url, headers=headers, timeout=60)
        r.raise_for_status()
    except requests.RequestException as e:
        print(f"  [ERROR] {url}: {e}", file=sys.stderr)
        return None
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(r.content)
    time.sleep(PAUSA)
    return r.content


def trocear(texto: str, max_palabras: int = PALABRAS_POR_SECCION) -> list[str]:
    """Agrupa párrafos hasta ~max_palabras. Sin cortar párrafos por la mitad."""
    parrafos = [p.strip() for p in re.split(r"\n\s*\n|\n", texto) if p.strip()]
    trozos, actual, cuenta = [], [], 0
    for p in parrafos:
        w = n_palabras(p)
        if actual and cuenta + w > max_palabras:
            trozos.append("\n".join(actual))
            actual, cuenta = [], 0
        actual.append(p)
        cuenta += w
    if actual:
        trozos.append("\n".join(actual))
    return trozos


def doc(doc_id, tema, fuente, titulo, seccion, url, texto) -> dict:
    return {
        "doc_id": doc_id, "tema": tema, "fuente": fuente, "titulo": titulo,
        "seccion": seccion, "url": url, "fecha_descarga": HOY, "texto": texto,
    }


# ----------------------------------------------------------------------------
# 4. PARSERS
# ----------------------------------------------------------------------------

def parse_boe_consolidado(xml: bytes, norma: dict) -> list[dict]:
    """
    Estructura de /texto: response > data > texto > bloque(id, tipo, titulo) > version > p
    Nos quedamos con la ÚLTIMA versión de cada bloque (texto vigente).
    """
    soup = BeautifulSoup(xml, "lxml-xml")
    docs = []
    for bloque in soup.find_all("bloque"):
        if bloque.get("tipo") != "precepto":   # artículos, disposiciones y anexos
            continue
        versiones = bloque.find_all("version")
        if not versiones:
            continue
        ultima = versiones[-1]
        texto = limpiar("\n".join(p.get_text(" ", strip=True)
                                  for p in ultima.find_all(["p", "blockquote"])))
        if n_palabras(texto) < MIN_PALABRAS:
            continue
        bid = bloque.get("id")
        docs.append(doc(
            doc_id=f"{norma['id']}_{bid}",
            tema=norma["tema"], fuente="BOE", titulo=norma["titulo"],
            seccion=bloque.get("titulo", bid),
            url=f"https://www.boe.es/buscar/act.php?id={norma['id']}#{bid}",
            texto=texto,
        ))
    return docs


def parse_boe_diario(xml: bytes, item: dict) -> list[dict]:
    soup = BeautifulSoup(xml, "lxml-xml")
    nodo = soup.find("texto")
    if nodo is None:
        return []
    texto = limpiar("\n".join(p.get_text(" ", strip=True) for p in nodo.find_all("p")))
    url = f"https://www.boe.es/diario_boe/txt.php?id={item['id']}"
    return [doc(f"{item['id']}_s{i:03d}", item["tema"], "BOE", item["titulo"],
                f"Sección {i}", url, t)
            for i, t in enumerate(trocear(texto), 1)]


ART_RE = re.compile(r"^\s*Artículo\s+(\d+\s*(?:bis|ter)?)\s*$", re.IGNORECASE)


def parse_eurlex(html: bytes, item: dict) -> list[dict]:
    """Divide el texto del reglamento por líneas 'Artículo N'. Descarta los considerandos."""
    soup = BeautifulSoup(html, "lxml")
    for t in soup(["script", "style", "nav", "header", "footer"]):
        t.decompose()
    lineas = [l.strip() for l in soup.get_text("\n").split("\n") if l.strip()]
    url = f"https://eur-lex.europa.eu/legal-content/ES/TXT/?uri=CELEX:{item['celex']}"
    docs, art, buffer = [], None, []

    def cerrar():
        texto = limpiar("\n".join(buffer))
        if art and n_palabras(texto) >= MIN_PALABRAS:
            docs.append(doc(f"EU-{item['celex']}_art{art.replace(' ', '')}",
                            item["tema"], "EUR-Lex", item["titulo"],
                            f"Artículo {art}", url, texto))

    for linea in lineas:
        m = ART_RE.match(linea)
        if m:
            cerrar()
            art, buffer = m.group(1), [linea]
        elif art:
            buffer.append(linea)
    cerrar()
    return docs


def texto_de_archivo(ruta: Path) -> str:
    suf = ruta.suffix.lower()
    if suf == ".pdf":
        import fitz  # pymupdf
        with fitz.open(ruta) as pdf:
            return limpiar("\n".join(pagina.get_text() for pagina in pdf))
    if suf in (".html", ".htm"):
        soup = BeautifulSoup(ruta.read_bytes(), "lxml")
        for t in soup(["script", "style", "nav", "header", "footer", "aside"]):
            t.decompose()
        return limpiar(soup.get_text("\n"))
    return limpiar(ruta.read_text(encoding="utf-8", errors="ignore"))


def docs_de_guia(ruta: Path, tema: str, titulo: str, url: str, prefijo: str) -> list[dict]:
    texto = texto_de_archivo(ruta)
    if n_palabras(texto) < MIN_PALABRAS:
        print(f"  [AVISO] {ruta.name} sin texto extraíble (¿PDF escaneado?)", file=sys.stderr)
        return []
    return [doc(f"{prefijo}_s{i:03d}", tema, "guía", titulo, f"Sección {i}", url, t)
            for i, t in enumerate(trocear(texto), 1)]


# ----------------------------------------------------------------------------
# 5. PIPELINE
# ----------------------------------------------------------------------------

def slug(texto: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", texto.lower()).strip("-")[:60]


def main():
    corpus: list[dict] = []

    print("BOE, legislación consolidada")
    for norma in BOE_NORMAS:
        url = f"https://www.boe.es/datosabiertos/api/legislacion-consolidada/id/{norma['id']}/texto"
        xml = descargar(url, RAW_DIR / "boe" / f"{norma['id']}.xml", accept="application/xml")
        if xml:
            docs = parse_boe_consolidado(xml, norma)
            print(f"  {norma['id']}: {len(docs)} artículos")
            corpus += docs

    print("BOE, diario")
    for item in BOE_DIARIO:
        url = f"https://www.boe.es/diario_boe/xml.php?id={item['id']}"
        xml = descargar(url, RAW_DIR / "boe_diario" / f"{item['id']}.xml")
        if xml:
            docs = parse_boe_diario(xml, item)
            print(f"  {item['id']}: {len(docs)} secciones")
            corpus += docs

    print("EUR-Lex")
    for item in EURLEX:
        url = f"https://eur-lex.europa.eu/legal-content/ES/TXT/HTML/?uri=CELEX:{item['celex']}"
        html = descargar(url, RAW_DIR / "eurlex" / f"{item['celex']}.html")
        if html:
            docs = parse_eurlex(html, item)
            print(f"  {item['celex']}: {len(docs)} artículos")
            if not docs:
                print("  [AVISO] 0 artículos: EUR-Lex puede haber devuelto una página de "
                      "verificación. Descarga el HTML a mano en data/manual/viajes/",
                      file=sys.stderr)
            corpus += docs

    print("Guías web")
    for item in WEB:
        ext = ".pdf" if item["url"].lower().endswith(".pdf") else ".html"
        ruta = RAW_DIR / "web" / f"{slug(item['titulo'])}{ext}"
        if descargar(item["url"], ruta):
            docs = docs_de_guia(ruta, item["tema"], item["titulo"], item["url"],
                                f"WEB-{slug(item['titulo'])}")
            print(f"  {item['titulo']}: {len(docs)} secciones")
            corpus += docs

    print("Documentos manuales")
    if MANUAL_DIR.exists():
        for ruta in sorted(MANUAL_DIR.glob("*/*")):
            if ruta.suffix.lower() not in (".pdf", ".html", ".htm", ".txt", ".md"):
                continue
            tema = ruta.parent.name
            docs = docs_de_guia(ruta, tema, ruta.stem, f"local:{ruta}",
                                f"MAN-{tema}-{slug(ruta.stem)}")
            print(f"  {tema}/{ruta.name}: {len(docs)} secciones")
            corpus += docs

    # IDs únicos (requisito para queries.jsonl del M1)
    ids = [d["doc_id"] for d in corpus]
    assert len(ids) == len(set(ids)), "Hay doc_id duplicados"

    CORPUS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CORPUS_PATH.open("w", encoding="utf-8") as f:
        for d in corpus:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")

    print(f"\nTotal: {len(corpus)} documentos en {CORPUS_PATH}")
    por_tema: dict[str, int] = {}
    for d in corpus:
        por_tema[d["tema"]] = por_tema.get(d["tema"], 0) + 1
    for tema, n in sorted(por_tema.items()):
        print(f"  {tema:10s} {n}")


if __name__ == "__main__":
    main()
