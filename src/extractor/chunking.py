from langchain.text_splitter import RecursiveCharacterTextSplitter

#Seria melhor aplicar um chunk por semantica e não por tamanaho: Repensar na lógica 
def chunk_documents(documents, chunk_size=1000, chunk_overlap=200, separator="\n\n"):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separator=separator
    )
    return text_splitter.split_documents(documents)

