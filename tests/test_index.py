from core.index import PostingList, HashTable, build_index_hash

def test_posting_list_insert_increments_frequency():
    pl = PostingList()
    pl.insert("doc1")
    pl.insert("doc1")
    assert len(pl) == 1
    assert pl.head.frequency == 2

def test_posting_list_multiple_docs():
    pl = PostingList()
    pl.insert("doc1")
    pl.insert("doc2")
    assert len(pl) == 2
    assert set(pl.get_doc_ids()) == {"doc1", "doc2"}

def test_posting_list_bool():
    pl = PostingList()
    assert not pl
    pl.insert("doc1")
    assert pl

def test_hash_table_insert_and_get():
    ht = HashTable()
    ht.insert("neural", "doc1")
    ht.insert("neural", "doc2")
    pl = ht.get("neural")
    assert pl is not None
    assert set(pl.get_doc_ids()) == {"doc1", "doc2"}

def test_hash_table_get_missing_term():
    ht = HashTable()
    assert ht.get("missing") is None

def test_hash_table_serialization():
    ht = HashTable()
    ht.insert("learn", "doc1")
    ht.insert("learn", "doc1")
    ht.insert("learn", "doc2")
    d  = ht.to_dict()
    ht2 = HashTable.from_dict(d)
    pl  = ht2.get("learn")
    assert set(pl.get_doc_ids()) == {"doc1", "doc2"}
    assert d["learn"]["doc1"] == 2

def test_build_index_hash():
    docs = [
        {"id": "doc1", "tokens": ["neural", "network"]},
        {"id": "doc2", "tokens": ["neural", "gradient"]},
    ]
    ht = build_index_hash(docs)
    assert set(ht.get("neural").get_doc_ids()) == {"doc1", "doc2"}
    assert ht.get("gradient").get_doc_ids() == ["doc2"]