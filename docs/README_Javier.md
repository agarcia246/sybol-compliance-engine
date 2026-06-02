# docs/ — Javier

You own the technical documentation in this folder.
Keep it up to date as the system evolves — Jana uses this to write
paper Chapter 4, so accuracy here directly affects the paper.

Create two files:

architecture.md
Describe the four system components and how data flows between them:
RAG Compliance Engine → Media Scoring Module → VC Generation Layer →
Sybol Identity Integration. Include the supporting infrastructure
(FastAPI, Qdrant, Railway). Keep it plain enough that a non-technical
reader can follow it.

vc_schema.md
Document every field in the Verifiable Credential with its type,
description, and example value. Use the field list from
src/credentials/README_Javier.md as your source.
