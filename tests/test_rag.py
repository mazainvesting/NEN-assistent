from io import BytesIO
from types import SimpleNamespace
import numpy as np
import pytest
from pypdf import PdfWriter
from rag import Chunk, extract_chunks, embed, retrieve, citations_valid


class FakeClient:
    def __init__(self):
        self.embeddings = self

    def create(self, model, input, **kwargs):
        return SimpleNamespace(data=[
            SimpleNamespace(index=i, embedding=[1., 0.] if "veilig" in text else [0., 1.])
            for i, text in enumerate(input)
        ])


def test_invalid_and_scanned_pdf():
    with pytest.raises(ValueError, match="herkenbaar"):
        extract_chunks([("x.pdf", b"not pdf")])
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    data = BytesIO()
    writer.write(data)
    with pytest.raises(ValueError, match="leesbare tekst"):
        extract_chunks([("scan.pdf", data.getvalue())])


def test_pdf_metadata_and_chunks():
    from reportlab.pdfgen.canvas import Canvas
    data = BytesIO()
    canvas = Canvas(data)
    canvas.drawString(30, 700, "Dit is een eigen oefentekst over veilig leren.")
    canvas.showPage()
    canvas.drawString(30, 700, "Een tweede pagina met uitleg.")
    canvas.save()
    chunks, warnings = extract_chunks([("les.pdf", data.getvalue())])
    assert {c.page for c in chunks} == {1, 2}
    assert all(c.source == "les.pdf" for c in chunks)
    assert not warnings


def test_retrieval_and_abstention():
    client = FakeClient()
    chunks = [Chunk("a.pdf", 1, "veilig"), Chunk("b.pdf", 2, "anders")]
    matrix = embed(client, [c.text for c in chunks], "test")
    hits = retrieve(client, "veilig", chunks, matrix, "test")
    assert len(hits) == 1 and hits[0][0].source == "a.pdf"
    assert retrieve(client, "veilig", chunks, np.array([[0., 1.], [0., 1.]]), "test") == []


def test_citation_guard():
    assert citations_valid("Uitleg [B1].", 2)
    assert not citations_valid("Uitleg [B3].", 2)
    assert not citations_valid("Geen bron", 2)
