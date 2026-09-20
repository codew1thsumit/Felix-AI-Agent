# FELIX AI --- Command Reference

This file collects the commands used during the FELIX AI development,
testing, and local running workflow.

> Note: Commands are grouped by purpose. Some commands were used for
> troubleshooting or testing specific components. Replace paths,
> usernames, IP addresses, or environment-specific values with your own
> when necessary.

------------------------------------------------------------------------

## 1. Open the FELIX project

Open Command Prompt or PowerShell and move into the project folder:

``` powershell
cd "D:\AI Agent"
```

If your project is stored somewhere else, use that folder instead.

------------------------------------------------------------------------

## 2. Check Python

``` powershell
python --version
```

Also useful:

``` powershell
py --version
```

Check which Python executable is being used:

``` powershell
where python
```

------------------------------------------------------------------------

## 3. Create a virtual environment

If creating the environment for the first time:

``` powershell
python -m venv .venv
```

Activate it in PowerShell:

``` powershell
.\.venv\Scripts\Activate.ps1
```

Activate it in Command Prompt:

``` cmd
.venv\Scripts\activate
```

Deactivate:

``` powershell
deactivate
```

------------------------------------------------------------------------

## 4. Upgrade pip

``` powershell
python -m pip install --upgrade pip
```

------------------------------------------------------------------------

## 5. Install FELIX dependencies

Install everything from `requirements.txt`:

``` powershell
pip install -r requirements.txt
```

Or:

``` powershell
python -m pip install -r requirements.txt
```

Check installed packages:

``` powershell
pip list
```

Check a specific package:

``` powershell
pip show aiosqlite
pip show pymongo
pip show langgraph-checkpoint-sqlite
pip show langchain
pip show langchain-google-genai
```

------------------------------------------------------------------------

## 6. Important FELIX packages

The project uses packages including:

``` text
langchain
langchain-community
langchain-google-genai
langgraph-checkpoint-sqlite
aiosqlite
pymongo
python-dotenv
requests
websockets
fastapi
rich
pydantic
wikipedia
```

If a package is missing, install it with:

``` powershell
pip install <package-name>
```

Example:

``` powershell
pip install aiosqlite
```

> `aiosqlite` is required by the async SQLite checkpointer used by the
> website backend.

------------------------------------------------------------------------

# 7. Run the terminal FELIX

The terminal version is started with:

``` powershell
python main.py
```

Stop it:

``` text
Ctrl+C
```

The terminal FELIX uses the synchronous SQLite checkpointer.

------------------------------------------------------------------------

# 8. Run the FELIX website

Start the website/backend:

``` powershell
python server.py
```

Stop the server:

``` text
Ctrl+C
```

Open the website in Chrome:

``` text
http://127.0.0.1:8000
```

Alternative:

``` text
http://localhost:8000
```

------------------------------------------------------------------------

# 9. Check whether the website is running

Open:

``` text
http://127.0.0.1:8000
```

Health endpoint:

``` text
http://127.0.0.1:8000/health
```

If the health endpoint is available, it can be used to confirm that the
FastAPI backend is alive.

------------------------------------------------------------------------

# 10. FastAPI / Swagger testing

FELIX's FastAPI backend can be tested through Swagger when the API
exposes the documentation.

Open:

``` text
http://127.0.0.1:8000/docs
```

Alternative OpenAPI JSON:

``` text
http://127.0.0.1:8000/openapi.json
```

------------------------------------------------------------------------

# 11. Test the WebSocket

The FELIX WebSocket endpoint is:

``` text
ws://127.0.0.1:8000/ws/<session_id>
```

For example:

``` text
ws://127.0.0.1:8000/ws/test-session
```

------------------------------------------------------------------------

# 12. WebSocket test client

Create a temporary file such as:

``` text
test_websocket.py
```

Use:

``` python
import asyncio
import json
import websockets

async def main():
    uri = "ws://127.0.0.1:8000/ws/test-session"

    async with websockets.connect(uri) as websocket:
        print("Connected to FELIX WebSocket.")

        await websocket.send(json.dumps({
            "type": "message",
            "message": "Who is Albert Einstein?"
        }))

        while True:
            message = await websocket.recv()
            data = json.loads(message)

            print("\nSERVER:")
            print(json.dumps(data, indent=2, ensure_ascii=False))

            if data.get("type") in ("response", "error", "stopped"):
                break

asyncio.run(main())
```

Run it:

``` powershell
python test_websocket.py
```

Expected behavior is that the server sends events/streaming information
and eventually a response.

------------------------------------------------------------------------

# 13. Test a simple WebSocket message

Example test question:

``` text
Who is Albert Einstein?
```

Another useful test:

``` text
What is Python?
```

Wikipedia test:

``` text
Who was Isaac Newton?
```

------------------------------------------------------------------------

# 14. Test FELIX memory

Use a specific user/session when testing memory isolation.

Example first message:

``` text
My name is Debjeet.
```

Then ask:

``` text
What is my name?
```

Test a second user/session and confirm that unrelated users do not
automatically receive the first user's memories.

------------------------------------------------------------------------

# 15. Test long-term memory

Project memory is stored in MongoDB Atlas.

Useful tests:

``` text
My name is Debjeet.
```

Then:

``` text
Remember that I am building FELIX AI.
```

Then later:

``` text
What project am I building?
```

------------------------------------------------------------------------

# 16. Test Wikipedia

Ask something that benefits from Wikipedia:

``` text
Who is Albert Einstein?
```

``` text
Tell me about the Roman Empire.
```

``` text
Who was Nikola Tesla?
```

FELIX should use the Wikipedia tool when it is useful rather than
calling it for every normal question.

------------------------------------------------------------------------

# 17. Check the Wikipedia tool directly

The project tool is:

``` text
wikipedia_tool.py
```

It uses the Wikipedia API.

A direct Python syntax check can be performed with:

``` powershell
python -m py_compile wikipedia_tool.py
```

------------------------------------------------------------------------

# 18. Python syntax checks

Check the main terminal application:

``` powershell
python -m py_compile main.py
```

Check the website server:

``` powershell
python -m py_compile server.py
```

Check the memory module:

``` powershell
python -m py_compile memory.py
```

Check MongoDB module:

``` powershell
python -m py_compile mongodb.py
```

Check the Wikipedia tool:

``` powershell
python -m py_compile wikipedia_tool.py
```

Check the events module:

``` powershell
python -m py_compile events.py
```

Check the Obsidian module:

``` powershell
python -m py_compile obsidian_manager.py
```

Check several files at once:

``` powershell
python -m py_compile main.py server.py memory.py mongodb.py wikipedia_tool.py events.py obsidian_manager.py
```

------------------------------------------------------------------------

# 19. Check the FELIX folder

PowerShell:

``` powershell
Get-ChildItem
```

Recursive:

``` powershell
Get-ChildItem -Recurse
```

Command Prompt:

``` cmd
dir
```

Recursive:

``` cmd
dir /s
```

------------------------------------------------------------------------

# 20. Check the static website files

``` powershell
Get-ChildItem .\static
```

Expected important files:

``` text
index.html
style.css
app.js
felix-logo.png
```

------------------------------------------------------------------------

# 21. Check the database folder

``` powershell
Get-ChildItem .\database
```

Important databases:

``` text
database\felix_memory.db
database\chat_sessions.db
```

------------------------------------------------------------------------

# 22. Check environment variables

The project uses a `.env` file.

Check that the file exists:

``` powershell
Test-Path .env
```

Expected:

``` text
True
```

Do **not** print or share the actual API key.

The `.env` file should contain values such as:

``` text
GOOGLE_API_KEY=...
MONGODB_URI=...
```

Never commit the real `.env` file to GitHub.

------------------------------------------------------------------------

# 23. Check MongoDB package

``` powershell
pip show pymongo
```

Check PyMongo version:

``` powershell
python -c "import pymongo; print(pymongo.version)"
```

------------------------------------------------------------------------

# 24. Check aiosqlite

``` powershell
pip show aiosqlite
```

Or:

``` powershell
python -c "import aiosqlite; print(aiosqlite.__version__)"
```

------------------------------------------------------------------------

# 25. Check WebSockets package

``` powershell
pip show websockets
```

Or:

``` powershell
python -c "import websockets; print(websockets.__version__)"
```

------------------------------------------------------------------------

# 26. Check FastAPI

``` powershell
pip show fastapi
```

------------------------------------------------------------------------

# 27. Check LangGraph SQLite package

``` powershell
pip show langgraph-checkpoint-sqlite
```

------------------------------------------------------------------------

# 28. Check Google Gemini package

``` powershell
pip show langchain-google-genai
```

------------------------------------------------------------------------

# 29. Check which process is using port 8000

If FELIX cannot start because port 8000 is already being used:

``` cmd
netstat -ano | findstr :8000
```

The final number is the PID.

Example:

``` text
TCP    127.0.0.1:8000    0.0.0.0:0    LISTENING    12345
```

Find the process:

``` cmd
tasklist /FI "PID eq 12345"
```

Stop it if necessary:

``` cmd
taskkill /PID 12345 /F
```

Then start FELIX again:

``` powershell
python server.py
```

------------------------------------------------------------------------

# 30. Local network URL

Find your laptop's IP:

``` cmd
ipconfig
```

Look for:

``` text
IPv4 Address
```

For example:

``` text
192.168.1.15
```

Then another device on the same network may be able to open:

``` text
http://192.168.1.15:8000
```

This requires the server/firewall/network to allow the connection.

------------------------------------------------------------------------

# 31. Browser hard refresh

After changing HTML/CSS/JavaScript/logo files:

``` text
Ctrl + Shift + R
```

If the favicon/logo is cached, close the FELIX browser tab completely
and open:

``` text
http://127.0.0.1:8000
```

again.

------------------------------------------------------------------------

# 32. Useful browser debugging

Open Chrome DevTools:

``` text
F12
```

Or:

``` text
Ctrl + Shift + I
```

JavaScript console:

``` text
Ctrl + Shift + J
```

Network tab:

``` text
F12 → Network
```

Check WebSocket:

``` text
F12 → Network → WS
```

Look for:

``` text
/ws/<session_id>
```

------------------------------------------------------------------------

# 33. Test frontend JavaScript

The main frontend file is:

``` text
static/app.js
```

The HTML loads it with:

``` html
<script src="/static/app.js"></script>
```

The main styling file is:

``` text
static/style.css
```

The main page is:

``` text
static/index.html
```

The FELIX logo is:

``` text
static/felix-logo.png
```

------------------------------------------------------------------------

# 34. Test chat functionality

Run:

``` powershell
python server.py
```

Open:

``` text
http://127.0.0.1:8000
```

Test:

``` text
Hello FELIX
```

Then test:

``` text
What is Python?
```

Then test a code response:

``` text
Write a Python function that adds two numbers.
```

Verify:

-   Message appears
-   Response streams
-   Code block appears
-   Copy button works
-   Markdown renders
-   Conversation is saved
-   Chat remains after refresh

------------------------------------------------------------------------

# 35. Test Enter and Shift+Enter

Normal send:

``` text
Type message → Enter
```

New line:

``` text
Shift + Enter
```

------------------------------------------------------------------------

# 36. Test Stop Generation

Send a long request such as:

``` text
Explain artificial intelligence in great detail with examples, history, applications, advantages, disadvantages, and future possibilities.
```

While it is generating:

``` text
Click Stop
```

Verify that generation actually stops.

------------------------------------------------------------------------

# 37. Test New Chat

Click:

``` text
New chat
```

Then send:

``` text
Hello
```

Verify that a new conversation is created.

------------------------------------------------------------------------

# 38. Test chat persistence

1.  Send a message.
2.  Refresh the browser:

``` text
Ctrl + R
```

3.  Open the same conversation.
4.  Verify the messages remain.

------------------------------------------------------------------------

# 39. Test rename

Rename a conversation and refresh:

``` text
Ctrl + R
```

Verify the new name remains.

------------------------------------------------------------------------

# 40. Test delete

Delete a conversation from the sidebar.

Then refresh:

``` text
Ctrl + R
```

Verify it remains deleted.

------------------------------------------------------------------------

# 41. Test clear current chat

Open a conversation and use the top-right clear button.

Verify the current conversation messages are cleared.

------------------------------------------------------------------------

# 42. Test theme

Use:

``` text
Appearance
```

or the top-right theme button.

Verify:

``` text
Dark
Light
```

both work without changing the rest of the UI structure.

------------------------------------------------------------------------

# 43. Test model display

The current UI identifies the configured model as:

``` text
Gemini 3.5 Flash-Lite
```

The sidebar profile identifies:

``` text
Gemini 3.5 Flash-Lite · LangGraph
```

------------------------------------------------------------------------

# 44. Test response activity

During a response, verify that FELIX only shows tools/agents that are
actually involved.

For example:

``` text
FELIX
Memory
Gemini
```

If Wikipedia is actually used:

``` text
FELIX
Memory
Wikipedia
Gemini
```

Wikipedia should not appear for every normal response.

------------------------------------------------------------------------

# 45. Check running Python processes

``` cmd
tasklist | findstr python
```

PowerShell alternative:

``` powershell
Get-Process python
```

------------------------------------------------------------------------

# 46. Stop a Python process

If you need to stop a specific Python process:

``` cmd
taskkill /PID <PID> /F
```

Use this carefully.

------------------------------------------------------------------------

# 47. Important SQLite rule

The terminal FELIX and website FELIX use different SQLite checkpointer
modes.

Terminal:

``` text
SqliteSaver
```

Website:

``` text
AsyncSqliteSaver
```

For testing, avoid running both against the same checkpoint database at
the same time.

Recommended:

``` text
Terminal testing:
python main.py
```

or:

``` text
Website testing:
python server.py
```

Stop one before testing the other.

------------------------------------------------------------------------

# 48. Full basic startup sequence

For normal website development:

``` powershell
cd "D:\AI Agent"
.\.venv\Scripts\Activate.ps1
python server.py
```

Then open:

``` text
http://127.0.0.1:8000
```

------------------------------------------------------------------------

# 49. Full basic test sequence

``` powershell
cd "D:\AI Agent"
.\.venv\Scripts\Activate.ps1
python -m py_compile main.py server.py memory.py mongodb.py wikipedia_tool.py events.py obsidian_manager.py
python server.py
```

Then open:

``` text
http://127.0.0.1:8000
```

Test:

``` text
Hello FELIX
```

``` text
My name is Debjeet.
```

``` text
What is my name?
```

``` text
Who is Albert Einstein?
```

``` text
Write a Python function to calculate factorial.
```

Then test:

``` text
Enter
Shift + Enter
Stop
New Chat
Rename
Delete
Clear Chat
Dark/Light mode
Refresh
Copy code
```

------------------------------------------------------------------------

# 50. Stop FELIX

In the terminal running the server:

``` text
Ctrl+C
```

------------------------------------------------------------------------

# 51. Quick emergency restart

If something gets stuck:

``` text
Ctrl+C
```

Then:

``` powershell
python server.py
```

Refresh Chrome:

``` text
Ctrl + Shift + R
```

------------------------------------------------------------------------

# 52. Recommended daily workflow

``` powershell
cd "D:\AI Agent"
.\.venv\Scripts\Activate.ps1
python -m py_compile server.py
python server.py
```

Open:

``` text
http://127.0.0.1:8000
```

After frontend changes:

``` text
Ctrl + Shift + R
```

After stopping:

``` text
Ctrl+C
```

------------------------------------------------------------------------

# 53. Project URL summary

Local FELIX URL:

``` text
http://127.0.0.1:8000
```

Localhost equivalent:

``` text
http://localhost:8000
```

Swagger:

``` text
http://127.0.0.1:8000/docs
```

Health:

``` text
http://127.0.0.1:8000/health
```

WebSocket:

``` text
ws://127.0.0.1:8000/ws/<session_id>
```

------------------------------------------------------------------------

# 54. Important security reminders

Never paste your real Google API key into:

-   GitHub
-   screenshots
-   chat messages
-   frontend JavaScript
-   HTML
-   public documentation

Keep it in:

``` text
.env
```

Make sure `.env` is in `.gitignore`.

If an API key has ever been exposed publicly, rotate it before
publishing the project.

------------------------------------------------------------------------

# 55. FELIX main files

``` text
main.py                  Terminal FELIX
server.py                FastAPI + WebSocket website backend
memory.py                Long-term memory logic
mongodb.py               MongoDB connection
wikipedia_tool.py        Wikipedia tool
events.py                FELIX event system
obsidian_manager.py      Obsidian backup
static/index.html        Website structure
static/style.css         Website design
static/app.js            Website functionality
static/felix-logo.png    FELIX logo
database/felix_memory.db LangGraph checkpoint database
database/chat_sessions.db Website chat database
.env                     API/database secrets
requirements.txt         Python dependencies
```

------------------------------------------------------------------------

# 56. One-command syntax check

From the FELIX project folder:

``` powershell
python -m py_compile main.py server.py memory.py mongodb.py wikipedia_tool.py events.py obsidian_manager.py
```

If this command returns to the prompt without an error, Python syntax
compilation succeeded for those files.

------------------------------------------------------------------------

# 57. One-command dependency check

``` powershell
python -c "import fastapi, aiosqlite, pymongo, requests, websockets, langchain, langchain_google_genai; print('FELIX dependencies OK')"
```

------------------------------------------------------------------------

# 58. One-command Python environment check

``` powershell
python -c "import sys; print(sys.executable); print(sys.version)"
```

------------------------------------------------------------------------

## Quick Reference

### Start website

``` powershell
python server.py
```

### Start terminal FELIX

``` powershell
python main.py
```

### Website

``` text
http://127.0.0.1:8000
```

### Swagger

``` text
http://127.0.0.1:8000/docs
```

### Health

``` text
http://127.0.0.1:8000/health
```

### Check port 8000

``` cmd
netstat -ano | findstr :8000
```

### Check Python

``` powershell
python --version
```

### Check syntax

``` powershell
python -m py_compile main.py server.py memory.py mongodb.py wikipedia_tool.py events.py obsidian_manager.py
```

### Install dependencies

``` powershell
pip install -r requirements.txt
```

### Hard refresh

``` text
Ctrl + Shift + R
```

### Stop server

``` text
Ctrl+C
```
