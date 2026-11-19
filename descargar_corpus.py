"""Reconstruye la colección del Hito 1 a partir de las 11 copias del BOE."""

import argparse
import json
from pathlib import Path

from lxml import etree

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

DATA = Path(__file__).resolve().parent / "data"
MIN_PALABRAS = 15
PALABRAS_POR_FRAGMENTO = 300
SOLAPAMIENTO = 45
# Fecha registrada en el corpus anterior para estas mismas copias.
FECHA_DESCARGA = "2026-11-13"


def leer_jsonl(ruta):
    with ruta.open(encoding="utf-8") as archivo:
        return [json.loads(linea) for linea in archivo if linea.strip()]


def guardar_jsonl(ruta, filas):
    temporal = ruta.with_suffix(".jsonl.tmp")
    with temporal.open("w", encoding="utf-8", newline="\n") as archivo:
        for fila in filas:
            archivo.write(json.dumps(fila, ensure_ascii=False) + "\n")
    temporal.replace(ruta)


def bloques_de_texto(nodo):
    """Recorre el XML en orden, conservando citas y celdas sin repetir sus párrafos."""
    if nodo.tag == "a" and "refPost" in nodo.get("class", "").split():
        return
    if {"nota_pie", "nota_pie_2"}.intersection(nodo.get("class", "").split()):
        return
    if nodo.text and nodo.text.strip():
        yield nodo.text.strip()
    for hijo in nodo:
        if isinstance(hijo.tag, str):
            yield from bloques_de_texto(hijo)
        if hijo.tail and hijo.tail.strip():
            yield hijo.tail.strip()


def extraer_texto(version):
    # Avisos del BOE detectados en las copias, a veces con redacciones previas.
    avisos_editoriales = ("téngase en cuenta", "atención: esta disposición", "se modifica por")
    lineas = []
    for bloque in version:
        if not isinstance(bloque.tag, str):
            continue
        texto = " ".join(" ".join(bloques_de_texto(bloque)).split())
        if bloque.tag == "blockquote" and texto.lower().startswith(avisos_editoriales):
            continue
        if texto:
            lineas.append(texto)
    return "\n".join(lineas)


def parse_boe_consolidado(xml, norma):
    raiz = etree.fromstring(xml, parser=etree.XMLParser(resolve_entities=False, no_network=True))
    bloques = raiz.findall("./data/texto/bloque")
    if not bloques:
        raise ValueError(f"{norma['id']}: XML sin bloques de legislación consolidada")
    documentos = []
    for bloque in bloques:
        if bloque.get("tipo") != "precepto":
            continue
        versiones = bloque.findall("version")
        if not versiones:
            continue
        texto = extraer_texto(versiones[-1])
        if len(texto.split()) < MIN_PALABRAS:
            continue
        bid = bloque.get("id")
        if not bid:
            raise ValueError(f"{norma['id']}: precepto sin identificador")
        documentos.append({
            "doc_id": f"{norma['id']}_{bid}",
            "tema": norma["tema"],
            "fuente": "BOE",
            "titulo": norma["titulo"],
            "seccion": bloque.get("titulo", bid),
            "url": f"https://www.boe.es/buscar/act.php?id={norma['id']}#{bid}",
            "fecha_descarga": FECHA_DESCARGA,
            "texto": texto,
        })
    if not documentos:
        raise ValueError(f"{norma['id']}: XML sin preceptos con texto utilizable")
    return documentos


def dividir_documento(documento):
    palabras = documento["texto"].split()
    paso = PALABRAS_POR_FRAGMENTO - SOLAPAMIENTO
    piezas = []
    for numero, inicio in enumerate(range(0, len(palabras), paso), start=1):
        fin = min(inicio + PALABRAS_POR_FRAGMENTO, len(palabras))
        piezas.append({
            "chunk_id": f"{documento['doc_id']}_c{numero:04d}",
            "doc_id": documento["doc_id"],
            "texto": " ".join(palabras[inicio:fin]),
            "inicio_palabra": inicio,
            "fin_palabra": fin,
        })
        if fin == len(palabras):
            break
    return piezas


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--comprobar", action="store_true",
                        help="Compara con los JSONL guardados sin modificarlos")
    args = parser.parse_args()

    documentos = []
    for norma in BOE_NORMAS:
        ruta = DATA / "raw" / "boe" / f"{norma['id']}.xml"
        xml = ruta.read_bytes()
        if not xml.strip():
            raise ValueError(f"Copia local vacía: {ruta}")
        extraidos = parse_boe_consolidado(xml, norma)
        print(f"{norma['id']}: {len(extraidos)} documentos")
        documentos.extend(extraidos)
    if len({d["doc_id"] for d in documentos}) != len(documentos):
        raise ValueError("Hay doc_id duplicados")
    fragmentos = [f for d in documentos for f in dividir_documento(d)]
    for nombre, filas in (("corpus.jsonl", documentos), ("chunks.jsonl", fragmentos)):
        ruta = DATA / nombre
        if args.comprobar:
            if leer_jsonl(ruta) != filas:
                raise ValueError(f"{nombre} difiere de la reconstrucción local")
        else:
            guardar_jsonl(ruta, filas)
        print(f"{nombre}: {len(filas)} registros")


if __name__ == "__main__":
    main()
