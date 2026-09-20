import requests
from langchain.tools import tool
from events import emit_event

@tool
def wikipedia_search(query: str) -> str:
    """Search Wikipedia for factual information about a topic."""
    emit_event(
        event_type="tool",
        source="wikipedia",
        message=f"Searching Wikipedia: {query}"
    )
    url = "https://en.wikipedia.org/w/api.php"
    headers = {
        "User-Agent": "FELIX-AI/1.0 (AI Agent project)"
    }

    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": query,
        "srlimit": 3,
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=10
    )

    response.raise_for_status()
    data = response.json()
    results = []

    for result in data["query"]["search"]:
        results.append(
            f"Title: {result['title']}\n"
            f"Description: {result['snippet']}"
        )

    if not results:
        return "No Wikipedia results found."

    emit_event(
        event_type="tool",
        source="wikipedia",
        message="Wikipedia results found."
    )
    return "\n\n".join(results)