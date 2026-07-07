import os 
from dotenv import load_dotenv
from unstructured_client import UnstructuredClient

load_dotenv()

def get_client():
    UNSTRUCTURED_API_KEY = os.getenv("UNSTRUCTURED_API_KEY")
    client = UnstructuredClient(
        api_key_auth=UNSTRUCTURED_API_KEY
    )
    return client