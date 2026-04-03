def split_text_into_chunks(text, chunk_size=1000, chunk_overlap=200):
    """
    Splits long legal text into smaller, overlapping pieces 
    so the Vector DB can search through them easily.
    """
    if not text:
        return []
        
    chunks = []
    # Logic to slide through the text and create overlapping chunks
    # Overlap ensures no legal sentence is cut exactly in half
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += (chunk_size - chunk_overlap)
    
    return chunks