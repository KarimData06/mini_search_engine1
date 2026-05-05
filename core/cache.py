import pickle
import os

def save(obj, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(obj, f)

def load(path):
    with open(path, "rb") as f:
        return pickle.load(f)
    

def load_index(data, HashTable):
    index = HashTable()

    for term, docs in data.items():
        for doc_id, freq in docs.items():
            for _ in range(freq):
                index.insert(term, doc_id)

    return index