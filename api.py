from fastapi import FastAPI
from pydantic import BaseModel
from search_pipeline.rag_chain import answer_question
import logging

# ----------------------------
# Logging
# ----------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ----------------------------
# App
# ----------------------------
app = FastAPI()

class Query(BaseModel):
    question: str
    session_id: str = "default"
    use_general: bool = False


@app.post("/ask")
def ask(query: Query):

    logger.info(f"Question: {query.question}")

    try:
        result = answer_question(
            question=query.question,
            session_id=query.session_id,
            use_general=query.use_general
        )
        return result

    except Exception as e:
        logger.error(str(e))
        return {
            "status": "error",
            "message": "Something went wrong."
        }