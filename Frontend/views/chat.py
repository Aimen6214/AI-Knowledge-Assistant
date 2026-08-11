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
        "reply_to": None,
        "last_prompt": None,  # Stores last prompt for 1-click retry
        "busy_state": None,
        "busy_text": None,
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

    # -------------------------------------------------------------------------
    # 1. HANDLE SIDEBAR ACTIONS & QUERY PARAMS PERSISTENCE
    # -------------------------------------------------------------------------
    if action == "new":
        st.session_state.conversation_id = None
        st.session_state.messages = []
        st.session_state.reply_to = None
        st.session_state.last_prompt = None
        if "cid" in st.query_params:
            del st.query_params["cid"]
        st.rerun()

    elif action is not None:
        response = get_conversation(action, token)
        conversation = handle_response(response)
        if conversation:
            st.session_state.conversation_id = conversation["id"]
            st.session_state.messages = conversation["messages"]
            st.session_state.reply_to = None
            st.session_state.last_prompt = None
            st.query_params["cid"] = conversation["id"]  # 👈 Save active chat to URL
        st.rerun()

    # -------------------------------------------------------------------------
    # 2. RECOVER ACTIVE CHAT ON F5 HARD REFRESH
    # -------------------------------------------------------------------------
    cid_from_url = st.query_params.get("cid")
    if cid_from_url and st.session_state.conversation_id != cid_from_url:
        response = get_conversation(cid_from_url, token)
        conversation = handle_response(response)
        if conversation:
            st.session_state.conversation_id = conversation["id"]
            st.session_state.messages = conversation.get("messages", [])

    if st.session_state.upload_success:
        st.toast("✅ Document uploaded successfully!")
        st.session_state.upload_success = False

    # -------------------------------------------------------------------------
    # 3. HEADER BAR WITH FUNCTIONAL REFRESH & RE-FETCH
    # -------------------------------------------------------------------------
    col_title, col_refresh = st.columns([0.80, 0.20])
    with col_title:
        st.subheader("💬 SAFE AI Chat")
    with col_refresh:
        if st.button("🔄 Refresh", key="in_app_refresh_btn", use_container_width=True):
            st.session_state["busy_state"] = None
            st.session_state["busy_text"] = None

            # Re-fetch active conversation history straight from DB
            if st.session_state.get("conversation_id"):
                res = get_conversation(st.session_state.conversation_id, token)
                convo_data = handle_response(res)
                if convo_data and "messages" in convo_data:
                    st.session_state.messages = convo_data["messages"]

            st.toast("Chat synchronized with backend!", icon="✅")
            st.rerun()

    # Main scrollable message container
    chat_container = st.container()

    # Render history or empty state
    with chat_container:
        if not st.session_state.messages:
            st.markdown(
                """
                <div class='empty-state'>
                    <h1>What can I help with today?</h1>
                    <p>Ask anything about your uploaded documents or start a new conversation.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            for idx, message in enumerate(st.session_state.messages):
                render_message(message, index=idx)

    # Render Reply Preview Bar directly above the chat box if active
    if st.session_state.get("reply_to"):
        col_preview, col_cancel = st.columns([0.9, 0.1])
        with col_preview:
            snippet = (
                st.session_state.reply_to[:80] + "..."
                if len(st.session_state.reply_to) > 80
                else st.session_state.reply_to
            )
            st.info(f"↩️ **Replying to:** *\"{snippet}\"*")
        with col_cancel:
            if st.button("❌", key="cancel_reply_btn"):
                st.session_state.reply_to = None
                st.rerun()

    # Render fixed bottom input bar
    show_chat_box(chat_container)