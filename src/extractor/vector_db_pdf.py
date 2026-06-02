# Warning control
import warnings
import logging
from utils.api_auth import get_client
import json
from IPython.display import JSON

from unstructured_client import UnstructuredClient
from unstructured_client.models import shared, operations
from unstructured_client.models.errors import SDKError

from unstructured.chunking.basic import chunk_elements
from unstructured.chunking.title import chunk_by_title
from unstructured.staging.base import dict_to_elements
from IPython.display import Image

import chromadb

client = get_client()


warnings.filterwarnings('ignore')
logger = logging.getLogger()
logger.setLevel(logging.CRITICAL)

#Começar a codar o RAG:
Image(filename='images/winter-sports-cover.png', height=400, width=400)

#Run the document through the Unstructured API
filename = "files/winter-sports.pdf"

with open(filename, "rb") as f:
    #o arquivo enviado para API
    files = shared.Files(
        content = f.read(),
        file_name=filename
    )
#parâmetros da extração
"""
This is a data structure.

It organizes:

the binary content
metadata about the file
"""
params = shared.PartitionParameters(
    files=files,
    strategy="hi_res",
    pdf_infer_table_structure=True,
    languages=["en"]
)

req = operations.PartitionRequest(
    partition_parameters=params
)

#Faz a requisição para API
try:
    response = client.general.partition(request=req)
    #print(f"AQUI: {json.dumps(response.elements[:3], indent=2)}")
except SDKError as e:
    print(f"An error occurred: {e}")

## Find elements associated with chapters
teste = [x for x in response.elements if x['type'] == 'Title' and 'hockey' in x['text'].lower()]

chapters = [
    "THE SUN-SEEKER",
    "RINKS AND SKATERS",
    "TEES AND CRAMPITS",
    "ICE-HOCKEY",
    "SKI-ING",
    "NOTES ON WINTER RESORTS",
    "FOR PARENTS AND GUARDIANS",
]

# In this part of the code I'm trying to find the chapters id's.
def get_chapter_ids(elements, chapters):
    chapter_ids = {}

    for element in elements:
        for chapter in chapters:
            if chapter in element['text'] and element['type'] == 'Title':
                chapter_ids[element['element_id']] = chapter
                break
    return chapter_ids

chapter_ids = get_chapter_ids(response.elements, chapters)

chapter_to_id = {v: k for k, v in chapter_ids.items()}
print(chapter_to_id)

## Load documents into a vector db
client = chromadb.PersistentClient(path="chroma_tmp", settings=chromadb.Settings(allow_reset=True))
client.reset()

collection = client.create_collection(
    name="winter_sports",
    metadata={"hnsw:space": "cosine"}
)

#I'm assign a chapter to each element based on the parent_id. If the parent_id is in the chapter_ids, I assign the chapter to the element. Otherwise, I assign an empty string.
for element in response.elements:
    parent_id = element["metadata"].get("parent_id")
    chapter = chapter_ids.get(parent_id, "")
    collection.add(
        documents=[element["text"]],
        ids=[element["element_id"]],
        metadatas=[{"chapter": chapter}]
    )

#See the elements in Vector DB
results = collection.peek()
print(results["documents"])

## Perform a hybrid search with metadata
result = collection.query(
    query_texts=["How many players are on a team?"],
    n_results=2,
    where={"chapter": "ICE-HOCKEY"},
)
print(json.dumps(result, indent=2))

## Chunking Content

elements = dict_to_elements(response.elements)

chunks = chunk_by_title(
    elements,
    combine_text_under_n_chars=100,
    max_characters=3000,
)