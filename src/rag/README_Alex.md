# src/rag/ — Alex

This folder is the full RAG pipeline. You own everything here.

Step 1 — Ingest
Load the regulation PDFs from research/regulations/ using LlamaIndex
SimpleDirectoryReader. Attach regulation name, article number, and section
as metadata on every chunk so we can filter and cite them later.

Step 2 — Chunk
Split documents at article level using SentenceSplitter.
Target chunk size: 400–600 tokens with overlap.

Step 3 — Embed
Embed locally with sentence-transformers/all-MiniLM-L6-v2.
This runs fully on device — no external API calls. Keep it that way.
GDPR requires we don't send regulation content to third-party embedding services.

Step 4 — Index
Store vectors and metadata in Qdrant.
Tag each chunk with regulation type and article number so queries
can filter by source at retrieval time.

Step 5 — Query
On query: embed the query locally → similarity search top-k=5 →
pass retrieved chunks to Mistral Large for synthesis.
Mistral is accessed via the Mistral AI API — key is MISTRAL_API_KEY in .env.

Output
Your output must be a structured object containing:
- The compliance rules relevant to the query
- Article citations (regulation name + article number + source URL)
- A regulationRefs array formatted and ready to drop into the VC payload

This output feeds directly into Javier's VC builder — coordinate with him
on the exact schema so it plugs in cleanly.
