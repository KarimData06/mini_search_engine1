from core.index import build_index_hash
from core.search import SearchEngine

def make_engine(docs):
    index       = build_index_hash(docs)
    doc_lengths = {doc["id"]: len(doc["tokens"]) for doc in docs}
    return SearchEngine(index, doc_lengths, N=len(docs))

def test_search_returns_matching_doc():
    docs = [
        {"id": "doc1", "tokens": ["neural", "network"]},
        {"id": "doc2", "tokens": ["gradient", "descent"]},
    ]
    results = make_engine(docs).search("neural network")
    assert "doc1" in results
    assert "doc2" not in results

def test_search_ranking_by_tf():
    docs = [
        {"id": "doc1", "tokens": ["neural", "network", "neural"]},
        {"id": "doc2", "tokens": ["gradient", "descent"]},
    ]
    results = make_engine(docs).search("neural")
    assert "doc1" in results
    assert "doc2" not in results

def test_search_empty_query():
    docs = [{"id": "doc1", "tokens": ["neural"]}]
    assert make_engine(docs).search("") == {}

def test_search_unknown_term():
    docs = [{"id": "doc1", "tokens": ["neural"]}]
    assert make_engine(docs).search("zzzzunknown") == {}