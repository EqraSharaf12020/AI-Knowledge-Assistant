# Training the Knowledge Base

Your Legal AI Assistant now supports a global knowledge base that enhances Q&A responses with pre-trained documents.

## How It Works

1. **Upload Training Documents**: Place any PDF, DOCX, or TXT files in `backend/data/documents/`
2. **Run Training**: Execute the training script to process and embed all documents
3. **Enhanced Q&A**: When users ask questions, the system searches both:
   - Session-specific documents (uploaded PDFs)
   - Global knowledge base (pre-trained documents)

## Training Process

### Step 1: Add Documents
Copy your training documents to `backend/data/documents/`:
```
backend/data/documents/
├── legal_terms.pdf
├── contract_templates.docx
├── company_policies.txt
└── industry_standards.pdf
```

### Step 2: Run Training

**Fresh Training** (clears previous knowledge base, trains only on current documents):
```bash
cd backend
python train.py
```

**Append Training** (keeps previous knowledge base, adds new documents):
```bash
cd backend
python train.py --append
```

The script will:
- Clear previous knowledge base (fresh training) or append (append mode)
- Extract text from all supported files (PDF, DOCX, TXT) currently in the folder
- Split text into chunks with legal section detection
- Generate embeddings using BAAI/bge-small-en-v1.5
- Store everything in `backend/data/vector_store/global.index`

### Step 3: Start the Application
Run your backend and frontend as usual. The global knowledge base is automatically loaded.

## Supported Document Types

- **PDF**: Full text extraction
- **DOCX**: Microsoft Word documents
- **TXT**: Plain text files

## Benefits

- **Broader Knowledge**: Answers draw from both uploaded documents and training data
- **Better Context**: More comprehensive responses for legal questions
- **Persistent Learning**: Knowledge base persists across sessions
- **Flexible Sources**: Mix different document types in training

## Technical Details

- **Chunking**: 1000 characters with 200 character overlap
- **Embeddings**: 384-dimensional vectors
- **Search**: Combined results from session + global indices, reranked by relevance
- **Storage**: FAISS index + JSON metadata in `backend/data/vector_store/`

## Updating the Knowledge Base

### Fresh Training (Default)
To train **only on documents currently in the folder** and discard previous training:
```bash
python train.py
```
This:
- ✓ Clears old knowledge base
- ✓ Trains only on what's currently in `backend/data/documents/`
- ✓ Useful when you want to start fresh with new documents

### Append Training
To **add new documents while keeping previous training**:
```bash
python train.py --append
```
This:
- ✓ Keeps existing knowledge base
- ✓ Adds new documents from folder
- ✓ Useful when expanding knowledge gradually

## Clearing the Knowledge Base

The knowledge base is automatically cleared on each fresh training. To manually clear:

```bash
# Option 1: Delete the files
rm backend/data/vector_store/global.index
rm backend/data/vector_store/global_meta.json

# Option 2: Run fresh training (no files in documents folder)
python train.py
```