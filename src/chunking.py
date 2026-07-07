from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

#Seria melhor aplicar um chunk por semantica e não por size: Repensar na lógica 
def chunk_documents(documents, chunk_size=1000, chunk_overlap=200):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, 
        chunk_overlap=chunk_overlap,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            ""
        ]
    )
    return text_splitter.split_documents(documents)


def create_vector_store(
    chunks,
    embeddings,
    persist_directory="./chroma_db"
):

    return Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_directory
    )