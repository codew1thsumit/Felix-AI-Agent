from synapse.executor import execute


while True:

    message = input("\nYou: ").strip()

    if message.lower() in {
        "exit",
        "quit",
    }:
        break

    result = execute(message)

    print(
        f"\nModel: {result['model']}"
    )

    print(
        f"Fallback: {result['fallback']}"
    )

    print(
        f"\nFELIX: {result['response']}"
    )