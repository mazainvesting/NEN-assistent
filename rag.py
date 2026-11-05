"""PDF-extractie, LangChain-chunks en een kleine vectorindex in sessiegeheugen."""
from dataclasses import dataclass
from io import BytesIO
import json
import re

import numpy as np
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

MAX_FILES = 5
MAX_FILE_BYTES = 10 * 1024 * 1024
MAX_PAGES = 300
MAX_CHUNKS = 1500
MIN_SCORE = 0.30  # Heuristiek, geen zekerheidsscore; kalibreer met referentievragen.


@dataclass
class Chunk:
    source: str
    page: int
    text: str


def extract_chunks(files):
    if not files or len(files) > MAX_FILES:
        raise ValueError(f"Kies 1 tot {MAX_FILES} PDF-bestanden.")
    splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=200)
    chunks, warnings = [], []
    pages_total = 0
    for name, data in files:
        if len(data) > MAX_FILE_BYTES:
            raise ValueError(f"{name}: maximaal 10 MB per PDF.")
        if not data.startswith(b"%PDF-"):
            raise ValueError(f"{name}: dit is geen herkenbaar PDF-bestand.")
        try:
            reader = PdfReader(BytesIO(data))
            if reader.is_encrypted:
                raise ValueError("beveiligde PDF; gebruik een onbeveiligde versie")
            pages_total += len(reader.pages)
            if pages_total > MAX_PAGES:
                raise ValueError(f"maximaal {MAX_PAGES} pagina's in totaal")
            empty = 0
            for page_no, page in enumerate(reader.pages, 1):
                text = (page.extract_text() or "").strip()
                if not text:
                    empty += 1
                for part in splitter.split_text(text):
                    chunks.append(Chunk(name, page_no, part))
                    if len(chunks) > MAX_CHUNKS:
                        raise ValueError(f"maximaal {MAX_CHUNKS} tekststukken")
            if empty:
                warnings.append(f"{name}: {empty} pagina('s) zonder leesbare tekst; OCR is niet ingebouwd.")
        except ValueError:
            raise
        except Exception as exc:
            raise ValueError(f"{name}: PDF kon niet worden gelezen.") from exc
    if not chunks:
        raise ValueError("Geen leesbare tekst gevonden. Gebruik tekst-PDF's of voer eerst OCR uit.")
    return chunks, warnings


def embed(client, texts, model):
    vectors = []
    for offset in range(0, len(texts), 32):
        result = client.embeddings.create(
            model=model, input=texts[offset:offset + 32], encoding_format="float"
        )
        vectors.extend(item.embedding for item in sorted(result.data, key=lambda x: x.index))
    matrix = np.asarray(vectors, dtype=np.float32)
    return matrix / np.maximum(np.linalg.norm(matrix, axis=1, keepdims=True), 1e-12)


def retrieve(client, query, chunks, matrix, model, top_k=5):
    vector = embed(client, [query], model)[0]
    scores = matrix @ vector
    indices = np.argsort(scores)[::-1][:top_k]
    return [(chunks[int(i)], float(scores[i])) for i in indices if scores[i] >= MIN_SCORE]


def context_json(hits):
    return json.dumps([
        {"id": f"B{i}", "document": chunk.source, "pdf_page": chunk.page,
         "passage": chunk.text}
        for i, (chunk, _) in enumerate(hits, 1)
    ], ensure_ascii=False)


def citations_valid(answer, count):
    ids = re.findall(r"\[B(\d+)\]", answer)
    return bool(ids) and all(1 <= int(i) <= count for i in ids)
