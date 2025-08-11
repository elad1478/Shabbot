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
from tools.rag_tool import search_bible
from tools.qr_tool import generate_qr_code, python_repl_tool
from tools.search_tool import search_web
from tools.slack_tool import send_slack_message
from tools.gematria_tool import calculate_gematria
from tools.jewish_calendar_mcp import get_jewish_calendar_tools_sync
from tools.date_tool import get_today_date

# Load environment variables
load_dotenv()


def create_agent():
    """Create the main agent with all tools"""
    
    # Define the system prompt based on the diagram workflow
    system_prompt = """You are a comprehensive agent that can handle multiple types of tasks:

1. **RAG Search**: Answer questions about biblical figures and religious topics using the search_bible tool
2. **QR Code Generation**: Create QR codes for URLs, text, or other data
3. **Web Search**: Search the web for current information and general knowledge
4. **Code Execution**: Execute Python code for complex tasks
5. **Slack Integration**: Send messages to Slack channels
6. **Gematria**: Calculate numerical values of Hebrew text using traditional Jewish Gematria
7. **Jewish Calendar**: Convert dates between Hebrew and Gregorian calendars, get Jewish holidays, and more

You should:
- Use the appropriate tool for each task
- Combine tools when needed (e.g., search for info, then create QR code)
- Provide clear, helpful responses
- When asked about biblical topics, use the RAG search tool
- When asked to create QR codes, use the QR generation tools
- When asked for current information, use the web search tools
- When asked to send a message to Slack, use the send_slack_message tool
- When asked about Gematria or Hebrew numerical values, use the calculate_gematria tool
- When asked about Jewish dates, holidays, or calendar conversions, use the Jewish Calendar tools

Examples:
- "Who's Avraham's second wife?" → Use search_bible
- "Create a QR code for Wikipedia" → Use generate_qr_code
- "Search for LangChain information" → Use search_web
- "Send a message to Slack" → Use send_slack_message
- "Calculate Gematria for שלום" → Use calculate_gematria
- "What's the Gematria value of אהבה" → Use calculate_gematria with detailed=False
- "What's today's Hebrew date?" → Use Jewish Calendar tools
- "When is Passover this year?" → Use Jewish Calendar tools
- "Convert January 15, 2024 to Hebrew date" → Use Jewish Calendar tools
"""

    # Create the prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}")
    ])

    # Define all available tools
    tools = [
        # RAG and Bible search
        search_bible,
        
        # QR code tools
        generate_qr_code,
        
        # Search tools
        search_web,
        
        # Slack tools
        send_slack_message,
        
        # Gematria tools
        calculate_gematria,

        # Utility tools
        get_today_date,
    ]
    
    # Add Jewish Calendar MCP tools if available
    try:
        jewish_calendar_tools = get_jewish_calendar_tools_sync()
        if jewish_calendar_tools:
            tools.extend(jewish_calendar_tools)
            print(f"✅ Added {len(jewish_calendar_tools)} Jewish Calendar MCP tools")
        else:
            print("⚠️  Jewish Calendar MCP tools not available")
            print("To install: npm install -g @hebcal/mcp-server")
    except Exception as e:
        print(f"⚠️  Could not load Jewish Calendar MCP tools: {e}")
        print("To install: npm install -g @hebcal/mcp-server")
        print("Agent will continue without Jewish Calendar functionality")

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