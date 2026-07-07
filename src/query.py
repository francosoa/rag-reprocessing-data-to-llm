from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="intfloat/multilingual-e5-base"
)

vector_store = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings
)

results = vector_store.similarity_search(
    "What technologies does Francisco know?",
    k=5
)

for doc in results:
    print("=" * 50)
    print(doc.page_content)