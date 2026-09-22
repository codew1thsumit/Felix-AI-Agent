from synapse.router import route


tests = [
    "Hello, how are you?",

    "Explain photosynthesis",

    "Write a Python program for binary search",

    "Debug my JavaScript function",

    "Solve this difficult logic problem",

    "Design the architecture of an AI agent",
]


for message in tests:

    model_name, model = route(message)

    print("\n" + "=" * 70)

    print(f"USER:")
    print(message)

    print()

    print(f"SYNAPSE:")
    print(f"Selected -> {model_name}")

    print()

    response = model.invoke(message)

    print("RESPONSE:")
    print(response.content)