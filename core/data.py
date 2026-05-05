import json

def load_ml_articles(path, limit=10000):
    count = 0

    with open(path, encoding="utf-8") as f:
        for line in f:
            article = json.loads(line)
            categories = article.get("categories", "")

            if "cs.LG" in categories or "stat.ML" in categories:
                yield {
                    "id": article.get("id"),
                    "title": article.get("title", ""),
                    "abstract": article.get("abstract", ""),
                    "categories": categories,
                    "authors": article.get("authors", ""),
                    "pdf": f"https://arxiv.org/pdf/{article.get('id')}"
                }

                count += 1
                if count >= limit:
                    break