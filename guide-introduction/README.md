# FELIX AI

FELIX is a terminal-based AI assistant built with Python, LangChain, Gemini, Rich, and external tools.

The project is being developed as a learning-focused AI assistant that can be expanded over time with more AI APIs, tools, and capabilities.

> **Project status:** Early development / actively improving  
> **Current AI model:** Gemini  
> **Current external tool:** Wikipedia

## What FELIX Can Do

- Chat with Gemini from the terminal
- Use a LangChain agent to decide when a tool is useful
- Search Wikipedia through the Wikipedia API
- Display AI responses as formatted Markdown panels
- Handle startup input (`yes/y` or `no/n`)
- Exit the chat with `exit`
- Handle empty messages and API/tool errors
- Keep the project modular so more APIs and tools can be added later

## Current Architecture

```text
                         FELIX
                           |
                           v
                    LangChain Agent
                           |
                    +------+------+
                    |             |
                    v             v
                  Gemini       Wikipedia
                    |             |
                    |             v
                    |        Wikipedia API
                    |             |
                    +------+------+
                           |
                           v
                     Final Response
                           |
                           v
                        Terminal
```

The goal is **not** to send every question to every API. The LangChain agent can decide when an external tool is useful.

For example:

```text
User: Who was Albert Einstein?
        |
        v
   Gemini Agent
        |
        v
  Wikipedia needed
        |
        v
 Wikipedia Tool
        |
        v
   Gemini response
```

For a simple programming question, the agent may answer directly without using Wikipedia.

## Project Structure

```text
FELIX/
│
├── main.py
├── user_input.py
├── wikipedia_tool.py
├── config.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

### Main files

| File | Purpose |
|---|---|
| `main.py` | Main FELIX application and LangChain agent |
| `user_input.py` | Startup input and FELIX startup sequence |
| `wikipedia_tool.py` | Wikipedia API tool exposed to LangChain |
| `config.py` | Local configuration module |
| `requirements.txt` | Python dependencies |
| `.env.example` | Example environment-variable file |
| `.gitignore` | Prevents secrets and local files from being committed |
| `README.md` | Project documentation |

## Requirements

- Python 3.10 or newer
- Internet connection
- A Gemini API key
- Windows, macOS, or Linux

The project currently uses packages that support modern Python versions, including Python 3.14.

## Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd FELIX
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with your repository URL.

### 2. Create a virtual environment

#### Windows PowerShell

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

Then:

```powershell
.\venv\Scripts\Activate.ps1
```

You should see:

```text
(venv) PS D:\Your\Project>
```

#### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Install dependencies

With the virtual environment activated:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Configure the Gemini API key

Create a file named:

```text
.env
```

in the root of the project.

Add:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Do **not** commit `.env` to GitHub.

Google recommends keeping API keys in environment variables rather than hardcoding them in source code.

## 5. Run FELIX

With the virtual environment activated:

```bash
python main.py
```

You should see:

```text
Start FELIX AI (yes/no)
```

Enter:

```text
yes
```

or:

```text
y
```

to start FELIX.

Enter:

```text
no
```

or:

```text
n
```

to exit.

## Using FELIX

After FELIX starts:

```text
👤 You
›››
```

Type your question.

Example:

```text
››› Who was Albert Einstein?
```

If the agent decides Wikipedia is useful, the terminal can show the Wikipedia tool being used.

To leave the conversation:

```text
››› exit
```

## Checking Whether Wikipedia Is Being Used

`wikipedia_tool.py` contains debug messages so you can see when the tool is called.

For example:

```text
⠿ Felix is thinking...

📚 Wikipedia searching: Albert Einstein
📚 Wikipedia: results found
```

This is useful while testing the agent.

The absence of the Wikipedia message does not necessarily mean the tool is broken. It can mean that the agent decided the tool was unnecessary.

## How the Wikipedia Tool Works

FELIX does not use the old `langchain-community` Wikipedia integration.

The current project calls the Wikipedia API directly using `requests` and exposes the function to LangChain with `@tool`.

```text
User
  |
  v
LangChain Agent
  |
  +---- No tool needed ----> Gemini
  |
  +---- Wikipedia needed --> Wikipedia API
                                  |
                                  v
                              Results
                                  |
                                  v
                                Gemini
                                  |
                                  v
                               Answer
```

This keeps the Wikipedia integration simple and makes it easier to add other APIs later.

## Planned Improvements

This project is intentionally designed to grow.

Possible future additions:

- [ ] Grok / xAI API
- [ ] Additional Gemini capabilities
- [ ] Web search
- [ ] Calculator tool
- [ ] Weather tool
- [ ] News/search tools
- [ ] Image understanding
- [ ] Voice input
- [ ] Text-to-speech
- [ ] Better Wikipedia article retrieval
- [ ] Conversation memory
- [ ] Streaming responses
- [ ] Better agent/tool status display
- [ ] Configuration system
- [ ] Better error handling
- [ ] Tests
- [ ] Logging
- [ ] More modular project structure

## Why This Project Exists

FELIX is primarily a learning and experimentation project.

The goal is to understand:

- Python
- APIs
- LangChain
- AI agents
- Tool calling
- Environment variables
- Virtual environments
- API integrations
- Terminal applications
- Modular project structure

More integrations will be added over time.

## Known Limitations

This is an early version, so you may encounter:

- API errors
- Model/API availability issues
- Wikipedia search limitations
- Agent decisions that are not always ideal
- Different behavior after dependency updates
- Internet/network-related failures
- Markdown formatting differences
- Model-name changes as providers update their APIs

If you find something that does not work, please report it.

## Bug Reports

If you find a bug, please open a GitHub Issue.

When reporting a bug, include:

1. What you were trying to do
2. What you expected to happen
3. What actually happened
4. The full error message or traceback
5. Your Python version
6. Your operating system
7. The package versions if possible
8. Steps to reproduce the problem

### Example

```text
Python: 3.14.x
OS: Windows 11

Problem:
Wikipedia tool fails when asking about a person.

Expected:
FELIX should search Wikipedia and answer.

Actual:
FELIX returns an HTTP 403 error.

Error:
[paste traceback here]

Steps:
1. Start FELIX
2. Enter yes
3. Ask "Who was Albert Einstein?"
4. Error appears
```

Please do not post API keys, passwords, `.env` contents, or other secrets in an issue.

## Contributing

Suggestions, bug reports, improvements, and new tool ideas are welcome.

If you want to contribute, fork the repository using GitHub's **Fork** button, then clone your fork.

Create a branch:

```bash
git checkout -b feature/your-feature
```

Make your changes, test them, and open a Pull Request.

For small projects or first-time contributions, opening an Issue first is also a good way to discuss an idea.

## Security

Never commit your real API key.

Your `.env` file should remain local:

```text
.env
```

Use `.env.example` as a template instead.

If an API key is accidentally pushed to GitHub, revoke/rotate it immediately.

## License

Choose a license before publishing the repository.

For example, you can use the MIT License by adding a `LICENSE` file to the repository.

## Project Roadmap

### v0.1 — Current

- Gemini chat
- LangChain agent
- Wikipedia tool
- Rich terminal interface
- Basic error handling
- Environment-variable configuration

### Future

```text
v0.2
 ├── More tools
 ├── Better Wikipedia retrieval
 └── Improved terminal UI

v0.3
 ├── Additional AI APIs
 ├── Better routing
 └── Tool selection improvements

v0.4+
 ├── Memory
 ├── Voice
 ├── Vision
 ├── More APIs
 └── Advanced agent capabilities
```

## Feedback

If you try FELIX, please let me know:

- What worked
- What broke
- What could be improved
- What API/tool should be added next

Even small bug reports are useful while the project is being developed.
