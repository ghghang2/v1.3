# app/push_to_github.py
"""
Entry point that wires the `RemoteClient` together.
"""

from pathlib import Path
import os
import argparse
from git_util.remote import RemoteClient, REPO_NAME

def main() -> None:
    """Create/attach the remote, pull, commit and push.

    The script accepts an optional ``--repo`` argument or the
    ``NEW_REPO`` environment variable.  If neither is supplied the default
    :data:`~nbchat.core.config.REPO_NAME` is used.
    """
    parser = argparse.ArgumentParser(description="Push local repo to GitHub")
    parser.add_argument("--repo", help="GitHub repository name (overrides default)")
    # Use parse_known_args to ignore any extraneous arguments (e.g., Jupyter kernel flags)
    args, _ = parser.parse_known_args()

    # Prefer CLI argument, otherwise environment variable, otherwise config default
    repo_name = args.repo or os.getenv("NEW_REPO") or REPO_NAME

    client = RemoteClient(Path(__file__).resolve().parent.parent)  # repo root

    client.ensure_repo(repo_name)   # 1   Ensure the GitHub repo exists
    client.attach_remote(repo_name) # 2   Attach (or re‑attach) the HTTPS remote

    client.fetch()                  # 3️⃣  Pull latest changes
    client.pull(rebase=False)

    client.write_gitignore()        # 4️⃣  Write .gitignore

    client.commit_all("Initial commit")  # 5️⃣  Commit everything

    # Ensure we are on the main branch
    if "main" not in [b.name for b in client.repo.branches]:
        client.repo.git.checkout("-b", "main")
        client.repo.git.reset("--hard")
    else:
        client.repo.git.checkout("main")
        client.repo.git.reset("--hard")
    
    client.ensure_main_branch()

    client.push()                   # 7️⃣  Push to GitHub

if __name__ == "__main__":
    main()