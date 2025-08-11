"""
ShabaBot Tool Wrapper
Exposes the ShabaBot sub-agent as a single tool callable by the main agent.
"""
import asyncio
from langchain_core.tools import tool
from agents.shababot import create_shababot_agent


@tool
def shababot(query: str) -> str:
    """
    Use ShabaBot for Jewish utilities: today's date, Gematria, and Bible search.
    Pass a natural language query. ShabaBot will decide which sub-tool to use.
    """
    agent = create_shababot_agent()
    if agent is None:
        return "ShabaBot unavailable (missing OPENAI_API_KEY)."

    try:
        result = asyncio.run(agent.ainvoke({"input": query}))
        return result.get("output", str(result))
    except Exception as e:
        return f"Error calling ShabaBot: {e}"