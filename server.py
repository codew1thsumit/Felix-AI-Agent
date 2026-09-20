import uuid
import sqlite3
import json
import asyncio

from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from wikipedia_tool import wikipedia_search
from memory import get_memories, process_new_message
from obsidian_manager import save_message
from events import emit_event


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# DATABASE PATHS
# ============================================================

CHECKPOINT_DB_PATH = "database/felix_memory.db"
CHAT_DB_PATH = "database/chat_sessions.db"


# The sqlite files live in ./database — create the folder on
# first run, otherwise both databases fail to open and the
# server crashes immediately.
import os
os.makedirs("database", exist_ok=True)


# ============================================================
# WEBSITE USER
# ============================================================
#
# There is no login system yet, so the website uses one
# persistent FELIX user identity.
#
# thread_id = individual conversation
# user_id   = same user across conversations
#

WEBSITE_USER_ID = "default-user"


# ============================================================
# ACTIVE GENERATIONS
# ============================================================

active_generations = {}


# ============================================================
# CHAT DATABASE
# ============================================================

def get_chat_db():

    conn = sqlite3.connect(
        CHAT_DB_PATH,
        check_same_thread=False
    )

    conn.row_factory = sqlite3.Row

    return conn


# ============================================================
# INITIALIZE CHAT DATABASE
# ============================================================

def init_chat_db():

    conn = get_chat_db()

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL DEFAULT 'New Chat',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,

            FOREIGN KEY (session_id)
            REFERENCES sessions(id)
            ON DELETE CASCADE
        )
        """
    )

    conn.commit()
    conn.close()


# ============================================================
# MEMORY CONTEXT
# ============================================================

def build_memory_context(user_id):

    try:

        memories = get_memories(
            user_id=user_id,
            limit=10
        )

        if not memories:

            return ""

        memory_lines = []

        for memory in memories:

            memory_lines.append(
                f"- {memory['memory']}"
            )

        return (
            "Here are some long-term memories about the user. "
            "Use them only when relevant to the current conversation. "
            "Do not mention the memory system unless necessary.\n\n"
            + "\n".join(memory_lines)
        )

    except Exception as e:

        print(
            f"  ⚠️ Memory retrieval warning: {e}"
        )

        return ""


# ============================================================
# TEXT EXTRACTION
# ============================================================

def extract_text(content):

    if content is None:

        return ""

    if isinstance(content, str):

        return content

    if isinstance(content, list):

        parts = []

        for item in content:

            if isinstance(item, str):

                parts.append(item)

            elif isinstance(item, dict):

                text = item.get("text")

                if text:

                    parts.append(text)

        return "".join(parts)

    return str(content)


# ============================================================
# FELIX AGENT
# ============================================================

def create_felix_agent(checkpointer):

    return create_agent(

        model=ChatGoogleGenerativeAI(
            model="gemini-3.5-flash-lite"
        ),

        tools=[
            wikipedia_search
        ],

        system_prompt=(
            "You are FELIX, a helpful AI assistant. "

            "Use the Wikipedia tool when it would provide "
            "useful factual information. "

            "Do not use Wikipedia when it is not necessary. "

            "Give the user a clear and helpful answer. "

            "Use markdown formatting when useful. "

            "When long-term memory about the user is provided, "
            "use it only when relevant to the current conversation. "

            "Do not mention the memory system unless the user asks."
        ),

        checkpointer=checkpointer
    )


# ============================================================
# FASTAPI LIFESPAN
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    init_chat_db()

    print()
    print("==============================================")
    print("          FELIX AI WEB SERVER")
    print("==============================================")
    print("  SQLite chat database : Online")
    print("  Async checkpointer   : Online")
    print("  Gemini               : Online")
    print("==============================================")
    print()

    async with AsyncSqliteSaver.from_conn_string(
        CHECKPOINT_DB_PATH
    ) as checkpointer:

        app.state.checkpointer = checkpointer

        app.state.agent = create_felix_agent(
            checkpointer
        )

        yield


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title="FELIX AI",
    version="1.0.0",
    lifespan=lifespan
)


# ============================================================
# STATIC FILES
# ============================================================

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


# ============================================================
# HOME
# ============================================================

@app.get(
    "/",
    response_class=HTMLResponse
)
async def root():

    with open(
        "static/index.html",
        "r",
        encoding="utf-8"
    ) as file:

        return HTMLResponse(
            content=file.read()
        )


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
async def health():

    return {
        "status": "healthy",
        "service": "FELIX AI",
        "streaming": True,
        "async_checkpointer": True
    }


# ============================================================
# LIST SESSIONS
# ============================================================

@app.get("/api/sessions")
async def list_sessions():

    conn = get_chat_db()

    rows = conn.execute(
        """
        SELECT
            s.id,
            s.title,
            s.created_at,
            s.updated_at
        FROM sessions s
        WHERE EXISTS (
            SELECT 1
            FROM messages m
            WHERE m.session_id = s.id
        )
        ORDER BY s.updated_at DESC
        """
    ).fetchall()

    conn.close()

    return [
        dict(row)
        for row in rows
    ]


# ============================================================
# CREATE SESSION
# ============================================================

@app.post("/api/sessions")
async def create_session():

    session_id = str(
        uuid.uuid4()
    )

    now = datetime.now().isoformat()

    conn = get_chat_db()

    conn.execute(
        """
        INSERT INTO sessions
        (
            id,
            title,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            session_id,
            "New Chat",
            now,
            now
        )
    )

    conn.commit()
    conn.close()

    return {
        "id": session_id,
        "title": "New Chat",
        "created_at": now,
        "updated_at": now
    }


# ============================================================
# GET SESSION MESSAGES
# ============================================================

@app.get(
    "/api/sessions/{session_id}/messages"
)
async def get_messages(
    session_id: str
):

    conn = get_chat_db()

    rows = conn.execute(
        """
        SELECT
            role,
            content,
            created_at
        FROM messages
        WHERE session_id = ?
        ORDER BY id ASC
        """,
        (
            session_id,
        )
    ).fetchall()

    conn.close()

    return [
        dict(row)
        for row in rows
    ]


# ============================================================
# CLEAR CURRENT CHAT
# ============================================================

@app.delete(
    "/api/sessions/{session_id}/clear"
)
async def clear_session_messages(
    session_id: str
):
    generation = active_generations.get(session_id)

    if generation and not generation.done():
        generation.cancel()
        try:
            await generation
        except BaseException:
            pass
        active_generations.pop(session_id, None)

    conn = get_chat_db()

    conn.execute(
        """
        DELETE FROM messages
        WHERE session_id = ?
        """,
        (session_id,)
    )

    conn.execute(
        """
        UPDATE sessions
        SET updated_at = ?
        WHERE id = ?
        """,
        (
            datetime.now().isoformat(),
            session_id
        )
    )

    conn.commit()
    conn.close()

    return {"ok": True}


# ============================================================
# DELETE SESSION
# ============================================================

@app.delete(
    "/api/sessions/{session_id}"
)
async def delete_session(
    session_id: str
):

    # --------------------------------------------------------
    # Cancel active generation
    # --------------------------------------------------------

    generation = active_generations.get(
        session_id
    )

    if generation:

        generation.cancel()

        try:

            await generation

        except asyncio.CancelledError:

            pass

        except Exception:

            pass

        active_generations.pop(
            session_id,
            None
        )


    # --------------------------------------------------------
    # Delete chat history
    # --------------------------------------------------------

    conn = get_chat_db()

    conn.execute(
        """
        DELETE FROM messages
        WHERE session_id = ?
        """,
        (
            session_id,
        )
    )

    conn.execute(
        """
        DELETE FROM sessions
        WHERE id = ?
        """,
        (
            session_id,
        )
    )

    conn.commit()
    conn.close()

    return {
        "ok": True
    }


# ============================================================
# RENAME SESSION
# ============================================================

@app.patch(
    "/api/sessions/{session_id}"
)
async def rename_session(
    session_id: str,
    body: dict
):

    title = str(
        body.get(
            "title",
            "New Chat"
        )
    ).strip()

    if not title:

        title = "New Chat"

    title = title[:100]

    now = datetime.now().isoformat()

    conn = get_chat_db()

    conn.execute(
        """
        UPDATE sessions
        SET
            title = ?,
            updated_at = ?
        WHERE id = ?
        """,
        (
            title,
            now,
            session_id
        )
    )

    conn.commit()
    conn.close()

    return {
        "ok": True,
        "title": title
    }


# ============================================================
# SEND JSON
# ============================================================

async def send_json(
    websocket,
    payload
):

    await websocket.send_text(
        json.dumps(
            payload,
            ensure_ascii=False
        )
    )


# ============================================================
# GENERATE RESPONSE
# ============================================================

async def generate_response(
    websocket,
    session_id,
    user_message,
    agent
):

    full_response = ""
    wikipedia_announced = False

    try:

        # ====================================================
        # MEMORY DETECTION
        # ====================================================

        try:

            new_memories = await asyncio.to_thread(
                process_new_message,
                user_id=WEBSITE_USER_ID,
                user_message=user_message
            )

            for memory in new_memories:

                message = (
                    f"Memory saved: "
                    f"{memory['memory']}"
                )

                try:

                    emit_event(
                        event_type="memory",
                        source="memory",
                        message=message
                    )

                except Exception:
                    pass

                await send_json(
                    websocket,
                    {
                        "type": "event",
                        "event": {
                            "type": "memory",
                            "source": "memory",
                            "message": message
                        }
                    }
                )

        except Exception as e:

            print(
                f"  ⚠️ Memory save warning: {e}"
            )


        # ====================================================
        # MEMORY RETRIEVAL
        # ====================================================

        await send_json(
            websocket,
            {
                "type": "event",
                "event": {
                    "type": "memory",
                    "source": "memory",
                    "message": "Checking long-term memory..."
                }
            }
        )

        memory_context = await asyncio.to_thread(
            build_memory_context,
            WEBSITE_USER_ID
        )


        if memory_context:

            await send_json(
                websocket,
                {
                    "type": "event",
                    "event": {
                        "type": "memory",
                        "source": "memory",
                        "message": "Long-term memory loaded."
                    }
                }
            )

        else:

            await send_json(
                websocket,
                {
                    "type": "event",
                    "event": {
                        "type": "memory",
                        "source": "memory",
                        "message": "No stored memories found."
                    }
                }
            )


        # ====================================================
        # BUILD INPUT
        # ====================================================

        messages = []

        if memory_context:

            messages.append(
                {
                    "role": "system",
                    "content": memory_context
                }
            )

        messages.append(
            {
                "role": "user",
                "content": user_message
            }
        )


        # ====================================================
        # MODEL EVENT
        # ====================================================

        try:

            emit_event(
                event_type="model",
                source="gemini",
                message="Generating response..."
            )

        except Exception:
            pass


        await send_json(
            websocket,
            {
                "type": "event",
                "event": {
                    "type": "model",
                    "source": "gemini",
                    "message": "Generating response..."
                }
            }
        )


        # ====================================================
        # STREAM GEMINI
        # ====================================================

        config = {
            "configurable": {
                "thread_id": session_id
            }
        }


        async for token, metadata in agent.astream(
            {
                "messages": messages
            },
            config=config,
            stream_mode="messages"
        ):

            # Report real tool usage to the frontend. Wikipedia is
            # shown only when the agent actually invokes the tool.
            token_name = getattr(token, "name", "") or ""
            tool_calls = getattr(token, "tool_calls", None) or []
            tool_names = []

            if isinstance(tool_calls, list):
                for call in tool_calls:
                    if isinstance(call, dict):
                        name = call.get("name")
                        if name:
                            tool_names.append(str(name))

            metadata_text = str(metadata or {})
            combined_tool_text = " ".join([token_name, *tool_names, metadata_text]).lower()

            if "wikipedia_search" in combined_tool_text and not wikipedia_announced:
                wikipedia_announced = True
                try:
                    await send_json(
                        websocket,
                        {
                            "type": "event",
                            "event": {
                                "type": "tool",
                                "source": "wikipedia",
                                "message": "Wikipedia search in use."
                            }
                        }
                    )
                except Exception:
                    pass

            text = extract_text(
                getattr(
                    token,
                    "content",
                    ""
                )
            )

            if not text:

                continue


            # Ignore tool-call JSON / non-text chunks
            if getattr(
                token,
                "tool_calls",
                None
            ):

                continue


            full_response += text


            await send_json(
                websocket,
                {
                    "type": "token",
                    "content": text
                }
            )


        # ====================================================
        # SAVE ASSISTANT RESPONSE
        # ====================================================

        if full_response.strip():

            conn = get_chat_db()

            conn.execute(
                """
                INSERT INTO messages
                (
                    session_id,
                    role,
                    content,
                    created_at
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    session_id,
                    "assistant",
                    full_response,
                    datetime.now().isoformat()
                )
            )

            conn.execute(
                """
                UPDATE sessions
                SET updated_at = ?
                WHERE id = ?
                """,
                (
                    datetime.now().isoformat(),
                    session_id
                )
            )

            conn.commit()
            conn.close()


            # ------------------------------------------------
            # Obsidian backup
            # ------------------------------------------------

            try:

                await asyncio.to_thread(
                    save_message,
                    user_message,
                    full_response
                )

            except Exception as e:

                print(
                    f"  ⚠️ Obsidian warning: {e}"
                )


        # ====================================================
        # FINAL RESPONSE
        # ====================================================

        await send_json(
            websocket,
            {
                "type": "response",
                "content": full_response
            }
        )


        return full_response


    except asyncio.CancelledError:

        # ====================================================
        # REAL STOP
        # ====================================================

        print(
            f"  ⏹ Generation stopped: {session_id}"
        )


        # Save whatever text was generated
        if full_response.strip():

            conn = get_chat_db()

            conn.execute(
                """
                INSERT INTO messages
                (
                    session_id,
                    role,
                    content,
                    created_at
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    session_id,
                    "assistant",
                    full_response,
                    datetime.now().isoformat()
                )
            )

            conn.commit()
            conn.close()


        try:
            await send_json(
                websocket,
                {
                    "type": "stopped",
                    "content": full_response
                }
            )
        except Exception:
            pass

        raise


    except Exception as e:

        print(
            f"  ❌ Generation error: {e}"
        )

        try:
            await send_json(
                websocket,
                {
                    "type": "error",
                    "message": str(e)
                }
            )
        except Exception:
            pass

        return ""


# ============================================================
# WEBSOCKET
# ============================================================

@app.websocket(
    "/ws/{session_id}"
)
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str
):

    await websocket.accept()

    print(
        f"  🌐 WebSocket connected: {session_id}"
    )

    agent = websocket.app.state.agent

    conn = get_chat_db()

    generation_task = None


    try:

        while True:

            # ==================================================
            # RECEIVE MESSAGE
            # ==================================================

            raw_data = await websocket.receive_text()

            try:

                payload = json.loads(
                    raw_data
                )

            except json.JSONDecodeError:

                await send_json(
                    websocket,
                    {
                        "type": "error",
                        "message": "Invalid JSON."
                    }
                )

                continue


            message_type = payload.get(
                "type",
                "message"
            )


            # ==================================================
            # STOP
            # ==================================================

            if message_type == "stop":

                if (
                    generation_task
                    and not generation_task.done()
                ):

                    generation_task.cancel()

                    try:

                        await generation_task

                    except asyncio.CancelledError:

                        pass

                    except Exception:
                        pass

                    generation_task = None

                    active_generations.pop(
                        session_id,
                        None
                    )

                else:

                    await send_json(
                        websocket,
                        {
                            "type": "stopped",
                            "content": ""
                        }
                    )

                continue


            # ==================================================
            # REGENERATE
            # ==================================================

            if message_type == "regenerate":

                if (
                    generation_task
                    and not generation_task.done()
                ):

                    continue


                # Find previous user message
                row = conn.execute(
                    """
                    SELECT content
                    FROM messages
                    WHERE session_id = ?
                      AND role = 'user'
                    ORDER BY id DESC
                    LIMIT 1
                    """,
                    (
                        session_id,
                    )
                ).fetchone()


                if not row:

                    await send_json(
                        websocket,
                        {
                            "type": "error",
                            "message": "Nothing to regenerate."
                        }
                    )

                    continue


                user_message = row["content"]


                # Remove previous assistant response
                conn.execute(
                    """
                    DELETE FROM messages
                    WHERE id = (
                        SELECT id
                        FROM messages
                        WHERE session_id = ?
                          AND role = 'assistant'
                        ORDER BY id DESC
                        LIMIT 1
                    )
                    """,
                    (
                        session_id,
                    )
                )

                conn.commit()


                await send_json(
                    websocket,
                    {
                        "type": "thinking"
                    }
                )


                generation_task = asyncio.create_task(
                    generate_response(
                        websocket,
                        session_id,
                        user_message,
                        agent
                    )
                )

                active_generations[
                    session_id
                ] = generation_task

                continue


            # ==================================================
            # NORMAL MESSAGE
            # ==================================================

            user_message = payload.get(
                "message",
                ""
            ).strip()


            if not user_message:

                continue


            # Prevent multiple generations
            if (
                generation_task
                and not generation_task.done()
            ):

                continue


            # ==================================================
            # VERIFY SESSION
            # ==================================================

            session = conn.execute(
                """
                SELECT id, title
                FROM sessions
                WHERE id = ?
                """,
                (
                    session_id,
                )
            ).fetchone()


            if not session:

                now = datetime.now().isoformat()

                conn.execute(
                    """
                    INSERT INTO sessions
                    (
                        id,
                        title,
                        created_at,
                        updated_at
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        session_id,
                        "New Chat",
                        now,
                        now
                    )
                )

                conn.commit()


            # ==================================================
            # SAVE USER MESSAGE
            # ==================================================

            now = datetime.now().isoformat()

            conn.execute(
                """
                INSERT INTO messages
                (
                    session_id,
                    role,
                    content,
                    created_at
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    session_id,
                    "user",
                    user_message,
                    now
                )
            )

            conn.execute(
                """
                UPDATE sessions
                SET updated_at = ?
                WHERE id = ?
                """,
                (
                    now,
                    session_id
                )
            )

            conn.commit()


            # ==================================================
            # AUTO TITLE
            # ==================================================

            title_row = conn.execute(
                """
                SELECT title
                FROM sessions
                WHERE id = ?
                """,
                (
                    session_id,
                )
            ).fetchone()


            if (
                title_row
                and title_row["title"] == "New Chat"
            ):

                new_title = (
                    user_message[:40]
                    +
                    (
                        "..."
                        if len(user_message) > 40
                        else ""
                    )
                )

                conn.execute(
                    """
                    UPDATE sessions
                    SET
                        title = ?,
                        updated_at = ?
                    WHERE id = ?
                    """,
                    (
                        new_title,
                        now,
                        session_id
                    )
                )

                conn.commit()


                await send_json(
                    websocket,
                    {
                        "type": "title_update",
                        "title": new_title
                    }
                )


            # ==================================================
            # THINKING
            # ==================================================

            await send_json(
                websocket,
                {
                    "type": "thinking"
                }
            )


            # ==================================================
            # START GENERATION
            # ==================================================

            generation_task = asyncio.create_task(
                generate_response(
                    websocket,
                    session_id,
                    user_message,
                    agent
                )
            )

            active_generations[
                session_id
            ] = generation_task


            # ==================================================
            # KEEP RECEIVING WHILE GEMINI GENERATES
            # ==================================================
            #
            # Do not await generation_task here. The WebSocket
            # must remain free to receive a STOP command.
            # ==================================================

            def generation_done(task):
                if active_generations.get(session_id) is task:
                    active_generations.pop(session_id, None)

            generation_task.add_done_callback(generation_done)


    except WebSocketDisconnect:

        print(
            f"  🌐 WebSocket disconnected: {session_id}"
        )


    except Exception as e:

        print(
            f"  ❌ WebSocket error: {e}"
        )


    finally:

        # =====================================================
        # CANCEL ACTIVE GENERATION
        # =====================================================

        if (
            generation_task
            and not generation_task.done()
        ):

            generation_task.cancel()

            try:

                await generation_task

            except BaseException:

                pass


        active_generations.pop(
            session_id,
            None
        )

        conn.close()


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000
    )