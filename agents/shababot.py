"""
ShabaBot - Jewish utilities sub-agent
Provides date, Gematria, and Bible search capabilities.
"""
import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_openai import ChatOpenAI

# Tools used by ShabaBot
from tools.date_tool import get_today_date
from tools.gematria_tool import calculate_gematria
from tools.rag_tool import search_bible
from tools.jewish_calendar_mcp import get_jewish_calendar_tools_sync

load_dotenv()


def create_shababot_agent() -> AgentExecutor | None:
    """Create the ShabaBot agent with its tools.
    Returns None if LLM credentials are missing.
    """
    if not os.environ.get("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY missing: ShabaBot will not be available")
        return None

    system_prompt = (
        "You are ShabaBot, a helpful Jewish assistant with tools for: "
        "- get_today_date (today's Gregorian date), "
        "- calculate_gematria (Hebrew Gematria), "
        "- search_bible (RAG for biblical topics), "
        "- Jewish Calendar (Hebrew/Gregorian conversions, holidays, Daf Yomi, parasha) via MCP. "
        "Use tools precisely and respond concisely."
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}")
    ])

    shababot_tools = [
        get_today_date,
        calculate_gematria,
        search_bible,
    ]

    # Try to add Jewish Calendar MCP tools (hosted Hebcal MCP)
    try:
        jc_tools = get_jewish_calendar_tools_sync()
        if jc_tools:
            shababot_tools.extend(jc_tools)
            print(f"✅ ShabaBot: Added {len(jc_tools)} Jewish Calendar MCP tools")
        else:
            print("⚠️  ShabaBot: Jewish Calendar MCP tools not available")
    except Exception as e:
        print(f"⚠️  ShabaBot: Could not load Jewish Calendar MCP tools: {e}")

    llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")
    agent = create_tool_calling_agent(llm, shababot_tools, prompt)
    executor = AgentExecutor(
        agent=agent,
        tools=shababot_tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=8,
    )
    return executor