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


    # Styling
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
            padding: 12px;
            border-radius: 10px;
            border: 1px solid #ddd;
            margin-bottom: 10px;
            background-color: #fafafa;
        }

        </style>
        """,
        unsafe_allow_html=True
    )


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

            response = upload_document(
                file,
                token
            )


            data = handle_response(
                response
            )


            if data:

                st.session_state.upload_success = True

                st.rerun()



    st.divider()


    st.subheader(
        "📚 Your Documents"
    )


    response = get_documents(
        token
    )


    documents = handle_response(
        response
    )


    if not documents:

        st.info(
            "No documents uploaded"
        )

        return



    for doc in documents:


        col1, col2 = st.columns(
            [6,1]
        )


        with col1:

            st.markdown(
                f"""
                <div class="doc-card">
                    📄 <b>{doc['file_name']}</b>
                </div>
                """,
                unsafe_allow_html=True
            )


        with col2:

            if st.button(
                "🗑️",
                key=f"delete_doc_{doc['id']}"
            ):

                response = delete_document(
                    doc["id"],
                    token
                )


                handle_response(
                    response
                )


                st.rerun()