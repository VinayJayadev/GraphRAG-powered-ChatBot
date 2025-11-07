import os
from app.services.vector_store import VectorStore

def load_text_files_from_directory(directory_path):
    """Load all text files from a directory and return them as documents."""
    documents = []
    
    if not os.path.exists(directory_path):
        print(f"Directory {directory_path} does not exist. Creating it...")
        os.makedirs(directory_path, exist_ok=True)
        return documents
    
    for filename in os.listdir(directory_path):
        if filename.endswith('.txt'):
            file_path = os.path.join(directory_path, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read().strip()
                    if content:  # Only add non-empty files
                        # Extract topic from filename
                        topic = filename.replace('.txt', '').replace('_', ' ').title()
                        documents.append({
                            "text": content,
                            "metadata": {
                                "source": "knowledge_base",
                                "filename": filename,
                                "topic": topic,
                                "category": get_category_from_filename(filename)
                            }
                        })
                        print(f"✅ Loaded: {filename}")
            except Exception as e:
                print(f"❌ Error loading {filename}: {str(e)}")
    
    return documents

def get_category_from_filename(filename):
    """Determine category based on filename."""
    filename_lower = filename.lower()
    
    if any(word in filename_lower for word in ['ai', 'artificial', 'machine', 'data', 'quantum', 'blockchain']):
        return "Technology"
    elif any(word in filename_lower for word in ['biotech', 'renewable', 'space', 'climate']):
        return "Science"
    elif any(word in filename_lower for word in ['digital', 'startup', 'sustainable', 'fintech', 'remote']):
        return "Business"
    elif any(word in filename_lower for word in ['telemedicine', 'precision', 'mental', 'public', 'healthcare']):
        return "Health"
    else:
        return "General"

def main():
    # Initialize the vector store
    print("🚀 Initializing Vector Store...")
    vector_store = VectorStore()
    
    # Original test documents
    print("\n📚 Adding original test documents...")
    original_documents = [
        {
            "text": "RAG (Retrieval-Augmented Generation) is a technique that combines information retrieval with text generation. It enhances LLM responses by providing relevant context from a knowledge base, improving accuracy and reducing hallucinations.",
            "metadata": {"category": "AI", "topic": "RAG", "source": "original"}
        },
        {
            "text": "Vector databases are specialized databases designed to store and efficiently search through vector embeddings. They are crucial for implementing RAG systems as they enable semantic search capabilities.",
            "metadata": {"category": "AI", "topic": "vector_databases", "source": "original"}
        },
        {
            "text": "Graph-based RAG enhances traditional RAG systems by considering relationships between documents. This allows for better context retrieval by following semantic connections in the knowledge base.",
            "metadata": {"category": "AI", "topic": "graph_rag", "source": "original"}
        },
        {
            "text": "Python is a high-level programming language known for its simplicity and readability. It supports multiple programming paradigms, including procedural, object-oriented, and functional programming.",
            "metadata": {"category": "programming", "topic": "python", "source": "original"}
        },
        {
            "text": "Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed. Common applications include image recognition and natural language processing.",
            "metadata": {"category": "technology", "topic": "machine_learning", "source": "original"}
        },
        {
            "text": "Docker is a platform for developing, shipping, and running applications in containers. Containers package up code and all its dependencies, ensuring the application runs quickly and reliably across different computing environments.",
            "metadata": {"category": "technology", "topic": "containers", "source": "original"}
        }
    ]
    
    # Add original documents
    for doc in original_documents:
        vector_store.add_documents([doc["text"]], [doc["metadata"]])
        print(f"✅ Added original: {doc['metadata']['topic']}")
    
    # Load and add knowledge base files
    print("\n📁 Loading knowledge base files...")
    knowledge_base_path = "knowledge_base"
    knowledge_documents = load_text_files_from_directory(knowledge_base_path)
    
    if knowledge_documents:
        print(f"\n📖 Adding {len(knowledge_documents)} knowledge base documents...")
        for doc in knowledge_documents:
            vector_store.add_documents([doc["text"]], [doc["metadata"]])
            print(f"✅ Added KB: {doc['metadata']['topic']} ({doc['metadata']['category']})")
    else:
        print("⚠️ No knowledge base files found. Please ensure the knowledge_base directory exists with .txt files.")
    
    # Summary
    total_docs = len(original_documents) + len(knowledge_documents)
    print(f"\n🎉 Successfully added {total_docs} documents to the vector store!")
    print(f"   - Original documents: {len(original_documents)}")
    print(f"   - Knowledge base documents: {len(knowledge_documents)}")
    
    # Show categories
    categories = {}
    for doc in original_documents + knowledge_documents:
        cat = doc['metadata']['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"\n📊 Document categories:")
    for category, count in categories.items():
        print(f"   - {category}: {count} documents")

if __name__ == "__main__":
    main()
