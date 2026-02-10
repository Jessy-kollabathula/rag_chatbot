import os
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI

load_dotenv()


def get_llm():

    llm = ChatMistralAI(
        model="mistral-small",
        temperature=0.4
    )

    return llm