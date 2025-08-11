"""
LangChain Demo Agent - Main Implementation
Implements the workflow shown in the whiteboard diagram
"""
import os
import asyncio
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain_experimental.tools import PythonREPLTool

# Import our custom tools
from tools.qr_tool import generate_qr_code, python_repl_tool
from tools.search_tool import search_web
from tools.slack_tool import send_slack_message
from tools.jewish_calendar_mcp import get_jewish_calendar_tools_sync
from tools.shababot_tool import shababot

# Load environment variables
load_dotenv()


def create_agent():
    """Create the main agent with all tools"""
    
    # Define the system prompt for the main orchestrator agent
    system_prompt = """You are the Main Agent orchestrator. Use tools to accomplish tasks accurately and concisely.

Capabilities:
1. **Jewish Utilities (ShabaBot)**: Use the `shababot` tool for all Jewish utilities:
   - Today's Gregorian date
   - Gematria calculations
   - Bible search (RAG)
   - Jewish Calendar via MCP (Hebrew/Gregorian conversions, holidays, Daf Yomi, parasha)
   Always route these requests through `shababot`. Do not call MCP tools directly.
2. **QR Code Generation**: Create QR codes for URLs or text using `generate_qr_code`.
3. **Web Search**: Search for current information using `search_web`.
4. **Slack Integration**: Send messages to Slack channels using `send_slack_message`.

Guidelines:
- Select the appropriate tool for each request and keep responses focused.
- Combine tools when helpful (e.g., search, then produce a QR code).
- For any date, Gematria, Bible, or Jewish calendar task, always use `shababot`.
- If a tool returns multiple items, summarize the most relevant results first.

Examples:
- "Who's Avraham's second wife?" → Use `shababot`
- "What's today's date?" → Use `shababot`
- "Calculate Gematria for שלום" → Use `shababot`
- "Create a QR code for Wikipedia" → Use `generate_qr_code`
- "Search for LangChain information" → Use `search_web`
- "Send a message to Slack" → Use `send_slack_message`
- "What's today's Hebrew date?" → Use `shababot`
- "When is Passover this year?" → Use `shababot`
- "Convert January 15, 2024 to Hebrew date" → Use `shababot`
"""

    # Create the prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}")
    ])

    # Define all available tools
    tools = [
        # Sub-agent tool (Jewish utilities)
        shababot,

        # QR code tools
        generate_qr_code,
        
        # Search tools
        search_web,
        
        # Slack tools
        send_slack_message,
    ]
    
    # Jewish Calendar MCP tools are now managed within ShabaBot

    # Create the LLM (handle missing API key gracefully)
    try:
        if os.environ.get("OPENAI_API_KEY"):
            llm = ChatOpenAI(
                temperature=0,
                model="gpt-4o-mini",
            )
        else:
            print("⚠️  OpenAI API key not found. Agent will use tools directly without LLM reasoning.")
            return None
    except Exception as e:
        print(f"⚠️  Error creating LLM: {e}")
        return None

    # Create the agent
    agent = create_tool_calling_agent(llm, tools, prompt)
    
    # Create the executor
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=10
    )
    
    return executor


def main():
    """Main function to run the agent"""
    print("🚀 Starting LangChain Demo Agent...")
    print("=" * 50)
    
    # Check for required environment variables
    if not os.environ.get("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not found in environment variables")
        print("   Some features may not work properly")
    
    if not os.environ.get("TAVILY_API_KEY"):
        print("⚠️  Warning: TAVILY_API_KEY not found in environment variables")
        print("   Web search features may not work properly")
    
    # Create the agent
    agent_executor = create_agent()
    
    if agent_executor is None:
        print("\n❌ Agent could not be created due to missing API keys")
        print("Please set the required environment variables:")
        print("• OPENAI_API_KEY (required for LLM reasoning)")
        print("• TAVILY_API_KEY (optional for web search)")
        print("• PINECONE_API_KEY (optional for advanced RAG)")
        return
    
    print("\n✅ Agent created successfully!")
    print("\nAvailable capabilities:")
    print("• Biblical/RAG search (e.g., 'Who's Avraham's second wife?')")
    print("• QR code generation (e.g., 'Create QR code for https://wikipedia.org')")
    print("• Web search (e.g., 'Search for LangChain information')")
    print("• Code execution (e.g., 'Generate 5 QR codes for different URLs')")
    print("• Jewish Calendar (e.g., 'What's today's Hebrew date?', 'When is Passover?')")
    print("\n" + "=" * 50)
    
    # Interactive mode
    while True:
        try:
            user_input = input("\n🤖 Ask me anything (or 'quit' to exit): ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            print(f"\n🔍 Processing: {user_input}")
            print("-" * 30)
            
            # Execute the agent (async tools require async invocation)
            result = asyncio.run(agent_executor.ainvoke({"input": user_input}))
            
            print("\n📝 Response:")
            print(result["output"])
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again with a different query.")


def run_demo_queries():
    """Run some demo queries to showcase the agent's capabilities"""
    print("🎯 Running demo queries...")
    
    agent_executor = create_agent()
    
    if agent_executor is None:
        print("❌ Cannot run demo queries without OpenAI API key")
        print("Please set OPENAI_API_KEY environment variable to test the full agent")
        return
    
    demo_queries = [
        "Who's Avraham's second wife?",
        "Create a QR code for https://www.wikipedia.org",
        "Search for information about LangChain",
        "Calculate Gematria for שלום",
        "What's today's Hebrew date?"
    ]
    
    for i, query in enumerate(demo_queries, 1):
        print(f"\n{i}. Demo Query: {query}")
        print("-" * 40)
        
        try:
            result = asyncio.run(agent_executor.ainvoke({"input": query}))
            print(f"Response: {result['output']}")
        except Exception as e:
            print(f"Error: {e}")
        
        print()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        run_demo_queries()
    else:
        main() 