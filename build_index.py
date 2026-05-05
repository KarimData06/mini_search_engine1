from core.data import load_ml_articles
from core.preprocessing import preprocess
from core.index import build_index_hash
from core.markov import MarkovChain
from core.cache import save

def build():
    path = "data/arxiv-metadata-oai-snapshot.json"

    docs = []
    articles = {}
    print("📥 Loading dataset...")

    for article in load_ml_articles(path, limit=10000):
        text = article["title"] + " " + article["abstract"]

        tokens = preprocess(text)

        docs.append({
            "id": article["id"],
            "tokens": tokens
        })

        articles[article["id"]] = article

    print("🔨 Building index...")
    index = build_index_hash(docs)

    print("🔗 Training Markov chain...")
    markov = MarkovChain()
    for doc in docs:
        markov.train(doc["tokens"])

    print("📐 Computing doc lengths...")
    doc_lengths = {doc["id"]: len(doc["tokens"]) for doc in docs}

    print("💾 Saving cache...")
    save(index.to_dict(),  "cache/index.pkl")
    save(docs,  "cache/docs.pkl")
    save(articles,  "cache/articles.pkl")
    save(doc_lengths, "cache/doc_lengths.pkl")   # ← nouveau
    save(markov, "cache/markov.pkl")         # ← nouveau

    print("✅ Done!")

if __name__ == "__main__":
    build()