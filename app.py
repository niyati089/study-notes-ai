# app.py
import streamlit as st
from dotenv import load_dotenv
load_dotenv()

import uuid
from utils.extract import extract_pdf, display_pdf
from utils.preprocess import clean_text, detect_topics
from utils.embed import semantic_chunks, build_faiss_index, embed_model
from utils.rag import retrieve
from utils.llm import generate_summary, answer_with_context
from utils.export import export_text_to_pdf
from utils.notes_db import init_db, save_chat, get_chats, save_note, get_notes, save_flashcard, get_flashcards
from utils.flashcards import generate_flashcards_from_text

init_db()

# page config
st.set_page_config(page_title="AI Study Notes — Premium", layout="wide")
st.title("📚 AI Study Notes — Premium Suite")

# -----------------------------
# SIDEBAR — LLM SETTINGS (FIXED)
# -----------------------------
st.sidebar.header("Settings & LLM")

llm_choice = st.sidebar.selectbox(
    "LLM Provider",
    ["Groq (cloud)", "Ollama (local)"]
)

selected_llm = "groq" if llm_choice.startswith("Groq") else "ollama"

# Groq models
groq_models = [
    "llama-3.1-8b-instant",
    "llama-3.1-70b-versatile",
    "llama-3.2-11b-text-preview",
    "llama-3.3-70b-specdec",
    "llama3-70b-8192",
    "mixtral-8x7b-32768",
    "gemma2-9b-it"
]

# Ollama models (local)
ollama_models = [
    "llama3",
    "llama3.1",
    "llama2",
    "mistral",
    "qwen2.5"
]

model_option = st.sidebar.selectbox(
    "Model (auto filters based on LLM)",
    groq_models if selected_llm == "groq" else ollama_models
)

temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.15)
top_k = st.sidebar.slider("Top-k retrieval", 1, 10, 5)
max_chunk_words = st.sidebar.slider("Max chunk (words)", 100, 800, 450)


# file uploader (multiple)
uploaded_files = st.file_uploader("Upload one or more PDFs", accept_multiple_files=True, type=["pdf"])

# main UI layout: left = pdf & toc, center = chat, right = notebook/flashcards
col1, col2, col3 = st.columns([1, 2, 1])

# store project session id
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# process uploaded files
if uploaded_files:
    st.sidebar.success(f"{len(uploaded_files)} files uploaded")
    combined_text = ""
    file_names = []
    for f in uploaded_files:
        file_names.append(f.name)
        combined_text += extract_pdf(f) + "\n\n"

    combined_text = clean_text(combined_text)
    st.session_state["combined_text"] = combined_text

    # sidebar: doc list & TOC
    with st.sidebar.expander("Documents & TOC", expanded=True):
        st.write("Files:")
        for n in file_names:
            st.write(f"- {n}")
        st.write("---")
        st.write("Detected topics (TOC keywords):")
        topics = detect_topics(combined_text, top_n=12)
        for t in topics:
            st.button(f"{t}", key=f"toc_{t}")

    # left column: preview
    with col1:
        st.subheader("PDF Preview")
        # show first PDF preview
        st.markdown(display_pdf(uploaded_files[0]), unsafe_allow_html=True)

        st.subheader("Document Summary (quick)")
        if st.button("Quick auto summary"):
            with st.spinner("Generating quick summary..."):
                quick = generate_summary(combined_text[:6000], llm=("ollama" if selected_llm=="ollama" else "groq"), model=model_option, temperature=temperature)
            st.write(quick)
            if st.button("Save quick summary to Notes"):
                save_note("Quick Summary", quick)
                st.success("Saved to Notes")

    # build chunks & index
    with st.spinner("Creating semantic chunks & building index..."):
        chunks = semantic_chunks(combined_text, max_words=max_chunk_words)
        index, embeddings = build_faiss_index(chunks)
    st.session_state["chunks"] = chunks
    st.session_state["index"] = index
    st.session_state["embeddings"] = embeddings

    # center column: chat-like QA
    with col2:
        st.subheader("Chat with your PDFs")
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # chat input
        user_input = st.text_input("Ask a question about the uploaded documents:", key="user_q")

        if user_input:
            # save user message
            save_chat(st.session_state.session_id, "user", user_input)
            # retrieve top-k chunks
            retrieved = retrieve(user_input, index, embeddings, chunks, top_k=top_k)
            # answer using chosen LLM
            result = answer_with_context(user_input, retrieved, llm=("ollama" if selected_llm=="ollama" else "groq"), model=model_option, temperature=temperature)
            answer = result["answer"]
            used_chunks = result["used_chunks"]
            # save assistant message
            save_chat(st.session_state.session_id, "assistant", answer)
            st.session_state.chat_history.append(("user", user_input))
            st.session_state.chat_history.append(("assistant", answer))

        # show chat history from DB for this session
        st.markdown("### Conversation")
        chats = get_chats(st.session_state.session_id)
        for role, message, ts in chats:
            if role == "user":
                st.markdown(f"**You** ({ts}): {message}")
            else:
                st.markdown(f"**Assistant** ({ts}): {message}")
                # Show the used chunks (if available for last assistant message)
                # We attempt to show top 3 used chunks stored in session (if present)
                if 'used_chunks' in locals():
                    with st.expander("Relevant passages used (click to expand)"):
                        for uc in used_chunks:
                            st.markdown(f"- **Chunk #{uc.get('index')}** (score {uc.get('norm_score'):.2f}):")
                            st.write(uc.get('chunk')[:750] + ("..." if len(uc.get('chunk'))>750 else ""))
                        st.write("---")
                # Download assistant message as PDF
                if st.button("Download this answer as PDF", key=f"dl_{ts}"):
                    fname = export_text_to_pdf(message, filename="answer.pdf")
                    with open(fname, "rb") as f:
                        st.download_button("Download PDF", f, file_name="answer.pdf")

    # right column: Notes, Flashcards, Settings
    with col3:
        st.subheader("Notebook")
        notes = get_notes()
        for nid, title, content, created in notes:
            with st.expander(f"{title} — {created}"):
                st.write(content)
        st.text_input("New note title", key="note_title")
        st.text_area("Note content", key="note_content", height=150)
        if st.button("Save Note"):
            t = st.session_state.note_title or "Untitled"
            save_note(t, st.session_state.note_content)
            st.success("Saved note")

        st.markdown("---")
        st.subheader("Flashcards")
        if st.button("Auto-generate flashcards from summary"):
            # generate quick summary then flashcards
            summ = generate_summary(combined_text[:8000], llm=("ollama" if selected_llm=="ollama" else "groq"), model=model_option, temperature=temperature)
            cards = generate_flashcards_from_text(summ, max_cards=40)
            st.success(f"Saved {len(cards)} flashcards")
            for front, back in cards[:10]:
                st.write(f"- Q: {front[:150]}...\n  A: {back[:150]}...")
        if st.button("Export all flashcards (CSV)"):
            import csv, io
            fcards = get_flashcards()
            buf = io.StringIO()
            writer = csv.writer(buf)
            writer.writerow(["front","back","tags","created_at"])
            for fid, front, back, tags, created in fcards:
                writer.writerow([front, back, tags, created])
            st.download_button("Download CSV", buf.getvalue(), file_name="flashcards.csv")

# else: no upload
else:
    st.info("Upload one or more PDFs to begin. You can also drag-n-drop multiple files.")
    # show saved notes and flashcards even without upload
    with col3:
        st.subheader("Saved notes")
        notes = get_notes()
        for nid, title, content, created in notes:
            with st.expander(f"{title} — {created}"):
                st.write(content)
        st.subheader("Saved flashcards")
        fcards = get_flashcards()
        for fid, front, back, tags, created in fcards[:15]:
            st.write(f"- {front[:120]} ...")

# footer
st.markdown("---")
st.markdown("Made with ❤️ — Premium Suite. Toggle settings from the left. For local mode, ensure Ollama is running at the address in .env.")
