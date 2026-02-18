import subprocess

def changed_files():
    # 1. Get list of files changed since the last push
    diff = subprocess.check_output(
        ["git", "diff", "--name-only", "HEAD"],
        text=True
    ).splitlines()

    # Staged changes (optional)
    staged = subprocess.check_output(
        ["git", "diff", "--name-only", "--cached"], 
        text=True
    ).splitlines()

    all_changes = set(diff + staged)

    # 2. Filter according to your rules
    out = []
    for f in all_changes:
        if "__pycache__" in f:
            continue
        if f in {"run.py", "requirements.txt"}:
            out.append(f)
        elif f.startswith("nbchat/") and f.endswith(".py"):
            out.append(f)

    return out