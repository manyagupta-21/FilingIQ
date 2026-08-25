# 📂 FilingIQ — Banking Document Intelligence

> A Retrieval-Augmented Generation (RAG) system for grounded Q&A over real annual regulatory filings of major US banks. Answers are sourced directly from the documents and not hallucinated.

---

## 🎯 Motivation

Large Language Models (LLMs) often hallucinate when asked about specific financial figures — revenue, capital ratios, segment performance. In banking and finance, accuracy is non-negotiable.

**FilingIQ solves this** by combining semantic document retrieval with LLM generation:

- Retrieves the most relevant chunks from real bank annual reports for each query
- Passes them as grounded context to the LLM
- Every answer cites the source document it came from

---

## 🏗️ Architecture

```
User Query
    │
    ▼
Embedding Model (all-MiniLM-L6-v2)
    │
    ▼
FAISS Vector Search → Top-4 relevant chunks
    │
    ▼
Prompt = chunks + query
    │
    ▼
Groq-hosted LLM (GPT-OSS 20B)
    │
    ▼
Answer + Source Attribution
```

**Why RAG over pure LLM?**

|                          | Pure LLM                    | RAG                          |
|--------------------------|-----------------------------|------------------------------|
| Accuracy on specific facts | ❌ May hallucinate          | ✅ Grounded in documents      |
| Updatable knowledge      | ❌ Retrain required          | ✅ Add docs, re-index         |
| Source attribution       | ❌ None                     | ✅ Shows source file          |

---

## 🛠️ Tech Stack

| Component      | Technology                                      |
|----------------|-------------------------------------------------|
| LLM            | GPT-OSS 20B via [Groq](https://groq.com)        |
| Embeddings     | `all-MiniLM-L6-v2` (HuggingFace)               |
| Vector Store   | FAISS (local, no server needed)                 |
| RAG Framework  | LangChain                                       |
| UI             | Streamlit                                       |
| Data           | Bank annual regulatory filings (public domain)  |

---

## 📊 Coverage

| Bank              | Filing    | Period |
|-------------------|-----------|--------|
| JPMorgan Chase    | 10-K      | FY2025 |
| Bank of America   | 10-K      | FY2025 |
| Goldman Sachs     | 10-K      | FY2025 |

---

## 🚀 Quick Start

### 1. Clone & install

```bash
git clone https://github.com/manyagupta-21/FilingIQ.git
cd FilingIQ
pip install -r requirements.txt
```

### 2. Get a free Groq API key

Sign up at [console.groq.com](https://console.groq.com) → Create API Key (free, no credit card).

```bash
cp .env.example .env
# Edit .env and paste your key:
#   GROQ_API_KEY=gsk_xxxxxxxxxxxx
```

### 3. Build the FAISS index

```bash
python ingest.py
```

Expected output:

```
✅ Loaded 3 documents
✅ Split into 10870 chunks
⏳ Loading embedding model...
⏳ Building FAISS index...
✅ FAISS index saved to ./faiss_index/
```

### 4. Run the app

```bash
streamlit run app.py
```

Open `http://localhost:8501`.

---

## 💬 Example Queries

```
"What was JPMorgan's net revenue in 2025?"
"How does Goldman Sachs manage credit risk?"
"What are Bank of America's main business segments?"
"How do these banks describe cybersecurity risk?"
"What are the largest sources of non-interest revenue?"
```

---

## 📁 Project Structure

```
FilingIQ/
├── app.py              # Streamlit chat UI
├── rag_pipeline.py     # RAG chain (retriever + LLM)
├── ingest.py           # Document loading, chunking, indexing
├── fetch_sec.py        # Pulls latest filings from SEC EDGAR
├── data/
│   └── docs/
│       └── sec/        # Bank annual filings (ingested)
├── faiss_index/        # Auto-generated, gitignored
├── .env.example        # API key template
├── requirements.txt
└── README.md
```

---

## ➕ Add Your Own Documents

Drop any `.txt` or `.pdf` file into `data/docs/` then re-run:

```bash
python ingest.py
```

Good public sources for additional filings:
- [SEC EDGAR](https://www.sec.gov/edgar) — 10-K, 10-Q, 8-K filings
- Bank investor relations pages — annual reports, earnings releases
- Federal Reserve and Treasury publications

---

## ⚠️ Known Limitations

- **Cross-entity queries** — questions comparing two banks simultaneously (e.g. "Compare JPMorgan and BofA revenue") may fail due to top-k retrieval not capturing both entities in the same context window
- **Tabular data** — numeric figures embedded in tables may be retrieved at segment level rather than consolidated level depending on chunk boundaries
- **Single-document scope** — retrieval is chunk-level; the system cannot reason across the full filing in one pass

These are architectural constraints of standard RAG and documented here for transparency.

---

## 🔧 Configuration

Edit `rag_pipeline.py` to tune retrieval:

```python
search_kwargs={"k": 4}   # increase for broader retrieval
```

Edit `ingest.py` to tune chunking:

```python
chunk_size=500      # larger = more context per chunk
chunk_overlap=80    # higher = less info loss at boundaries
```

---

## 🔒 Security Notes

- `.env` is gitignored — never commit your API key
- `APP_PASSWORD` in `.env` enables a password gate for public exposure via ngrok
- Bank filings are public domain, safe to redistribute

---

## 📝 License

MIT License — free to use and modify.
