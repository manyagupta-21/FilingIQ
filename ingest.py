"""
ingest.py
Load documents → chunk → embed → save FAISS index
Run once before starting the app.
"""

import os
from pathlib import Path
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

DOCS_DIR = "data/docs"
INDEX_DIR = "faiss_index"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def load_documents(docs_dir: str):
    """Load all .txt and .pdf files from docs directory."""
    docs = []

    # Load .txt files
    txt_loader = DirectoryLoader(
        docs_dir,
        glob="**/*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
        show_progress=True,
    )
    docs.extend(txt_loader.load())

    # Load .pdf files if any
    try:
        from langchain_community.document_loaders import PyPDFDirectoryLoader
        pdf_loader = PyPDFDirectoryLoader(docs_dir)
        docs.extend(pdf_loader.load())
    except Exception:
        pass  # pypdf optional

    print(f"✅ Loaded {len(docs)} documents")
    return docs


def chunk_documents(docs):
    """Split documents into chunks for embedding."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=80,
        separators=["\n\n", "\n", ".", "。", " ", ""],
    )
    chunks = splitter.split_documents(docs)
    print(f"✅ Split into {len(chunks)} chunks")
    return chunks


def build_vectorstore(chunks, embed_model: str, index_dir: str):
    """Embed chunks and save FAISS index locally."""
    print(f"⏳ Loading embedding model: {embed_model}")
    embeddings = HuggingFaceEmbeddings(
        model_name=embed_model,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    print("⏳ Building FAISS index...")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(index_dir)
    print(f"✅ FAISS index saved to ./{index_dir}/")
    return vectorstore


def main():
    docs = load_documents(DOCS_DIR)
    if not docs:
        print("❌ No documents found in data/docs/")
        return

    chunks = chunk_documents(docs)
    build_vectorstore(chunks, EMBED_MODEL, INDEX_DIR)
    print("\n🎉 Done! Run: streamlit run app.py")


if __name__ == "__main__":
    main()
