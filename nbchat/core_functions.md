# Python Functions in `nbchat/core`

| File | Function | Signature |
|------|----------|-----------|
| `client.py` | `get_client` | `def get_client() -> OpenAI:` |
| `db.py` | `init_db` | `def init_db(conn: sqlite3.Connection | None = None) -> None:` |
| `db.py` | `log_message` | `def log_message(session_id: str, role: str, content: str) -> None:` |
| `db.py` | `log_tool_msg` | `def log_tool_msg(session_id: str, tool_id: str, tool_name: str, tool_args: str, content: str) -> None:` |
| `db.py` | `load_history` | `def load_history(session_id: str, limit: int | None = None) -> list[tuple[str, str, str, str, str]]:` |
| `db.py` | `get_session_ids` | `def get_session_ids() -> list[str]:` |
| `db.py` | `replace_session_history` | `def replace_session_history(session_id: str, history: list[tuple[str, str, str, str, str]]) -> None:` |
| `utils.py` | `lazy_import` | `def lazy_import(module_name: str):` |

This file lists all Python functions found in the `nbchat/core` package, along with the file they reside in and their signatures.
