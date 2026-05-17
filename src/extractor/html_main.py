from IPython.display import JSON
import json
from unstructured.partition.html import partition_html
#from unstructured.partition.pptx import partition_pptx
import requests 
    
#Exemplo com HTML:
def extract_html_content(url_text):
    response = requests.get(url_text)
    html_content = response.text

    elements = partition_html(filename=html_content)

    elements_dict = [el.to_dict() for el in elements]
    example_output = json.dumps(elements_dict[11:15], indent=2)
    return JSON(example_output)

extract_html_content("https://medium.com/@cadacidente/tenho-medo-de-me-apaixonar-840ea8e7a4c0")
