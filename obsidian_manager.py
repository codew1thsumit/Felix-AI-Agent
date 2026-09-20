from pathlib import Path
from datetime import datetime


VAULT_PATH = Path(r"D:\AI Agent")
CONVERSATIONS_PATH = VAULT_PATH / "Conversations"

MAIN_FILE = CONVERSATIONS_PATH / "FELIX Sessions.md"

session_time = datetime.now()
session_id = session_time.strftime("%Y-%m-%d-%H-%M-%S")

CONVERSATION_FILE = CONVERSATIONS_PATH / f"FELIX-{session_id}.md"


def setup_obsidian():
    CONVERSATIONS_PATH.mkdir(parents=True, exist_ok=True)

    if not MAIN_FILE.exists():
        MAIN_FILE.write_text(
            "# FELIX Sessions\n\n"
            "All FELIX conversation sessions.\n",
            encoding="utf-8"
        )

    date = session_time.strftime("%Y-%m-%d")
    time = session_time.strftime("%H:%M:%S")

    CONVERSATION_FILE.write_text(
        f"# FELIX Session — {date} {time}\n\n"
        f"[[FELIX Sessions]]\n\n"
        f"**Started:** {time}\n\n"
        f"---\n\n",
        encoding="utf-8"
    )

    with MAIN_FILE.open("a", encoding="utf-8") as file:
        file.write(
            f"- [[FELIX-{session_id}|Session {date} {time}]]\n"
        )


def save_message(user_message, felix_response):
    time = datetime.now().strftime("%H:%M:%S")

    with CONVERSATION_FILE.open("a", encoding="utf-8") as file:
        file.write(
            f"## 👤 You — {time}\n\n"
            f"{user_message}\n\n"
            f"## 🤖 FELIX — {time}\n\n"
            f"{felix_response}\n\n"
            f"---\n\n"
        )