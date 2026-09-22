from synapse.models import openrouter_free


print("Testing OpenRouter Free Router...")
print()


response = openrouter_free.invoke(
    "Explain what an AI agent is in 3 simple sentences."
)


print("RESPONSE:")
print(response.content)

print("\nMETADATA:")
print(response.response_metadata)