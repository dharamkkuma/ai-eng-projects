## Ask‑the‑Web Agent — Integration Guide

This guide explains how the project works, how to run it locally, and how to integrate the Ask‑the‑Web capability into your own app (by calling the provided FastAPI backend or embedding the agent directly).

### Repository Layout
- `backend/app.py` — FastAPI app exposing POST `/ask`; wraps a LangChain ReAct agent using an Ollama‑served model and a DuckDuckGo search tool.
- `frontend/` — Vite + React UI that calls the backend and renders responses.
- `ask_the_web_agent.ipynb` — Tutorial notebook showing manual tool‑calling, schema generation, and LangChain agent usage.
- `environment.yml` — Conda environment for Python runtime.
- `INTEGRATION_TEMPLATE.md` — This document.

### High‑Level Architecture
```
+-----------+        HTTP (POST /ask)        +------------------+      Local API       +-----------+
| Frontend  |  ───────────────────────────▶  | FastAPI Backend  |  ───────────────▶    |  Ollama   |
| (React)   |                                 |  (LangChain      |    http://localhost | (Models)  |
|           |  ◀──────── JSON ─────────────  |   Agent + Tools) |    :11434/v1        |           |
+-----------+                                 +------------------+                     +-----------+
                                              |
                                              | calls tool
                                              v
                                         +----------+
                                         | DuckDuck |
                                         |   Go     |
                                         +----------+
```

### Prerequisites
- macOS/Linux with Conda and Python 3.11
- Node.js 18+ for the frontend
- [Ollama](https://ollama.com) installed and able to run a local model

### Setup and Local Run
1) Create and activate the Python environment
```bash
cd /Users/dharmendra.kumar/magnum/zeus/ai-eng-projects/project_3
conda env create -f environment.yml
conda activate web_agent
python -m ipykernel install --user --name=web_agent --display-name "web_agent"
```

2) Start Ollama and pull a model
```bash
ollama serve
ollama pull llama3   # or gemma3 / mistral / qwen2.5 variants
```

3) Start the backend (from project root)
```bash
uvicorn backend.app:app --reload --port 8000
# If not starting from project root, set PYTHONPATH:
# PYTHONPATH=$PWD uvicorn backend.app:app --reload --port 8000
```

4) Start the frontend
```bash
cd frontend
npm install
npm run dev
# open http://localhost:5173
```

### Backend API
- Base URL: `http://127.0.0.1:8000`
- Endpoint: `POST /ask`
- Request body:
```json
{ "question": "What are the current events in San Francisco this week?" }
```
- Response body:
```json
{ "answer": "<agent final answer>" }
```

Quick test:
```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"What are the current events in San Francisco this week?"}'
```

### How It Works (Backend)
- The backend creates a LangChain agent:
  - LLM: `ChatOllama(model="llama3", temperature=0)`
  - Tools: `web_search(query: str)` implemented with `duckduckgo_search.DDGS`
  - Agent type: `ZERO_SHOT_REACT_DESCRIPTION` for simple ReAct‑style reasoning/action loops
- When `/ask` is called, the agent is invoked with the user question, may call `web_search`, then returns a final answer.

### Integrating Ask‑the‑Web into Your App

Option A — Call the provided backend (recommended to start)
- Run this repository’s backend and call its `/ask` endpoint from your service or UI.
- Pros: quickest path, no need to manage agent lifecycle or model I/O
- Cons: you operate a separate service

Option B — Embed the agent into your Python service
1) Ensure Ollama is running and your desired model is pulled.
2) Install deps similar to `environment.yml` (notably: `langchain`, `langchain-community`, `duckduckgo-search`, `openai` for the Ollama client shim if needed elsewhere).
3) Minimal snippet:
```python
from langchain_community.chat_models import ChatOllama
from langchain.agents import initialize_agent, Tool, AgentType
from duckduckgo_search import DDGS

def search_web(query: str, max_results: int = 10) -> str:
    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results):
            results.append(f"- {r['title']} — {r['href']}")
    return "\n".join(results) if results else "No results found."

tools = [Tool(name="web_search", func=search_web, description="Search the web and return links")] 
llm = ChatOllama(model="llama3", temperature=0)
agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)

print(agent.invoke({"input": "What are the current events in San Francisco this week?"})["output"])
```

### Changing Models
- Edit `backend/app.py` where `ChatOllama(model="llama3", ...)` is instantiated.
- Pull the model in Ollama first (e.g., `ollama pull gemma3`).
- Ensure your hardware can run the chosen model.

### Frontend Integration Notes
- The React app calls the backend `/ask` and renders the returned `answer`.
- If your backend runs on a different host/port, update the fetch base URL in `frontend/src/` accordingly.
- Consider streaming for long answers if needed; current API returns a single JSON payload.

### Troubleshooting
- `ModuleNotFoundError: backend` when starting uvicorn
  - Start uvicorn from the project root: `uvicorn backend.app:app --reload --port 8000`
  - Or set `PYTHONPATH` to the project root.
- `ModuleNotFoundError: langchain_community`
  - You are not in the `web_agent` conda env. Run `conda activate web_agent`.
- DuckDuckGo warnings (`use ddgs`)
  - The repo pins `duckduckgo-search==8.1.1` which exposes `from duckduckgo_search import DDGS`. Newer versions may rename to `ddgs`.
- Irrelevant search results
  - Web search is noisy. Tighten prompts, add basic filters, or switch to a different retrieval source.
- Ollama not reachable
  - Ensure `ollama serve` is running and the model is pulled. Default base URL is `http://localhost:11434`.

### Security & Production Considerations
- Add authentication/rate limiting in the backend if exposing publicly.
- Sanitize inputs passed into tools.
- Enable logging/monitoring for `/ask` usage and tool calls.
- Consider timeouts and concurrency limits around web tools.

### Extending with More Tools
Add functions and register them as LangChain tools. Example:
```python
from langchain.tools import tool

@tool
def get_current_weather(city: str, unit: str = "celsius") -> str:
    return f"It is 23°{unit[0].upper()} and sunny in {city}."
```
Append to your `tools` list, re‑initialize or reuse the agent.

### Sequence Diagram (Text)
```
User          Frontend          Backend (Agent)            Ollama              DuckDuckGo
 |  Type Q       |                     |                     |                      |
 |──────────────▶| fetch /ask          |                     |                      |
 |               |────────────────────▶| build prompt/tools  |                      |
 |               |                     | LLM call ─────────▶ |                      |
 |               |                     |      decide tool    |                      |
 |               |                     | call web_search ─────────────────────────▶ |
 |               |                     | ◀────────────────────────────────────────── |
 |               |                     | continue reasoning  |                      |
 |               |                     | final answer ◀───── |                      |
 |               | ◀───────────────────| return JSON         |                      |
 | ◀─────────────| render answer       |                     |                      |
```

### FAQ
- Can I use OpenAI API instead of Ollama?
  - This project is set up for local models via Ollama. You can swap `ChatOllama` for another chat model provider, but update dependencies and configuration accordingly.
- Can I stream partial tokens to the UI?
  - The current `/ask` returns a single JSON payload. You can adapt the backend to stream (e.g., Server‑Sent Events) if needed.
- How do I add RAG?
  - Add a retrieval tool (e.g., a vector store query) and surface it to the agent alongside `web_search`.

— End —



