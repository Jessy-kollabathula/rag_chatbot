from search_pipeline.retriever import get_retriever
from search_pipeline.llm import get_llm

# -------------------------
# In-Memory Conversation Store
# -------------------------
chat_sessions = {}

def get_history(session_id):
    return chat_sessions.get(session_id, [])

def append_history(session_id, role, content):
    if session_id not in chat_sessions:
        chat_sessions[session_id] = []
    chat_sessions[session_id].append({
        "role": role,
        "content": content
    })

    # Keep last 6 messages (3 exchanges)
    chat_sessions[session_id] = chat_sessions[session_id][-6:]


def answer_question(question, session_id="default", use_general=False):
    retriever = get_retriever()
    llm = get_llm()

    # -------------------------
    # STEP 1: Rewrite question using history (Conversational RAG)
    # -------------------------
    history = get_history(session_id)
    if history:
        history_text = "\n".join([f"{h['role']}: {h['content']}" for h in history])
        rewrite_prompt = f"""
Given the conversation history and the latest question,
rewrite the question to be standalone.

Conversation:
{history_text}

Latest Question:
{question}

Rewritten standalone question:
"""
        rewritten = llm.invoke(rewrite_prompt)
        question = rewritten.content.strip()

    # -------------------------
    # STEP 2: Retrieve
    # -------------------------
    docs_with_scores = retriever.vectorstore.similarity_search_with_score(question, k=5)

    # -------------------------
    # STEP 2b: Print retrieved chunks for debug
    # -------------------------
    print("\n=== TOP 5 RETRIEVED CHUNKS ===\n")
    for i, (doc, score) in enumerate(docs_with_scores, 1):
        source = doc.metadata.get("source", "Unknown PDF")
        page = doc.metadata.get("page", "Unknown Page")
        print(f"Chunk {i}")
        print(f"Score: {score:.4f}")
        print(f"Source: {source}")
        print(f"Page: {page}")
        print("Preview:", doc.page_content[:300].replace("\n", " "))
        print("-" * 60)

    SIMILARITY_THRESHOLD = 0.9
    filtered_docs = [(doc, score) for doc, score in docs_with_scores if score < SIMILARITY_THRESHOLD]

    # -------------------------
    # STEP 3: Outside documents
    # -------------------------
    if not filtered_docs:
        if use_general:
            response = llm.invoke(question)
            append_history(session_id, "user", question)
            append_history(session_id, "assistant", response.content)
            return {
                "status": "general",
                "answer": response.content
            }

        return {
            "status": "outside",
            "message": "This question is outside the uploaded documents. Can I answer using general knowledge?"
        }

    # -------------------------
    # STEP 4: Extract Context
    # -------------------------
    context = "\n\n".join(
    [
        f"Source {i+1} (Page {doc.metadata.get('page','?')}):\n{doc.page_content}"
        for i, (doc, _) in enumerate(filtered_docs[:3])
    ]
)

    # -------------------------
    # KEEPING YOUR ORIGINAL PROMPT (UNCHANGED)
    # -------------------------
    prompt = f"""
You are an AI Teacher Assistant.

RULES:
- Use ONLY the given context
- If context is insufficient say:
  "The document does not provide sufficient information."
- Give definition + explanation (5–7 sentences)
- Add bullet key points

Context:
{context}

Question:
{question}

Answer:
"""

    response = llm.invoke(prompt)
    answer = response.content

    # -------------------------
    # If LLM says insufficient
    # -------------------------
    if "The document does not provide sufficient information." in answer:
        return {
            "status": "outside",
            "message": "This question is outside the uploaded documents. Can I answer using general knowledge?"
        }

    # Save memory
    append_history(session_id, "user", question)
    append_history(session_id, "assistant", answer)

    return {
       "status": "doc",
       "answer": answer,
       "chunks": [
           {
               "text": doc.page_content[:250] + "...",
               "page": doc.metadata.get("page", "Unknown"),
               "source": doc.metadata.get("source", "Unknown"),
               "score": float(score)
           }
           for doc, score in filtered_docs
        ]
    }