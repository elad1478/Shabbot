# Shabbot Workshop: Building Practical Agents with LangChain and MCP

This hands-on workshop walks you through the Shabbot project and uses it to teach core concepts:
- LangChain tools and agent basics
- Composing agents from tools
- Sub-agents (an agent as a tool)
- Hosted MCP (Model Context Protocol) integration
- Web UI for agent interaction

By the end, you’ll know how to extend Shabbot with your own tools and agents.

---

## 1) Project Tour

Key directories and files:

```
langchain-demo-agent/
├── main.py                  # Main agent (orchestrator)
├── web_app.py               # Flask web app
├── templates/index.html     # Web UI (logo, loader, output)
├── tools/
│   ├── rag_tool.py          # RAG/Bible search (Pinecone + OpenAI)
│   ├── search_tool.py       # Web search (Tavily)
│   ├── qr_tool.py           # QR code generation
│   ├── slack_tool.py        # Slack messages
│   ├── gematria_tool.py     # Gematria calculator
│   ├── date_tool.py         # Today’s date
│   ├── shababot_tool.py     # Sub-agent exposed as a tool (Shabbot)
│   └── jewish_calendar_mcp.py # Hosted MCP (Hebcal) client
└── agents/
    └── shababot.py          # Shabbot sub-agent (date, gematria, bible, MCP calendar)
```

---

## 2) LangChain Tools

A LangChain tool is a function with a `@tool` decorator returning a user-facing string.

Example: `tools/date_tool.py`
```python
from datetime import date
from langchain_core.tools import tool

@tool
def get_today_date() -> str:
    """Return today's date (Gregorian) in YYYY-MM-DD format."""
    return date.today().isoformat()
```

Example: `tools/qr_tool.py` (trimmed)
```python
class QRCodeTool:
    def generate_qr_code(self, data: str, filename: str = None) -> str:
        # ... build and save QR ...
        return f"QR code generated successfully: {filepath}"

@tool
def generate_qr_code(data: str, filename: str = None) -> str:
    return qr_tool.generate_qr_code(data, filename)
```

Design tips:
- Tools should be deterministic, predictable, and return concise results.
- Keep side effects (like file writes) explicit in the return message.

---

## 3) Building an Agent

Agents choose which tools to call. In `main.py`, we configure the orchestrator agent with a system prompt, tool list, and LLM.

```python
# main.py (trimmed)
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_openai import ChatOpenAI

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)
```

The orchestrator agent exposes selected tools (including the Shabbot sub-agent as a single tool).

---

## 4) Designing Effective Prompts

The orchestrator’s system prompt instructs how to route tasks:

```python
# main.py (excerpt)
system_prompt = """You are the Main Agent orchestrator...

Capabilities:
1. **Jewish Utilities (Shabbot)**: Use the `shabbot` tool for all Jewish utilities...
2. **QR Code Generation**: ...
3. **Web Search**: ...
4. **Slack Integration**: ...

Guidelines:
- Select the appropriate tool...
- For any date, Gematria, Bible, or Jewish calendar task, always use `shabbot`.
..."""
```

Prompt guidelines:
- List capabilities and explicitly map them to tool names.
- Provide do/don’t rules (e.g., always use `shabbot` for X category).
- Include a few examples of the correct tool selection.

---

## 5) Sub-Agents: Shabbot (Agent-as-a-Tool)

Shabbot bundles multiple tools (date, gematria, bible RAG, Jewish calendar MCP) into one agent. We then expose Shabbot as a single tool for the main agent.

Create the sub-agent:
```python
# agents/shababot.py (trimmed)
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_openai import ChatOpenAI

from tools.date_tool import get_today_date
from tools.gematria_tool import calculate_gematria
from tools.rag_tool import search_bible
from tools.jewish_calendar_mcp import get_jewish_calendar_tools_sync

system_prompt = (
    "You are Shabbot, a helpful Jewish assistant...\n"
    "Guidelines:\n"
    "- When the user asks about biblical figures... ALWAYS use `search_bible`.\n"
)

shabbot_tools = [get_today_date, calculate_gematria, search_bible]
shabbot_tools.extend(get_jewish_calendar_tools_sync() or [])

agent = create_tool_calling_agent(ChatOpenAI(temperature=0, model="gpt-4o-mini"), shabbot_tools, prompt)
executor = AgentExecutor(agent=agent, tools=shabbot_tools, ...)
```

Expose it as a top-level tool:
```python
# tools/shababot_tool.py
from langchain_core.tools import tool
from agents.shababot import create_shabbot_agent

@tool
def shabbot(query: str) -> str:
    agent = create_shabbot_agent()
    result = asyncio.run(agent.ainvoke({"input": query}))
    return result.get("output", str(result))
```

Why sub-agents?
- Encapsulation: The orchestrator doesn’t need to know which specific tools handle Jewish utilities.
- Policy control: Shabbot can have its own system prompt and routing rules.
- Extensibility: Add/remove Jewish tools without touching the orchestrator.

---

## 6) RAG/Bible Search (Vector Retrieval)

`tools/rag_tool.py` configures Pinecone + OpenAI embeddings and a retrieval chain:

```python
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain

self.vectorstore = PineconeVectorStore(
    index_name=os.environ.get("PINECONE_INDEX_NAME"), embedding=self.embeddings
)
retriever = self.vectorstore.as_retriever(search_kwargs={"k": 10})
self.retrieval_chain = create_retrieval_chain(retriever=retriever, combine_docs_chain=combine_docs_chain)
```

Key points:
- Embedding model: `text-embedding-3-small`
- Retriever k raised to 10 for more context
- `search_bible(query: str)` tool invokes the chain and returns an answer

### Ingesting Your Own Documents

Shabbot includes an ingestion script to populate Pinecone with your `.txt` files for retrieval.

```bash
pipenv run python langchain-demo-agent/ingestion.py --path ./your_texts --chunk_size 1000 --chunk_overlap 150
```

What it does (`ingestion.py`):
- Loads `.txt` files from a file or directory (recursively)
- Splits with `RecursiveCharacterTextSplitter`
- Embeds with `OpenAIEmbeddings(text-embedding-3-small)`
- Upserts into `PINECONE_INDEX_NAME`

Make sure `.env` contains `OPENAI_API_KEY` and `PINECONE_INDEX_NAME`.

---

## 7) Hosted MCP (Hebcal) Integration

MCP enables tools to be served over a protocol. We’re using a hosted server (no local Node process) and convert MCP tools to LangChain tools.

```python
# tools/jewish_calendar_mcp.py (trimmed)
from langchain_mcp_adapters.client import MultiServerMCPClient

async def get_jewish_calendar_tools():
    client = MultiServerMCPClient({
        "hebcal": {
            "transport": "streamable_http",
            "url": "https://www.hebcal.com/mcp",
        }
    })
    tools = await client.get_tools()  # MCP -> LangChain tools
    return tools
```

Those tools (e.g., conversions, parasha, Daf Yomi) are loaded inside Shabbot and become available transparently to the main agent.

Tips:
- Hosted MCP avoids local server management.
- Async-only tools require calling the agent with `ainvoke`.

---

## 8) Web UI

A minimal Flask app renders a nice UI and displays text or QR images.

```python
# web_app.py (trimmed)
result = asyncio.run(agent.ainvoke({"input": query}))
output = result.get('output', '')
# If path to a saved QR is present, render it as an image
```

`templates/index.html` includes:
- Large logo
- Styled input & buttons
- Loader overlay while waiting
- Response card with optional QR image

---

## 9) Running the Project

1) Install deps
```bash
pipenv install
```

2) Create `.env` from `env.example` and set values (at least `OPENAI_API_KEY`).

3) Start the web app
```bash
pipenv run python langchain-demo-agent/web_app.py
```

Open `http://localhost:5001` and ask:
- “Who was Avraham’s second wife?”
- “Calculate Gematria for שלום”
- “Create a QR code for https://wikipedia.org”
- “What’s today’s Hebrew date?”

---

## 10) Extending Shabbot

Add a new tool (e.g., simple Hebrew calendar summary):
1. Create a tool in `tools/your_tool.py` with `@tool` and clear return text.
2. Import it into `agents/shababot.py` and append to `shabbot_tools`.
3. Optionally, add guidance in Shabbot’s system prompt for when to use it.

Add a new top-level tool:
1. Add your tool to `tools/`.
2. Import it into `main.py` and append to `tools` in the orchestrator.
3. Update the main system prompt’s capabilities/examples.

---

## 11) Troubleshooting

- “StructuredTool does not support sync invocation”
  - Use `asyncio.run(agent_executor.ainvoke({"input": ...}))` (already applied).
- MCP tools not available
  - Ensure internet access to `https://www.hebcal.com/mcp`.
- No QR image displayed
  - Ensure the QR tool saves under `outputs/qr_codes/` and the path appears in the result.

---

## 12) Further Reading

- LangChain docs: https://python.langchain.com/
- MCP protocol: https://modelcontextprotocol.io/
- Tavily search: https://python.langchain.com/docs/integrations/tools/tavily
- Pinecone vectors: https://docs.pinecone.io/

Happy hacking with Shabbot! 🚀