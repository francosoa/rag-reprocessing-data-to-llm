from dataclasses import dataclass
from typing import Any

#Estudar mais sobre isso
@dataclass(slots=True)
class ExtractedDocument:
    """
    Representa um documento processado pela API da Unstructured.
    """

    source: str
    elements: list[Any]