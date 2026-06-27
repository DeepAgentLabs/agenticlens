import hashlib


def prefix_hash(text: str, n_words: int) -> str:
    """Hash the first `n_words` whitespace-split words of `text`.

    Word-splitting is a deliberate approximation for prefix-matching (detecting
    repeated prompts) -- it is not a token count and should not be used for billing.
    """
    prefix = " ".join(text.split()[:n_words])
    return hashlib.sha256(prefix.encode("utf-8")).hexdigest()
