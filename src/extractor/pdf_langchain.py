import json
from unstructured_client.models import shared, operations
from unstructured_client.models.errors import SDKError
from chunking import chunk_documents
from unstructured.partition.html import partition_html
#from unstructured.partition.pptx import partition_pptx
from unstructured.staging.base import dict_to_elements, elements_to_json
from utils.api_auth import get_client
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
#from IPython.display import Image
import requests 
from collections import defaultdict

client = get_client()
file_pdf_name = "C:\\Users\\valde\\rag-reprocessing-data-to-llm\\src\\extractor\\files\\EN-FRANCISCO-MOTA-CV.pdf"

def load_pdf_file(file_path: str) -> shared.Files:
    """Lê o PDF e retorna o objeto Files da API."""

    with open(file_path, "rb") as f:
        content = f.read()

    return shared.Files(
        content=content,
        file_name=file_path,
    )


def create_partition_params(files: shared.Files, languages:list) -> shared.PartitionParameters:
    """Cria os parâmetros de processamento da Unstructured."""

    return shared.PartitionParameters(
        files=files,
        strategy="hi_res",
        pdf_infer_table_structure=True,
        skip_infer_table_types=[],
        languages=languages,
    )


def extract_elements(client, partition_params):
    """Executa o processamento do documento na API."""

    response = client.general.partition(
        request=operations.PartitionRequest(
            partition_parameters=partition_params
        )
    )

    return response.elements

def build_element_map(elements):

    return {
        element["element_id"]: element
        for element in elements
    }

def build_children_map(elements):
    """Cria o relacionamento pai -> filhos."""

    children = defaultdict(list)

    for element in elements:

        parent_id = element["metadata"].get("parent_id")

        if parent_id:
            children[parent_id].append(element)

    return children

def find_root_elements(elements):

    roots = []

    for element in elements:

        if not (
            element["metadata"]
            .get("parent_id")
        ):
            roots.append(element)

    return roots

def build_section_text(
    element,
    children_map
):

    text = element["text"]

    children = children_map.get(
        element["element_id"],
        []
    )

    for child in children:

        text += "\n\n"

        text += build_section_text(
            child,
            children_map
        )

    return text

def root_to_document(
    root,
    children_map,
    source_name
):

    section_text = build_section_text(
        root,
        children_map
    )

    return Document(
        page_content=section_text,
        metadata={
            "root_element_id":
                root["element_id"],

            "category":
                root["type"],

            "page_number":
                root["metadata"]
                .get("page_number"),

            "source":
                source_name
        }
    )

def build_hierarchical_documents(
    roots,
    children_map,
    source_name
):

    return [

        root_to_document(
            root,
            children_map,
            source_name
        )

        for root in roots
    ]

files = load_pdf_file(
    file_pdf_name
)

partition_params = (
    create_partition_params(
        files,
        languages=["eng"]
    )
)

elements = extract_elements(
    client,
    partition_params
)

element_map = build_element_map(
    elements
)

children_map = build_children_map(
    elements
)

roots = find_root_elements(
    elements
)

documents = (
    build_hierarchical_documents(
        roots,
        children_map,
        "EN-FRANCISCO-MOTA-CV.pdf"
    )
)

chunks = chunk_documents(documents)