from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from pathlib import Path

import re

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REGULATIONS_DIR = PROJECT_ROOT / "research" / "regulations"

REGULATION_NAME_MAP = {
    "eu_ai_act": "EU AI Act",
    "gdpr": "GDPR",
    "espr_dpp": "ESPR/DPP (EU 2024/1781)",
    "lopdgdd": "LOPDGDD",
    "ley_13_2022": "Ley 13/2022",
}


def load_documents():
    reader = SimpleDirectoryReader(
        input_dir=str(REGULATIONS_DIR),
        required_exts=[".pdf"],
        file_metadata=lambda path: {
            "regulation_name": REGULATION_NAME_MAP.get(
                Path(path).stem, Path(path).stem
            ),
            "regulation_type": Path(path).stem,
            "source_path": path,
        },
    )
    return reader.load_data()


def chunk_documents(documents):
    splitter = SentenceSplitter(
        chunk_size=512,
        chunk_overlap=64,
    )

    nodes = splitter.get_nodes_from_documents(documents)

    for node in nodes:
        text = node.get_content()

        article_match = re.search(r"Article\s+(\d+)", text, re.IGNORECASE)
        node.metadata["article_number"] = (
            article_match.group(1) if article_match else "unknown"
        )

        section_match = re.search(
            r"(?:Section|Chapter)\s+(\d+[\w.]*)", text, re.IGNORECASE
        )
        node.metadata["section"] = (
            section_match.group(1) if section_match else "unknown"
        )

    return nodes
