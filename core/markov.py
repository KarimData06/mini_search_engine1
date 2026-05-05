# core/markov.py
from collections import defaultdict

class MarkovChain:
    def __init__(self):
        self.model = {}              # ← dict normal, pas de lambda

    def train(self, tokens):
        for i in range(len(tokens) - 1):
            w1, w2 = tokens[i], tokens[i + 1]
            if w1 not in self.model:
                self.model[w1] = {}
            self.model[w1][w2] = self.model[w1].get(w2, 0) + 1

    def suggest(self, last_word, n=4):
        nexts = self.model.get(last_word, {})
        if not nexts:
            return []
        ranked = sorted(nexts.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in ranked[:n]]

    def suggest_from_query(self, query_tokens, n=4):
        if not query_tokens:
            return []
        return self.suggest(query_tokens[-1], n)