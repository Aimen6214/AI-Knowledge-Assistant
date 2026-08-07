import streamlit as st

from api.chat import get_history, get_conversation
from utils.session import get_token
from utils.helpers import handle_response

from components.sidebar import render_sidebar
from components.chat_box import show_chat_box
from components.message import render_message


def initialize_chat_state():
    defaults = {
        "conversation_id": None,
        "upload_success": False,
        "rename_mode": None,
        "messages": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def chat_page():
    initialize_chat_state()

    token = get_token()
    response = get_history(token)
    history = handle_response(response) or []

    action = render_sidebar(history)

    if action == "new":
        st.session_state.conversation_id = None
        st.session_state.messages = []
        st.rerun()
    elif action is not None:
        response = get_conversation(action, token)
        conversation = handle_response(response)
        if conversation:
            st.session_state.conversation_id = conversation["id"]
            st.session_state.messages = conversation["messages"]
        st.rerun()

    if st.session_state.upload_success:
        st.toast("✅ Document uploaded successfully!")
        st.session_state.upload_success = False

    # Main scrollable message container
    chat_container = st.container()

    # Render history or empty state inside container
    with chat_container:
        if not st.session_state.messages:
            st.markdown(
                """
                <div class='empty-state'>
                    <h1>What can I help with today?</h1>
                    <p>Ask anything about your uploaded documents or start a new conversation.</p>
                    <div class='empty-prompt-wrapper'>
                        <span class='empty-prompt'>📄 Summarize this document</span>
                        <span class='empty-prompt'>💡 Explain the key points</span>
                        <span class='empty-prompt'>❓ Answer my question</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            for message in st.session_state.messages:
                render_message(message)

    # Render fixed bottom input bar
    show_chat_box(chat_container)