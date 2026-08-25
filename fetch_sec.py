"""
fetch_sec.py
Download the most recent 10-K filings of major US banks from SEC EDGAR,
strip HTML to plain text, and save to data/docs/sec/.

SEC EDGAR is a public, free, official source. We follow their fair-use rules:
- Send a descriptive User-Agent
- Stay under 10 requests/sec
"""

import os
import re
import time
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

UA = os.getenv("SEC_USER_AGENT", "FinRAG Demo finrag-demo@example.com")
HEADERS = {"User-Agent": UA}

BANKS = {
    "JPMorgan_Chase": "0000019617",
    "Bank_of_America": "0000070858",
    "Goldman_Sachs": "0000886982",
}

OUT_DIR = Path("data/docs/sec")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def latest_10k(cik_padded: str):
    url = f"https://data.sec.gov/submissions/CIK{cik_padded}.json"
    sub = requests.get(url, headers=HEADERS, timeout=30).json()
    recent = sub["filings"]["recent"]
    for form, acc, doc, date in zip(
        recent["form"],
        recent["accessionNumber"],
        recent["primaryDocument"],
        recent["filingDate"],
    ):
        if form == "10-K":
            return acc, doc, date
    raise RuntimeError(f"No 10-K found for CIK {cik_padded}")


def download_filing(cik_padded: str, accession: str, primary_doc: str) -> str:
    cik_int = int(cik_padded)
    acc_no_dash = accession.replace("-", "")
    url = f"https://www.sec.gov/Archives/edgar/data/{cik_int}/{acc_no_dash}/{primary_doc}"
    r = requests.get(url, headers=HEADERS, timeout=60)
    r.raise_for_status()
    return r.text


def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def main():
    for name, cik in BANKS.items():
        print(f"[{name}] looking up latest 10-K...")
        accession, doc, date = latest_10k(cik)
        print(f"  filing {accession} ({date}) primary doc: {doc}")
        time.sleep(0.2)

        print(f"  downloading...")
        html = download_filing(cik, accession, doc)
        text = html_to_text(html)
        out_path = OUT_DIR / f"{name}_10K_{date}.txt"
        out_path.write_text(text, encoding="utf-8")
        print(f"  saved {out_path} ({len(text):,} chars)")
        time.sleep(0.2)

    print("\nDone. Run: python ingest.py")


if __name__ == "__main__":
    main()
