from synapse.models import get_model


OPENROUTER_KEYWORDS = [
    # Programming
    "code",
    "coding",
    "program",
    "programming",
    "python",
    "java",
    "javascript",
    "typescript",
    "c++",
    "sql",
    "html",
    "css",

    # Development
    "debug",
    "bug",
    "error",
    "function",
    "class",
    "api",
    "backend",
    "frontend",
    "database",

    # Reasoning
    "solve",
    "calculate",
    "algorithm",
    "logic",
    "reasoning",
    "analyze",
    "architecture",
    "system design",
]


def choose_model(user_message: str) -> str:
    """
    Select which model provider should handle the request.

    Gemini:
        General conversation and normal questions.

    OpenRouter Free:
        Coding, technical, reasoning and complex tasks.
    """

    message = user_message.lower()

    if any(
        keyword in message
        for keyword in OPENROUTER_KEYWORDS
    ):
        return "openrouter_free"

    return "gemini"


def route(user_message: str):
    """
    Return the selected model and its name.
    """

    model_name = choose_model(user_message)

    model = get_model(model_name)

    return model_name, model