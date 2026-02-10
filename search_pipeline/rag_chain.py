from search_pipeline.retriever import get_retriever
from search_pipeline.llm import get_llm


def answer_question(question):

    retriever = get_retriever()
    llm = get_llm()

    # --- Step 1: Retrieve documents ---
    docs = retriever.vectorstore.similarity_search_with_score(question, k=5)

    print("\n🔍 Retrieved Chunks:\n")

    context = []
    scores = []

    for i, (doc, score) in enumerate(docs):
        print(f"Chunk {i+1} (score={score:.3f}):\n{doc.page_content}\n")
        context.append(doc.page_content.strip())
        scores.append(score)

    # --- Step 2: Smart relevance check (dynamic threshold) ---
    avg_score = sum(scores) / len(scores)

    # keyword safety check
    keyword_match = question.lower() in " ".join(context).lower()

    relevant = avg_score < 1.2 or keyword_match

    # --- Outside document ---
    if not relevant:

        choice = input(
            "\n⚠️ Question may be outside the uploaded documents.\n"
            "Answer using general knowledge? (yes/no): "
        )

        if choice.lower() != "yes":
            return "Okay 👍 Please ask a question related to the uploaded documents."

        resp = llm.invoke(question)
        return resp.content if hasattr(resp, "content") else str(resp)

    # --- Step 3: RAG Answer ---
    prompt = f"""
You are an AI Teacher Assistant.

RULES:
- Use ONLY the given context
- If context is insufficient say:
  "The document does not provide sufficient information."
- Give definition + explanation (5–7 sentences)
- Add bullet key points

Context:
{" ".join(context)}

Question:
{question}

Answer:
"""

    resp = llm.invoke(prompt)
    answer = resp.content if hasattr(resp, "content") else str(resp)

    # --- Insufficient context fallback ---
    if "The document does not provide sufficient information." in answer:

        choice = input(
            "\n⚠️ Not enough info in documents.\n"
            "Answer using general knowledge? (yes/no): "
        )

        if choice.lower() == "yes":
            resp = llm.invoke(question)
            return resp.content if hasattr(resp, "content") else str(resp)

        return "Okay 👍 Please ask a question related to the uploaded documents."

    return answer