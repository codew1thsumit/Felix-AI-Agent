import asyncio

from fastapi import (
    FastAPI,
    WebSocket,
    WebSocketDisconnect,
)
from pydantic import BaseModel

from main import process_message
from events import subscribe, unsubscribe


# ==========================================
# FELIX API
# ==========================================

app = FastAPI(
    title="FELIX AI",
    description="FELIX AI Backend API",
    version="1.0.0"
)


# ==========================================
# REQUEST MODEL
# ==========================================

class ChatRequest(BaseModel):

    message: str
    user_id: str = "default-user"


# ==========================================
# ROOT
# ==========================================

@app.get("/")
def root():

    return {
        "status": "online",
        "message": "FELIX AI backend is running."
    }


# ==========================================
# HEALTH
# ==========================================

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# ==========================================
# NORMAL CHAT API
# ==========================================

@app.post("/chat")
def chat(request: ChatRequest):

    response = process_message(
        user_message=request.message,
        user_id=request.user_id,
        thread_id=request.user_id
    )

    return {
        "response": response
    }


# ==========================================
# WEBSOCKET
# ==========================================

@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket
):

    await websocket.accept()

    print("  🌐 WebSocket client connected.")

    loop = asyncio.get_running_loop()

    event_queue = asyncio.Queue()


    # ======================================
    # EVENT CALLBACK
    # ======================================

    def handle_event(event):

        loop.call_soon_threadsafe(
            event_queue.put_nowait,
            event
        )


    subscribe(handle_event)


    try:

        while True:

            # ----------------------------------
            # RECEIVE USER MESSAGE
            # ----------------------------------

            data = await websocket.receive_json()

            user_message = data.get(
                "message",
                ""
            ).strip()

            user_id = data.get(
                "user_id",
                "default-user"
            )


            # ----------------------------------
            # VALIDATE
            # ----------------------------------

            if not user_message:

                await websocket.send_json(
                    {
                        "type": "error",
                        "message": "Message cannot be empty."
                    }
                )

                continue


            # ----------------------------------
            # START PROCESSING
            # ----------------------------------

            task = asyncio.create_task(
                asyncio.to_thread(
                    process_message,
                    user_message,
                    user_id,
                    user_id
                )
            )


            # ----------------------------------
            # STREAM EVENTS
            # ----------------------------------

            while not task.done():

                try:

                    event = await asyncio.wait_for(
                        event_queue.get(),
                        timeout=0.1
                    )

                    await websocket.send_json(
                        {
                            "type": "event",
                            "event": event
                        }
                    )

                except asyncio.TimeoutError:

                    continue


            # ----------------------------------
            # SEND REMAINING EVENTS
            # ----------------------------------

            while not event_queue.empty():

                event = event_queue.get_nowait()

                await websocket.send_json(
                    {
                        "type": "event",
                        "event": event
                    }
                )


            # ----------------------------------
            # GET FINAL RESPONSE
            # ----------------------------------

            try:

                response = task.result()

                await websocket.send_json(
                    {
                        "type": "response",
                        "response": response
                    }
                )

            except Exception as e:

                await websocket.send_json(
                    {
                        "type": "error",
                        "message": str(e)
                    }
                )


    except WebSocketDisconnect:

        print(
            "  🌐 WebSocket client disconnected."
        )


    finally:

        unsubscribe(handle_event)