from core.preprocessing import preprocess
import math

class SearchEngine:
    def __init__(self, index, doc_lengths, N):
        self.index = index
        self.doc_lengths = doc_lengths
        self.N  = N


    def _tfidf(self, term, doc_id, freq):
        tf  = freq / max(self.doc_lengths.get(doc_id, 1), 1)
        pl  = self.index.get(term)
        df  = len(pl.get_doc_ids()) if pl else 1
        idf = math.log(self.N / df)
        return tf * idf

    def and_multi(self, tokens):
        token_sets = []

        for t in tokens:
            pl = self.index.get(t)
            if not pl:
                return set()
            token_sets.append(set(pl.get_doc_ids()))

        return set.intersection(*token_sets)

    def or_multi(self, tokens):
        result = set()

        for token in tokens:
            pl = self.index.get(token)
            if pl:
                result.update(pl.get_doc_ids())

        return result

    def search(self, query):
        tokens = [t.lower() for t in preprocess(query)]

        if not tokens:
            return {}

        scores = {}

    # 🔥 scoring
        for token in tokens:
            pl = self.index.get(token)
            if not pl:
                continue

            for node in pl:
                score = self._tfidf(token, node.doc_id, node.frequency)
                scores[node.doc_id] = scores.get(node.doc_id, 0) + score

    # 🔥 si on a des résultats → ranking
        if scores:
            return dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))

    # 🔥 fallback AND
        results = self.and_multi(tokens)
        if results:
            return {doc_id: 1 for doc_id in results}

    # 🔥 fallback OR
        return {doc_id: 1 for doc_id in self.or_multi(tokens)}