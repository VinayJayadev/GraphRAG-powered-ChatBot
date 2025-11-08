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
        
        # Get fresh settings to ensure we have the latest API key
        current_settings = get_settings()
        
        # Configure OpenRouter client with current settings
        if not current_settings.OPENROUTER_API_KEY:
            raise ValueError(
                "OPENROUTER_API_KEY is not configured. "
                "Please set it in the .env file and restart the server."
            )
        
        self.openai_client = openai.OpenAI(
            api_key=current_settings.OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1"
        )
        
        self.tool_gateway = ToolGateway()
        print("Tool service initialized successfully")
        print("OpenRouter client initialized successfully")
        
    async def get_response(self, query: str, chat_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """Generate a response using RAG and OpenRouter with tool execution."""
        # Store the top matching document for citation
        top_document = None
        top_source_info = None
        
        try:
            # Get relevant documents from knowledge base (get multiple for analysis, but use only top one)
            relevant_docs = self.vector_store.semantic_search(query, limit=5)
            print(f"DEBUG: Vector search found {len(relevant_docs)} documents from knowledge base")
            
            # Show what documents were found
            for i, doc in enumerate(relevant_docs):
                try:
                    topic = doc.get('metadata', {}).get('topic', 'Unknown')
                    category = doc.get('metadata', {}).get('category', 'Unknown')
                    score = doc.get('score', 0.0)
                    print(f"   Document {i+1}. {topic} ({category}) - Score: {score:.3f}")
                except Exception as e:
                    print(f"   Could not parse document {i+1}: {e}")
            
            # Select only the highest scoring document (top match)
            if relevant_docs:
                # Sort by score (highest first) and take the top one
                sorted_docs = sorted(relevant_docs, key=lambda x: x.get('score', 0.0), reverse=True)
                top_document = sorted_docs[0]
                
                print(f"DEBUG: Using top match - Score: {top_document.get('score', 0.0):.3f}")
                print(f"DEBUG: Top document topic: {top_document.get('metadata', {}).get('topic', 'Unknown')}")
                
                # Prepare the single document for context
                enhanced_context = [{
                    "id": "doc_0",
                    "text": top_document.get("text", ""),
                    "metadata": top_document.get("metadata", {}),
                    "score": top_document.get("score", 0.0)
                }]
                
                # Prepare source info for citation
                metadata = top_document.get("metadata", {})
                topic = metadata.get("topic", "Unknown")
                source_type = metadata.get("source", "")
                
                # Get filename from metadata - only knowledge_base files have this
                filename = metadata.get("filename")
                
                # Only consider it a valid file if:
                # 1. Filename exists in metadata
                # 2. Filename is not "Unknown"
                # 3. Source is not "original" (original test docs don't have files)
                has_file = (
                    filename is not None 
                    and filename != "Unknown" 
                    and source_type != "original"
                )
                
                # If no valid filename, set to None
                if not has_file:
                    filename = None
                
                top_source_info = {
                    "type": "knowledge_base",
                    "topic": topic,
                    "category": metadata.get("category", "Unknown"),
                    "filename": filename,  # None for sources without files
                    "score": top_document.get("score", 0.0),
                    "relevance_score": f"{top_document.get('score', 0.0):.3f}",
                    "has_file": has_file  # Explicit flag to indicate if file exists
                }
            else:
                enhanced_context = []
                print("DEBUG: No documents found in knowledge base")
        except Exception as e:
            print(f"WARNING: Error during RAG retrieval: {e}")
            enhanced_context = []
        
        # Prepare conversation context
        messages = []
        if chat_history:
            for msg in chat_history:
                messages.append({"role": "user", "content": msg["user"]})
                if "assistant" in msg:
                    messages.append({"role": "assistant", "content": msg["assistant"]})
        
        # Create knowledge base context from top document only
        # Limit context to prevent sending entire documents (max 2000 characters for context)
        context_str = ""
        if enhanced_context and len(enhanced_context) > 0:
            # Use only the top document (highest score)
            top_doc = enhanced_context[0]
            full_text = top_doc["text"]
            
            # Create a limited context for the LLM (first 2000 characters)
            # This prevents the LLM from repeating the entire document
            if len(full_text) > 2000:
                context_str = full_text[:2000] + "..."
            else:
                context_str = full_text
            
            # Get source information for citation (fallback if not already set)
            if top_source_info is None:
                metadata = top_doc.get("metadata", {})
                topic = metadata.get("topic", "Unknown")
                source_type = metadata.get("source", "")
                
                # Get filename from metadata - only knowledge_base files have this
                filename = metadata.get("filename")
                
                # Only consider it a valid file if:
                # 1. Filename exists in metadata
                # 2. Filename is not "Unknown"
                # 3. Source is not "original" (original test docs don't have files)
                has_file = (
                    filename is not None 
                    and filename != "Unknown" 
                    and source_type != "original"
                )
                
                # If no valid filename, set to None
                if not has_file:
                    filename = None
                
                # Create text preview for source display (first 300 chars)
                preview_text = full_text[:300] + "..." if len(full_text) > 300 else full_text
                
                top_source_info = {
                    "type": "knowledge_base",
                    "topic": topic,
                    "category": metadata.get("category", "Unknown"),
                    "filename": filename,  # None for sources without files
                    "score": top_doc.get("score", 0.0),
                    "relevance_score": f"{top_doc.get('score', 0.0):.3f}",
                    "has_file": has_file,  # Explicit flag to indicate if file exists
                    "text_preview": preview_text  # Short preview for UI
                }
            else:
                # Add text preview to existing top_source_info if not already set
                if 'text_preview' not in top_source_info:
                    preview_text = full_text[:300] + "..." if len(full_text) > 300 else full_text
                    top_source_info['text_preview'] = preview_text
        
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
        
        # Create system message with single top source
        source_name = "the knowledge base"
        if top_source_info:
            source_name = f"'{top_source_info.get('topic', 'the knowledge base')}' from the knowledge base"
            source_category = top_source_info.get('category', '')
            if source_category:
                source_name += f" (Category: {source_category})"
        
        if context_str and web_search_result:
            system_content = f"""You are a helpful AI assistant with access to a knowledge base and current web information.

PRIMARY SOURCE (Highest Matching Document from Knowledge Base):
Source: {source_name}
Relevance Score: {top_source_info.get('relevance_score', 'N/A') if top_source_info else 'N/A'}

RELEVANT CONTENT FROM PRIMARY SOURCE (excerpt):
{context_str}

CURRENT WEB INFORMATION (Supplementary):
{web_search_result}

INSTRUCTIONS:
1. Provide a CONCISE, natural answer based on the knowledge base content above
2. DO NOT repeat or copy the entire document - only use relevant information that answers the user's question
3. Use web information only to supplement or provide additional context if needed
4. ALWAYS cite the source: Mention "{source_name}" in your response (e.g., "According to {source_name}, ...")
5. Keep your response focused and answer only what was asked
6. If the primary source doesn't fully answer the question, acknowledge this and use web information to fill gaps
7. The user can click on the source to view the full document if they need more details"""
        elif context_str:
            system_content = f"""You are a helpful AI assistant with access to a knowledge base.

PRIMARY SOURCE (Highest Matching Document):
Source: {source_name}
Relevance Score: {top_source_info.get('relevance_score', 'N/A') if top_source_info else 'N/A'}

RELEVANT CONTENT FROM SOURCE (excerpt):
{context_str}

INSTRUCTIONS:
1. Provide a CONCISE, natural answer based on the content provided above
2. DO NOT repeat or copy the entire document - only extract and present relevant information that answers the user's question
3. ALWAYS cite the source at the beginning or end of your response
4. Format your response naturally: "According to {source_name}, [your concise answer]" or "[your concise answer] (Source: {source_name})"
5. Keep your response focused - answer only what was asked, not everything in the document
6. If the source doesn't contain enough information to fully answer the question, acknowledge this limitation
7. Do not make up information not in the provided source
8. The user can click on the source citation to view the full document if they need more details
9. Your answer should be brief and to the point - the full document is available if the user wants to read it"""
        else:
            system_content = """You are a helpful AI assistant. The knowledge base search didn't return relevant results for this query. Please provide a general answer based on your training data and mention that you don't have specific information in your knowledge base for this topic."""
        
        system_message = {
            "role": "system",
            "content": system_content
        }
        
        messages = [system_message] + messages + [{"role": "user", "content": query}]
        
        # Check if API key is configured before making the request
        if not settings.OPENROUTER_API_KEY or settings.OPENROUTER_API_KEY == "your-openrouter-api-key-here":
            error_msg = (
                "OPENROUTER_API_KEY is not configured. "
                "Please set your API key in the .env file. "
                "Get your API key from: https://openrouter.ai/keys"
            )
            print(f"ERROR: {error_msg}")
            return {
                "response": error_msg,
                "context": enhanced_context,
                "sources": [],
                "metadata": {
                    "model": "openai/gpt-3.5-turbo",
                    "error": "API key not configured",
                }
            }
        
        # Generate response using OpenRouter
        try:
            print(f"DEBUG: Generating response with OpenRouter...")
            response = self.openai_client.chat.completions.create(
                model="openai/gpt-3.5-turbo",  # Using GPT-3.5 Turbo which is more reliable
                messages=messages,
                temperature=0.7,
                max_tokens=500  # Reduced to encourage concise responses
            )
            
            # Get response text
            response_text = response.choices[0].message.content
            
            # Source attribution will be handled in the response structure
            # We'll format it in the frontend for better presentation
            
        except Exception as e:
            error_str = str(e)
            print(f"DEBUG: OpenRouter API call failed: {error_str}")
            
            # Provide more helpful error messages
            if "401" in error_str or "No auth credentials" in error_str or "Invalid API key" in error_str or "Unauthorized" in error_str:
                error_msg = (
                    "Authentication failed. Please check your OPENROUTER_API_KEY in the .env file. "
                    "Make sure it's set correctly (without quotes) and restart the server after updating it. "
                    "Get your API key from: https://openrouter.ai/keys"
                )
            elif "403" in error_str or "Forbidden" in error_str:
                error_msg = (
                    "Access forbidden. Please check your OpenRouter API key permissions and account status. "
                    "Visit https://openrouter.ai to verify your account."
                )
            else:
                error_msg = f"API Error: {error_str}. Please check your API key and try again."
            
            return {
                "response": error_msg,
                "context": enhanced_context,
                "sources": [],
                "metadata": {
                    "model": "openai/gpt-3.5-turbo",
                    "error": error_str,
                }
            }
        
        # Prepare sources - only include the top matching document
        sources_list = []
        
        # Add only the top matching knowledge base source
        if top_source_info:
            print(f"DEBUG: Preparing top source for citation: {top_source_info.get('topic', 'Unknown')}")
            sources_list.append(top_source_info)
            print(f"   Added source: {top_source_info.get('topic')} (Score: {top_source_info.get('relevance_score', 'N/A')})")
        else:
            print("DEBUG: No top source available for citation")
        
        # Add web search source if used (as supplementary)
        if web_search_result:
            sources_list.append({
                "type": "web_search",
                "source": "Brave Search API",
                "query": query,
                "note": "Supplementary information"
            })
            print(f"DEBUG: Added web search as supplementary source")
        
        print(f"DEBUG: Total sources in response: {len(sources_list)} (Primary: {len([s for s in sources_list if s.get('type') == 'knowledge_base'])})")
        
        return {
            "response": response_text,
            "context": enhanced_context,  # Contains only the top matching document
            "sources": sources_list,  # Contains only the top source for citation
            "metadata": {
                "model": response.model,
                "total_tokens": response.usage.total_tokens,
                "rag_documents_used": 1 if enhanced_context else 0,  # Only top document
                "top_match_score": enhanced_context[0].get("score", 0.0) if enhanced_context else None,
                "web_search_used": bool(web_search_result),
                "primary_source": top_source_info.get("topic", "None") if top_source_info else "None"
            }
        }
