import networkx as nx # networkx is a library for creating and manipulating graphs
from typing import List, Dict, Any
import numpy as np
from sentence_transformers import util

class GraphRAG:
    def __init__(self):
        self.graph = nx.Graph()
        self.embeddings = {}
        self.texts = {}
        
    def add_document(self, doc_id: str, text: str, embedding: np.ndarray, metadata: Dict[str, Any] = None):
        """Add a document to the graph."""
        self.graph.add_node(doc_id, text=text, metadata=metadata or {})
        self.embeddings[doc_id] = embedding
        self.texts[doc_id] = text
        
        # Create edges between similar documents
        for existing_id in self.embeddings:
            if existing_id != doc_id:
                similarity = util.cos_sim(
                    embedding.reshape(1, -1),
                    self.embeddings[existing_id].reshape(1, -1)
                ).item()
                
                # Add edge if similarity is above threshold
                if similarity > 0.7:  # Configurable threshold
                    self.graph.add_edge(doc_id, existing_id, weight=similarity)
    
    def get_context(self, relevant_docs: List[str], depth: int = 1) -> List[Dict[str, Any]]:
        """Get context by exploring the graph around relevant documents."""
        if not relevant_docs:
            return []
        
        context = set(relevant_docs)
        
        # Explore neighbors up to specified depth
        neighbors = set()  # Initialize neighbors set outside the loop
        for doc_id in relevant_docs:
            if doc_id not in self.graph:
                continue
            current_neighbors = {doc_id}
            
            for _ in range(depth):
                new_neighbors = set()
                for node in current_neighbors:
                    if node in self.graph:
                        new_neighbors.update(self.graph.neighbors(node))
                neighbors.update(new_neighbors)
                current_neighbors = new_neighbors
        
        context.update(neighbors)
        
        # Return context documents with their text and metadata
        results = []
        for doc_id in context:
            if doc_id in self.texts and doc_id in self.graph:
                results.append({
                    "id": doc_id,
                    "text": self.texts[doc_id],
                    "metadata": self.graph.nodes[doc_id].get("metadata", {})
                })
        
        return results
    
    def get_document_relationships(self, doc_id: str) -> List[Dict[str, Any]]:
        """Get related documents for a given document."""
        if doc_id not in self.graph:
            return []
        
        relationships = []
        for neighbor in self.graph.neighbors(doc_id):
            relationships.append({
                "id": neighbor,
                "text": self.texts[neighbor],
                "similarity": self.graph.edges[doc_id, neighbor]["weight"],
                "metadata": self.graph.nodes[neighbor]["metadata"]
            })
        
        return sorted(relationships, key=lambda x: x["similarity"], reverse=True)
