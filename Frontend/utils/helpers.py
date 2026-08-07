import streamlit as st
import sys


def handle_response(response):
    try:
        # Check if response succeeded
        if response.status_code == 204:
            return {"status": "ok"}
        
        response.raise_for_status()
        
        # Try to parse JSON
        if response.content:
            data = response.json()
            # Debug: print to see what we got
            print(f"DEBUG: Response data type: {type(data)}, Status: {response.status_code}", file=sys.stderr)
            return data
        
        return {"status": "ok"}
        
    except Exception as e:
        # Log the actual error for debugging
        error_msg = str(e)
        print(f"DEBUG: Error in handle_response: {error_msg}, Status: {response.status_code}", file=sys.stderr)
        try:
            error_data = response.json()
            if isinstance(error_data, dict) and "detail" in error_data:
                st.error(f"Error: {error_data['detail']}")
            else:
                st.error(f"Error: {error_msg}")
        except:
            st.error(f"Error: Server error ({response.status_code})")
        
        return None


def format_date(date):
    if not date:
        return ""
    return date[:10]


def clear_chat():
    st.session_state.messages = []
    st.session_state.conversation_id = None
    st.session_state.sources = []