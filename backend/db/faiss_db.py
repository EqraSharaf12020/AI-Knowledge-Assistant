import faiss
import os

# This points to the actual file that will be created in your db/ folder
DB_PATH = os.path.join(os.path.dirname(__file__), "legal_vector.index")

def save_index(index):
    """Saves the FAISS index to a physical file."""
    try:
        faiss.write_index(index, DB_PATH)
        print(f"💾 FAISS index successfully saved to: {DB_PATH}")
    except Exception as e:
        print(f"❌ Error saving FAISS index: {e}")

def load_index():
    """Loads the FAISS index from disk if it exists."""
    if os.path.exists(DB_PATH):
        print(f"📁 loading existing FAISS index from: {DB_PATH}")
        return faiss.read_index(DB_PATH)
    print("ℹ️ No existing FAISS index found. Starting fresh.")
    return None