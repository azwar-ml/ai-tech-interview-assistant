import streamlit as st
from huggingface_hub import InferenceClient
import os
import uuid
from dotenv import load_dotenv

# Page Configurations
st.set_page_config(page_title="Tech Interview Assistant", page_icon="💻", layout="wide")

# Load environment variables
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

# Initialize Hugging Face Client
repo_id = "Qwen/Qwen2.5-7B-Instruct"
client = InferenceClient(model=repo_id, token=HF_TOKEN)

# System prompt guardrail
SYSTEM_PROMPT = """You are an expert Technical Interview Coach. 
Help users practice coding concepts and system design.
Keep answers under 250 words. Do not comply with absurd requests like 'count to a million'. If asked, politely redirect to interview prep."""

# --- ADVANCED STATE INITIALIZATION ---
# chats format: { session_id: { "title": "Chat Title", "messages": [...] } }
if "chats" not in st.session_state:
    st.session_state.chats = {}
if "current_chat_id" not in st.session_state:
    # Auto-create the very first chat session
    first_id = str(uuid.uuid4())
    st.session_state.chats[first_id] = {"title": "New Chat Session", "messages": []}
    st.session_state.current_chat_id = first_id

# --- SIDEBAR COMPONENT ---
with st.sidebar:
    st.header("⚙️ Assistant Dashboard")
    st.markdown("---")
    
    # 1. New Chat Controller
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        new_id = str(uuid.uuid4())
        st.session_state.chats[new_id] = {"title": "New Chat Session", "messages": []}
        st.session_state.current_chat_id = new_id
        st.rerun()
        
    st.markdown("---")
    
    # 2. Interactive Chat History Index (Select & Delete management)
    st.subheader("📜 Saved Chat History")
    
    if st.session_state.chats:
        # Create columns or a vertical layout to separate Selection from Deletion
        for chat_id, chat_data in list(st.session_state.chats.items()):
            col1, col2 = st.columns([0.85, 0.15])
            
            # Button to select and switch to that specific chat
            with col1:
                is_active = "👉 " if chat_id == st.session_state.current_chat_id else ""
                if st.button(f"{is_active}{chat_data['title']}", key=f"sel_{chat_id}", use_container_width=True):
                    st.session_state.current_chat_id = chat_id
                    st.rerun()
            
            # Button to delete that specific chat turn
            with col2:
                if st.button("❌", key=f"del_{chat_id}"):
                    del st.session_state.chats[chat_id]
                    # If we deleted our active chat, find another one or create a fresh fallback
                    if st.session_state.current_chat_id == chat_id:
                        if st.session_state.chats:
                            st.session_state.current_chat_id = list(st.session_state.chats.keys())[0]
                        else:
                            fallback_id = str(uuid.uuid4())
                            st.session_state.chats[fallback_id] = {"title": "New Chat Session", "messages": []}
                            st.session_state.current_chat_id = fallback_id
                    st.rerun()
    else:
        st.caption("No active sessions.")
        
    st.markdown("---")
    
    # 3. Token Status Indicator
    st.subheader("🔑 API Configuration")
    if HF_TOKEN and HF_TOKEN.startswith("hf_"):
        st.success("HF Token: Connected")
    else:
        st.error("HF Token: Missing/Invalid")
    
    # 4. Performance Constraints Metrics
    st.metric(label="Max Generation Output", value="300 Tokens")

# --- MAIN CHAT INTERFACE ---
st.title("💻 AI Tech Interview Prep Assistant")
st.caption("Practice mock algorithms, system design trade-offs, and conceptual programming questions.")

# Pull details for the active session
active_chat = st.session_state.chats[st.session_state.current_chat_id]
active_messages = active_chat["messages"]

# Render history of the CURRENT active session only
for message in active_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle User Input
if prompt := st.chat_input("Ask for a mock interview question..."):
    
    # If it was a default placeholder name, rename the session title using your first prompt text
    if chat_data["title"] == "New Chat Session":
        active_chat["title"] = prompt[:20] + "..." if len(prompt) > 20 else prompt
        
    # Append and render user message inside active collection
    active_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Process and stream AI response turn
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        # Package active context memory history context 
        api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for msg in active_messages:
            api_messages.append({"role": msg["role"], "content": msg["content"]})
        
        try:
            stream = client.chat_completion(
                messages=api_messages,
                max_tokens=300,
                stream=True,
                temperature=0.7
            )
            
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    full_response += content
                    response_placeholder.markdown(full_response + "▌")
            
            response_placeholder.markdown(full_response)
            active_messages.append({"role": "assistant", "content": full_response})
            st.rerun()
            
        except Exception as e:
            response_placeholder.error(f"⚠️ API Error: {str(e)}")