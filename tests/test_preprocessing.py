from core.preprocessing import preprocess, simple_stem, clean_latex

def test_stopwords_removed():
    tokens = preprocess("the neural network is learning")
    assert "the" not in tokens
    assert "is"  not in tokens

def test_numbers_removed():
    tokens = preprocess("we trained 100 models")
    assert "100" not in tokens

def test_short_words_removed():
    tokens = preprocess("a neural go network")
    assert "a"  not in tokens
    assert "go" not in tokens

def test_latex_removed():
    tokens = preprocess("minimize $\\mathcal{L}$ gradient descent")
    assert "gradient" in tokens
    assert "descent"  in tokens

def test_stemming():
    assert simple_stem("learning") == "learn"
    assert simple_stem("gradient") == "gradient"

def test_clean_latex():
    result = clean_latex("loss $x^2$ function")
    assert "$" not in result