# AI Maintenance Assistant for Fanuc Robodrill  
Offline RAG system for CNC diagnostics and maintenance

---

## Overview

This project implements a fully offline Retrieval-Augmented Generation (RAG) assistant designed for Fanuc Robodrill CNC machines.  
The system processes the 988‑page Robodrill Operation & Maintenance Manual, extracts structured knowledge, builds a local vector database, and integrates with a locally hosted LLM (Ollama + Llama3) to answer technical maintenance and diagnostic questions.

All data stays on‑premise, making the solution suitable for industrial environments with strict confidentiality requirements.

---

# 1. Data Engineering

## 1.1 PDF Extraction

The manual *Robodrill_Operation_And_Maintenance_Handbook_16i_160i_160is_18i_180i* is parsed using **pyMuPDF**, which handles:

- mixed formatting (text + diagrams),
- irregular PDF structures,
- page-level text extraction.

Processing steps:

- load PDF  
- clean empty lines and broken fragments  
- normalize whitespace  
- store cleaned text  

---

## 1.2 Chapter Extraction

The system reconstructs the chapter structure using the PDF outline.

Process:

- read bookmarks  
- extract chapter titles + starting pages  
- compute page ranges  
- extract text for each chapter  
- return structured objects: `{ chapter_title, chapter_text }`

Detected chapters include:

- PREFACE  
- 1. SCREEN DISPLAY AND OPERATION  
- 2. OPERATION LIST  
- 3. G CODE  
- 4. PROGRAM FORMAT  
- 5. CUSTOM MACRO  
- 6. HARDWARE  
- 7. PARAMETERS  
- 8. ALARM LIST  
- 9. SIGNAL LIST  
- 10. PMC  
- 11. ETHERNET  
- 12. POWER MATE CNC MANAGER  
- 13. DIAGNOSIS INFORMATION  
- 14. HISTORY FUNCTION  
- 15. WAVEFORM DIAGNOSTIC FUNCTION  
- 16. DIGITAL SERVO  
- 17. AC SPINDLE  
- 18. MAINTENANCE INFORMATION  
- 19. MAINTENANCE FUNCTION  

---

## 1.3 Chunking & Embeddings

### Chunking
- `chunk_size = 1500`
- overlapping enabled
- each chunk contains text + metadata + unique ID

### Embeddings
Model: **sentence-transformers/all-MiniLM-L6-v2**

Key characteristics:

- 6 Transformer layers  
- self-attention + FFN  
- residual connections + LayerNorm  
- mean pooling → 384‑dim vector  

Trained on:

- paraphrase mining  
- semantic similarity  
- Q&A datasets  
- large-scale internet corpora  

---

# 2. Local Vector Database (ChromaDB)

## 2.1 Database Construction

`create_vector_db()`:

- generates embeddings  
- assigns unique IDs  
- stores text, embeddings, metadata  
- builds a local semantic index  

---

## 2.2 Query Pipeline

`ask_the_manual(query)`:

1. load ChromaDB  
2. embed user query  
3. retrieve top‑3 most similar chunks  
4. return chapter names + text fragments  
5. pass retrieved context to LLM  

This ensures answers remain grounded in the manual.

---

# 3. LLM Integration (Ollama + Llama3)

## 3.1 Offline Execution

The system uses **Ollama** to run Llama3 locally.

Benefits:

- no cloud dependency  
- no data leaves the factory network  
- NDA‑safe  
- suitable for industrial deployment  

---

## 3.2 RAG Workflow

1. User asks a question  
2. System retrieves relevant manual fragments  
3. Fragments are inserted into the LLM prompt  
4. Llama3 generates a technical answer  
5. System displays:
   - final answer  
   - chapters used as sources  

---

## 3.3 Example Queries

### Daily maintenance procedure  
Sources: *SAFETY PRECAUTIONS*, *18. MAINTENANCE INFORMATION*

### APC battery location & replacement  
Sources: *16. DIGITAL SERVO*, *13. DIAGNOSIS INFORMATION*, *SAFETY PRECAUTIONS*, *8. ALARM LIST*

### G76 fine boring cycle parameters  
Sources: *3. G CODE*, *7. PARAMETERS*, *4. PROGRAM FORMAT*, *8. ALARM LIST*

---

# 4. Notebooks

## 4.1 `01_data_engineering.ipynb`
Includes:

- PDF loading  
- text cleaning  
- chapter extraction  
- chunking  
- embedding generation  

Outputs:

- cleaned text  
- chapter dataset  
- chunk dataset  
- embedding vectors  

---

## 4.2 `02_vector_db_and_rag.ipynb`
Includes:

- building ChromaDB  
- semantic search  
- RAG pipeline  
- Ollama integration  
- example queries  

Outputs:

- local vector DB  
- working RAG assistant  

---

# 5. System Architecture
PDF Manual (988 pages)
↓
pyMuPDF Extraction
↓
Chapter Reconstruction
↓
Chunking + Embeddings (MiniLM-L6-v2)
↓
ChromaDB (local vector store)
↓
Semantic Retrieval
↓
LLM (Ollama + Llama3)
↓
Final Answer + Sources


---

# 6. Why Offline RAG?

Industrial CNC environments require:

- confidentiality of machine parameters  
- protection of maintenance logs  
- NDA compliance  
- zero cloud data transfer  

Local execution ensures:

- full data privacy  
- no external dependencies  
- safe deployment in production environments  

---

# 7. How to Run

### Requirements
- Python 3.10+  
- pyMuPDF  
- sentence-transformers  
- ChromaDB  
- Ollama installed locally  
- Llama3 model pulled via:



