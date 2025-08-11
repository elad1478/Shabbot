"""
Shabbot Tool Wrapper
Exposes the Shabbot sub-agent as a single tool callable by the main agent.
"""
import asyncio
from langchain_core.tools import tool
from agents.shababot import create_shabbot_agent


@tool
def shabbot(query: str) -> str:
    """
    Use Shabbot for Jewish utilities: today's date, Gematria, and Bible search.
    Pass a natural language query. Shabbot will decide which sub-tool to use.
    """
    agent = create_shabbot_agent()
    if agent is None:
        return "Shabbot unavailable (missing OPENAI_API_KEY)."

    try:
        result = asyncio.run(agent.ainvoke({"input": query}))
        return result.get("output", str(result))
    except Exception as e:
        return f"Error calling Shabbot: {e}"