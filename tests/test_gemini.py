from synapse.models import gemini


print("Testing Gemini...")
print()


response = gemini.invoke(
    "Explain what an AI agent is in 3 simple sentences."
)


print("RESPONSE:")
print(response.content)