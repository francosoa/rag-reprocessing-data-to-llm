from IPython.display import JSON

import json
import os 
from dotenv import load_dotenv
from unstructured_client import UnstructuredClient
from unstructured_client.models import shared, operations
from unstructured_client.models.errors import SDKError

from unstructured.partition.html import partition_html
#from unstructured.partition.pptx import partition_pptx
from unstructured.staging.base import dict_to_elements, elements_to_json

from IPython.display import Image
import requests 

load_dotenv()

UNSTRUCTURED_API_KEY = os.getenv("UNSTRUCTURED_API_KEY")
SERVER_URL = os.getenv("SERVER_URL")
print(f"API Key: {UNSTRUCTURED_API_KEY}")
client = UnstructuredClient(
    api_key_auth=UNSTRUCTURED_API_KEY
)

#Exemplo com HTML:
url_text = "https://medium.com/@cadacidente/tenho-medo-de-me-apaixonar-840ea8e7a4c0"
response = requests.get(url_text)
html_content = response.text

elements = partition_html(filename=html_content)

elements_dict = [el.to_dict() for el in elements]
example_output = json.dumps(elements_dict[11:15], indent=2)
#JSON(example_output)

#EXEMPLO COM PDF:
file_pdf_name = "boleto.pdf"

with open(file_pdf_name, "rb") as f:
    #o arquivo enviado para API
    files = shared.Files(
        content = f.read(),
        file_name=file_pdf_name
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
    languages=["pt"]
)

req = operations.PartitionRequest(
    partition_parameters=params
)

#Faz a requisição para API
try:
    response = client.general.partition(request=req)
    print(f"AQUI: {json.dumps(response.elements[:3], indent=2)}")
except SDKError as e:
    print(f"An error occurred: {e}")