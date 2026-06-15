import logging
import os

from llama_index.core import VectorStoreIndex
from llama_index.llms.mistralai import MistralAI

from .models import ComplianceResult, RegulationRef

logger = logging.getLogger(__name__)

SYNTHESIS_PROMPT = """
You are a EU regulatory compliance expert. Using ONLY the provided regulation excerpts,
answer the query. Be precise about which article you are citing.
If a requirement is not covered by the excerpts, say so explicitly.
"""


def _validate_refs(refs: list[RegulationRef]) -> list[RegulationRef]:
    """Drop citations with missing attribution (Unknown regulation/article)."""
    valid = []
    for ref in refs:
        if ref.regulation == "Unknown" or ref.article == "Unknown":
            logger.warning(
                "Dropping hallucinated/unattributed citation: regulation=%r article=%r",
                ref.regulation,
                ref.article,
            )
        else:
            valid.append(ref)
    return valid


def query_regulations(
    query: str,
    index: VectorStoreIndex,
    regulation_type: str | None = None,
) -> ComplianceResult:
    llm = MistralAI(
        model="mistral-large-latest",
        api_key=os.environ["MISTRAL_API_KEY"],
        system_prompt=SYNTHESIS_PROMPT,
    )

    filters = None
    if regulation_type:
        from llama_index.core.vector_stores import MetadataFilter, MetadataFilters

        filters = MetadataFilters(
            filters=[
                MetadataFilter(
                    key="regulation_type",
                    value=regulation_type,
                )
            ]
        )

    retriever = index.as_retriever(similarity_top_k=5, filters=filters)
    nodes = retriever.retrieve(query)

    refs = []
    for node in nodes:
        meta = node.node.metadata
        refs.append(
            RegulationRef(
                regulation=meta.get("regulation_name", "Unknown"),
                article=meta.get("article_number", "Unknown"),
                source_url=meta.get("source_path", ""),
                excerpt=node.node.get_content()[:300],
            )
        )

    context = "\n\n---\n\n".join(n.node.get_content() for n in nodes)
    response = llm.complete(f"Context:\n{context}\n\nQuery: {query}")

    return ComplianceResult(
        summary=str(response),
        regulation_refs=_validate_refs(refs),
    )
