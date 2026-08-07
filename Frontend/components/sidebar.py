import streamlit as st

from api.chat import search_conversations, delete_conversation, rename_conversation
from api.documents import get_documents, delete_document

from utils.session import get_token, logout
from utils.helpers import handle_response


def render_sidebar(history):
    action = None
    token = get_token()

    st.sidebar.markdown(
        "<div class='sidebar-brand' style='font-size:1.25rem;font-weight:700;margin-bottom:0.8rem;'>🛡️ SAFE AI</div>",
        unsafe_allow_html=True,
    )

    if st.sidebar.button("➕ New chat", use_container_width=True):
        action = "new"

    search_query = st.sidebar.text_input(
        "Search conversations",
        placeholder="🔍 Search chats",
        label_visibility="collapsed",
    )

    conversations = []

    if search_query:
        query_str = search_query.strip().lower()
        
        # 1. Query Backend Search API
        with st.spinner("Searching..."):
            response = search_conversations(search_query, token)
            data = handle_response(response)

        # 2. Safely extract list from various possible JSON response shapes
        if isinstance(data, list):
            conversations = data
        elif isinstance(data, dict):
            conversations = (
                data.get("conversations")
                or data.get("results")
                or data.get("data")
                or []
            )

        # 3. Fallback: Local client-side filter if API search returned no list
        if not conversations and history:
            conversations = [
                c for c in history
                if query_str in c.get("title", "").lower()
            ]
    else:
        conversations = history or []

    st.sidebar.markdown(
        "<div class='sidebar-section-label'>Chats</div>", unsafe_allow_html=True
    )

    if not conversations:
        st.sidebar.caption("No conversations found" if search_query else "No conversations yet")
    else:
        for chat in conversations:
            # Skip invalid objects
            if not isinstance(chat, dict) or "id" not in chat:
                continue

            chat_title = chat.get("title", "Untitled Chat")
            chat_id = chat["id"]

            # FIX: Use st.sidebar.columns with [0.82, 0.18] for better spacing
            col1, col2 = st.sidebar.columns([0.82, 0.18])

            with col1:
                if st.button(
                    chat_title,
                    key=f"open_{chat_id}",
                    use_container_width=True,
                ):
                    action = chat_id

            with col2:
                with st.popover("⋮"):
                    if st.button(
                        "✏️ Rename",
                        key=f"rename_{chat_id}",
                        use_container_width=True,
                    ):
                        st.session_state.rename_mode = chat_id
                        st.rerun()

                    if st.button(
                        "🗑️ Delete",
                        key=f"delete_{chat_id}",
                        use_container_width=True,
                    ):
                        with st.spinner("Deleting chat..."):
                            response = delete_conversation(chat_id, token)
                            handle_response(response)

                        if st.session_state.conversation_id == chat_id:
                            action = "new"
                        st.rerun()

            # Handle Inline Rename
            if st.session_state.get("rename_mode") == chat_id:
                new_title = st.sidebar.text_input(
                    "New title",
                    value=chat_title,
                    key=f"title_{chat_id}",
                    label_visibility="collapsed",
                )
                rc1, rc2 = st.sidebar.columns(2)
                with rc1:
                    if st.button(
                        "Save",
                        key=f"save_{chat_id}",
                        use_container_width=True,
                    ):
                        response = rename_conversation(chat_id, new_title, token)
                        handle_response(response)
                        st.session_state.rename_mode = None
                        st.rerun()
                with rc2:
                    if st.button(
                        "Cancel",
                        key=f"cancel_{chat_id}",
                        use_container_width=True,
                    ):
                        st.session_state.rename_mode = None
                        st.rerun()

    # Documents Section
    with st.sidebar.expander("📂 Documents", expanded=False):
        response = get_documents(token)
        documents = handle_response(response)
        if not documents or not isinstance(documents, list):
            st.caption("No documents uploaded yet")
        else:
            for doc in documents:
                if not isinstance(doc, dict):
                    continue
                doc_id = doc.get("id")
                file_name = doc.get("file_name", "Document")

                # FIX 1: Use st.columns() instead of st.sidebar.columns() so it stays INSIDE the expander
                # FIX 2: Adjusted ratio to [0.8, 0.2] so dustbin button stays strictly inside
                col_doc1, col_doc2 = st.columns([0.8, 0.2])
                with col_doc1:
                    st.markdown(
                        f"<div style='font-size:0.85rem; padding-top:4px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;'>📄 {file_name}</div>",
                        unsafe_allow_html=True,
                    )
                with col_doc2:
                    if st.button(
                        "🗑️",
                        key=f"delete_doc_{doc_id}",
                        use_container_width=True,
                    ):
                        with st.spinner("Deleting document..."):
                            delete_response = delete_document(doc_id, token)
                            handle_response(delete_response)
                        st.rerun()

    st.sidebar.markdown(
        "<div class='sidebar-spacer'></div>", unsafe_allow_html=True
    )
    if st.sidebar.button("🚪 Log out", use_container_width=True):
        logout()
        st.rerun()

    return action