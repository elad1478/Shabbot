# Shabbot – LangChain Demo Agent

Shabbot is a LangChain-based agent with a focused set of Jewish utilities and a simple web UI. It demonstrates sub-agents, hosted MCP integration, RAG/Bible search, QR code generation, and web search.

## 🎯 Features

1. **Shabbot sub‑agent** (single tool `shabbot`)
   - Today’s Gregorian date
   - Gematria calculations
   - Bible search (RAG)
   - Jewish Calendar via hosted MCP (Hebrew/Gregorian conversions, holidays, Daf Yomi, parasha)
2. **QR Code generation** – Create QR codes for URLs or text
3. **Web search** – Tavily-powered search (requires `TAVILY_API_KEY`)
4. **Slack messaging** – Send text messages to Slack channels (optional)
5. **Web app** – Clean Flask UI with logo, loader, and QR image rendering

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pipenv (for dependency management)

### Installation

1) Navigate to the project directory:

```bash
cd langchain-demo-agent
```

2) Install dependencies:

```bash
pipenv install
```

3) Set up environment variables (copy `env.example` to `.env` and edit values):

```bash
cp env.example .env
```

### Environment Variables

```env
# Required for LLM reasoning
OPENAI_API_KEY=your_openai_api_key_here

# Optional – for web search
TAVILY_API_KEY=your_tavily_api_key_here

# Optional – for advanced RAG with Pinecone (if configured)
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX_NAME=your_pinecone_index_name_here

# Optional – Slack messaging
SLACK_BOT_TOKEN=your_slack_bot_token
SLACK_CHANNEL_ID=your_channel_id
```

## 🎮 Usage

### Run the CLI agent

```bash
pipenv run python langchain-demo-agent/main.py
```

### Run the Web App (recommended)

```bash
pipenv run python langchain-demo-agent/web_app.py
```

Then open `http://localhost:5001`. The page shows a large logo, an input box, and renders text or QR image responses. A loader is shown while waiting for results.

### Ingest documents for RAG (Pinecone)

Use the ingestion script to load your own `.txt` files into the Pinecone index used by Bible/RAG queries.

```bash
pipenv run python langchain-demo-agent/ingestion.py --path ./data_or_file --chunk_size 1000 --chunk_overlap 150
```

Requirements:
- `OPENAI_API_KEY` and `PINECONE_INDEX_NAME` set in `.env`
- Files must be `.txt` (use any directory; subfolders are supported)

## 📝 Usage Examples

### Shabbot (sub-agent via `shabbot` tool)
- "Who was Avraham’s second wife?"
- "Calculate Gematria for שלום"
- "What’s today’s date?"
- "What’s today’s Hebrew date?"
- "When is Passover this year?"
- "Convert 2025-09-22 to Hebrew date"

### QR Code Generation
- "Create a QR code for https://www.wikipedia.org"

### Web Search
- "Search for information about LangChain"

### Slack Integration
- "Send a test message to Slack"

## 🏗️ Project Structure

```
langchain-demo-agent/
├── main.py                 # Main agent implementation (CLI)
├── web_app.py              # Flask web app (UI)
├── Pipfile                 # Dependencies
├── env.example             # Environment variables template
├── README.md               # This file
├── templates/
│   └── index.html          # Web UI template (logo, loader, outputs)
├── static/
│   └── ShabotLogo.png      # Logo (place your file here)
├── tools/                  # Custom tools
│   ├── __init__.py
│   ├── rag_tool.py         # RAG/Biblical search tool
│   ├── qr_tool.py          # QR code generation tool
│   ├── search_tool.py      # Web search tool (Tavily)
│   ├── slack_tool.py       # Slack integration (messages only)
│   ├── gematria_tool.py    # Gematria calculation tool
│   ├── date_tool.py        # Today’s date tool
│   ├── shababot_tool.py    # Exposes Shabbot sub-agent as a tool
│   └── jewish_calendar_mcp.py # Hosted MCP client (Hebcal) used by Shabbot
├── agents/
│   └── shababot.py         # Shabbot sub-agent (date, gematria, bible, MCP calendar)
└── outputs/                # Generated outputs
    └── qr_codes/           # Generated QR codes
```

## 🔧 Tools Overview

### RAG Tool (`search_bible`)
- Searches biblical knowledge for answers via Pinecone + OpenAI

### QR Code Tool
- `generate_qr_code`: Creates single QR codes and saves to `outputs/qr_codes/`

### Search Tool
- `search_web`: Tavily-based web search (requires `TAVILY_API_KEY`)

### Slack Tool
- `send_slack_message`: Send text messages to Slack (requires `SLACK_BOT_TOKEN`, `SLACK_CHANNEL_ID`)

### Gematria Tool
- `calculate_gematria(detailed=True|False)`: Detailed breakdown or simple value

### Date Tool
- `get_today_date`: Returns today’s date (YYYY-MM-DD)

### Shabbot Tool (`shabbot`)
- Routes: today’s date, gematria, Bible RAG, Jewish calendar (via hosted MCP)
- Internally loads Hebcal MCP tools using `MultiServerMCPClient` (no local server to run)

## 🎨 Agent Workflow (high level)

1. User asks a question
2. Main agent selects the appropriate tool (often `shabbot`)
3. Sub-agent or tool executes and returns structured results
4. Web app displays text and/or QR images

## 🔍 Troubleshooting

1. **"OpenAI API key not found"**
   - Set `OPENAI_API_KEY` in `.env`

2. **"Tavily API key not found"**
   - Set `TAVILY_API_KEY` for web search functionality

3. **MCP calendar tools not available**
   - Shabbot prints a warning; other features continue to work
   - Hosted MCP is used (`https://www.hebcal.com/mcp`); ensure internet access

4. **QR code generation fails**
   - Ensure the `outputs/qr_codes/` directory exists and is writable

5. **Slack messaging fails**
   - Ensure `SLACK_BOT_TOKEN` and `SLACK_CHANNEL_ID` are set correctly
   - Check that the bot has `chat:write` scope and is invited to the channel

## 🚀 Future Enhancements

- [x] Hosted MCP (Hebcal) integration via `MultiServerMCPClient`
- [x] Web interface with loader and QR rendering
- [ ] Enhanced RAG with more document sources
- [ ] Voice input/output capabilities
- [ ] More language support
- [ ] Advanced QR code customization
- [ ] Slack bot interactive features
- [ ] Scheduled message sending

## 📄 License

This project is for educational purposes and demonstrates LangChain tool-calling agents.

## 🤝 Contributing

Feel free to submit issues and enhancement requests!
# LangChain Demo Agent

This project implements a comprehensive LangChain agent that demonstrates multiple capabilities as shown in the whiteboard diagram. The agent can handle various tasks including RAG search, translation, QR code generation, web search, and code execution.

## 🎯 Features

1. **RAG (Retrieval-Augmented Generation)** - Search the Bible for answers to questions
2. **Translation Tool** - Translate text to Hebrew and other languages
3. **Search Tool** - General web search capabilities using Tavily
4. **QR Code Generation** - Create QR codes for URLs or text
5. **Slack MCP Integration** - Send messages and files (including QR codes) to Slack channels using MCP-style interface
6. **Code Execution** - Execute Python code for various tasks

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pipenv (for dependency management)

### Installation

1. Clone or navigate to the project directory:
   ```bash
   cd langchain-demo-agent
   ```

2. Install dependencies:
   ```bash
   pipenv install
   ```

3. Set up environment variables (copy `env.example` to `.env`):
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

### Environment Variables

Create a `.env` file with the following variables:

```env
# Required for LLM reasoning
OPENAI_API_KEY=your_openai_api_key_here

# Required for web search
TAVILY_API_KEY=your_tavily_api_key_here

# Optional - for advanced RAG with Pinecone
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX_NAME=your_pinecone_index_name_here
```

## 🎮 Usage

### Demo Mode (No API Keys Required)
Test the individual tools without requiring API keys:

```bash
pipenv run python demo_tools.py
```

This will demonstrate:
- Biblical/RAG search queries
- Hebrew translation
- QR code generation
- Search tool (with fallback message)
- Slack integration (with fallback message)

### MCP Slack Integration Demo
Test the full agent with proper MCP Slack integration:

```bash
pipenv run python mcp_slack_agent.py --demo
```

This requires SLACK_BOT_TOKEN and SLACK_TEAM_ID environment variables.

### Legacy Slack Demo
Test the Slack integration:

```bash
pipenv run python test_slack.py
```

This requires SLACK_BOT_TOKEN and SLACK_CHANNEL_ID environment variables.

Test the Gematria tool:

```bash
pipenv run python test_gematria.py
```

### Full Agent Mode (Requires OpenAI API Key)
Run the complete agent with LLM reasoning:

```bash
pipenv run python main.py
```

### Standard Agent Mode (All Features Including Slack)
Run the main agent with all features including Slack integration:

```bash
pipenv run python main.py
```

**Required Environment Variables:**
- `OPENAI_API_KEY`: Your OpenAI API key
- `SLACK_BOT_TOKEN`: Your Slack bot token
- `SLACK_CHANNEL_ID`: Your channel ID to send messages to

**Slack Bot Setup:**
1. Create a Slack app at https://api.slack.com/apps
2. Add the following OAuth scopes to your bot:
   - `chat:write` (to send messages)
   - `files:write` (to upload files/QR codes)
3. Install the app to your workspace
4. Copy the Bot User OAuth Token to `SLACK_BOT_TOKEN`
5. Invite the bot to your channel: `/invite @your-bot-name`
6. Copy the channel ID to `SLACK_CHANNEL_ID`

### Test Individual Tools
Test all tools to ensure they work correctly:

```bash
pipenv run python test_tools.py
```

## 📝 Usage Examples

### Biblical/RAG Search
- "Who's Avraham's second wife?"
- "Tell me about Sarah"
- "Who is Isaac?"

### Translation
- "Translate 'Hello world' to Hebrew"
- "Translate 'Thank you' to Hebrew"

### QR Code Generation
- "Create a QR code for https://www.wikipedia.org"
- "Generate 3 QR codes for: https://www.google.com, https://www.github.com, https://www.python.org"
- "Create a QR code for Wikipedia and send it to Slack"

### Web Search
- "Search for information about LangChain"
- "What's the weather in New York?"

### Slack Integration
- "Send a test message to Slack"
- "Send this QR code to Slack"
- "Create a QR code and send it to Slack"

### Code Execution
- "Generate 5 QR codes for different URLs"
- "Create a Python script to process data"

### Gematria
- "Calculate Gematria for שלום"
- "What's the Gematria value of אהבה"
- "Get the numerical value of חיים"

## 🏗️ Project Structure

```
langchain-demo-agent/
├── main.py                 # Main agent implementation
├── demo_tools.py           # Demo script for tools
├── test_tools.py           # Test script for tools
├── Pipfile                 # Dependencies
├── env.example             # Environment variables template
├── README.md               # This file
├── tools/                  # Custom tools
│   ├── __init__.py
│   ├── rag_tool.py         # RAG/Biblical search tool
│   ├── translation_tool.py # Translation tool
│   ├── qr_tool.py          # QR code generation tool
│   ├── search_tool.py      # Web search tool
│   ├── slack_tool.py       # Slack integration tool
│   └── gematria_tool.py    # Gematria calculation tool
├── data/                   # Sample data
│   └── sample_bible_data.txt
└── outputs/                # Generated outputs
    └── qr_codes/           # Generated QR codes
```

## 🔧 Tools Overview

### RAG Tool (`search_bible`)
- Searches biblical knowledge for answers
- Falls back to local knowledge if Pinecone is not available
- Handles queries about biblical figures and events

### Translation Tool
- `translate_to_hebrew`: Translates text to Hebrew
- `translate_text`: Translates to any language
- `detect_language`: Detects the language of text
- Includes fallback translations for common phrases

### QR Code Tool
- `generate_qr_code`: Creates single QR codes
- `generate_multiple_qr_codes`: Creates multiple QR codes
- Saves QR codes to `outputs/qr_codes/` directory

### Search Tool
- `search_web`: Basic web search using Tavily
- `tavily_search`: Advanced web search with better formatting
- Requires TAVILY_API_KEY

### Slack Tool
- `send_slack_message`: Send text messages to Slack
- `send_slack_file`: Upload files to Slack
- `send_qr_code_to_slack`: Send QR codes with descriptions
- Requires SLACK_BOT_TOKEN and SLACK_CHANNEL_ID

### Gematria Tool
- `calculate_gematria`: Detailed Gematria calculation with breakdown
- `get_gematria_value`: Simple numerical value only
- Uses traditional Jewish Gematria values
- Supports all Hebrew letters including final letters

### Code Execution
- `python_repl_tool`: Executes Python code
- Useful for complex tasks and automation

## 🎨 Agent Workflow

The agent follows the workflow shown in the whiteboard diagram:

1. **Starting Agent** - Receives user queries
2. **Tool Selection** - Chooses appropriate tools based on the query
3. **Execution** - Runs the selected tools
4. **Response** - Returns formatted results

### Example Workflow
1. User asks: "Who's Avraham's second wife?"
2. Agent uses RAG tool to search biblical knowledge
3. Returns: "Keturah was Abraham's second wife..."

### Slack MCP Integration Workflow
1. User asks: "Post a message to #general"
2. Agent uses Slack MCP tools to list channels and find channel ID
3. Agent posts message using the official MCP Slack server
4. Returns: "Message posted successfully to #general"

### Combined Workflow
1. User asks: "Create a QR code for Wikipedia and send it to Slack"
2. Agent generates QR code using QR tool
3. Agent uses Slack MCP tools to upload the QR code file
4. Returns: "QR code generated and sent to Slack"

## 🔍 Troubleshooting

### Common Issues

1. **"OpenAI API key not found"**
   - Set OPENAI_API_KEY in your .env file
   - Tools will still work without it, but LLM reasoning won't

2. **"Tavily API key not found"**
   - Set TAVILY_API_KEY for web search functionality
   - Search tools will show fallback messages

3. **Translation errors**
   - The tool includes fallback translations for common phrases
   - Check your internet connection for online translation

4. **QR code generation fails**
   - Ensure the `outputs/qr_codes/` directory exists
   - Check file permissions

5. **Slack MCP integration fails**
   - Ensure SLACK_BOT_TOKEN and SLACK_TEAM_ID are set correctly
   - Check that the bot has permissions to post to the channel
   - Verify the bot token has the required scopes (chat:write, files:write)
   - Make sure Node.js and npx are available for the MCP server

### Getting API Keys

1. **OpenAI API Key**: Get from [OpenAI Platform](https://platform.openai.com/)
2. **Tavily API Key**: Get from [Tavily](https://tavily.com/)
3. **Pinecone API Key**: Get from [Pinecone](https://www.pinecone.io/) (optional)
4. **Slack Bot Token & Team ID**: Get from [Slack API](https://api.slack.com/apps) (optional for MCP integration)

## 🚀 Future Enhancements

- [x] Slack MCP integration (as shown in diagram)
- [ ] Enhanced RAG with more document sources
- [ ] Voice input/output capabilities
- [ ] Web interface
- [ ] More language support
- [ ] Advanced QR code customization
- [ ] Slack bot interactive features
- [ ] Scheduled message sending
- [ ] Full MCP server integration

## 📄 License

This project is for educational purposes and demonstrates LangChain tool calling agents.

## 🤝 Contributing

Feel free to submit issues and enhancement requests! 