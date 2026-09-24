"""Indexa os documentos de data/docs (rode uma vez, ou sempre que adicionar/alterar arquivos)."""
from src.rag import build_index

if __name__ == "__main__":
    n_chunks, n_docs = build_index()
    print(f"Índice criado: {n_docs} documentos, {n_chunks} trechos.")
