import streamlit as st

from api.chat import new_chat, continue_chat
from api.documents import upload_document

from utils.helpers import handle_response
from utils.session import get_token

from components.message import render_message


def show_chat_box(chat_container):
    token = get_token()

    # -------------------------------------------------------------------------
    # 1. AUTO-DETECT PENDING / UNANSWERED USER PROMPT
    # -------------------------------------------------------------------------
    pending_prompt = None
    if st.session_state.messages and st.session_state.messages[-1].get("role") == "user":
        # The last message is from the user and has no AI response yet
        pending_prompt = st.session_state.messages[-1].get("content")

    # Document upload popover and Chat Input Layout
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
                        if "cid" in st.query_params:
                            del st.query_params["cid"]
                        st.success("✅ Document uploaded successfully.")
                    else:
                        st.warning("⚠️ Upload did not complete. Please try again.")

    with input_col2:
        question = st.chat_input("Message SAFE AI...", key="main_chat_input")

    # Determine prompt to process: either fresh input OR pending unanswered prompt on reload
    prompt_to_process = question or pending_prompt

    if not prompt_to_process:
        return None

    # If user typed a NEW question, format reply quote & append to session state
    if question:
        final_question = question
        if st.session_state.get("reply_to"):
            final_question = f"> Replying to: \"{st.session_state.reply_to}\"\n\n{question}"
            st.session_state.reply_to = None

        prompt_to_process = final_question
        st.session_state.messages.append({"role": "user", "content": prompt_to_process})

    # -------------------------------------------------------------------------
    # 2. CALL AI API (Auto-executes on F5 / Refresh if prompt is unanswered)
    # -------------------------------------------------------------------------
    st.session_state["busy_state"] = "chat"
    st.session_state["busy_text"] = "Thinking..."

    data = None
    with chat_container:
        with st.spinner("Thinking..."):
            try:
                if st.session_state.conversation_id is None:
                    response = new_chat(prompt_to_process, token)
                else:
                    response = continue_chat(st.session_state.conversation_id, prompt_to_process, token)

                data = handle_response(response)
            except Exception as err:
                st.error(f"⚠️ Connection Error: {str(err)}")
                data = None

    st.session_state["busy_state"] = None
    st.session_state["busy_text"] = None

    # Handle error or retry
    if not data:
        st.error("⚠️ AI failed to respond or connection timed out.")
        col_retry, _ = st.columns([2, 8])
        with col_retry:
            if st.button("⚡ Retry Prompt", key="retry_failed_prompt"):
                st.rerun()
        return None

    # Update conversation ID and URL parameters
    if st.session_state.conversation_id is None:
        st.session_state.conversation_id = data.get("conversation_id")
        if data.get("conversation_id"):
            st.query_params["cid"] = data["conversation_id"]

    # Append AI response to chat history
    assistant_message = {
        "role": "assistant",
        "content": data["answer"],
        "sources": data.get("source_documents", [])
    }
    st.session_state.messages.append(assistant_message)

    st.rerun()
    return data