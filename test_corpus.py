"""Comprobaciones de regresión sobre la extracción del BOE."""

import unittest

from lxml import etree

from descargar_corpus import (
    BOE_NORMAS, DATA, dividir_documento, extraer_texto, parse_boe_consolidado,
)


class ExtraccionBOE(unittest.TestCase):
    def test_cita_y_tabla_sin_duplicados(self):
        version = etree.fromstring("""
            <version>
              <p>Artículo de ejemplo.</p>
              <blockquote>
                <p>Texto de la cita.</p>
                <p class="nota_pie">Nota editorial.</p>
                <p class="nota_pie_2"><a class="refPost">Referencia.</a></p>
              </blockquote>
              <blockquote><p>Téngase en cuenta esta actualización.</p></blockquote>
              <table><tr><th>Cabecera</th><td><p>Celda.</p></td></tr></table>
            </version>
        """.encode("utf-8"))
        self.assertEqual(
            extraer_texto(version),
            "Artículo de ejemplo.\nTexto de la cita.\nCabecera Celda.",
        )

    def test_rechaza_xml_sin_corpus(self):
        for contenido in (b"", b"<html/>", b"<response><data><texto/></data></response>"):
            with self.subTest(contenido=contenido):
                with self.assertRaises((ValueError, etree.XMLSyntaxError)):
                    parse_boe_consolidado(contenido, BOE_NORMAS[0])

    def test_ejemplos_del_boe(self):
        ejemplos = {
            "BOE-A-2009-9481": ("a4", "Clase de permiso", "Se consideran combustibles alternativos"),
            "BOE-A-2006-20764": (
                "dtvigesimatercera", "31 de agosto de 2012", "en su redacción vigente a 1 de enero de 2012",
            ),
            "BOE-A-2003-23514": ("a12", "Normas relativas a ciclomotores y motocicletas",),
            "BOE-A-2015-11430": ("a37", "imposibilidad de acceder al centro de trabajo",),
        }
        for norma in BOE_NORMAS:
            id_norma = norma["id"]
            if id_norma not in ejemplos:
                continue
            with self.subTest(norma=id_norma):
                id_bloque, *evidencias = ejemplos[id_norma]
                copia = DATA / "raw" / "boe" / f"{id_norma}.xml"
                documentos = parse_boe_consolidado(copia.read_bytes(), norma)
                doc = next(d for d in documentos if d["doc_id"] == f"{id_norma}_{id_bloque}")
                for evidencia in evidencias:
                    self.assertEqual(doc["texto"].count(evidencia), 1)
                for aviso in ("Ref. BOE-A-", "Téngase en cuenta", "Redacción anterior:"):
                    self.assertNotIn(aviso, doc["texto"])
                if id_bloque == "a37":
                    fragmentos = dividir_documento(doc)
                    self.assertGreater(len(fragmentos), 1)
                    for anterior, siguiente in zip(fragmentos, fragmentos[1:]):
                        self.assertEqual(anterior["fin_palabra"] - siguiente["inicio_palabra"], 45)
                        self.assertEqual(anterior["texto"].split()[-45:], siguiente["texto"].split()[:45])
