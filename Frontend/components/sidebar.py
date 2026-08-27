import streamlit as st
from st_keyup import st_keyup

from api.chat import search_conversations, delete_conversation, rename_conversation
from utils.session import get_token, logout
from utils.helpers import handle_response


# ==============================================================
# HIGHLIGHT SEARCH TEXT
# ==============================================================

def _highlight(text: str, query: str) -> str:
    if not query:
        return text

    idx = text.lower().find(query.lower())

    if idx == -1:
        return text

    return (
        text[:idx]
        + f"<b>{text[idx:idx + len(query)]}</b>"
        + text[idx + len(query):]
    )


# ==============================================================
# CLEAR SEARCH CALLBACK
#
# Must run as an on_click callback, NOT inline after the widget
# has been instantiated in the same script run - otherwise
# Streamlit raises StreamlitAPIException.
# ==============================================================

def _clear_search():
    # st_keyup is a custom JS component - it keeps its own text
    # in the browser, so just clearing session_state.search_query
    # does not visually clear the box. Instead, bump a counter to
    # change the widget's key, forcing Streamlit to fully remount
    # the component with a fresh (empty) value.
    st.session_state.search_reset = (
        st.session_state.get("search_reset", 0) + 1
    )


# ==============================================================
# SIDEBAR CSS
# ==============================================================

def _inject_sidebar_css():

    st.markdown(
        """
        <style>

        /* ======================================================
           SIDEBAR BASE
        ====================================================== */

        [data-testid="stSidebar"] {
            background-color: #ffffff !important;
        }


        /*
        The sidebar itself becomes the positioning parent.
        This allows the bottom navigation to stay INSIDE
        the sidebar.
        */

        [data-testid="stSidebar"] > div:first-child {
            position: relative !important;

            height: 100vh !important;

            overflow: hidden !important;
        }


        /* ======================================================
           SIDEBAR CONTENT
        ====================================================== */

        [data-testid="stSidebarContent"] {
            height: 100vh !important;

            overflow: hidden !important;

            box-sizing: border-box !important;

            padding-bottom: 125px !important;
        }


        /* ======================================================
           BRAND
        ====================================================== */

        .safe-ai-brand {

            font-size: 1.25rem;

            font-weight: 700;

            color: #0f172a;

            padding: 0.2rem 0.25rem 0.8rem 0.25rem;
        }


        /* ======================================================
           SECTION LABEL
        ====================================================== */

        .sidebar-section-label {

            font-size: 0.75rem;

            font-weight: 600;

            color: #64748b;

            text-transform: uppercase;

            letter-spacing: 0.04em;

            margin-top: 0.8rem;

            margin-bottom: 0.4rem;
        }


        /* ======================================================
           SCROLLABLE CHAT AREA
        ====================================================== */

        [data-testid="stSidebar"] .st-key-chat_area {

            height: calc(100vh - 300px) !important;

            max-height: calc(100vh - 300px) !important;

            overflow-y: auto !important;

            overflow-x: hidden !important;

            padding-right: 4px !important;

            box-sizing: border-box !important;
        }


        /* ======================================================
           CHAT SCROLLBAR
        ====================================================== */

        [data-testid="stSidebar"] .st-key-chat_area::-webkit-scrollbar {

            width: 6px !important;
        }


        [data-testid="stSidebar"] .st-key-chat_area::-webkit-scrollbar-track {

            background: transparent !important;
        }


        [data-testid="stSidebar"] .st-key-chat_area::-webkit-scrollbar-thumb {

            background: #cbd5e1 !important;

            border-radius: 10px !important;
        }


        [data-testid="stSidebar"] .st-key-chat_area::-webkit-scrollbar-thumb:hover {

            background: #94a3b8 !important;
        }


        /* ======================================================
           ALL SIDEBAR BUTTONS
        ====================================================== */

        [data-testid="stSidebar"] button {

            border-radius: 8px !important;
        }


        /* ======================================================
           CHAT BUTTONS
        ====================================================== */

        [data-testid="stSidebar"] .st-key-chat_area button {

            text-align: left !important;

            white-space: nowrap !important;

            overflow: hidden !important;

            text-overflow: ellipsis !important;

            border: 1px solid transparent !important;

            background-color: transparent !important;

            color: #374151 !important;
        }


        [data-testid="stSidebar"] .st-key-chat_area button:hover {

            background-color: #f3f4f6 !important;
        }


        /* ======================================================
           FIXED BOTTOM AREA
           
           Documents + Logout
        ====================================================== */

        [data-testid="stSidebar"] .st-key-sidebar_bottom {

            position: absolute !important;

            left: 0 !important;

            right: 0 !important;

            bottom: 0 !important;

            width: 100% !important;

            background-color: #ffffff !important;

            padding: 0.55rem 0.75rem 0.75rem 0.75rem !important;

            border-top: 1px solid #e5e7eb !important;

            z-index: 999999 !important;

            box-sizing: border-box !important;
        }


        /* ======================================================
           DOCUMENTS BUTTON
        ====================================================== */

        [data-testid="stSidebar"] .st-key-sidebar_bottom button {

            width: 100% !important;

            min-height: 2.45rem !important;

            background-color: #ffffff !important;

            color: #374151 !important;

            border: 1px solid transparent !important;

            font-size: 0.9rem !important;

            text-align: left !important;
        }


        [data-testid="stSidebar"] .st-key-sidebar_bottom button:hover {

            background-color: #f3f4f6 !important;

            border-color: #e5e7eb !important;
        }


        /* ======================================================
           LOGOUT
        ====================================================== */

        [data-testid="stSidebar"] .st-key-logout_container {

            width: 100% !important;
        }


        [data-testid="stSidebar"] .st-key-logout_container button {

            width: 100% !important;

            min-height: 2.45rem !important;

            background-color: #ffffff !important;

            color: #374151 !important;

            border: 1px solid transparent !important;

            font-size: 0.9rem !important;

            text-align: left !important;
        }


        [data-testid="stSidebar"] .st-key-logout_container button:hover {

            background-color: #fef2f2 !important;

            color: #b91c1c !important;

            border-color: #fecaca !important;
        }


        /* ======================================================
           SEARCH INPUT
        ====================================================== */

        [data-testid="stSidebar"] input {

            border-radius: 8px !important;
        }


        /* ======================================================
           POPOVER
        ====================================================== */

        [data-testid="stSidebar"] [data-testid="stPopover"] button {

            text-align: center !important;
        }


        </style>
        """,
        unsafe_allow_html=True,
    )


# ==============================================================
# RENDER SIDEBAR
# ==============================================================

def render_sidebar(history):

    action = None

    token = get_token()

    _inject_sidebar_css()


    # ==========================================================
    # BRAND
    # ==========================================================

    st.sidebar.markdown(
        """
        <div class="safe-ai-brand">
            🛡️ SAFE AI
        </div>
        """,
        unsafe_allow_html=True,
    )


    # ==========================================================
    # NEW CHAT
    # ==========================================================

    if st.sidebar.button(
        "➕  New chat",
        use_container_width=True,
        key="new_chat_button",
    ):

        action = "new"


    # ==========================================================
    # SEARCH (real-time, ChatGPT-style)
    # ==========================================================

    col_search, col_clear = st.sidebar.columns(
        [0.85, 0.15]
    )


    with col_search:

        # Dynamic key: bumping search_reset forces Streamlit to
        # fully remount the st_keyup component (fresh, empty box)
        # instead of trying to mutate its session_state in place.
        search_reset = st.session_state.get("search_reset", 0)

        # st_keyup reruns the script on every keystroke (debounced),
        # unlike st.text_input which only reruns on Enter/blur.
        search_query = st_keyup(
            "Search conversations",
            placeholder="🔍  Search chats",
            label_visibility="collapsed",
            key=f"search_query_{search_reset}",
            debounce=300,
        )


    with col_clear:

        if search_query:

            st.button(
                "✕",
                key="clear_search",
                use_container_width=True,
                on_click=_clear_search,
            )


    query_str = (
        search_query.strip().lower()
        if search_query
        else ""
    )


    # ==========================================================
    # GET CONVERSATIONS
    # ==========================================================

    if query_str:

        # First search currently loaded history

        conversations = [
            c
            for c in (history or [])
            if (
                isinstance(c, dict)
                and query_str in c.get(
                    "title",
                    ""
                ).lower()
            )
        ]


        # If nothing found, search backend

        if (
            not conversations
            and len(query_str) >= 3
        ):

            with st.spinner(
                "Searching messages..."
            ):

                response = search_conversations(
                    search_query,
                    token,
                )

                data = handle_response(
                    response
                )


            if isinstance(data, list):

                conversations = data

            elif isinstance(data, dict):

                conversations = (
                    data.get("conversations")
                    or data.get("results")
                    or data.get("data")
                    or []
                )

    else:

        conversations = history or []


    # ==========================================================
    # SCROLLABLE CHAT AREA
    # ==========================================================

    chat_area = st.sidebar.container(
        key="chat_area"
    )


    with chat_area:

        # ------------------------------------------------------
        # CHAT LABEL
        # ------------------------------------------------------

        st.markdown(
            f"""
            <div class="sidebar-section-label">
                {
                    "Search results"
                    if query_str
                    else "Chats"
                }
            </div>
            """,
            unsafe_allow_html=True,
        )


        # ------------------------------------------------------
        # EMPTY STATE
        # ------------------------------------------------------

        if not conversations:

            st.caption(
                "No matches found"
                if query_str
                else "No conversations yet"
            )


        # ------------------------------------------------------
        # CHAT LIST
        # ------------------------------------------------------

        else:

            for chat in conversations:

                if (
                    not isinstance(chat, dict)
                    or "id" not in chat
                ):
                    continue


                chat_title = chat.get(
                    "title",
                    "Untitled Chat"
                )

                chat_id = chat["id"]


                # =================================================
                # CHAT ROW
                # =================================================

                col1, col2 = st.columns(
                    [0.84, 0.16]
                )


                # -------------------------------------------------
                # CHAT TITLE
                # -------------------------------------------------

                with col1:

                    if query_str:

                        st.markdown(
                            f"""
                            <div style="
                                font-size:0.9rem;
                                padding:6px 4px;
                                overflow:hidden;
                                text-overflow:ellipsis;
                                white-space:nowrap;
                            ">
                                {
                                    _highlight(
                                        chat_title,
                                        search_query
                                    )
                                }
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )


                        if st.button(
                            "Open",
                            key=f"open_search_{chat_id}",
                            use_container_width=True,
                        ):

                            action = chat_id


                    else:

                        if st.button(
                            chat_title,
                            key=f"open_{chat_id}",
                            use_container_width=True,
                        ):

                            action = chat_id


                # -------------------------------------------------
                # THREE DOT MENU
                # -------------------------------------------------

                with col2:

                    with st.popover("⋮"):

                        # -----------------------------------------
                        # RENAME
                        # -----------------------------------------

                        if st.button(
                            "✏️ Rename",
                            key=f"rename_{chat_id}",
                            use_container_width=True,
                        ):

                            st.session_state.rename_mode = chat_id

                            st.rerun()


                        # -----------------------------------------
                        # DELETE
                        # -----------------------------------------

                        if st.button(
                            "🗑️ Delete",
                            key=f"delete_{chat_id}",
                            use_container_width=True,
                        ):

                            with st.spinner(
                                "Deleting chat..."
                            ):

                                response = delete_conversation(
                                    chat_id,
                                    token,
                                )

                                handle_response(
                                    response
                                )


                            if (
                                st.session_state.get(
                                    "conversation_id"
                                )
                                == chat_id
                            ):

                                action = "new"


                            st.rerun()


                # =================================================
                # RENAME MODE
                # =================================================

                if (
                    st.session_state.get(
                        "rename_mode"
                    )
                    == chat_id
                ):

                    new_title = st.text_input(
                        "New title",
                        value=chat_title,
                        key=f"title_{chat_id}",
                        label_visibility="collapsed",
                    )


                    rc1, rc2 = st.columns(2)


                    # ------------------------------------------------
                    # SAVE
                    # ------------------------------------------------

                    with rc1:

                        if st.button(
                            "Save",
                            key=f"save_{chat_id}",
                            use_container_width=True,
                        ):

                            response = rename_conversation(
                                chat_id,
                                new_title,
                                token,
                            )

                            handle_response(
                                response
                            )

                            st.session_state.rename_mode = None

                            st.rerun()


                    # ------------------------------------------------
                    # CANCEL
                    # ------------------------------------------------

                    with rc2:

                        if st.button(
                            "Cancel",
                            key=f"cancel_{chat_id}",
                            use_container_width=True,
                        ):

                            st.session_state.rename_mode = None

                            st.rerun()


    # ==========================================================
    # FIXED BOTTOM NAVIGATION
    #
    # This stays INSIDE the sidebar.
    # ==========================================================

    bottom = st.sidebar.container(
        key="sidebar_bottom"
    )


    with bottom:

        # ========================================================
        # DOCUMENTS
        # ========================================================

        if st.button(
            "📂  Documents",
            key="documents_button",
            use_container_width=True,
        ):

            st.session_state.page = "documents"

            st.rerun()


        # ========================================================
        # LOGOUT
        # ========================================================

        logout_container = st.container(
            key="logout_container"
        )


        with logout_container:

            if st.button(
                "🚪  Log out",
                key="logout",
                use_container_width=True,
            ):

                logout()

                st.session_state.page = "login"

                st.rerun()


    # ==========================================================
    # RETURN ACTION
    # ==========================================================

    return action
