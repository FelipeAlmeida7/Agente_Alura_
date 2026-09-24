"""RAG simples: indexa os documentos, busca os trechos mais parecidos e responde com o LLM (OCI Generative AI)."""
import json

import cohere
import numpy as np

from . import config
from .loaders import SUPPORTED, load_file

SYSTEM_PROMPT = """Você é o assistente virtual interno da Nova Aurora Tecnologia e ajuda colaboradores \
a tirar dúvidas sobre documentos da empresa (RH, financeiro, operacional, estratégia, jurídico, \
marketing, dados e sistemas, P&D, qualidade e comunicação interna).

Regras:
- Responda SOMENTE com base nos trechos de contexto fornecidos.
- Se a resposta não estiver no contexto, diga claramente que não encontrou essa informação nos documentos \
e sugira procurar a área responsável. Nunca invente valores, prazos ou nomes.
- Responda em português, de forma direta e objetiva.
- Ao final, indique as fontes usadas no formato: Fonte: arquivo (local)."""


# ---------- cliente OCI ----------
def get_client():
    kwargs = {"oci_region": config.OCI_REGION, "oci_compartment_id": config.OCI_COMPARTMENT_ID}
    if config.OCI_AUTH == "instance_principal":
        kwargs["auth_type"] = "instance_principal"  # VM na OCI: sem chaves no código
    elif config.OCI_PROFILE:
        kwargs["oci_profile"] = config.OCI_PROFILE
    return cohere.OciClientV2(**kwargs)


def embed_texts(client, texts, input_type):
    """Gera embeddings (em lotes de 96) e normaliza os vetores."""
    vectors = []
    for i in range(0, len(texts), 96):
        resp = client.embed(model=config.EMBED_MODEL, texts=texts[i:i + 96], input_type=input_type)
        vectors += resp.embeddings.float_
    m = np.array(vectors, dtype="float32")
    return m / np.linalg.norm(m, axis=1, keepdims=True)


# ---------- ingestão ----------
def chunk_text(text, size=900, overlap=150):
    text = text.strip()
    if len(text) <= size:
        return [text] if text else []
    chunks, start = [], 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            cut = max(text.rfind("\n", start, end), text.rfind(". ", start, end))
            if cut > start + size // 2:
                end = cut + 1
        chunks.append(text[start:end].strip())
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return [c for c in chunks if c]


def collect_chunks():
    """Lê todos os arquivos suportados em data/docs e devolve a lista de chunks com metadados."""
    records = []
    for path in sorted(config.DOCS_DIR.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED:
            continue
        rel = path.relative_to(config.DOCS_DIR)
        category = rel.parts[0] if len(rel.parts) > 1 else "geral"
        try:
            segments = load_file(path)
        except Exception as exc:  # um arquivo com problema não derruba a indexação
            print(f"[aviso] não foi possível ler {rel}: {exc}")
            continue
        for seg in segments:
            for chunk in chunk_text(seg["text"]):
                records.append({"text": chunk, "source": rel.as_posix(), "category": category,
                                "location": seg["location"]})
    return records


def build_index(client=None):
    client = client or get_client()
    records = collect_chunks()
    if not records:
        raise RuntimeError(f"Nenhum documento encontrado em {config.DOCS_DIR}")
    # o nome do arquivo e a categoria entram no embedding para melhorar a busca
    inputs = [f"[{r['category']} / {r['source']}]\n{r['text']}" for r in records]
    matrix = embed_texts(client, inputs, "search_document")
    config.INDEX_DIR.mkdir(parents=True, exist_ok=True)
    np.save(config.INDEX_DIR / "embeddings.npy", matrix)
    (config.INDEX_DIR / "chunks.json").write_text(json.dumps(records, ensure_ascii=False), encoding="utf-8")
    return len(records), len({r["source"] for r in records})


def index_exists():
    return (config.INDEX_DIR / "embeddings.npy").exists() and (config.INDEX_DIR / "chunks.json").exists()


# ---------- consulta ----------
class KnowledgeBase:
    def __init__(self, client=None):
        self.client = client or get_client()
        self.matrix = np.load(config.INDEX_DIR / "embeddings.npy")
        self.chunks = json.loads((config.INDEX_DIR / "chunks.json").read_text(encoding="utf-8"))

    def search(self, query, k=config.TOP_K):
        q = embed_texts(self.client, [query], "search_query")[0]
        scores = self.matrix @ q
        top = np.argsort(-scores)[:k]
        return [self.chunks[i] | {"score": float(scores[i])} for i in top]

    def ask(self, question, history=None):
        """Retorna (resposta, fontes). history = lista de {'role', 'content'} da conversa."""
        history = history or []
        # perguntas de acompanhamento ("e para estagiários?"): junta a pergunta anterior na busca
        prev_user = [m["content"] for m in history if m["role"] == "user"][-1:]
        hits = self.search(" ".join(prev_user + [question]))

        context = "\n\n".join(
            f"[{i}] {h['source']} ({h['location']})\n{h['text']}" for i, h in enumerate(hits, start=1)
        )
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages += history[-6:]
        messages.append({"role": "user", "content": f"Contexto:\n{context}\n\nPergunta: {question}"})

        resp = self.client.chat(model=config.CHAT_MODEL, messages=messages, temperature=0.2)
        answer = resp.message.content[0].text.strip()

        sources, seen = [], set()
        for h in hits:
            key = (h["source"], h["location"])
            if key not in seen:
                seen.add(key)
                sources.append({"source": h["source"], "location": h["location"], "category": h["category"]})
        return answer, sources

