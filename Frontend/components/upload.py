import streamlit as st

from api.documents import (
    upload_document,
    get_documents,
    delete_document
)

from utils.session import get_token
from utils.helpers import handle_response


def show_upload():

    token = get_token()

    # -------------------------------------------------------------------------
    # STYLING
    # -------------------------------------------------------------------------
    st.markdown(
        """
        <style>

        div.stButton > button:first-child {
            background-color: #2563eb;
            color: white;
            border-radius: 8px;
            height: 42px;
            width: 160px;
            font-weight: 600;
            border: none;
        }

        div.stButton > button:first-child:hover {
            background-color: #1d4ed8;
            color: white;
        }

        .doc-card {
            padding: 12px 16px;
            border-radius: 10px;
            border: 1px solid #e5e7eb;
            margin-bottom: 10px;
            background-color: #fafafa;
        }

        .doc-meta {
            font-size: 13px;
            color: #6b7280;
            margin-top: 4px;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    # -------------------------------------------------------------------------
    # UPLOAD SECTION
    # -------------------------------------------------------------------------
    st.subheader("📂 Upload Documents")

    file = st.file_uploader(
        "Choose PDF, DOCX or TXT",
        type=[
            "pdf",
            "docx",
            "txt"
        ]
    )

    if file:

        st.info(
            f"Selected: {file.name}"
        )

        if st.button(
            "⬆️ Upload Document"
        ):

            with st.spinner("Uploading and indexing document..."):

                # Reset pointer buffer before passing payload
                file.seek(0)

                response = upload_document(
                    file,
                    token
                )

                data = handle_response(
                    response
                )

            if data:

                st.session_state.upload_success = True

                st.toast(
                    "✅ Document uploaded and indexed successfully!",
                    icon="🎉"
                )

                st.rerun()

    st.divider()

    # -------------------------------------------------------------------------
    # DOCUMENT LIST SECTION
    # -------------------------------------------------------------------------
    st.subheader(
        "📚 Your Documents"
    )

    response = get_documents(
        token
    )

    raw_data = handle_response(
        response
    )

    # 1. Handle case where handle_response returns dict e.g. {"documents": [...]}
    if isinstance(raw_data, dict):
        documents = raw_data.get("documents") or raw_data.get("data") or []
    elif isinstance(raw_data, list):
        documents = raw_data
    else:
        documents = []

    if not documents:

        st.info(
            "No documents uploaded"
        )

        return

    for doc in documents:

        if not isinstance(doc, dict):
            continue

        col1, col2 = st.columns(
            [6, 1],
            vertical_alignment="center"
        )

        # 2. Extract values safely checking every common key variant
        file_name = (
            doc.get("file_name") 
            or doc.get("fileName") 
            or doc.get("filename") 
            or "Untitled"
        )
        
        file_size = (
            doc.get("file_size") 
            or doc.get("fileSize") 
            or doc.get("size") 
            or "N/A"
        )
        
        file_type = (
            doc.get("file_type") 
            or doc.get("fileType") 
            or doc.get("type") 
            or ""
        )

        doc_id = doc.get("id")

        with col1:

            st.markdown(
                f"""
                <div class="doc-card">
                    📄 <b>{file_name}</b>
                    <div class="doc-meta">
                        💾 <b>Size:</b> {file_size} | <b>Type:</b> {file_type}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:

            if st.button(
                "🗑️",
                key=f"delete_doc_{doc_id}"
            ):

                with st.spinner("Deleting..."):

                    response = delete_document(
                        doc_id,
                        token
                    )

                    handle_response(
                        response
                    )

                st.toast(
                    "🗑️ Document deleted successfully!"
                )

                st.rerun()