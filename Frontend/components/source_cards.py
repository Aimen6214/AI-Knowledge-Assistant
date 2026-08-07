import streamlit as st


def show_sources(sources):
    if not sources:
        return

    with st.expander("📚 View citations", expanded=False):
        for source in sources:
            file_name = source.get("file_name", "Document")
            page = source.get("page", "")
            st.caption(f"📄 {file_name} (Page {page})" if page else f"📄 {file_name}")