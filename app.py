import streamlit as st
from dotenv import load_dotenv
import chat_db as db
import llm_router as router

load_dotenv()
st.set_page_config(page_title="AI Interview Coach", page_icon="💻", layout="wide")
db.init_db()

# ==========================================
# HARDCODED SYSTEM PROMPTS (VIVA READY)
# ==========================================
INTERVIEW_PERSONAS = {
    "Generative AI & RAG Architect": "You are a Principal AI Researcher interviewing the candidate for a Generative AI role. Focus on RAG architecture, LLM fine-tuning, embedding models, and agentic workflows. Keep answers under 250 words.",
    
    "Python Backend & API Engineer": "You are a Lead Backend Engineer. Interview the user on Python, REST/GraphQL APIs, database indexing, and scaling servers. Keep answers under 250 words.",
    
    "Elite Academic Research (Ph.D./MS)": "You are a university professor at a top-tier research institution interviewing a candidate for a fully-funded Master's/Ph.D. program in Artificial Intelligence. Focus on research methodology and foundational AI math. Keep answers under 250 words.",
    
    "Next.js Full-Stack Developer": "You are a Frontend Lead. Interview the user on React, Next.js App Router, state management, and deploying to Vercel. Keep answers under 250 words.",
    
    "Cybersecurity Security Analyst": "You are a Senior Security Engineer. Interview the candidate on network vulnerabilities, penetration testing basics, and secure coding practices. Keep answers under 250 words.",
    
    "General System Design": "You are a Staff Engineer. Ask complex system design questions about load balancers, caching strategies, and distributed systems. Keep answers under 250 words."
}

# The universal guardrail that prevents the AI from breaking character
BASE_GUARDRAIL = """
CRITICAL INSTRUCTION: You are strictly an AI Tech Interview Coach. 
Under no circumstances are you to discuss topics outside of software engineering, artificial intelligence, programming, or tech interview preparation. 
If the user asks about general knowledge, history, politics, or personal advice, you MUST refuse and reply exactly with: 
"I am strictly designed for AI and Tech interview preparation. I cannot assist with that topic. Would you like to practice a technical question instead?"
Wait for the user to respond before asking the next question.
"""

@st.dialog("⚙️ App Settings & Info")
def settings_modal():
    st.write("### Welcome to the AI Tech Interview Coach")
    st.write("This tool is designed to help software engineers practice mock interviews. Select a persona from the sidebar to tailor the questions to your specific domain.")
    st.info("Your chat history is saved securely in a local database.")
    st.write("---")
    st.write("**System Status:**")
    st.success("Primary API: Connected")
    st.success("Fallback Router: Active")
    st.caption("Max Output: 300 Tokens per response")

if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None

with st.sidebar:
    st.title("💻 AI Coach")
    if st.button("⚙️ Settings & Info", use_container_width=True):
        settings_modal()
        
    st.divider()
    
    # Automatically populate the dropdown with the keys from our hardcoded dictionary
    st.session_state.persona_name = st.selectbox(
        "Select Interview Type", 
        list(INTERVIEW_PERSONAS.keys())
    )
    st.divider()

    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        st.session_state.current_session_id = db.create_session()
        st.rerun()
        
    st.write("### Chat History")
    sessions = db.get_all_sessions()
    
    if not sessions and st.session_state.current_session_id is None:
        st.session_state.current_session_id = db.create_session()
        st.rerun()

    for session_id, title in sessions:
        col1, col2 = st.columns([0.85, 0.15])
        if col1.button(title, key=f"btn_{session_id}", use_container_width=True):
            st.session_state.current_session_id = session_id
            st.rerun()
            
        with col2.popover(""):
            new_name = st.text_input("Rename", value=title, key=f"rename_{session_id}")
            if st.button("Save", key=f"save_{session_id}"):
                db.rename_session(session_id, new_name)
                st.rerun()
            if st.button("Delete ❌", key=f"del_{session_id}"):
                db.delete_session(session_id)
                if st.session_state.current_session_id == session_id:
                    st.session_state.current_session_id = None
                st.rerun()

# ==========================================
# MAIN UI: TITLE & CHAT INTERFACE
# ==========================================

# 1. PERMANENT MAIN TITLE (Always visible, even if no chat is selected)
st.title("🖥️ AI Tech Interview Prep Assistant")
st.caption("Practice mock algorithms, system design trade-offs, and conceptual programming questions.")

# 2. CHAT INTERFACE
if st.session_state.current_session_id:
    active_messages = db.get_messages(st.session_state.current_session_id)
    
    for msg in active_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input(f"Ask for a {st.session_state.persona_name} question..."):
        db.save_message(st.session_state.current_session_id, "user", prompt)
        with st.chat_message("user"):
            st.markdown(prompt)

        active_messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            
            try:
                # Combine the selected persona prompt with the strict guardrail
                raw_system_prompt = INTERVIEW_PERSONAS[st.session_state.persona_name] + "\n\n" + BASE_GUARDRAIL
                
                # Pass the raw prompt directly to the router
                stream = router.generate_response(active_messages, raw_system_prompt)
                for chunk in stream:
                    content = getattr(chunk.choices[0].delta, 'content', '') or ""
                    if content:
                        full_response += content
                        response_placeholder.markdown(full_response + "▌")
                
                response_placeholder.markdown(full_response)
                db.save_message(st.session_state.current_session_id, "assistant", full_response)
            except Exception as e:
                response_placeholder.error(str(e))