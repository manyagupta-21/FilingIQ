"""
rag_pipeline.py
Core RAG pipeline: load FAISS index → retriever → LLM chain
"""

import os
from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

INDEX_DIR = "faiss_index"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

PROMPT_TEMPLATE = PROMPT_TEMPLATE = """You are a financial analyst assistant specialising in bank regulatory filings. Answer the question based only on the provided documents.
If the documents do not contain relevant information, say "I could not find this information in the documents."
When reporting financial metrics such as revenue, profit, or ratios, always prefer the firmwide or consolidated total figure over segment-level figures, and explicitly state which figure you are reporting.
Answer in English, clearly and concisely.

Reference documents:
{context}

Question: {question}
Answer:"""


def load_vectorstore():
    """Load existing FAISS index from disk."""
    if not os.path.exists(INDEX_DIR):
        raise FileNotFoundError(
            f"FAISS index not found at ./{INDEX_DIR}/\n"
            "Please run: python ingest.py"
        )

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBED_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
    vectorstore = FAISS.load_local(
        INDEX_DIR,
        embeddings,
        allow_dangerous_deserialization=True,
    )
    return vectorstore


def build_rag_chain(vectorstore):
    """Build RetrievalQA chain with Groq LLM."""
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError(
            "GROQ_API_KEY not set.\n"
            "Get free key at: https://console.groq.com\n"
            "Then: export GROQ_API_KEY=your_key_here"
        )

    llm = ChatGroq(
        model="openai/gpt-oss-20b",
        temperature=0.1,
        max_tokens=1024,
        groq_api_key=groq_api_key,
    )

    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4},
    )

    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE,
        input_variables=["context", "question"],
    )

    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt},
    )
    return chain


def query(chain, question: str) -> dict:
    """Run a query and return answer + sources."""
    result = chain.invoke({"query": question})
    sources = list({
        doc.metadata.get("source", "unknown")
        for doc in result["source_documents"]
    })
    return {
        "answer": result["result"],
        "sources": sources,
    }
