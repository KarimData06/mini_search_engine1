from fastapi import FastAPI
from core.search import SearchEngine
from core.index import HashTable
import pickle
import os
import math 
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

#
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


print("📦 Loading index...")

for f in ["cache/index.pkl", "cache/articles.pkl", "cache/doc_lengths.pkl", "cache/markov.pkl"]:
    if not os.path.exists(f):
        raise Exception(f"❌ {f} not found. Run build_index.py first!")

with open("cache/index.pkl", "rb") as f: raw_index   = pickle.load(f)
with open("cache/articles.pkl","rb") as f: doc_map     = pickle.load(f)
with open("cache/doc_lengths.pkl","rb") as f: doc_lengths = pickle.load(f)
with open("cache/markov.pkl", "rb") as f: markov      = pickle.load(f)


N = len(doc_lengths)
index  = HashTable.from_dict(raw_index)

engine = SearchEngine(index, doc_lengths, N)

@app.get("/")
def home():
    return {"message": "Mini Search Engine API", "docs":N}

@app.get("/search")
def search(q: str, category : str = None, author : str = None, page: int=1, size: int =10):
    results = engine.search(q)

    enriched_results = []

    for doc_id, score in results.items():
        doc = doc_map.get(doc_id)

        if not doc:
            continue

        # ── Filtres ──────────────────────────────────────────
        if category and category.lower() not in doc.get("categories", "").lower():
            continue
        if author and author.lower() not in doc.get("authors", "").lower():
            continue

        enriched_results.append({
            "doc_id": doc_id,
            "title": doc.get("title"),
            "abstract": doc.get("abstract")[:200] + "...",
            "score": round(score, 4),
            "pdf": doc.get("pdf"),
            "category": doc.get("categories"),
            "authors":  doc.get("authors"),
        })


    total = len(enriched_results)
    pages = max(1, math.ceil(total / size))
    page = max(1, min(page, pages))
    start = (page-1)*size
    end = start + size

    return {
        "query": q,
        "total":   total,
        "page":    page,
        "pages":   pages,
        "size":    size,
        "results": enriched_results[start:end]
    }

@app.get("/suggest")
def suggest(q: str):
    from core.preprocessing import preprocess
    tokens = preprocess(q)
    suggestions = markov.suggest_from_query(tokens, n=4)
    return {"suggestions": suggestions}