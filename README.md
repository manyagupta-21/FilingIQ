# 🏦 FinRAG — Financial Document Q&A with RAG

> A Retrieval-Augmented Generation (RAG) chatbot over real **SEC 10-K filings** of major US banks. Answers are grounded in the source filings — not hallucinated.

---

## 🎯 Motivation

Large Language Models (LLMs) often hallucinate when asked about specific financial figures (revenue, capital ratios, segment performance). In fintech, accuracy is critical.

**FinRAG solves this** by combining document retrieval with LLM generation:

- Retrieves the most relevant chunks from real 10-K filings for each query
- Passes them as context to the LLM
- Answers cite the source document

---

## 🏗️ Architecture

```
User Query
    │
    ▼
Embedding Model (HuggingFace all-MiniLM-L6-v2)
    │
    ▼
FAISS Vector Search → Top-4 relevant chunks
    │
    ▼
Prompt = chunks + query
    │
    ▼
Groq LLM (Llama-3.1-8b-instant)
    │
    ▼
Answer + Source Documents
```

**Why RAG over pure LLM?**

| | Pure LLM | RAG |
|---|---|---|
| Accuracy on specific facts | ❌ May hallucinate | ✅ Grounded in docs |
| Updatable knowledge | ❌ Retrain required | ✅ Add docs, re-index |
| Source attribution | ❌ None | ✅ Shows source file |

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM | Llama-3.1-8b-instant via [Groq](https://groq.com) |
| Embeddings | `all-MiniLM-L6-v2` (HuggingFace) |
| Vector Store | FAISS (local, no server needed) |
| RAG Framework | LangChain |
| UI | Streamlit |
| Data | SEC EDGAR 10-K filings (public domain) |

---

## 🚀 Quick Start

### 1. Clone & install

```bash
git clone https://github.com/ctrlc0704/FinRAG.git
cd FinRAG
pip install -r requirements.txt
```

### 2. Get a free Groq API key

Sign up at [console.groq.com](https://console.groq.com) → Create API Key (free, no credit card).

```bash
cp .env.example .env
# Edit .env and paste your key:
#   GROQ_API_KEY=gsk_xxxxxxxxxxxx
```

### 3. (Optional) Refresh the SEC dataset

The repo ships with 10-K filings already in `data/docs/sec/`. To pull the latest filings from SEC EDGAR:

```bash
python fetch_sec.py
```

This downloads the most recent 10-K of JPMorgan, Bank of America, and Goldman Sachs into `data/docs/sec/`. Edit the `BANKS` dict in [fetch_sec.py](fetch_sec.py) to add or change tickers (provide the SEC CIK).

> SEC asks API users for a real contact email. Set `SEC_USER_AGENT` in your `.env` before running.

### 4. Build the FAISS index

```bash
python ingest.py
```

Output:

```
✅ Loaded 3 documents
✅ Split into 10870 chunks
⏳ Loading embedding model...
⏳ Building FAISS index...
✅ FAISS index saved to ./faiss_index/
```

### 5. Run the app

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

## 🌐 Exposing the App Publicly (ngrok)

When tunneling the local app to the public internet, **always enable the password gate** — otherwise anyone with the URL can burn through your Groq quota.

### 1. Set a password

Add to your `.env`:

```bash
APP_PASSWORD=pick-a-strong-secret
```

When `APP_PASSWORD` is set, the app shows a password prompt before any chat UI is reachable.

### 2. Bind Streamlit to localhost only

```bash
streamlit run app.py --server.address=127.0.0.1 --server.port=8501
```

Binding to `127.0.0.1` means the LAN and the public IP cannot see the app directly — only an explicit tunnel (ngrok) can reach it.

### 3. Start an ngrok tunnel

```bash
ngrok http 8501
```

ngrok prints a public HTTPS URL (e.g. `https://abc123.ngrok-free.app`). Share that — visitors will hit the password gate first.

> ⚠️ The password gate is a minimal deterrent. For higher-risk exposure consider: ngrok's built-in OAuth (paid plans), Cloudflare Tunnel + Access, or putting the app behind a reverse proxy with proper auth.

---

## 📁 Project Structure

```
FinRAG/
├── app.py              # Streamlit chat UI + password gate
├── rag_pipeline.py     # RAG chain (retriever + LLM)
├── ingest.py           # Document loading, chunking, indexing
├── fetch_sec.py        # Pulls latest 10-K filings from SEC EDGAR
├── data/
│   ├── docs/
│   │   └── sec/        # SEC 10-K filings (ingested)
│   └── docs_demo/      # Toy FAQ files (NOT ingested, kept for reference)
├── faiss_index/        # Auto-generated, gitignored
├── .env.example        # API key + password template
├── requirements.txt
└── README.md
```

---

## ➕ Add Your Own Documents

Drop any `.txt` or `.pdf` file into `data/docs/` (or a subfolder), then re-run:

```bash
python ingest.py
```

Good public sources for finance documents:

- SEC EDGAR ([sec.gov/edgar](https://www.sec.gov/edgar)) — 10-K, 10-Q, 8-K filings
- Federal Reserve and Treasury publications
- Bank investor relations pages (annual reports, earnings releases)

---

## 🔧 Configuration

Edit [rag_pipeline.py](rag_pipeline.py) to tune:

```python
search_kwargs={"k": 4}          # retrieved chunks per query
model="llama-3.1-8b-instant"    # fastest Groq model
# model="llama-3.1-70b-versatile" # more capable
```

Edit [ingest.py](ingest.py) to tune chunking:

```python
chunk_size=500      # larger = more context per chunk
chunk_overlap=80    # higher = less info loss at boundaries
```

---

## 🔒 Security Notes

- `.env` is gitignored — never commit your API key
- `APP_PASSWORD` enables a simple password gate; required for public exposure
- Streamlit binds to all interfaces by default — use `--server.address=127.0.0.1` for local-only
- SEC filings are public domain, safe to redistribute

---

## 📝 License

MIT License — free to use and modify.
