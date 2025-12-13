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
from utils.notes_db import init_db, save_chat, get_chats, save_note, get_notes, save_flashcard, get_flashcards, delete_note, update_note
from utils.flashcards import generate_flashcards_from_text
from utils.ui_styles import apply_whimsical_theme, get_decorative_emoji, create_gradient_text, create_badge

init_db()

# page config
st.set_page_config(
    page_title="AI Study Notes — Premium", 
    layout="wide",
    page_icon="🍎",
    initial_sidebar_state="expanded"
)

# Apply whimsical theme
st.markdown(apply_whimsical_theme(), unsafe_allow_html=True)

# Title with gradient effect
st.markdown(f"<h1>🍎 AI Study Notes — Premium Suite ✨</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #AF52DE; font-size: 1.1rem; margin-top: -1rem;'>Your whimsical study companion 🦋</p>", unsafe_allow_html=True)

# -----------------------------
# SIDEBAR — LLM SETTINGS
# -----------------------------
st.sidebar.markdown(f"## {get_decorative_emoji('settings')} Settings & Magic")

llm_choice = st.sidebar.selectbox(
    "🔮 LLM Provider",
    ["Groq (cloud)", "Ollama (local)"],
    help="Choose your AI provider"
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
    "🤖 Model",
    groq_models if selected_llm == "groq" else ollama_models,
    help="Select your AI model"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎛️ Fine-tuning")

temperature = st.sidebar.slider(
    "🌡️ Temperature", 
    0.0, 1.0, 0.15,
    help="Higher = more creative, Lower = more focused"
)
top_k = st.sidebar.slider(
    "🔍 Top-k retrieval", 
    1, 10, 5,
    help="Number of relevant chunks to retrieve"
)
max_chunk_words = st.sidebar.slider(
    "📏 Max chunk (words)", 
    100, 800, 450,
    help="Size of text chunks for processing"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎨 Theme Info")
st.sidebar.info("✨ Whimsical Apple-inspired design\n🍎 Smooth animations & gradients\n🌈 Optimized for joy!")

# file uploader (multiple)
st.markdown("---")
uploaded_files = st.file_uploader(
    "🍎 Drop your PDFs here!", 
    accept_multiple_files=True, 
    type=["pdf"],
    help="Upload one or more PDF files to get started"
)

# main UI layout: left = pdf & toc, center = chat, right = notebook/flashcards
col1, col2, col3 = st.columns([1, 2, 1])

# store project session id
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# process uploaded files
if uploaded_files:
    # Show uploaded files count with badge
    st.sidebar.markdown(f"### {get_decorative_emoji('upload')} Uploaded Files")
    for f in uploaded_files:
        st.sidebar.markdown(f"- 📄 **{f.name}**")
    
    combined_text = ""
    file_names = []
    for f in uploaded_files:
        file_names.append(f.name)
        combined_text += extract_pdf(f) + "\n\n"

    combined_text = clean_text(combined_text)
    st.session_state["combined_text"] = combined_text

    # left column: preview & summary
    with col1:
        st.markdown(f"### {get_decorative_emoji('pdf')} PDF Preview")
        # show first PDF preview
        st.markdown(display_pdf(uploaded_files[0]), unsafe_allow_html=True)

        st.markdown("---")
        st.markdown(f"### {get_decorative_emoji('summary')} Quick Summary")
        
        if st.button(f"{get_decorative_emoji('generate')} Generate Summary", use_container_width=True):
            with st.spinner("✨ Generating magical summary..."):
                st.session_state.quick_summary = generate_summary(
                    combined_text[:6000],
                    llm=("ollama" if selected_llm=="ollama" else "groq"),
                    model=model_option,
                    temperature=temperature
                )
        
        # Display summary if it exists
        if "quick_summary" in st.session_state and st.session_state.quick_summary:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, rgba(255, 229, 217, 0.6), rgba(230, 230, 250, 0.6));
                padding: 1rem;
                border-radius: 12px;
                border-left: 4px solid #AF52DE;
                margin: 1rem 0;
            ">
                {st.session_state.quick_summary}
            </div>
            """, unsafe_allow_html=True)
            
            # Save button appears AFTER summary is generated
            if st.button(f"{get_decorative_emoji('save')} Save to Notes", use_container_width=True):
                save_note("Quick Summary", st.session_state.quick_summary)
                st.success("✅ Saved to Notes!")
                st.balloons()

    # build chunks & index
    with st.spinner("🔮 Creating semantic chunks & building index..."):
        chunks = semantic_chunks(combined_text, max_words=max_chunk_words)
        index, embeddings = build_faiss_index(chunks)
    st.session_state["chunks"] = chunks
    st.session_state["index"] = index
    st.session_state["embeddings"] = embeddings

    # center column: chat-like QA
    with col2:
        st.markdown(f"### {get_decorative_emoji('chat')} Chat with your PDFs")
        
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # chat input
        user_input = st.text_input(
            "💭 Ask me anything about your documents...", 
            key="user_q",
            placeholder="e.g., What are the main topics discussed?"
        )

        if user_input:
            with st.spinner("🤔 Thinking..."):
                # save user message
                save_chat(st.session_state.session_id, "user", user_input)
                # retrieve top-k chunks
                retrieved = retrieve(user_input, index, embeddings, chunks, top_k=top_k)
                # answer using chosen LLM
                result = answer_with_context(
                    user_input, 
                    retrieved, 
                    llm=("ollama" if selected_llm=="ollama" else "groq"), 
                    model=model_option, 
                    temperature=temperature
                )
                answer = result["answer"]
                used_chunks = result["used_chunks"]
                # save assistant message
                save_chat(st.session_state.session_id, "assistant", answer)
                st.session_state.chat_history.append(("user", user_input))
                st.session_state.chat_history.append(("assistant", answer))

        # show chat history from DB for this session
        st.markdown("---")
        st.markdown("#### 💬 Conversation History")
        chats = get_chats(st.session_state.session_id)
        
        for role, message, ts in chats:
            if role == "user":
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, rgba(0, 122, 255, 0.1), rgba(90, 200, 250, 0.1));
                    padding: 1rem;
                    border-radius: 12px;
                    margin: 0.5rem 0;
                    border-left: 3px solid #007AFF;
                ">
                    <strong>🧑 You</strong> <span style="color: #999; font-size: 0.85rem;">({ts})</span><br/>
                    {message}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, rgba(175, 82, 222, 0.1), rgba(255, 45, 85, 0.1));
                    padding: 1rem;
                    border-radius: 12px;
                    margin: 0.5rem 0;
                    border-left: 3px solid #AF52DE;
                ">
                    <strong>🤖 Assistant</strong> <span style="color: #999; font-size: 0.85rem;">({ts})</span>
                </div>
                """, unsafe_allow_html=True)
                st.write(message)  # Use st.write instead of embedding in HTML
                
                # Show the used chunks
                if 'used_chunks' in locals() and used_chunks:
                    with st.expander("🔍 Sources used (click to expand)"):
                        for idx, uc in enumerate(used_chunks):
                            chunk_content = uc.get('chunk', '')
                            if chunk_content:
                                chunk_str = str(chunk_content)
                                st.markdown(f"**Source #{idx + 1}** (relevance: {uc.get('norm_score', 0):.0%})")
                                st.text(chunk_str[:500] + ("..." if len(chunk_str) > 500 else ""))
                                st.markdown("---")
                
                # Download button
                if st.button(f"{get_decorative_emoji('download')} Download as PDF", key=f"dl_{ts}"):
                    fname = export_text_to_pdf(message, filename="answer.pdf")
                    with open(fname, "rb") as f:
                        st.download_button("📥 Download PDF", f, file_name="answer.pdf")

    # right column: Notes, Flashcards
    with col3:
        st.markdown(f"### {get_decorative_emoji('notes')} Notebook")
        
        # Display existing notes
        notes = get_notes()
        if notes:
            for nid, title, content, created in notes:
                with st.expander(f"📝 {title}"):
                    st.markdown(f"*{created}*")
                    
                    # Check if this note is being edited
                    if f"edit_{nid}" in st.session_state and st.session_state[f"edit_{nid}"]:
                        # Edit mode
                        edit_title = st.text_input("Title", value=title, key=f"edit_title_{nid}")
                        edit_content = st.text_area("Content", value=content, height=150, key=f"edit_content_{nid}")
                        
                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            if st.button("💾 Save", key=f"save_{nid}", use_container_width=True):
                                from utils.notes_db import update_note
                                update_note(nid, edit_title, edit_content)
                                st.session_state[f"edit_{nid}"] = False
                                st.success("✅ Note updated!")
                                st.rerun()
                        with col_cancel:
                            if st.button("❌ Cancel", key=f"cancel_{nid}", use_container_width=True):
                                st.session_state[f"edit_{nid}"] = False
                                st.rerun()
                    else:
                        # View mode
                        st.write(content)
                        
                        col_edit, col_delete = st.columns(2)
                        with col_edit:
                            if st.button("✏️ Edit", key=f"btn_edit_{nid}", use_container_width=True):
                                st.session_state[f"edit_{nid}"] = True
                                st.rerun()
                        with col_delete:
                            if st.button("🗑️ Delete", key=f"btn_delete_{nid}", use_container_width=True):
                                from utils.notes_db import delete_note
                                delete_note(nid)
                                st.success("✅ Note deleted!")
                                st.rerun()
        else:
            st.info("No notes yet. Create your first one below! ✨")
        
        st.markdown("---")
        st.markdown("#### ✍️ New Note")
        
        note_title = st.text_input("Title", key="note_title", placeholder="My Brilliant Note")
        note_content = st.text_area("Content", key="note_content", height=150, placeholder="Write something amazing...")
        
        if st.button(f"{get_decorative_emoji('save')} Save Note", use_container_width=True):
            t = note_title or "Untitled"
            c = note_content
            if c and c.strip():
                save_note(t, c)
                st.success("✅ Note saved!")
                st.balloons()
                st.session_state.note_title = ""
                st.session_state.note_content = ""
                st.rerun()
            else:
                st.warning("⚠️ Note content cannot be empty")

        # Export notes section
        if notes:
                    st.markdown("---")
                    st.markdown("#### 📥 Export Notes")
                    if st.button("📄 Export as PDF", use_container_width=True, key="export_notes_pdf"):
                        from utils.export import export_notes_to_pdf
                        fname = export_notes_to_pdf(notes, "my_notes.pdf")
                        with open(fname, "rb") as f:
                            st.download_button(
                                "⬇️ Download PDF", 
                                f, 
                                file_name="my_study_notes.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )

        st.markdown("---")
        st.markdown(f"### {get_decorative_emoji('flashcards')} Flashcards")


        if st.button(f"🤖 Generate Smart Flashcards", use_container_width=True):
            with st.spinner("✨ Creating flashcards from your document..."):
                # Use clean text directly instead of summary
                # This avoids markdown formatting issues
                clean_content = combined_text[:8000]
                
                # Generate flashcards using LLM
                cards = generate_flashcards_from_text(
                    clean_content,  # <-- Use original text, not summary
                    max_cards=40,
                    llm=("ollama" if selected_llm=="ollama" else "groq"),
                    model=model_option,
                    temperature=temperature
                )
                st.success(f"✅ Generated {len(cards)} flashcards!")
                st.balloons()
                
                # Show preview
                st.markdown("**🎴 Preview (first 5):**")
                for i, (front, back) in enumerate(cards[:5], 1):
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, rgba(255, 229, 217, 0.4), rgba(212, 241, 244, 0.4));
                        padding: 1rem;
                        border-radius: 12px;
                        margin: 0.5rem 0;
                        border: 2px solid rgba(175, 82, 222, 0.2);
                    ">
                        <strong>Card {i}</strong><br/>
                        <span style="color: #007AFF;">❓ {front[:100]}{'...' if len(front)>100 else ''}</span><br/>
                        <span style="color: #34C759;">✅ {back[:100]}{'...' if len(back)>100 else ''}</span>
                    </div>
                    """, unsafe_allow_html=True)
        
        if st.button(f"{get_decorative_emoji('download')} Export Flashcards as PDF", use_container_width=True):
                    fcards = get_flashcards()
                    if fcards:
                        from utils.export import export_flashcards_to_pdf
                        fname = export_flashcards_to_pdf(fcards, "flashcards.pdf")
                        with open(fname, "rb") as f:
                            st.download_button(
                                "⬇️ Download PDF", 
                                f, 
                                file_name="my_flashcards.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                    else:
                        st.warning("No flashcards to export yet")
# else: no upload
else:
    # Centered welcome message
    st.markdown("""
    <div style="
        text-align: center;
        padding: 3rem;
        background: linear-gradient(135deg, rgba(255, 229, 217, 0.4), rgba(230, 230, 250, 0.4));
        border-radius: 20px;
        margin: 2rem 0;
    ">
        <h2>🍎 Welcome to your Study Companion! ✨</h2>
        <p style="font-size: 1.2rem; color: #AF52DE;">
            Upload PDFs above to unlock the magic 🦋
        </p>
        <p style="color: #666;">
            Drag & drop multiple files or click to browse
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # show saved notes and flashcards even without upload
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown(f"### {get_decorative_emoji('notes')} Your Saved Notes")
        notes = get_notes()
        if notes:
            for nid, title, content, created in notes[:5]:
                with st.expander(f"📝 {title}"):
                    st.markdown(f"*{created}*")
                    st.write(content[:200] + ("..." if len(content)>200 else ""))
        else:
            st.info("No notes yet! ✨")
    
    with col_b:
        st.markdown(f"### {get_decorative_emoji('flashcards')} Your Flashcards")
        fcards = get_flashcards()
        if fcards:
            for fid, front, back, tags, created in fcards[:5]:
                st.markdown(f"**Q:** {front[:80]}...")
                st.markdown(f"*A:* {back[:80]}...")
                st.markdown("---")
        else:
            st.info("No flashcards yet! 🎴")

# footer
st.markdown("---")
st.markdown("""
<div style="
    text-align: center;
    padding: 2rem;
    background: rgba(255, 255, 255, 0.5);
    border-radius: 20px;
    backdrop-filter: blur(10px);
">
    <p style="font-size: 1.1rem; color: #AF52DE;">
        Made with 💜 by your friendly AI — Premium Suite
    </p>
    <p style="color: #999; font-size: 0.9rem;">
        Toggle settings from the left sidebar ⚙️ | For local mode, ensure Ollama is running
    </p>
</div>
""", unsafe_allow_html=True)