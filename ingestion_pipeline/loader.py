from langchain_community.document_loaders import PyPDFLoader
import os


def load_pdfs(pdf_folder):
    documents = []
    for file in os.listdir(pdf_folder):
        if file.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(pdf_folder, file))
            documents.extend(loader.load())
    return documents
