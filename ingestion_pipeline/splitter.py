from langchain_text_splitters import RecursiveCharacterTextSplitter

def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )

    # Debug prints
    print(f"Chunk size: {splitter._chunk_size}")
    print(f"Chunk overlap: {splitter._chunk_overlap}")

    split_docs = splitter.split_documents(documents)
    print(split_docs[0].metadata)

    return split_docs
