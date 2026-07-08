import streamlit as st
import uuid
from datetime import datetime

def init_db():
    # Initialize the memory dictionaries if they don't exist in the user's browser session
    if "db_sessions" not in st.session_state:
        st.session_state.db_sessions = {} 
    if "db_messages" not in st.session_state:
        st.session_state.db_messages = {}

def create_session(title="New Chat Session"):
    session_id = str(uuid.uuid4())
    st.session_state.db_sessions[session_id] = {"title": title, "updated_at": datetime.now()}
    st.session_state.db_messages[session_id] = []
    return session_id

def get_all_sessions():
    # Fetch and sort sessions by the time they were updated
    sessions = sorted(st.session_state.db_sessions.items(), key=lambda x: x[1]['updated_at'], reverse=True)
    return [(sid, data["title"]) for sid, data in sessions]

def rename_session(session_id, new_title):
    if session_id in st.session_state.db_sessions:
        st.session_state.db_sessions[session_id]["title"] = new_title

def delete_session(session_id):
    if session_id in st.session_state.db_sessions:
        del st.session_state.db_sessions[session_id]
    if session_id in st.session_state.db_messages:
        del st.session_state.db_messages[session_id]

def save_message(session_id, role, content):
    if session_id not in st.session_state.db_messages:
        st.session_state.db_messages[session_id] = []
    
    st.session_state.db_messages[session_id].append({"role": role, "content": content})
    
    if session_id in st.session_state.db_sessions:
        st.session_state.db_sessions[session_id]["updated_at"] = datetime.now()

def get_messages(session_id):
    return st.session_state.db_messages.get(session_id, [])