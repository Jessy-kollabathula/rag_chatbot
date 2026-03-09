import streamlit as st
import requests
import uuid
import os
def auto_scroll():
    st.markdown(
        """
        <script>
            const chatContainer = window.parent.document.querySelector('section.main');
            chatContainer.scrollTo({
                top: chatContainer.scrollHeight,
                behavior: 'smooth'
            });
        </script>
        """,
        unsafe_allow_html=True
    )

API_URL = "http://127.0.0.1:8000/ask"

st.set_page_config(page_title="Intelligent Teacher Assistant",layout='wide')
 
# -----------------------
# Sidebar
# -----------------------
with st.sidebar:
    st.title("📚 Intelligent TA")

    # Session Info
    with st.expander("🔐 Session Info", expanded=False):
       if "session_id" not in st.session_state:
           st.session_state.session_id = str(uuid.uuid4())

       st.code(st.session_state.session_id[:8])
    
    # System Info
    with st.expander("🤖 System Info", expanded=False):
        st.write("Model: GPT-based LLM")
        st.write("Retriever: Vector Search")
        st.write("Mode: Conversational RAG")

    # Documents
    
        pdf_folder = "all_pdfs"
        files = []
        if os.path.exists(pdf_folder):
            files = [f for f in os.listdir(pdf_folder) if f.endswith(".pdf")]
    with st.expander("📄 Available Documents", expanded=True):
            if files:
                for f in files:
                    st.markdown(f"- {f}")
            else:
                st.write("No documents found.")
    
     # Clear Chat
    with st.expander("⚙️ Chat Settings", expanded=False): 
        
        if st.button("🗑 Clear Chat"):
            st.session_state.messages = []
            st.session_state.pending_question = None
            st.session_state.waiting_for_confirmation = False
            st.session_state.session_id = str(uuid.uuid4())
            st.rerun()
            

# Main Title
st.title("📚 Intelligent Teacher Assistant")

# -----------------------
# Session State
# -----------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

if "waiting_for_confirmation" not in st.session_state:
    st.session_state.waiting_for_confirmation = False

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())



# -----------------------
# Custom WhatsApp-style message function
# -----------------------
def chat_bubble(role, content):
    """Render chat bubble style like WhatsApp"""
    if role == "user":
        st.markdown(
            f"""
            <div style="
                display: flex;
                justify-content: flex-end;
                margin-bottom: 10px;
                align-items:flex-end;">
                <div style="
                    background-color: #dcf8c6;
                    color: black;
                    padding: 10px 15px;
                    border-radius: 20px;
                    max-width: 60%;
                    word-wrap: break-word;
                    margin-right:8px;">
                    {content}
                </div>
                <div style="font-size:18px;">🧑‍💻</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div style="
                display: flex;
                justify-content: flex-start;
                align-item:flex-end;
                margin-bottom: 8px;">
                <div style="front-size:24px;margin:10px;">🤖</div>
                <div style="
                    background-color: #f1f0f0;
                    color: black;
                    padding: 10px 15px;
                    border-radius: 20px;
                    max-width: 60%;
                    word-wrap: break-word;
                    box-shadow: 1px 1px 2px #aaa;">
                    {content}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

# -----------------------
# Display Chat History
# -----------------------
for msg in st.session_state.messages:
    chat_bubble(msg["role"], msg["content"])
    
    #show source if available
    if msg.get("chunks"):
        with st.expander("🔎 Sources "):
            for i, c in enumerate(msg["chunks"]):
                source = os.path.basename(c.get("source", "document.pdf"))
                page = c.get("page", "N/A")
                score = c.get("score", 0)
                st.markdown(
                    f"** {i+1}. {source} - Page {page} Score {score:.2f}**"
                )
                st.caption(c["text"] + "...")
auto_scroll()              

# -----------------------
# Chat Input
# -----------------------
user_input = st.chat_input("Ask your question")


if user_input:

    # ---------------------------------
    #  YES / NO Flow 
    # ---------------------------------
    if st.session_state.waiting_for_confirmation:

        if user_input.lower() == "yes":

            response = requests.post(
                API_URL,
                json={
                    "question": st.session_state.pending_question,
                    "session_id": st.session_state.session_id,
                    "use_general": True
                }
            ).json()

            answer = response.get("answer", "Something went wrong.")

            st.session_state.messages.append(
                {"role": "assistant", "content": answer}
            )

        elif user_input.lower() == "no":

            answer = "Okay 👍 Please ask a question related to the uploaded documents."

            st.session_state.messages.append(
                {"role": "assistant", "content": answer}
            )

        else:
            answer = "Please type 'yes' or 'no'."
            st.session_state.messages.append(
                {"role": "assistant", "content": answer}
            )
            st.rerun()

        st.session_state.waiting_for_confirmation = False
        st.session_state.pending_question = None
        st.rerun()

    # ---------------------------------
    # Normal Question Flow
    # ---------------------------------
    else:
        #save user msg
        st.session_state.messages.append(
            {"role": "user", "content": user_input}
        )
        #immediately display it
        chat_bubble("user", user_input)

        #now call backend
        with st.spinner("Thinking..."):
            response = requests.post(
                API_URL,
                json={
                    "question": user_input,
                    "session_id": st.session_state.session_id,
                    "use_general": False
                }
            ).json()

        status = response.get("status")

        if status == "doc":

            answer = response.get("answer")
            chunks = response.get("chunks", [])

            st.session_state.messages.append(
                {"role": "assistant", "content": answer, "chunks": chunks}
            )

        elif status == "outside":

            message = response.get("message")

            st.session_state.messages.append(
                {"role": "assistant", "content": message}
            )

            st.session_state.pending_question = user_input
            st.session_state.waiting_for_confirmation = True

        else:
            st.session_state.messages.append(
                {"role": "assistant", "content": "Something went wrong."}
            )

        st.rerun()