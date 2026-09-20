import sqlite3
import config
import user_input

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from wikipedia_tool import wikipedia_search
from langchain.agents import create_agent
from langgraph.checkpoint.sqlite import SqliteSaver
from obsidian_manager import setup_obsidian, save_message

from memory import get_memories, process_new_message
from events import emit_event

load_dotenv()
console = Console()

llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite"
)

connection = sqlite3.connect(
    "database/felix_memory.db",
    check_same_thread=False
)

checkpointer = SqliteSaver(connection)

agent = create_agent(
    model=llm,
    tools=[wikipedia_search],
    system_prompt=(
        "You are FELIX, a helpful AI assistant. "
        "Use the Wikipedia tool when it would provide useful "
        "factual information. "
        "Do not use Wikipedia when it is not necessary. "
        "Give the user a clear and helpful answer. "
        "When long-term memory about the user is provided, "
        "use it only when relevant to the current conversation. "
        "Do not mention the memory system unless the user asks."
    ),
    checkpointer=checkpointer
)

thread_id = "felix-main"
user_id = "default-user"

def process_message(
    user_message: str,
    user_id: str = "default-user",
    thread_id: str = "felix-main"
):
    
    try:
        new_memories = process_new_message(
            user_id=user_id,
            user_message=user_message
        )
        for memory in new_memories:

            emit_event(
                event_type="memory",
                source="memory",
                message=f"Memory saved: {memory['memory']}"
            )
    except Exception as e:
        print(
            f"  ⚠️ Memory system warning: {e}"
        )
    try:

        emit_event(
            event_type="memory",
            source="memory",
            message="Checking long-term memory..."
        )
        memories = get_memories(
            user_id=user_id,
            limit=10
        )
        if memories:
            emit_event(
                event_type="memory",
                source="memory",
                message=f"Found {len(memories)} stored memories."
            )
        else:
            emit_event(
                event_type="memory",
                source="memory",
                message="No stored memories found."
            )
    except Exception as e:
        print(
            f"  ⚠️ Could not retrieve memories: {e}"
        )
        memories = []

    memory_context = ""

    if memories:
        memory_lines = []
        for memory in memories:
            memory_lines.append(
                f"- {memory['memory']}"
            )
        memory_context = (
            "Here are some long-term memories about the user. "
            "Use them only when relevant to the current conversation. "
            "Do not mention the memory system unless necessary.\n\n"
            + "\n".join(memory_lines)
        )
    emit_event(
        event_type="model",
        source="gemini",
        message="Generating response..."
    )
    try:
        messages = []
        if memory_context:
            messages.append(
                {
                    "role": "system",
                    "content": memory_context
                }
            )
        messages.append(
            {
                "role": "user",
                "content": user_message
            }
        )
        response = agent.invoke(
            {
                "messages": messages
            },
            config={
                "configurable": {
                    "thread_id": thread_id
                }
            }
        )
        final_response = response["messages"][-1].content

        if isinstance(final_response, list):
            final_response = "\n".join(
                item["text"]
                for item in final_response
                if isinstance(item, dict)
                and "text" in item
            )
        try:
            save_message(
                user_message,
                final_response
            )
        except Exception as e:

            print(
                f"  ⚠️ Obsidian warning: {e}"
            )
        return final_response

    except Exception as e:
        emit_event(
            event_type="error",
            source="error",
            message=f"FELIX encountered an error: {e}"
        )

        raise

def run_terminal():
    """
    Start the FELIX terminal interface.
    """
    user_choice = user_input.input_from_user()

    if user_choice == "no":

        print("  👋 FELIX AI shutting down...")

        return
    print("""
╭────────────────────────────────────────────────────────────╮
│                                                            │
│   ███████╗███████╗██╗     ██╗██╗██╗  ██╗                   │
│   ██╔════╝██╔════╝██║     ██║██║╚██╗██╔╝                   │
│   █████╗  █████╗  ██║     ██║██║ ╚███╔╝                    │
│   ██╔══╝  ██╔══╝  ██║     ██║██║ ██╔██╗                    │
│   ██║     ███████╗███████╗██║██║██╔╝ ██╗                   │
│   ╚═╝     ╚══════╝╚══════╝╚═╝╚═╝╚═╝  ╚═╝                   │
│                                                            │
│                     🤖  AI ASSISTANT                       │
│                                                            │
│             ⚡  Gemini  •  LangChain  •  Python            │
│                                                            │
╰────────────────────────────────────────────────────────────╯
""")
    print(    "╭────────────── 🟢 FELIX STATUS ──────────────╮")
    print(    "│ 🚀 System  : Online                         │")
    print(    "│ 🧠 Model   : Gemini 3.5 Flash-Lite          │")
    print(    "│ ⚡ Status  : Ready for conversation         │")
    print(    "│ 💬 Chat    : Unlimited session              │")
    print(    "│ 🚪 Exit    : Type 'exit' anytime            │")
    print(    "╰─────────────────────────────────────────────╯\n")
    print(    "╭─ Felix ────────────────────────────────────────────────╮")
    print(    "│ Hello! I'm Felix. How can I help you today?            │")
    print(    "╰────────────────────────────────────────────────────────╯\n")

    setup_obsidian()

    while True:
        print(" 👤 You")
        user_message = input(" ››› ").strip()
        if user_message.lower() == "exit":
            print(
                "\n 👋 FELIX AI shutting down..."
            )
            break
        if user_message == "":
            print(
                "  ⚠️  Please enter a message.\n"
            )
            continue

        try:
            final_response = process_message(
                user_message=user_message,
                user_id=user_id,
                thread_id=thread_id
            )

            console.print(
                Panel(
                    Markdown(final_response),
                    title="[bold cyan]🤖 Felix[/bold cyan]",
                    border_style="cyan",
                    padding=(1, 2)
                )
            )
        except Exception as e:
            print(
                f"\n  ❌ FELIX error: {e}\n"
            )
if __name__ == "__main__":
    run_terminal()