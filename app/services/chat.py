from typing import List, Dict, Any
import openai
import asyncio
from app.core.config import get_settings
from app.services.vector_store import VectorStore
from app.services.rag.graph_rag import GraphRAG
from app.services.tool_gateway import ToolGateway

settings = get_settings()

class ChatService:
    def __init__(self):
        self.vector_store = VectorStore()
        self.graph_rag = GraphRAG()
        
        # Configure OpenRouter client
        self.openai_client = openai.OpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1"
        )
        
        self.tool_gateway = ToolGateway()
        print("✅ Tool service initialized successfully")
        print("✅ OpenRouter client initialized successfully")
        
    async def get_response(self, query: str, chat_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """Generate a response using RAG and OpenRouter with tool execution."""
        enhanced_context = []
        try:
            # Get relevant documents from knowledge base
            relevant_docs = self.vector_store.semantic_search(query, limit=5)
            print(f"🔍 DEBUG: Vector search found {len(relevant_docs)} documents from knowledge base")
            
            # Show what documents were found
            for i, doc in enumerate(relevant_docs):
                try:
                    topic = doc.get('metadata', {}).get('topic', 'Unknown')
                    category = doc.get('metadata', {}).get('category', 'Unknown')
                    score = doc.get('score', 0.0)
                    print(f"   📄 {i+1}. {topic} ({category}) - Score: {score:.3f}")
                except Exception as e:
                    print(f"   ⚠️ Could not parse document {i+1}: {e}")
            
            # Enhance context using graph-based retrieval
            if relevant_docs:
                doc_ids = [f"doc_{i}" for i in range(len(relevant_docs))]
                for doc_id, doc in zip(doc_ids, relevant_docs):
                    try:
                        self.graph_rag.add_document(
                            doc_id=doc_id,
                            text=doc.get("text", ""),
                            embedding=self.vector_store.encoder.encode(doc.get("text", "")),
                            metadata=doc.get("metadata", {})
                        )
                    except Exception as e:
                        print(f"⚠️ WARNING: Could not add document {doc_id} to graph: {e}")
                
                try:
                    enhanced_context = self.graph_rag.get_context(doc_ids)
                    print(f"🔗 DEBUG: Graph RAG enhanced context to {len(enhanced_context)} documents")
                    
                    # Add scores from original search to enhanced context
                    for enhanced_doc in enhanced_context:
                        doc_idx = int(enhanced_doc["id"].replace("doc_", ""))
                        if doc_idx < len(relevant_docs):
                            enhanced_doc["score"] = relevant_docs[doc_idx].get("score", 0.0)
                except Exception as e:
                    print(f"⚠️ WARNING: Graph RAG context retrieval failed: {e}")
                    # Fallback to original documents with scores
                    enhanced_context = [
                        {
                            "id": f"doc_{i}",
                            "text": doc.get("text", ""),
                            "metadata": doc.get("metadata", {}),
                            "score": doc.get("score", 0.0)
                        }
                        for i, doc in enumerate(relevant_docs)
                    ]
        except Exception as e:
            print(f"⚠️ WARNING: Error during RAG retrieval: {e}")
            enhanced_context = []
        
        # Prepare conversation context
        messages = []
        if chat_history:
            for msg in chat_history:
                messages.append({"role": "user", "content": msg["user"]})
                if "assistant" in msg:
                    messages.append({"role": "assistant", "content": msg["assistant"]})
        
        # Create knowledge base context
        knowledge_sources = []
        context_str = ""
        if enhanced_context:
            context_str = "\n\n".join([doc["text"] for doc in enhanced_context])
            knowledge_sources = [doc['metadata'].get('topic', 'Unknown') for doc in enhanced_context]
        
        # Determine if we need web search (expanded triggers for more comprehensive answers)
        needs_web_search = any(keyword in query.lower() for keyword in [
            'current', 'latest', 'today', 'recent', 'now', '2024', '2025', 'breaking', 'news',
            'more', 'additional', 'expand', 'elaborate', 'details', 'comprehensive', 'complete',
            'update', 'new', 'advance', 'development', 'trend', 'state of', 'overview'
        ])
        
        web_search_result = None
        if needs_web_search:
            print(f"WEB DEBUG: Query appears to need current information, fetching web search...")
            try:
                web_search_result = await self.tool_gateway.execute_tool(
                    tool_name="web_search",
                    arguments={"query": query}
                )
                print(f"WEB DEBUG: Web search completed")
            except Exception as tool_err:
                print(f"WEB DEBUG: Web search failed: {tool_err}")
        else:
            print(f"KB DEBUG: Using knowledge base only (no web search needed)")
        
        # Create system message prioritizing knowledge base
        if context_str and web_search_result:
            system_content = f"""You are a helpful AI assistant with access to a knowledge base and current web information.

KNOWLEDGE BASE CONTEXT (Primary Source):
{context_str}

CURRENT WEB INFORMATION (Secondary Source):
{web_search_result}

INSTRUCTIONS:
1. Prioritize the knowledge base context for your main answer
2. Use web information only to supplement or update knowledge base information
3. Always cite your sources in your response
4. If knowledge base has sufficient information, use it as the primary source"""
        elif context_str:
            system_content = f"""You are a helpful AI assistant with access to a knowledge base.

KNOWLEDGE BASE CONTEXT:
{context_str}

INSTRUCTIONS:
1. Answer based primarily on the knowledge base context provided
2. If the context doesn't contain enough information, acknowledge this limitation
3. Always mention that your answer is based on the knowledge base
4. If the user asks for more details, suggest they ask for "more information" or "additional details" to get web search results
5. Do not make up information not in the context"""
        else:
            system_content = """You are a helpful AI assistant. The knowledge base search didn't return relevant results for this query. Please provide a general answer based on your training data and mention that you don't have specific information in your knowledge base for this topic."""
        
        system_message = {
            "role": "system",
            "content": system_content
        }
        
        messages = [system_message] + messages + [{"role": "user", "content": query}]
        
        # Generate response using OpenRouter
        try:
            print(f"🤖 DEBUG: Generating response with OpenRouter...")
            response = self.openai_client.chat.completions.create(
                model="openai/gpt-3.5-turbo",  # Using GPT-3.5 Turbo which is more reliable
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            # Get response text
            response_text = response.choices[0].message.content
            
            # Source attribution will be handled in the response structure
            # We'll format it in the frontend for better presentation
            
        except Exception as e:
            print(f"❌ DEBUG: OpenRouter API call failed: {str(e)}")
            return {
                "response": f"Sorry, I encountered an error: {str(e)}",
                "context": enhanced_context,
                "sources": [],  # Always return sources as a list
                "metadata": {
                    "model": "openai/gpt-3.5-turbo",
                    "error": str(e),
                }
            }
        
        # Prepare sources with document references
        sources_list = []
        
        # Add knowledge base sources with document details
        if enhanced_context:
            print(f"📚 DEBUG: Preparing {len(enhanced_context)} sources for response")
            for doc in enhanced_context:
                try:
                    doc_metadata = doc.get("metadata", {})
                    source_info = {
                        "type": "knowledge_base",
                        "topic": doc_metadata.get("topic", "Unknown"),
                        "category": doc_metadata.get("category", "Unknown"),
                        "filename": doc_metadata.get("filename", "Unknown"),
                        "text_preview": doc.get("text", "")[:200] + "..." if len(doc.get("text", "")) > 200 else doc.get("text", ""),
                        "score": doc.get("score", 0.0) if "score" in doc else None
                    }
                    sources_list.append(source_info)
                    print(f"   ✅ Added source: {source_info['topic']} ({source_info['category']})")
                except Exception as e:
                    print(f"   ⚠️ Error creating source info: {e}")
        else:
            print("📚 DEBUG: No enhanced_context available for sources")
        
        # Add web search source if used
        if web_search_result:
            sources_list.append({
                "type": "web_search",
                "source": "Brave Search API",
                "query": query
            })
            print(f"🌐 DEBUG: Added web search source")
        
        print(f"📋 DEBUG: Total sources in response: {len(sources_list)}")
        
        return {
            "response": response_text,
            "context": enhanced_context,
            "sources": sources_list,  # Always include sources, even if empty
            "metadata": {
                "model": response.model,
                "total_tokens": response.usage.total_tokens,
                "rag_documents_used": len(enhanced_context),
                "web_search_used": bool(web_search_result),
            }
        }
