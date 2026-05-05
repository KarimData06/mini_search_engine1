# core/index.py

## ── Nœud de la PostingList 

class PostingNode:
    def __init__(self, doc_id):
        self.doc_id    = doc_id
        self.frequency = 1
        self.next      = None

## ── Liste chaînée de postings 

class PostingList:
    def __init__(self):
        self.head = None

    def insert(self, doc_id):
        # Si le doc existe déjà → on incrémente juste sa fréquence
        node = self.head
        while node:
            if node.doc_id == doc_id:
                node.frequency += 1
                return
            node = node.next

        # Sinon → nouveau nœud en tête de liste
        new_node      = PostingNode(doc_id)
        new_node.next = self.head
        self.head     = new_node

    def get_doc_ids(self):
        ids, node = [], self.head
        while node:
            ids.append(node.doc_id)
            node = node.next
        return ids
    
    def __iter__(self):
        node = self.head
        while node:
            yield node
            node = node.next

    def __bool__(self):
        return self.head is not None
    
    def __len__(self):          # ← nouveau : donne le df (nb de docs)
        count, node = 0, self.head
        while node:
            count += 1
            node = node.next
        return count
    
    ## ── Table de hachage (polynomial rolling)

# ── Polynomial rolling hash 

def _poly_hash(term, p, m):
    h, pow_p = 0, 1
    for c in term:
        h = (h + ord(c) * pow_p) % m
        pow_p = (pow_p * p) % m
    return h


class HashTable:
    def __init__(self, size=65537):   # nombre premier
        self.size    = size
        self.buckets = [None] * size

    def _slot(self, term):
        h1 = _poly_hash(term, 31, 10**9 + 7)
        h2 = _poly_hash(term, 37, 10**9 + 9)
        return (h1 * (10**9 + 9) + h2) % self.size   # combinaison des deux

    
    def insert(self, term, doc_id):
        slot = self._slot(term)

        if self.buckets[slot] is None:
            self.buckets[slot] = {}

        if term not in self.buckets[slot]:
            self.buckets[slot][term] = PostingList()

        self.buckets[slot][term].insert(doc_id)


    def get(self, term):
        slot   = self._slot(term)
        bucket = self.buckets[slot]
        if bucket is None:
            return None
        return bucket.get(term)
    

    # Sérialisation → dict simple pour pickle
    def to_dict(self):
        data = {}
        for bucket in self.buckets:
            if bucket is None:
                continue
            for term, pl in bucket.items():
                data[term] = {node.doc_id: node.frequency for node in pl}
        return data
    
    # Désérialisation → recrée le HashTable depuis le dict
    @classmethod
    def from_dict(cls, data):
        table = cls()
        for term, docs in data.items():
            for doc_id, freq in docs.items():
                for _ in range(freq):
                    table.insert(term, doc_id)
        return table
    
## ── Construction de l'index ─────────────────────────────────────

def build_index_hash(docs):
    table = HashTable()

    for doc in docs:
        for token in doc["tokens"]:
            table.insert(token, doc["id"])

    return table