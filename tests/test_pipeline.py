"""Testes rápidos: leitura dos 8 formatos e pipeline RAG com um cliente falso (não usa a OCI)."""
import hashlib
from types import SimpleNamespace

import numpy as np
import pytest

from src import config, rag
from src.loaders import load_file

DOCS = config.DOCS_DIR

# arquivo -> trecho que deve aparecer na leitura
EXPECTED = {
    "rh/politica_ferias.pdf": "30 dias corridos",
    "rh/beneficios_e_onboarding.docx": "R$ 45,00",
    "financeiro/politica_despesas.md": "R$ 450,00",
    "financeiro/dre_2025.xlsx": "Lucro Líquido",
    "operacional/sla_suporte.html": "30 minutos",
    "estrategico/okrs_2026.pptx": "NPS de 45 para 60",
    "marketing_comercial/tabela_precos.csv": "299,00",
    "dados_sistemas/api_clientes.json": "100 requisições por minuto",
}


@pytest.mark.parametrize("rel,expected", EXPECTED.items())
def test_loaders(rel, expected):
    text = "\n".join(seg["text"] for seg in load_file(DOCS / rel))
    assert expected in text


def test_chunk_text_makes_progress():
    chunks = rag.chunk_text("Frase de teste. " * 500)
    assert len(chunks) > 1 and all(len(c) <= 1000 for c in chunks)


# ---------- cliente falso: embeddings por hash de palavras + chat que devolve o contexto ----------
class FakeClient:
    def embed(self, model, texts, input_type):
        vecs = []
        for t in texts:
            v = np.zeros(256)
            for w in t.lower().split():
                v[int(hashlib.md5(w.encode()).hexdigest(), 16) % 256] += 1
            vecs.append(v.tolist())
        return SimpleNamespace(embeddings=SimpleNamespace(float_=vecs))

    def chat(self, model, messages, temperature):
        return SimpleNamespace(message=SimpleNamespace(content=[SimpleNamespace(text=messages[-1]["content"])]))


def test_index_and_ask(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "INDEX_DIR", tmp_path)
    n_chunks, n_docs = rag.build_index(FakeClient())
    assert n_docs == 12 and n_chunks >= 12

    kb = rag.KnowledgeBase(FakeClient())
    _, sources = kb.ask("Qual o limite de hospedagem por diária em viagens?")
    assert "financeiro/politica_despesas.md" in [s["source"] for s in sources]
