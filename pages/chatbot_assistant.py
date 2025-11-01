"""
Chatbot Assistant Page
"""
import streamlit as st
from utils.api_handlers import get_chatbot_response
from datetime import datetime

def show():
    st.title("💬 Travel Chatbot Assistant")
    st.markdown("Ask me anything about travel planning!")
    st.markdown("---")
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = [{
            "role": "assistant",
            "content": "Hello! 👋 How can I help you plan your trip?",
            "timestamp": datetime.now().strftime("%H:%M")
        }]
    
    # Display chat
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['content']}")
        else:
            st.markdown(f"**🤖 Assistant:** {msg['content']}")
        st.caption(msg["timestamp"])
        st.markdown("---")
    
    # Chat input
    user_input = st.text_input("Type your message:", key="chat_input")
    
    if st.button("📤 Send", type="primary"):
        if user_input:
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_input,
                "timestamp": datetime.now().strftime("%H:%M")
            })
            
            response = get_chatbot_response(user_input)
            
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now().strftime("%H:%M")
            })
            
            st.rerun()
    
    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = [{
            "role": "assistant",
            "content": "Hello! 👋 How can I help you plan your trip?",
            "timestamp": datetime.now().strftime("%H:%M")
        }]
        st.rerun()
