from datetime import datetime, timezone

_subscribers = []

def subscribe(callback):
    """
    Add a listener for FELIX events.
    """
    if callback not in _subscribers:
        _subscribers.append(callback)

def unsubscribe(callback):
    """
    Remove a listener.
    """
    if callback in _subscribers:
        _subscribers.remove(callback)


# ==========================================
# CREATE EVENT
# ==========================================

def create_event(
    event_type: str,
    message: str,
    source: str = "felix",
):
    return {
        "type": event_type,
        "source": source,
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ==========================================
# TERMINAL DISPLAY
# ==========================================

def print_event(event):

    source = event["source"]
    message = event["message"]

    icons = {
        "memory": "🧠",
        "wikipedia": "📚",
        "reddit": "🔴",
        "web": "🌐",
        "gemini": "🤖",
        "gpt": "🤖",
        "claude": "🤖",
        "synapse": "⚡",
        "felix": "◆",
        "error": "❌",
    }

    icon = icons.get(source, "•")

    print(f"  {icon} {message}")


# ==========================================
# EMIT EVENT
# ==========================================

def emit_event(
    event_type: str,
    source: str,
    message: str,
):

    event = create_event(
        event_type=event_type,
        source=source,
        message=message,
    )

    # Terminal
    print_event(event)

    # WebSocket subscribers
    for callback in list(_subscribers):

        try:
            callback(event)

        except Exception as e:

            print(
                f"  ⚠️ Event subscriber error: {e}"
            )

    return event