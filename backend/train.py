#!/usr/bin/env python3
"""
Training script for the Legal AI Knowledge Assistant.

This script processes all documents in the backend/data/documents/ folder
and stores their embeddings in the global vector database for enhanced Q&A.

Usage:
    python train.py              # Fresh training (clears previous knowledge base)
    python train.py --append     # Append to existing knowledge base
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from services.document_service import extract_text_from_file
from services.vector_service import add_global_documents
from rag.chunking import split_text_into_chunks

def clear_global_knowledge_base():
    """Delete existing global knowledge base to start fresh."""
    vector_store_dir = backend_dir / "data" / "vector_store"
    
    if vector_store_dir.exists():
        index_file = vector_store_dir / "global.index"
        meta_file = vector_store_dir / "global_meta.json"
        
        if index_file.exists():
            os.remove(index_file)
            print(f"  ✓ Removed old index: {index_file.name}")
        
        if meta_file.exists():
            os.remove(meta_file)
            print(f"  ✓ Removed old metadata: {meta_file.name}")

def train_knowledge_base(fresh: bool = True):
    """
    Process all documents in data/documents/ and add to global knowledge base.
    
    Args:
        fresh (bool): If True, clear previous knowledge base before training.
                     If False, append to existing knowledge base.
    """
    documents_dir = backend_dir / "data" / "documents"

    if not documents_dir.exists():
        print(f"Documents directory not found: {documents_dir}")
        print("Please create the directory and add training documents.")
        return

    # Clear previous knowledge base if fresh training
    if fresh:
        print("🔄 Clearing previous knowledge base...")
        clear_global_knowledge_base()
        print()

    # Get all supported files
    supported_extensions = {'.pdf', '.docx', '.txt'}
    document_files = []

    for file_path in documents_dir.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
            document_files.append(file_path)

    if not document_files:
        print(f"❌ No supported documents found in {documents_dir}")
        print("Supported formats: PDF, DOCX, TXT")
        return

    document_files.sort()  # Sort for consistent training

    print(f"📚 Found {len(document_files)} documents to process:")
    for doc in document_files:
        print(f"   - {doc.name}")
    print()

    total_chunks = 0
    total_skipped = 0

    for doc_path in document_files:
        print(f"Processing: {doc_path.name}")

        # Extract text
        text = extract_text_from_file(str(doc_path))
        
        # Check for errors
        if not text or not text.strip():
            print(f"  ❌ Failed: No text extracted")
            print(f"     File size: {doc_path.stat().st_size} bytes")
            print(f"     This may be a scanned/image-based PDF or encrypted file.")
            total_skipped += 1
            continue
        
        if "Error" in text:
            print(f"  ❌ Failed to extract text")
            print(f"     Reason: {text}")
            total_skipped += 1
            continue

        print(f"  ✓ Extracted {len(text)} characters")

        # Split into chunks
        chunks = split_text_into_chunks(text, return_metadata=True)
        print(f"  ✓ Split into {len(chunks)} chunks")

        # Add to global knowledge base
        add_global_documents(chunks, source_file=doc_path.name)
        total_chunks += len(chunks)

    print("\n" + "="*60)
    print("🎉 Training Complete!")
    print("="*60)
    print(f"✓ Total chunks added: {total_chunks}")
    if total_skipped > 0:
        print(f"⚠ Documents skipped: {total_skipped}")
    print(f"📝 Knowledge base saved to: backend/data/vector_store/")
    print(f"💡 Tip: Run 'python train.py --append' to add more documents later")
    print("="*60)

if __name__ == "__main__":
    # Check for command line arguments
    fresh_training = True
    
    if "--append" in sys.argv:
        fresh_training = False
        print("🚀 Starting Legal AI Knowledge Base Training (Append Mode)")
        print("   (Previous knowledge base will be preserved)")
    else:
        print("🚀 Starting Legal AI Knowledge Base Training (Fresh Mode)")
        print("   (Previous knowledge base will be cleared)")
    
    print()
    train_knowledge_base(fresh=fresh_training)