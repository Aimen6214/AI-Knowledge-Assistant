import streamlit as st
import streamlit.components.v1 as components


def render_copy_button(text_to_copy: str, btn_id: str):
    """Zero-reload JS Copy Button styled to perfectly match Streamlit's 38px native button."""
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        html, body {{
            background: transparent !important;
            overflow: hidden !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            height: 100%;
            width: 100%;
            display: flex;
            align-items: center;
        }}
        .copy-btn {{
            background-color: #ffffff;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            padding: 6px 12px;
            cursor: pointer;
            font-size: 0.85rem;
            color: #475569;
            font-weight: 500;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            transition: all 0.2s ease;
            height: 38px;
            width: 100%;
            white-space: nowrap;
        }}
        .copy-btn:hover {{
            background-color: #f8fafc;
            border-color: #94a3b8;
            color: #0f172a;
        }}
    </style>
    </head>
    <body>
        <button id="copy-btn-{btn_id}" class="copy-btn" onclick="copyToClipboard()">
            📋 Copy
        </button>
        <script>
        function copyToClipboard() {{
            navigator.clipboard.writeText({repr(text_to_copy)});
            var btn = document.getElementById("copy-btn-{btn_id}");
            btn.innerHTML = "✅ Copied!";
            setTimeout(function() {{
                btn.innerHTML = "📋 Copy";
            }}, 2000);
        }}
        </script>
    </body>
    </html>
    """
    # height=45 gives enough vertical room so Streamlit never clips the iframe
    components.html(html_code, height=45)


def render_message(message: dict, index: int = 0):
    role = message.get("role", "")
    content = message.get("content", "")
    sources = message.get("source_documents", []) or message.get("sources", []) or []

    # Detect user vs assistant
    is_user = role.lower() in ["user", "human"]
    chat_role = "user" if is_user else "assistant"

    with st.chat_message(chat_role):
        st.markdown(content)

        # Referenced Sources (AI messages only)
        if not is_user and sources:
            st.markdown("---")
            st.caption("📄 **Sources Referenced:**")
            
            # Divide source chips across up to 3 columns
            cols = st.columns(min(len(sources), 3))
            
            for idx, s in enumerate(sources):
                name = s.get("file_name", "Source Document")
                # Handle both 'page' and 'page_number' dictionary keys
                page = s.get("page") or s.get("page_number") or "N/A"
                # Extract file size
                file_size = s.get("file_size") or s.get("size")
                
                size_badge = f" `({file_size})`" if file_size and file_size != "N/A" else ""
                
                cols[idx % 3].caption(f"📑 **{name}**{size_badge} — *(Pg {page})*")

        # Action Buttons (Copy & Reply) with equal proportional width
        col_copy, col_reply, _ = st.columns([1.2, 1.2, 5])

        with col_copy:
            render_copy_button(content, f"{chat_role}_{index}")

        with col_reply:
            if st.button("↩️ Reply", key=f"reply_action_{chat_role}_{index}", use_container_width=True):
                st.session_state.reply_to = content
                st.rerun()