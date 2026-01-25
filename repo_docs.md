## app/__init__.py

```python
__all__ = ["client", "config", "utils", "docs_extractor"]
```

## app/client.py

```python
from openai import OpenAI
from .config import NGROK_URL

def get_client() -> OpenAI:
    """Return a client that talks to the local OpenAI‑compatible server."""
    return OpenAI(base_url=f"{NGROK_URL}/v1", api_key="token")
```

## app/config.py

```python
# Configuration – tweak these values as needed
NGROK_URL = "http://localhost:8000"
MODEL_NAME = "unsloth/gpt-oss-20b-GGUF:F16"
DEFAULT_SYSTEM_PROMPT = "Be concise and accurate at all times"
```

## app/docs_extractor.py

```python
# app/docs_extractor.py
"""
extract_docs.py → docs_extractor.py
-----------------------------------
Walk a directory tree and write a single Markdown file that contains:

* The relative path of each file (as a level‑2 heading)
* The raw source code of that file (inside a fenced code block)
"""

from __future__ import annotations

import pathlib
import sys
import logging

log = logging.getLogger(__name__)

def walk_python_files(root: pathlib.Path) -> list[pathlib.Path]:
    """Return all *.py files sorted alphabetically."""
    return sorted(root.rglob("*.py"))

def write_docs(root: pathlib.Path, out: pathlib.Path) -> None:
    """Append file path + code to *out*."""
    with out.open("w", encoding="utf-8") as f_out:
        for p in walk_python_files(root):
            rel = p.relative_to(root)
            f_out.write(f"## {rel}\n\n")
            f_out.write("```python\n")
            f_out.write(p.read_text(encoding="utf-8"))
            f_out.write("\n```\n\n")

def extract(repo_root: pathlib.Path | str = ".", out_file: pathlib.Path | str | None = None) -> pathlib.Path:
    """
    Extract the repo into a Markdown file and return the path.

    Parameters
    ----------
    repo_root : pathlib.Path | str
        Root of the repo to walk.  Defaults to the current dir.
    out_file : pathlib.Path | str | None
        Path to write the Markdown.  If ``None`` uses ``repo_docs.md``.
    """
    root = pathlib.Path(repo_root).resolve()
    out = pathlib.Path(out_file or "repo_docs.md").resolve()

    log.info("Extracting docs from %s → %s", root, out)
    write_docs(root, out)
    log.info("✅  Wrote docs to %s", out)
    return out

def main() -> None:  # CLI entry point
    import argparse

    parser = argparse.ArgumentParser(description="Extract a repo into Markdown")
    parser.add_argument("repo_root", nargs="?", default=".", help="Root of the repo")
    parser.add_argument("output", nargs="?", default="repo_docs.md", help="Output Markdown file")
    args = parser.parse_args()

    extract(args.repo_root, args.output)

if __name__ == "__main__":
    main()
```

## app/utils.py

```python
# app/utils.py  (only the added/modified parts)
from typing import List, Tuple, Dict, Optional
from .config import DEFAULT_SYSTEM_PROMPT, MODEL_NAME
from .client import get_client
from openai import OpenAI

# --------------------------------------------------------------------------- #
# Build the messages list that the OpenAI API expects
# --------------------------------------------------------------------------- #
def build_api_messages(
    history: List[Tuple[str, str]],
    system_prompt: str,
    repo_docs: Optional[str] = None,
) -> List[Dict]:
    """
    Convert local chat history into the format expected by the OpenAI API.

    Parameters
    ----------
    history : List[Tuple[str, str]]
        (user, assistant) pairs.
    system_prompt : str
        Prompt given to the model.
    repo_docs : str | None
        Full code‑base text.  If supplied it is sent as the *first* assistant
        message so the model can read it before answering.
    """
    msgs = [{"role": "system", "content": system_prompt}]
    if repo_docs:
        msgs.append({"role": "assistant", "content": repo_docs})
    for user_msg, bot_msg in history:
        msgs.append({"role": "user", "content": user_msg})
        msgs.append({"role": "assistant", "content": bot_msg})
    return msgs

# --------------------------------------------------------------------------- #
# Stream the assistant reply token‑by‑token
# --------------------------------------------------------------------------- #
def stream_response(
    history: List[Tuple[str, str]],
    user_msg: str,
    client: OpenAI,
    system_prompt: str,
    repo_docs: Optional[str] = None,
):
    """Yield the cumulative assistant reply while streaming."""
    new_hist = history + [(user_msg, "")]
    api_msgs = build_api_messages(new_hist, system_prompt, repo_docs)

    stream = client.chat.completions.create(
        model=MODEL_NAME, messages=api_msgs, stream=True
    )

    full_resp = ""
    for chunk in stream:
        token = chunk.choices[0].delta.content or ""
        full_resp += token
        yield full_resp
```

## app.py

```python
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
```

