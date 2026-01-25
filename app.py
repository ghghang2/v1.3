# app.py  (only the parts that changed)
import streamlit as st
import pathlib
import subprocess
import sys

from app.config import DEFAULT_SYSTEM_PROMPT
from app.client import get_client
from app.utils import stream_response, build_api_messages
from app.docs_extractor import extract

# --------------------------------------------------------------------------- #
# Helper – run the extractor once (same folder as app.py)
# --------------------------------------------------------------------------- #
def refresh_docs() -> str:
    """Run the extractor once (same folder as app.py)."""
    # 1️⃣  Call the extractor function
    out_path = extract()  # defaults to current dir + repo_docs.md
    # 2️⃣  Read the generated file
    return out_path.read_text(encoding="utf‑8")

# --------------------------------------------------------------------------- #
# Streamlit UI
# --------------------------------------------------------------------------- #
def main():
    st.set_page_config(page_title="Chat with GPT‑OSS", layout="wide")

    # ---- Session state ----------------------------------------------------
    if "history" not in st.session_state:
        st.session_state.history = []          # [(user, bot), ...]
    if "system_prompt" not in st.session_state:
        st.session_state.system_prompt = DEFAULT_SYSTEM_PROMPT
    if "repo_docs" not in st.session_state:
        st.session_state.repo_docs = ""        # will hold the full codebase

    # ---- Sidebar ----------------------------------------------------------
    with st.sidebar:
        st.header("Settings")

        # 1️⃣  System‑prompt editor (unchanged)
        prompt = st.text_area(
            "System prompt",
            st.session_state.system_prompt,
            height=120,
        )
        if prompt != st.session_state.system_prompt:
            st.session_state.system_prompt = prompt

        # 2️⃣  One‑click “Refresh Docs” button
        if st.button("Refresh Docs"):
            st.session_state.repo_docs = refresh_docs()
            st.success("Codebase docs updated!")

    # ---- Conversation UI --------------------------------------------------
    for user_msg, bot_msg in st.session_state.history:
        with st.chat_message("user"):
            st.markdown(user_msg)
        with st.chat_message("assistant"):
            st.markdown(bot_msg)

    # ---- Input -------------------------------------------------------------
    if user_input := st.chat_input("Enter request…"):
        st.chat_message("user").markdown(user_input)

        client = get_client()
        assistant_placeholder = st.empty()
        bot_output = ""

        # Pass the docs into the message chain
        with st.chat_message("assistant"):
            for partial in stream_response(
                st.session_state.history,
                user_input,
                client,
                st.session_state.system_prompt,
                st.session_state.repo_docs,   # <-- new argument
            ):
                bot_output = partial
                assistant_placeholder.markdown(bot_output, unsafe_allow_html=True)

        st.session_state.history.append((user_input, bot_output))

if __name__ == "__main__":
    main()