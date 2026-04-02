def split_legal_text(text: str, chunk_size: int = 1000, overlap: int = 200):
    """
    The 'Editor': Breaks long contracts into smaller, overlapping pieces.
    Overlap ensures we don't cut a legal clause in half!
    """
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunk = text[i : i + chunk_size]
        chunks.append(chunk)
    return chunks