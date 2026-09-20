import time

def input_from_user():

    while True:

        print("╭─ Terminal ─────────────────────────────────────────────╮")
        print("│ 🤖 Start FELIX AI (yes/no)                             │")
        print("╰────────────────────────────────────────────────────────╯")

        print(" 👤 You")
        user_choice = input(" ››› ").lower().strip()

        if user_choice in ("yes", "y"):

            startup_messages = [
                "⚡ Initializing FELIX AI core...",
                "🔐 Establishing secure connection...",
                "🔗 Connecting to Gemini API...",
                "⚙️  Loading system modules...",
                "🚀 Starting FELIX server...",
            ]

            for message in startup_messages:
                print(f"  {message}")
                time.sleep(0.3)

            print()
            print("  🟢 FELIX AI SYSTEM ONLINE")
            print("    ▸ Connection established")
            print("    ▸ Neural engine ready")
            print("    ▸ Awaiting input...")
            print()

            return "yes"
        
        elif user_choice in ("no", "n"):

            return "no"
        else:
            print()
            print(" ❌ Invalid input.")
            print(" ››› Please enter only: yes/no")
            print()