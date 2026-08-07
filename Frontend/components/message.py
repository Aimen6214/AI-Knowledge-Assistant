import streamlit as st


def render_message(message):
    role = message.get("role", "")
    content = message.get("content", "")
    sources = message.get("sources", []) or []

    if role == "user":
        with st.chat_message("user"):
            st.markdown(content)

    elif role == "assistant":
        with st.chat_message("assistant"):
            # Direct markdown rendering enables bolding, bullet lists, headers, code blocks
            st.markdown(content)

            # Sources formatted neatly below
            if sources:
                st.markdown("---")
                st.caption("📄 **Sources Referenced:**")
                file_names = list({s.get("file_name", "Source Document") for s in sources if s.get("file_name")})
                
                if file_names:
                    cols = st.columns(min(len(file_names), 3))
                    for idx, name in enumerate(file_names):
                        cols[idx % 3].caption(f"📑 {name}")