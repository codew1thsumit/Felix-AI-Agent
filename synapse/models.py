import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openrouter import ChatOpenRouter


load_dotenv()

if not os.getenv("GOOGLE_API_KEY"):
    raise RuntimeError(
        "GOOGLE_API_KEY is missing from the .env file."
    )

if not os.getenv("OPENROUTER_API_KEY"):
    raise RuntimeError(
        "OPENROUTER_API_KEY is missing from the .env file."
    )

gemini = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite"
)

openrouter_free = ChatOpenRouter(
    model="openrouter/free"
)

MODELS = {
    "gemini": gemini,
    "openrouter_free": openrouter_free,
}

def get_model(name: str):
    if name not in MODELS:
        raise ValueError(f"Unknown model: {name}")

    return MODELS[name]