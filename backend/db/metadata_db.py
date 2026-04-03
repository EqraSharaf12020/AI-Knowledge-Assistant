import json
import os

# This points to the JSON file that will store the text chunks
METADATA_PATH = os.path.join(os.path.dirname(__file__), "metadata.json")

def save_metadata(chunks):
    """Saves the list of text strings to a JSON file."""
    try:
        with open(METADATA_PATH, "w", encoding="utf-8") as f:
            json.dump(chunks, f, indent=4)
        print(f"📝 Metadata (text chunks) saved to: {METADATA_PATH}")
    except Exception as e:
        print(f"❌ Error saving metadata: {e}")

def load_metadata():
    """Loads the text chunks from the JSON file."""
    if os.path.exists(METADATA_PATH):
        try:
            with open(METADATA_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading metadata: {e}")
    return []