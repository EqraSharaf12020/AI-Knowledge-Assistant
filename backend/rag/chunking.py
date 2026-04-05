import re


# Legal abbreviations that should NOT trigger sentence splits
LEGAL_ABBREVIATIONS = {
    'sec.', 'no.', 'vs.', 'art.', 'cl.', 'para.', 'sub.', 'exh.', 'sch.',
    'ltd.', 'inc.', 'corp.', 'et al.', 'i.e.', 'e.g.', 'dba.', 'esq.',
    'jr.', 'sr.', 'ph.d.', 'm.d.', 'b.a.', 'b.s.', 'm.a.', 'm.b.a.',
    'p.c.', 'llc.', 'llp.', 'pllc.', 'c.p.a.', 'esq.', 'etc.'
}


def _is_legal_abbreviation(word: str) -> bool:
    """Check if word (lowercase) is a legal abbreviation."""
    return word.lower() in LEGAL_ABBREVIATIONS


def _detect_section_header(line: str) -> str:
    """
    Detect if a line is a section header and return the section name.
    Returns empty string if not a header.
    
    Patterns:
    - "Section 1", "Section 2.3", "SECTION 2.3"
    - "Clause 4", "CLAUSE 4.1"
    - "Article I", "ARTICLE II"
    - Numbered: "1.", "2.1", "3.1.2" at start of stripped line
    - ALL CAPS: "PAYMENT TERMS", "GOVERNING LAW"
    """
    stripped = line.strip()
    
    if not stripped:
        return ""
    
    # Pattern 1: Section/Clause/Article with numbers
    section_pattern = r'^(?:Section|SECTION|Clause|CLAUSE|Article|ARTICLE)\s+[\d\.ivx]+[\.\s]*'
    match = re.match(section_pattern, stripped, re.IGNORECASE)
    if match:
        header = match.group().strip()
        return header
    
    # Pattern 2: Numbered like "1.", "2.1", "3.1.2" at start
    numbered_pattern = r'^[\d]+(?:\.[\d]+)*[\.\s]*[A-Z]'
    match = re.match(numbered_pattern, stripped)
    if match:
        # Extract the number part
        num_match = re.match(r'^([\d\.]+)', stripped)
        if num_match:
            num = num_match.group(1).rstrip('.')
            return num
    
    # Pattern 3: ALL CAPS heading (but not whole paragraph in caps)
    # Only if it's relatively short (< 60 chars) and mostly uppercase
    if len(stripped) < 60 and re.match(r'^[A-Z\s]+$', stripped) and ' ' in stripped:
        return stripped
    
    return ""


def _split_into_sentences(text: str) -> list:
    """
    Split text into sentences, respecting legal abbreviations.
    Returns list of sentences.
    """
    # Replace known abbreviations with placeholder to protect them
    protected_text = text
    abbrev_map = {}
    
    for i, abbr in enumerate(LEGAL_ABBREVIATIONS):
        placeholder = f"__ABBR_{i}__"
        abbrev_map[placeholder] = abbr
        # Case-insensitive replacement
        pattern = re.escape(abbr)
        protected_text = re.sub(pattern, placeholder, protected_text, flags=re.IGNORECASE)
    
    # Split on sentence boundaries: period, question mark, exclamation
    # But not if followed by lowercase (likely abbreviation) or number
    sentence_pattern = r'(?<!\s)([.!?])\s+(?=[A-Z])'
    
    sentences = []
    parts = re.split(sentence_pattern, protected_text)
    
    # Reconstruct sentences (split alternates between text and punctuation)
    current_sentence = ""
    for i, part in enumerate(parts):
        if i % 2 == 0:
            current_sentence += part
        else:
            current_sentence += part  # Add the punctuation back
            sentences.append(current_sentence.strip())
            current_sentence = ""
    
    if current_sentence.strip():
        sentences.append(current_sentence.strip())
    
    # Restore original abbreviations
    restored_sentences = []
    for sentence in sentences:
        restored = sentence
        for placeholder, abbr in abbrev_map.items():
            restored = restored.replace(placeholder, abbr)
        restored_sentences.append(restored)
    
    return [s for s in restored_sentences if s]


def split_text_into_chunks(text, chunk_size=1000, chunk_overlap=200, return_metadata=False):
    """
    Splits legal text into chunks with sentence awareness and section detection.
    
    Args:
        text: Input legal document text
        chunk_size: Target size per chunk in characters
        chunk_overlap: Overlap between consecutive chunks in characters
        return_metadata: If True, return list of dicts with metadata; if False, return list of strings
    
    Returns:
        - If return_metadata=False: list of strings (backward compatible)
        - If return_metadata=True: list of dicts with {"text", "chunk_index", "section", "char_start", "char_end", "word_count"}
    """
    if not text:
        return []
    
    chunks_data = []
    current_section = "General"
    char_position = 0
    chunk_index = 0
    
    # Split into lines to detect sections
    lines = text.split('\n')
    
    current_chunk_text = ""
    current_chunk_start = 0
    
    for line_idx, line in enumerate(lines):
        # Check for section header
        section_name = _detect_section_header(line)
        if section_name:
            # If we have a current chunk, save it
            if current_chunk_text.strip():
                chunk_dict = {
                    "text": current_chunk_text.strip(),
                    "chunk_index": chunk_index,
                    "section": current_section,
                    "char_start": current_chunk_start,
                    "char_end": char_position,
                    "word_count": len(current_chunk_text.split())
                }
                chunks_data.append(chunk_dict)
                chunk_index += 1
            
            # Update section and start new chunk
            current_section = section_name
            current_chunk_text = line + "\n"
            current_chunk_start = char_position
            char_position += len(line) + 1
            continue
        
        # Add line to current chunk
        potential_chunk = current_chunk_text + line + "\n"
        char_position += len(line) + 1
        
        if len(potential_chunk) >= chunk_size:
            # Need to split this chunk
            if current_chunk_text.strip():
                # Save current chunk
                chunk_dict = {
                    "text": current_chunk_text.strip(),
                    "chunk_index": chunk_index,
                    "section": current_section,
                    "char_start": current_chunk_start,
                    "char_end": char_position - len(line) - 1,
                    "word_count": len(current_chunk_text.split())
                }
                chunks_data.append(chunk_dict)
                chunk_index += 1
                
                # Start new chunk with overlap
                # Recalculate: we want to include some overlap from previous chunk
                overlap_text = current_chunk_text.strip()[-chunk_overlap:] if len(current_chunk_text.strip()) > chunk_overlap else current_chunk_text.strip()
                current_chunk_text = overlap_text + "\n" + line + "\n"
                current_chunk_start = max(0, char_position - len(overlap_text) - len(line) - 2)
            else:
                current_chunk_text = line + "\n"
                current_chunk_start = char_position - len(line) - 1
        else:
            current_chunk_text = potential_chunk
    
    # Don't forget the last chunk
    if current_chunk_text.strip():
        chunk_dict = {
            "text": current_chunk_text.strip(),
            "chunk_index": chunk_index,
            "section": current_section,
            "char_start": current_chunk_start,
            "char_end": char_position,
            "word_count": len(current_chunk_text.split())
        }
        chunks_data.append(chunk_dict)
    
    if return_metadata:
        return chunks_data
    else:
        # Backward compatible: return just the text strings
        return [chunk["text"] for chunk in chunks_data]