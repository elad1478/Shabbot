import os
import sys
import argparse
from pathlib import Path
from typing import List
from dotenv import load_dotenv

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

load_dotenv()


def load_text_files_from_path(path: Path) -> List:
    docs = []
    if path.is_file():
        docs.extend(TextLoader(str(path)).load())
    elif path.is_dir():
        for file in path.rglob("*.txt"):
            docs.extend(TextLoader(str(file)).load())
    else:
        raise FileNotFoundError(f"Path not found: {path}")
    return docs


def main():
    parser = argparse.ArgumentParser(description="Ingest text files into Pinecone for RAG (Shabbot)")
    parser.add_argument("--path", required=True, help="File or directory of .txt files to ingest")
    parser.add_argument("--chunk_size", type=int, default=1000, help="Chunk size for splitting")
    parser.add_argument("--chunk_overlap", type=int, default=150, help="Chunk overlap for splitting")
    args = parser.parse_args()

    index_name = os.environ.get("PINECONE_INDEX_NAME")
    if not index_name:
        print("❌ PINECONE_INDEX_NAME is not set in environment (.env)")
        sys.exit(1)

    if not os.environ.get("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY is not set in environment (.env)")
        sys.exit(1)

    path = Path(args.path).expanduser().resolve()
    print(f"📄 Loading documents from: {path}")
    documents = load_text_files_from_path(path)
    if not documents:
        print("⚠️ No .txt documents found to ingest.")
        sys.exit(0)

    print("✂️ Splitting documents into chunks...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_documents(documents)
    print(f"✅ Number of chunks: {len(chunks)}")

    print("🧠 Creating embeddings and upserting to Pinecone...")
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    PineconeVectorStore.from_documents(chunks, embeddings, index_name=index_name)

    print(f"🎉 Finished loading embeddings into Pinecone index: {index_name}")


if __name__ == "__main__":
    main()