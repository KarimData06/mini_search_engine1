import re

STOPWORDS = {
    "the", "is", "in", "and", "to", "of", "a", "for", "on", "with",
    "as", "by", "an", "be", "this", "that", "we", "are", "from"
}

LATEX_INLINE  = re.compile(r"\$.*?\$", re.DOTALL)
LATEX_CMD     = re.compile(r"\\[a-zA-Z]+")
SPECIAL_CHARS = re.compile(r"[^a-z0-9\s]")

def simple_stem(word):
    suffixes = ["ing", "ed", "ly", "ment", "tion", "ions", "ies"]
    
    for suffix in suffixes:
        if word.endswith(suffix) and len(word) > len(suffix) + 2:
            return word[:-len(suffix)]
    return word

def clean_latex(text):
    text = LATEX_INLINE.sub(" ", text)
    text = LATEX_CMD.sub(" ", text)
    text = re.sub(r"[{}]", " ", text)
    return text

def preprocess(text):
    if not isinstance(text, str):
        return []

    text = clean_latex(text)
    text = text.lower()
    text = SPECIAL_CHARS.sub(" ", text)

    tokens = text.split()
    processed_tokens = []

    for word in tokens:
        if len(word) <= 2:             # trop court
            continue
        if word.isdigit():             # ← nombres filtrés
            continue
        if word in STOPWORDS:          # ← stopwords AVANT stemming
            continue
        word = re.sub(r"[^a-z]", "", word)
        if not word:
            continue

        word = simple_stem(word)
        processed_tokens.append(word)

    return processed_tokens