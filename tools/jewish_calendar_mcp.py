"""
Jewish Calendar MCP Tool Integration (Hosted MCP)
Uses the hosted Jewish Calendar MCP server via MultiServerMCPClient
"""
import asyncio
from typing import List
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()


async def get_jewish_calendar_tools() -> List:
    """Get Jewish Calendar MCP tools from the hosted MCP server.

    Returns a list of LangChain-compatible tools converted by the adapter.
    """
    try:
        client = MultiServerMCPClient(
            {
                "hebcal": {
                    "transport": "streamable_http",
                    "url": "https://www.hebcal.com/mcp",
                    # "headers": {"Authorization": "Bearer ..."},
                }
            }
        )
        tools = await client.get_tools()
        return tools
    except Exception as e:
        print(f"⚠️  Could not load Jewish Calendar MCP tools (hosted): {e}")
        return []


def get_jewish_calendar_tools_sync() -> List:
    """Synchronous wrapper to get Jewish Calendar MCP tools from hosted server."""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(get_jewish_calendar_tools())
        finally:
            loop.close()
    except Exception as e:
        print(f"⚠️  Error in synchronous MCP tools loader: {e}")
        return []