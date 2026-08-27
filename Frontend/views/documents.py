import streamlit as st

from api.documents import get_documents, delete_document
from utils.session import get_token
from utils.helpers import handle_response


def documents_page():

    token = get_token()

    # ========================================================
    # HEADER
    # ========================================================

    st.title("📂 Documents")

    st.caption(
        "Manage the documents you have uploaded to SAFE AI."
    )

    st.divider()


    # ========================================================
    # BACK TO CHAT
    # ========================================================

    if st.button("← Back to chat"):

        st.session_state.page = "chat"

        st.rerun()


    st.write("")


    # ========================================================
    # GET DOCUMENTS
    # ========================================================

    with st.spinner("Loading documents..."):

        response = get_documents(token)

        documents = handle_response(response)


    # ========================================================
    # EMPTY STATE
    # ========================================================

    if not documents or not isinstance(documents, list):

        st.info(
            "You haven't uploaded any documents yet."
        )

        return


    # ========================================================
    # DOCUMENT COUNT
    # ========================================================

    st.subheader(
        f"Your Documents ({len(documents)})"
    )


    # ========================================================
    # DOCUMENT LIST
    # ========================================================

    for doc in documents:

        if not isinstance(doc, dict):
            continue


        doc_id = doc.get("id")

        file_name = doc.get(
            "file_name",
            "Document"
        )

        file_size = (
            doc.get("file_size")
            or doc.get("fileSize")
            or "N/A"
        )


        # ----------------------------------------------------
        # DOCUMENT CARD
        # ----------------------------------------------------

        with st.container(border=True):

            col1, col2 = st.columns(
                [0.85, 0.15]
            )


            # ------------------------------------------------
            # DOCUMENT INFORMATION
            # ------------------------------------------------

            with col1:

                st.markdown(
                    f"### 📄 {file_name}"
                )

                st.caption(
                    f"💾 Size: {file_size}"
                )


            # ------------------------------------------------
            # DELETE
            # ------------------------------------------------

            with col2:

                if st.button(
                    "🗑️",
                    key=f"delete_document_{doc_id}",
                    help="Delete document",
                    use_container_width=True,
                ):

                    with st.spinner(
                        "Deleting document..."
                    ):

                        response = delete_document(
                            doc_id,
                            token,
                        )

                        handle_response(response)


                    st.rerun()