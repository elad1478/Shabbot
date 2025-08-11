"""
RAG (Retrieval-Augmented Generation) Tool for searching documents
"""
import os
from typing import List
from langchain_core.tools import tool
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_pinecone import PineconeVectorStore
from langchain import hub
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

class RAGTool:
    def __init__(self):
        self.embeddings = None
        self.llm = None
        self.vectorstore = None
        self.retrieval_chain = None
        self._setup_vectorstore()
    
    def _setup_vectorstore(self):
        """Setup Pinecone vector store if credentials are available"""
        try:
            # Only setup OpenAI components if API key is available
            if os.environ.get("OPENAI_API_KEY"):
                self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
                self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
                
                if os.environ.get("PINECONE_API_KEY") and os.environ.get("PINECONE_INDEX_NAME"):
                    self.vectorstore = PineconeVectorStore(
                        index_name=os.environ.get("PINECONE_INDEX_NAME"),
                        embedding=self.embeddings,
                    )
                    retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")
                    combine_docs_chain = create_stuff_documents_chain(self.llm, retrieval_qa_chat_prompt)
                    # Configure retriever to get more chunks (default is usually 4)
                    retriever = self.vectorstore.as_retriever(
                        search_kwargs={"k": 10}  # Increase from default to 10 chunks
                    )
                    self.retrieval_chain = create_retrieval_chain(
                        retriever=retriever,
                        combine_docs_chain=combine_docs_chain,
                    )
                    print("✅ Pinecone vector store initialized")
                else:
                    print("⚠️  Pinecone credentials not found, using local document search")
            else:
                print("⚠️  OpenAI API key not found, using local document search only")
        except Exception as e:
            print(f"⚠️  Could not initialize vector store: {e}")
    
    def search_documents(self, query: str) -> str:
        """Search documents using RAG"""
        try:
            result = self.retrieval_chain.invoke(input={"input": query})
            return result["answer"]
        except Exception as e:
            return f"Error searching documents: {e}"
    


# Create global instance
rag_tool = RAGTool()


@tool
def search_bible(query: str) -> str:
    """
    Search the Bible and religious texts for answers to questions.
    Use this tool when asked about biblical figures, events, or religious topics.
    
    Args:
        query: The question or topic to search for
        
    Returns:
        Answer based on biblical knowledge
    """
    return rag_tool.search_documents(query) 