from utils.config import get_client
from collections.abc import Iterator
from pathlib import Path
from unstructured_client.models import shared, operations
from models.schemas import ExtractedDocument

client = get_client()

def load_pdf_files(directory: str) -> Iterator[shared.Files]:
    """
    Percorre um diretório e produz um arquivo PDF por vez.
    """

    for pdf_path in Path(directory).glob("*.pdf"):
        with open(pdf_path, "rb") as f:
            yield shared.Files(
                content=f.read(),
                file_name=pdf_path.name,
            )


def create_partition_params(
    file: shared.Files,
    languages: list[str] | None = None,
) -> shared.PartitionParameters:
    """
    Cria os parâmetros de processamento da Unstructured.
    """

    if languages is None:
        languages = ["eng"]

    return shared.PartitionParameters(
        files=file,
        strategy="hi_res",
        pdf_infer_table_structure=True,
        skip_infer_table_types=[],
        languages=languages,
    )

def extract_elements(
    client,
    partition_params: shared.PartitionParameters,
):
    """
    Envia o documento para a API e retorna os elementos extraídos.
    """

    response = client.general.partition(
        request=operations.PartitionRequest(
            partition_parameters=partition_params
        )
    )

    return response.elements

def process_pdf(
    client,
    pdf_file: shared.Files,
    languages: list[str] | None = None,
):
    params = create_partition_params(
        pdf_file,
        languages
    )

    elements = extract_elements(
        client,
        params
    )

    return ExtractedDocument(
    source=pdf_file.file_name,
    elements=elements,
)