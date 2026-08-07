import streamlit as st

from api.chat import new_chat, continue_chat
from api.documents import upload_document

from utils.helpers import handle_response
from utils.session import get_token

from components.message import render_message


def show_chat_box(chat_container):
    token = get_token()

    # Direct column layout without invalid HTML div wrappers
    input_col1, input_col2 = st.columns([1, 11], vertical_alignment="center")

    with input_col1:
        with st.popover("➕", help="Upload document"):
            st.markdown("#### Upload document")
            with st.form("upload_form", clear_on_submit=True):
                file_type = st.selectbox(
                    "File type",
                    ["pdf", "docx", "txt"],
                    index=0,
                    key="upload_file_type"
                )
                uploaded_file = st.file_uploader(
                    f"Choose {file_type.upper()} file",
                    type=[file_type],
                    label_visibility="collapsed",
                    key="chat_upload"
                )
                submitted = st.form_submit_button("Upload", use_container_width=True)

                if submitted and uploaded_file:
                    with st.spinner("Uploading document..."):
                        response = upload_document(uploaded_file, token)
                        data = handle_response(response)

                    if data:
                        st.session_state.upload_success = True
                        st.session_state.messages = []
                        st.session_state.conversation_id = None
                        st.success("✅ Document uploaded successfully.")
                    else:
                        st.warning("⚠️ Upload did not complete. Please try again.")

    with input_col2:
        question = st.chat_input("Message SAFE AI...", key="main_chat_input")

    if not question:
        return None

    # Append user message
    st.session_state["busy_state"] = "chat"
    st.session_state["busy_text"] = "Thinking..."
    st.session_state.messages.append({"role": "user", "content": question})

    # Render inside top container
    with chat_container:
        render_message(st.session_state.messages[-1])

        with st.spinner("Thinking..."):
            if st.session_state.conversation_id is None:
                response = new_chat(question, token)
            else:
                response = continue_chat(st.session_state.conversation_id, question, token)

            data = handle_response(response)

    st.session_state["busy_state"] = None
    st.session_state["busy_text"] = None

    if not data:
        st.session_state.messages.pop()
        st.error("Failed to fetch response.")
        return None

    if st.session_state.conversation_id is None:
        st.session_state.conversation_id = data["conversation_id"]

    assistant_message = {
        "role": "assistant",
        "content": data["answer"],
        "sources": data.get("source_documents", [])
    }
    st.session_state.messages.append(assistant_message)

    st.rerun()
    return data