import re
from datetime import datetime, timezone

from bson import ObjectId
from mongodb import get_database


# FELIX database
db = get_database()

# Memory collection
memories = db["memories"]


def save_memory(
    user_id: str,
    memory: str,
    category: str = "general",
    importance: float = 0.5,
):
    """
    Save a long-term memory for a user.

    Prevents exact duplicate memories from being saved.
    """

    existing = memories.find_one(
        {
            "user_id": user_id,
            "memory": memory,
        }
    )

    if existing:
        return str(existing["_id"])

    now = datetime.now(timezone.utc)

    document = {
        "user_id": user_id,
        "memory": memory,
        "category": category,
        "importance": importance,
        "created_at": now,
        "updated_at": now,
    }

    result = memories.insert_one(document)

    return str(result.inserted_id)


def get_memories(
    user_id: str,
    category: str | None = None,
    limit: int = 10,
):
    """
    Retrieve memories belonging to a user.
    """

    query = {
        "user_id": user_id
    }

    if category:
        query["category"] = category

    results = memories.find(
        query
    ).sort(
        [
            ("importance", -1),
            ("updated_at", -1),
        ]
    ).limit(limit)

    return list(results)


def delete_memory(
    user_id: str,
    memory_id: str,
):
    """
    Delete a specific memory.
    """

    result = memories.delete_one(
        {
            "_id": ObjectId(memory_id),
            "user_id": user_id,
        }
    )

    return result.deleted_count > 0


def detect_memories(user_message: str):
    """
    Detect simple long-term memories from a user message.

    This is intentionally rule-based for now so FELIX
    does not spend an extra LLM call on every message.
    """

    detected = []

    message = user_message.strip()

    # --------------------------------
    # NAME
    # --------------------------------

    name_patterns = [
        r"\bmy name is ([A-Za-z][A-Za-z .'-]{1,40})",
        r"\bcall me ([A-Za-z][A-Za-z .'-]{1,40})",
    ]

    for pattern in name_patterns:
        match = re.search(pattern, message, re.IGNORECASE)

        if match:
            name = match.group(1).strip(" .,!?")


            # Prevent very long accidental captures
            if len(name.split()) <= 5:
                detected.append(
                    {
                        "memory": f"The user's name is {name}.",
                        "category": "name",
                        "importance": 1.0,
                    }
                )

                break

    # --------------------------------
    # PROJECTS
    # --------------------------------

    project_patterns = [
        r"\bI(?:'m| am) building (.+)",
        r"\bI(?:'m| am) working on (.+)",
        r"\bI(?:'m| am) developing (.+)",
        r"\bI(?:'m| am) creating (.+)",
    ]

    for pattern in project_patterns:
        match = re.search(pattern, message, re.IGNORECASE)

        if match:
            project = match.group(1).strip(" .!?")

            if len(project) <= 150:
                detected.append(
                    {
                        "memory": f"The user is working on {project}.",
                        "category": "project",
                        "importance": 0.9,
                    }
                )

    # --------------------------------
    # PREFERENCES
    # --------------------------------

    preference_patterns = [
        r"\bI prefer (.+)",
        r"\bI like (.+)",
        r"\bI don't like (.+)",
    ]

    for pattern in preference_patterns:
        match = re.search(pattern, message, re.IGNORECASE)

        if match:
            preference = match.group(1).strip(" .!?")

            if len(preference) <= 150:
                detected.append(
                    {
                        "memory": f"The user said: {message}",
                        "category": "preference",
                        "importance": 0.7,
                    }
                )

    # --------------------------------
    # INTERESTS
    # --------------------------------

    interest_patterns = [
        r"\bI(?:'m| am) interested in (.+)",
        r"\bI love (.+)",
    ]

    for pattern in interest_patterns:
        match = re.search(pattern, message, re.IGNORECASE)

        if match:
            interest = match.group(1).strip(" .!?")

            if len(interest) <= 150:
                detected.append(
                    {
                        "memory": f"The user is interested in {interest}.",
                        "category": "interest",
                        "importance": 0.6,
                    }
                )

    return detected


def process_new_message(
    user_id: str,
    user_message: str,
):
    """
    Detect and save important memories from a new message.
    """

    detected = detect_memories(user_message)

    saved = []

    for item in detected:
        memory_id = save_memory(
            user_id=user_id,
            memory=item["memory"],
            category=item["category"],
            importance=item["importance"],
        )

        saved.append(
            {
                "id": memory_id,
                **item,
            }
        )

    return saved