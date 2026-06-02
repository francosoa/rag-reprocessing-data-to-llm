#from IPython.display import JSON

import json
from unstructured_client.models import shared, operations
from unstructured_client.models.errors import SDKError

from unstructured.partition.html import partition_html
#from unstructured.partition.pptx import partition_pptx
from unstructured.staging.base import dict_to_elements, elements_to_json
from utils.api_auth import get_client

from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from langchain.chains.summarize import load_summarize_chain

#from IPython.display import Image
import requests 

client = get_client()

filename = "images/embedded-images-tables.jpg"

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
    hi_res_model_name="yolox",
    skip_infer_table_types=[],
    pdf_infer_table_structure=True,
    languages=["en"]
)

req = operations.PartitionRequest(
    partition_parameters=params
)

#Faz a requisição para API
try:
    response = client.general.partition(request=req)
    elements = dict_to_elements(response.elements)
    #print(f"AQUI: {json.dumps(response.elements[:3], indent=2)}")
except SDKError as e:
    print(f"An error occurred: {e}")

tables = [el for el in elements if el.category == "Table"]

#É bom converter para um formato de HTML
table_html = tables[0].metadata.text_as_html

llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-1106")
chain = load_summarize_chain(llm, chain_type="stuff")
chain.invoke([Document(page_content=table_html)])