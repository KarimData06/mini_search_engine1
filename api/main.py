import os
import math
import pickle
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from huggingface_hub import hf_hub_download
from core.search import SearchEngine
from core.index import HashTable

HF_REPO = "karimbnr06/mini-search-cache"

def download_cache():
    os.makedirs("cache", exist_ok=True)
    for f in ["index.pkl", "articles.pkl", "doc_lengths.pkl", "markov.pkl"]:
        dest = f"cache/{f}"
        if not os.path.exists(dest):
            print(f"⬇️  Downloading {f}...")
            hf_hub_download(
                repo_id=HF_REPO,
                filename=f,
                repo_type="dataset",
                local_dir="cache"
            )
            print(f"✅ {f} ready")

download_cache()

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])

print("📦 Loading cache...")
with open("cache/index.pkl",       "rb") as f: raw_index   = pickle.load(f)
with open("cache/articles.pkl",    "rb") as f: doc_map     = pickle.load(f)
with open("cache/doc_lengths.pkl", "rb") as f: doc_lengths = pickle.load(f)
with open("cache/markov.pkl",      "rb") as f: markov      = pickle.load(f)

N      = len(doc_lengths)
index  = HashTable.from_dict(raw_index)
engine = SearchEngine(index, doc_lengths, N)
print(f"✅ Ready — {N} documents")

@app.get("/")
def home():
    return {"message": "Mini Search Engine API", "docs": N}

@app.get("/search")
def search(q: str, category: str = None, author: str = None,
           page: int = 1, size: int = 10):
    results = engine.search(q)
    enriched = []
    for doc_id, score in results.items():
        doc = doc_map.get(doc_id)
        if not doc: continue
        if category and category.lower() not in doc.get("categories","").lower(): continue
        if author   and author.lower()   not in doc.get("authors","").lower():    continue
        enriched.append({
            "doc_id":   doc_id,
            "title":    doc.get("title"),
            "abstract": doc.get("abstract","")[:200] + "...",
            "score":    round(score, 4),
            "pdf_link": doc.get("pdf"),
            "category": doc.get("categories"),
            "authors":  doc.get("authors"),
        })
    total = len(enriched)
    pages = max(1, math.ceil(total / size))
    page  = max(1, min(page, pages))
    return {"query": q, "total": total, "page": page,
            "pages": pages, "size": size,
            "results": enriched[(page-1)*size : page*size]}

@app.get("/suggest")
def suggest(q: str):
    from core.preprocessing import preprocess
    tokens      = preprocess(q)
    suggestions = markov.suggest_from_query(tokens, n=4)
    return {"suggestions": suggestions}