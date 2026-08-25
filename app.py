"""
app.py
Streamlit chat UI for FilingIQ - Banking Document Intelligence
"""
import hmac
import os
import streamlit as st
from dotenv import load_dotenv
from rag_pipeline import load_vectorstore, build_rag_chain, query

load_dotenv()

st.set_page_config(
    page_title="FilingIQ — Banking Document Intelligence",
    page_icon="📂",
    layout="centered",
)

def check_password() -> bool:
    expected = os.getenv("APP_PASSWORD")
    if not expected:
        return True
    if st.session_state.get("auth_ok"):
        return True
    st.title("🔒 FilingIQ")
    pwd = st.text_input("Enter password", type="password")
    if pwd:
        if hmac.compare_digest(pwd, expected):
            st.session_state["auth_ok"] = True
            st.rerun()
        else:
            st.error("Incorrect password")
    return False

if not check_password():
    st.stop()

st.title("📂 FilingIQ")
st.subheader("Banking Document Intelligence")
st.caption(
    "Ask anything grounded in the annual reports of JPMorgan, Bank of America, and Goldman Sachs."
)

with st.sidebar:
    st.header("ℹ️ About FilingIQ")
    st.markdown("""
    **What it does:**
    Answers questions over real bank annual regulatory filings with source attribution.

    **Stack:**
    - 🤖 LLM: GPT-OSS 20B (Groq)
    - 🔍 Retrieval: FAISS + all-MiniLM-L6-v2
    - 🔗 Framework: LangChain
    - 🖥️ UI: Streamlit

    **Architecture:**
    ```
    Query → Embed → FAISS Search
    → Top-4 chunks → LLM → Answer
    ```

    **Coverage:**
    - JPMorgan Chase (FY2025)
    - Bank of America (FY2025)
    - Goldman Sachs (FY2025)
    """)
    st.divider()
    st.markdown("**Suggested questions:**")
    suggestions = [
        "What was JPMorgan's net revenue in 2025?",
        "How does Goldman Sachs manage credit risk?",
        "What are Bank of America's main business segments?",
        "How do these banks describe cybersecurity risk?",
        "What are the largest sources of non-interest revenue?",
    ]
    for s in suggestions:
        if st.button(s, use_container_width=True):
            st.session_state.pending_query = s

@st.cache_resource(show_spinner="⏳ Loading FilingIQ...")
def get_chain():
    vs = load_vectorstore()
    return build_rag_chain(vs)

try:
    chain = get_chain()
except FileNotFoundError as e:
    st.error(str(e))
    st.info("Run this command first: `python ingest.py`")
    st.stop()
except ValueError as e:
    st.error(str(e))
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander("📄 Source documents"):
                for src in msg["sources"]:
                    st.caption(f"• {src}")

user_input = st.chat_input("Ask about bank filings...")
if "pending_query" in st.session_state:
    user_input = st.session_state.pop("pending_query")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    with st.chat_message("assistant"):
        with st.spinner("🔍 Searching filings..."):
            result = query(chain, user_input)
            answer = result["answer"]
            sources = result["sources"]
        st.markdown(answer)
        if sources:
            with st.expander("📄 Source documents"):
                for src in sources:
                    st.caption(f"• {src}")
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources,
    })