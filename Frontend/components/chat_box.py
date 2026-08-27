import streamlit as st

from api.chat import continue_chat, new_chat
from api.documents import upload_document
from components.message import render_message
from utils.helpers import handle_response
from utils.session import get_token


def show_chat_box(chat_container):

    token = get_token()

    # -------------------------------------------------------------------------
    # STYLING
    # -------------------------------------------------------------------------
    st.markdown("""
<style>

    /* =========================================================
       ONLY THE POPOVER INSIDE THE CHAT INPUT ROW
       ========================================================= */

    div[data-testid="stHorizontalBlock"]:has(
        [data-testid="stChatInput"]
    )
    > div[data-testid="stColumn"]:first-child
    div[data-testid="stPopover"]
    > div
    > button.st-emotion-cache-en1taq {

        width: 40px !important;
        height: 40px !important;
        min-width: 40px !important;
        min-height: 40px !important;

        padding: 0 !important;
        margin: 0 !important;

        border-radius: 50% !important;

        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;

        box-sizing: border-box !important;
    }


    /* =========================================================
       THE + AND ARROW WRAPPER
       ========================================================= */

    div[data-testid="stHorizontalBlock"]:has(
        [data-testid="stChatInput"]
    )
    > div[data-testid="stColumn"]:first-child
    div[data-testid="stPopover"]
    > div
    > button.st-emotion-cache-en1taq
    > div.st-emotion-cache-3ex273 {

        display: flex !important;
        align-items: center !important;
        justify-content: center !important;

        gap: 3px !important;
        margin-right: 0 !important;
    }


    /* =========================================================
       MAKE THE + SLIGHTLY LARGER
       ========================================================= */

    div[data-testid="stHorizontalBlock"]:has(
        [data-testid="stChatInput"]
    )
    > div[data-testid="stColumn"]:first-child
    div[data-testid="stPopover"]
    > div
    > button.st-emotion-cache-en1taq
    > div.st-emotion-cache-3ex273
    p {

        font-size: 22px !important;
        font-weight: 400 !important;
        line-height: 1 !important;

        margin: 0 !important;
        padding: 0 !important;
    }


    /* =========================================================
       ROTATE THE ACTUAL STREAMLIT ARROW UPWARD
       ========================================================= */

    div[data-testid="stHorizontalBlock"]:has(
        [data-testid="stChatInput"]
    )
    > div[data-testid="stColumn"]:first-child
    div[data-testid="stPopover"]
    > div
    > button.st-emotion-cache-en1taq
    > div.st-emotion-cache-3ex273
    svg {

        transform: rotate(180deg) !important;
        transform-origin: center !important;

        width: 14px !important;
        height: 14px !important;
    }

</style>
""", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 1. AUTO-DETECT PENDING / UNANSWERED USER PROMPT
    # -------------------------------------------------------------------------
    pending_prompt = None

    if (
        st.session_state.messages
        and st.session_state.messages[-1].get("role") == "user"
    ):
        pending_prompt = st.session_state.messages[-1].get("content")

    # -------------------------------------------------------------------------
    # 2. DOCUMENT UPLOAD POPOVER + CHAT INPUT
    # -------------------------------------------------------------------------
    input_col1, input_col2 = st.columns(
        [1, 11],
        vertical_alignment="center"
    )

    # -------------------------------------------------------------------------
    # PLUS / UPLOAD POPOVER
    # -------------------------------------------------------------------------
    with input_col1:

        with st.popover("+", help="Upload document"):

            st.markdown("#### Upload document")

            with st.form(
                "upload_form",
                clear_on_submit=True
            ):

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

                submitted = st.form_submit_button(
                    "Upload",
                    use_container_width=True
                )

                if submitted and uploaded_file:

                    with st.spinner("Uploading and indexing document..."):

                        # Reset file pointer in case buffer was read previously
                        uploaded_file.seek(0)

                        response = upload_document(
                            uploaded_file,
                            token
                        )

                        data = handle_response(response)

                    # ---------------------------------------------------------
                    # STRICT SUCCESS VERIFICATION
                    # ---------------------------------------------------------
                    is_error = (
                        not data
                        or not isinstance(data, dict)
                        or "error" in data
                        or "detail" in data
                        or data.get("success") is False
                        or data.get("status") == "error"
                    )

                    if not is_error:

                        st.session_state.upload_success = True

                        # Reset conversation after uploading
                        st.session_state.messages = []
                        st.session_state.conversation_id = None

                        # Remove conversation ID from URL
                        if "cid" in st.query_params:
                            del st.query_params["cid"]

                        st.success(
                            "✅ Document uploaded and indexed successfully!"
                        )

                        # Trigger immediate rerun to update UI & sidebar
                        st.rerun()

                    else:

                        # Extract exact error detail from API response if present
                        error_msg = "Upload failed. Please check backend logs."
                        if isinstance(data, dict):
                            error_msg = (
                                data.get("detail")
                                or data.get("error")
                                or data.get("message")
                                or error_msg
                            )

                        st.error(f"⚠️ {error_msg}")

    # -------------------------------------------------------------------------
    # CHAT INPUT
    # -------------------------------------------------------------------------
    with input_col2:

        question = st.chat_input(
            "Message SAFE AI...",
            key="main_chat_input"
        )

    # -------------------------------------------------------------------------
    # 3. DETERMINE PROMPT
    # -------------------------------------------------------------------------
    prompt_to_process = question or pending_prompt

    if not prompt_to_process:
        return None

    # -------------------------------------------------------------------------
    # 4. HANDLE NEW USER QUESTION
    # -------------------------------------------------------------------------
    if question:

        final_question = question

        if st.session_state.get("reply_to"):

            final_question = (
                f'> Replying to: "{st.session_state.reply_to}"\n\n'
                f"{question}"
            )

            st.session_state.reply_to = None

        prompt_to_process = final_question

        # Add user message to history
        st.session_state.messages.append({
            "role": "user",
            "content": prompt_to_process
        })

        # Render user message immediately
        with chat_container:

            render_message(
                st.session_state.messages[-1],
                index=len(st.session_state.messages) - 1
            )

    # -------------------------------------------------------------------------
    # 5. CALL AI API
    # -------------------------------------------------------------------------
    st.session_state["busy_state"] = "chat"
    st.session_state["busy_text"] = "Thinking..."

    data = None

    with chat_container:

        with st.spinner("Thinking..."):

            try:

                if st.session_state.conversation_id is None:

                    response = new_chat(
                        prompt_to_process,
                        token
                    )

                else:

                    response = continue_chat(
                        st.session_state.conversation_id,
                        prompt_to_process,
                        token
                    )

                data = handle_response(response)

            except Exception as err:

                st.error(
                    f"⚠️ Connection Error: {str(err)}"
                )

                data = None

    # -------------------------------------------------------------------------
    # 6. LOCK CONVERSATION ID IMMEDIATELY (PREVENTS DUPLICATE CHATS)
    # -------------------------------------------------------------------------
    if data and isinstance(data, dict):
        new_cid = data.get("conversation_id") or data.get("id")
        if new_cid:
            st.session_state.conversation_id = new_cid
            st.query_params["cid"] = new_cid

    # -------------------------------------------------------------------------
    # 7. CLEAR BUSY STATE
    # -------------------------------------------------------------------------
    st.session_state["busy_state"] = None
    st.session_state["busy_text"] = None

    # -------------------------------------------------------------------------
    # 8. HANDLE ERROR / RETRY
    # -------------------------------------------------------------------------
    if not data or "answer" not in data:

        st.error(
            "⚠️ AI failed to respond or connection timed out."
        )

        col_retry, _ = st.columns([2, 8])

        with col_retry:

            if st.button(
                "⚡ Retry Prompt",
                key="retry_failed_prompt"
            ):
                st.rerun()

        return None

    # -------------------------------------------------------------------------
    # 9. APPEND AI RESPONSE
    # -------------------------------------------------------------------------
    assistant_message = {
        "role": "assistant",
        "content": data["answer"],
        "sources": data.get(
            "source_documents",
            []
        )
    }

    st.session_state.messages.append(
        assistant_message
    )

    # -------------------------------------------------------------------------
    # 10. RERENDER
    # -------------------------------------------------------------------------
    st.rerun()

    return data