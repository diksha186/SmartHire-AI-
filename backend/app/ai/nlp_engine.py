"""
spaCy wrapper.

The model is loaded only once (lazy singleton) because loading takes ~1 second.
If the model is missing we degrade gracefully to a blank English pipeline so the
application still starts - the README tells the user to run:

    python -m spacy download en_core_web_sm
"""
import re

import spacy

_nlp = None


def get_nlp():
    global _nlp
    if _nlp is None:
        try:
            _nlp = spacy.load("en_core_web_sm", disable=["ner", "parser"])
        except OSError:
            print("[SmartHire AI] en_core_web_sm not found - using blank English pipeline. "
                  "Run: python -m spacy download en_core_web_sm")
            _nlp = spacy.blank("en")
    return _nlp


def clean_text(raw_text: str) -> str:
    """Lowercase, remove odd characters and collapse whitespace."""
    text = raw_text.lower()
    text = text.replace("\u2022", " ").replace("\t", " ")
    text = re.sub(r"[^\w\s\+\#\.\,\-/@]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def lemmatised_tokens(text: str) -> list[str]:
    """spaCy tokenisation + lemmatisation, stop words and punctuation removed."""
    doc = get_nlp()(text)
    tokens = []
    for token in doc:
        if token.is_space or token.is_punct or token.is_stop:
            continue
        lemma = token.lemma_.lower().strip() if token.lemma_ else token.text.lower().strip()
        if len(lemma) > 1:
            tokens.append(lemma)
    return tokens
