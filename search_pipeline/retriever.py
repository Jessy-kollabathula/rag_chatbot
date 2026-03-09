import os
os.environ["HF_HUB_OFFLINE"] = "1"

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings


def get_retriever():

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectorstore = FAISS.load_local(
        "faiss_index",
        embeddings,
        allow_dangerous_deserialization=True
    )

    # 🔍 Print number of chunks (vectors)
    print(f"Total vectors stored in FAISS: {vectorstore.index.ntotal}")
    
    # ✅ Advanced retrieval: MMR (diverse + better chunks)
    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 5,          # fetch more chunks
            "fetch_k": 10    # search deeper
        }
    )

    return retriever
