# FELIX AI Agent

> A multi-model AI agent with memory, intelligent model routing, tools, and a real-time web interface.

FELIX is a Python-based AI assistant built with LangChain, LangGraph, Gemini, OpenRouter Free, MongoDB, SQLite, FastAPI, WebSockets, and a modular tool system.

## ✨ Features

- 🤖 Gemini + OpenRouter Free multi-model support
- ⚡ Synapse intelligent model routing
- 🧠 MongoDB Atlas long-term memory
- 💾 LangGraph SQLite checkpointing
- 💬 SQLite-based website chat sessions
- 🌐 FastAPI + WebSocket real-time streaming
- 📚 Wikipedia search
- 🌤️ Current weather
- 🕐 Current local time
- 📝 Obsidian Markdown conversation backup
- ⛔ Stop generation
- 🔄 Regenerate responses
- ✏️ Rename sessions
- 🗑️ Delete/clear sessions
- 🔎 Session search
- 🌙 Dark/light interface
- 📱 Responsive web UI
- 💻 Markdown and code formatting

## 🏗️ Architecture

```text
                         ┌──────────────────┐
                         │    FELIX UI      │
                         │ HTML / CSS / JS  │
                         └────────┬─────────┘
                                  │ WebSocket
                                  ▼
                         ┌──────────────────┐
                         │     FastAPI      │
                         │    server.py     │
                         └────────┬─────────┘
                                  ▼
                         ┌──────────────────┐
                         │      FELIX       │
                         │      Agent       │
                         └────────┬─────────┘
                                  ▼
                         ┌──────────────────┐
                         │     Synapse      │
                         │   Model Router   │
                         └───────┬───┬──────┘
                                 │   │
                    ┌────────────▼┐ ┌▼────────────────┐
                    │   Gemini    │ │ OpenRouter Free │
                    └─────────────┘ └─────────────────┘

                 Agent Tools
          ┌──────────┬──────────┐
          ▼          ▼          ▼
      Wikipedia   Weather      Time

          ┌────────────────────────────┐
          │      MongoDB Atlas        │
          │     Long-term Memory      │
          └────────────────────────────┘

          ┌────────────────────────────┐
          │     LangGraph SQLite      │
          │       Checkpointing       │
          └────────────────────────────┘

          ┌────────────────────────────┐
          │       Obsidian            │
          │    Markdown Backup        │
          └────────────────────────────┘
```

## 📁 Project Structure

```text
Felix-AI-Agent/
├── backend/
│   ├── __init__.py
│   └── app.py
├── guide-introduction/
│   ├── bug_report.md
│   ├── FELIX-all-commands.md
│   └── url.txt
├── static/
│   ├── app.js
│   ├── felix-logo.png
│   ├── index.html
│   └── style.css
├── synapse/
│   ├── __init__.py
│   ├── agent.py
│   ├── executor.py
│   ├── models.py
│   └── router.py
├── tests/
│   ├── test_executor.py
│   ├── test_gemini.py
│   ├── test_openrouter.py
│   └── test_synapse.py
├── config.py
├── events.py
├── main.py
├── memory.py
├── mongodb.py
├── obsidian_manager.py
├── requirements.txt
├── server.py
├── time_tool.py
├── user_input.py
├── weather_tool.py
├── wikipedia_tool.py
└── README.md
```

## ⚡ Synapse

Synapse separates model selection from the main FELIX agent:

```text
User Request
     │
     ▼
  Synapse
   ├── Gemini
   └── OpenRouter Free
```

This makes it possible to expand FELIX with additional models and routing rules without redesigning the agent.

## 🧠 Memory

FELIX uses MongoDB Atlas for long-term memory.

The memory system can store useful information such as:

- 👤 Names
- 💻 Projects
- ❤️ Preferences
- 🎮 Interests

Storage responsibilities are separated:

| Storage | Purpose |
|---|---|
| MongoDB | Long-term user memory |
| LangGraph SQLite | Agent checkpoint/state |
| Chat SQLite | Website sessions/messages |
| Obsidian | Local Markdown backup |

## 🛠️ Tools

### 📚 Wikipedia

Searches Wikipedia for useful factual information.

File:

```text
wikipedia_tool.py
```

### 🌤️ Weather

Gets current weather for a city, including:

- 🌥️ Condition
- 🌡️ Temperature
- 🥵 Feels-like temperature
- 💧 Humidity
- 🌧️ Precipitation
- 💨 Wind speed
- 🕐 Local time

File:

```text
weather_tool.py
```

Powered by Open-Meteo.

### 🕐 Time

Gets the current local time for a city, including:

- 📅 Date
- ⏰ Time
- 🌍 Timezone

File:

```text
time_tool.py
```

## 🌐 Web Interface

The frontend is served by FastAPI and communicates through WebSockets.

It supports:

- 💬 Real-time chat
- 📂 Session history
- 🔎 Search
- ✏️ Rename
- 🗑️ Delete
- 🧹 Clear chat
- ⛔ Stop generation
- 🔄 Regenerate
- 📋 Copy responses/code
- 🌙 Dark/light mode
- 📱 Responsive layout

Frontend:

```text
static/
├── index.html
├── style.css
├── app.js
└── felix-logo.png
```

## 🚀 Installation

### 1. Clone

```powershell
git clone https://github.com/sumit1ntech/Felix-AI-Agent.git
cd Felix-AI-Agent
```

### 2. Create virtual environment

```powershell
python -m venv .venv
```

### 3. Activate

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```powershell
pip install -r requirements.txt
```

## 🔐 Environment Variables

Create `.env` in the project root:

```env
GOOGLE_API_KEY=your_google_api_key
OPENROUTER_API_KEY=your_openrouter_api_key
MONGODB_URI=your_mongodb_connection_string
```

Never commit `.env` to GitHub.

## 🗄️ MongoDB

FELIX uses MongoDB Atlas for long-term memory.

Database:

```text
felix
```

Collection:

```text
memories
```

Set the connection string in:

```env
MONGODB_URI=your_mongodb_connection_string
```

## ▶️ Run FELIX

```powershell
python server.py
```

Open:

```text
http://127.0.0.1:8000
```

## 🧪 Testing

### Synapse

```powershell
python tests/test_synapse.py
```

### Gemini

```powershell
python tests/test_gemini.py
```

### OpenRouter

```powershell
python tests/test_openrouter.py
```

### Executor

```powershell
python tests/test_executor.py
```

### Weather

```powershell
python -c "from weather_tool import get_current_weather; print(get_current_weather.invoke('Kolkata'))"
```

### Time

```powershell
python -c "from time_tool import get_current_time; print(get_current_time.invoke('Kolkata'))"
```

## 💬 Example Prompts

```text
Explain what an AI agent is.
```

```text
What's the weather in Kolkata right now?
```

```text
What time is it in Tokyo right now?
```

```text
Who invented the C programming language?
```

```text
Explain Python classes with an example.
```

## 🧩 Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core language |
| LangChain | Agent framework |
| LangGraph | Agent state/checkpointing |
| Gemini | LLM |
| OpenRouter | Free model access |
| Synapse | Model routing |
| FastAPI | Backend |
| WebSocket | Real-time streaming |
| MongoDB Atlas | Long-term memory |
| SQLite | Checkpoints and chat sessions |
| Open-Meteo | Weather/time data |
| Wikipedia | Knowledge lookup |
| Obsidian | Markdown backup |
| HTML/CSS/JavaScript | Frontend |

## 🔒 Security

Never commit:

```text
.env
database/
.venv/
__pycache__/
```

Keep API keys and database credentials private.

## 🗺️ Roadmap

- 🔴 Reddit integration
- 🌐 Additional web search tools
- 🧠 Improved memory retrieval
- ⚡ More advanced model routing
- 🔀 Additional LLM providers
- 🛠️ Smarter tool routing
- 📊 Better agent/event observability
- 🚀 Production deployment
- 🔐 Authentication
- 👥 Multi-user support

## 📌 Project Status

**Active development**

Current major capabilities:

- ✅ Gemini
- ✅ OpenRouter Free
- ✅ Synapse routing
- ✅ MongoDB memory
- ✅ LangGraph checkpointing
- ✅ SQLite chat sessions
- ✅ Wikipedia
- ✅ Weather
- ✅ Time
- ✅ FastAPI
- ✅ WebSocket streaming
- ✅ Web interface
- ✅ Session management
- ✅ Stop/regenerate
- ✅ Obsidian integration

## 👨‍💻 Author

**Sumit Bhaya, 
Debjeet Paramanik, 
Munna Ruhidas, 
Sk Firoz**

GitHub: https://github.com/sumit1ntech

Project: https://github.com/sumit1ntech/Felix-AI-Agent

## Contributors

- [Sumit Bhaya](https://github.com/sumit1ntech) — Project Creator
- [Debjeet Paramanik](https://github.com/debjeet1ntech) — Contributor
- [Munna Ruhidas](https://github.com/codew1thmunna) — Contributor
- [Sk Firoz](https://github.com/) — Contributor

## 📄 License

This project is licensed under the MIT License.

See [LICENSE](LICENSE) for details.
