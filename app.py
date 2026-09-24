"""Interface de chat (Streamlit) do agente corporativo."""
import streamlit as st

from src import config
from src.loaders import SUPPORTED
from src.rag import KnowledgeBase, build_index, index_exists

st.set_page_config(page_title="Assistente Nova Aurora", page_icon="🤖")
st.title("🤖 Assistente Nova Aurora")
st.caption("Tire dúvidas sobre políticas, processos e documentos internos da empresa.")


@st.cache_resource(show_spinner=False)
def get_kb():
    if not index_exists():
        with st.spinner("Indexando documentos pela primeira vez..."):
            build_index()
    return KnowledgeBase()


# ---------- barra lateral ----------
docs = sorted(p for p in config.DOCS_DIR.rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED)
with st.sidebar:
    st.subheader("📚 Base de conhecimento")
    st.write(f"{len(docs)} documentos indexáveis")
    for p in docs:
        st.caption(f"• {p.relative_to(config.DOCS_DIR).as_posix()}")
    if st.button("🔄 Reindexar documentos"):
        with st.spinner("Reindexando..."):
            n_chunks, n_docs = build_index()
        get_kb.clear()
        st.success(f"{n_docs} documentos / {n_chunks} trechos")
    if st.button("🧹 Limpar conversa"):
        st.session_state.messages = []
        st.rerun()

# ---------- chat ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if m.get("sources"):
            with st.expander("Fontes"):
                for s in m["sources"]:
                    st.write(f"📄 **{s['source']}** — {s['location']}")

if question := st.chat_input("Ex.: Quantos dias de férias posso fracionar?"):
    with st.chat_message("user"):
        st.markdown(question)
    history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("assistant"):
        try:
            with st.spinner("Consultando os documentos..."):
                answer, sources = get_kb().ask(question, history)
            st.markdown(answer)
            with st.expander("Fontes"):
                for s in sources:
                    st.write(f"📄 **{s['source']}** — {s['location']}")
            st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})
        except Exception as exc:
            st.error(f"Erro ao consultar o serviço de IA da OCI: {exc}")
