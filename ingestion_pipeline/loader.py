
from langchain_community.document_loaders import PyPDFLoader
import os
import re

def load_pdfs(pdf_folder):
    documents = []

    for file in os.listdir(pdf_folder):
        if file.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(pdf_folder, file))
            docs = loader.load()

            for doc in docs:
                # Simple cleaning
                text = re.sub(r'\s+', ' ', doc.page_content)
                doc.page_content = text.strip()

            documents.extend(docs)

    return documents
