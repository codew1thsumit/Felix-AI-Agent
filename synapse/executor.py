from synapse.models import gemini
from synapse.router import route


def execute(user_message: str):

    model_name, model = route(user_message)

    try:

        response = model.invoke(user_message)

        return {
            "model": model_name,
            "response": response.content,
            "fallback": False,
        }

    except Exception as error:

        # If OpenRouter fails, fall back to Gemini.
        if model_name == "openrouter_free":

            print(
                f"OpenRouter failed: {error}"
            )

            print(
                "Falling back to Gemini..."
            )

            response = gemini.invoke(user_message)

            return {
                "model": "gemini",
                "response": response.content,
                "fallback": True,
            }

        raise