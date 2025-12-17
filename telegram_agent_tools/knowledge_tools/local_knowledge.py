"""Local Knowledge Tool - RAG-based document search"""

import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

from ..base_tool import BaseTool, ToolMetadata, ToolParameter, ToolCategory


class LocalKnowledgeTool(BaseTool):
    """Search and retrieve from local knowledge base"""
    
    _index: Optional[Any] = None
    _documents: List[Dict[str, Any]] = []
    _embeddings_model: Optional[Any] = None
    
    def _get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="local_knowledge",
            description="Search local documents using semantic search (RAG)",
            category=ToolCategory.KNOWLEDGE,
            version="1.0.0",
            requires_confirmation=False,
            parameters=[
                ToolParameter(
                    name="action",
                    param_type="string",
                    description="Action: search, add, list, clear",
                    required=True
                ),
                ToolParameter(
                    name="query",
                    param_type="string",
                    description="Search query (for search action)",
                    required=False
                ),
                ToolParameter(
                    name="document_path",
                    param_type="string",
                    description="Path to document to add",
                    required=False
                ),
                ToolParameter(
                    name="content",
                    param_type="string",
                    description="Text content to add directly",
                    required=False
                ),
                ToolParameter(
                    name="top_k",
                    param_type="int",
                    description="Number of results to return",
                    required=False,
                    default=5
                )
            ],
            examples=["Search for deployment instructions"]
        )
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute knowledge base operation"""
        try:
            action = parameters.get("action", "").lower()
            
            if action == "search":
                return await self._search(
                    parameters.get("query", ""),
                    parameters.get("top_k", 5)
                )
            elif action == "add":
                doc_path = parameters.get("document_path")
                content = parameters.get("content")
                
                if doc_path:
                    return await self._add_document(doc_path)
                elif content:
                    return await self._add_content(content)
                else:
                    return self._error_response("Provide document_path or content")
            elif action == "list":
                return await self._list_documents()
            elif action == "clear":
                return await self._clear()
            else:
                return self._error_response(f"Unknown action: {action}")
        
        except Exception as e:
            return self._error_response(str(e))
    
    async def _search(self, query: str, top_k: int) -> Dict[str, Any]:
        """Search the knowledge base"""
        if not query:
            return self._error_response("Query is required")
        
        if not LocalKnowledgeTool._documents:
            return self._success_response({
                "message": "Knowledge base is empty",
                "results": []
            })
        
        # Try to use sentence-transformers for semantic search
        try:
            from sentence_transformers import SentenceTransformer
            import numpy as np
            
            # Initialize model if needed
            if LocalKnowledgeTool._embeddings_model is None:
                LocalKnowledgeTool._embeddings_model = SentenceTransformer(
                    'all-MiniLM-L6-v2'
                )
            
            model = LocalKnowledgeTool._embeddings_model
            
            # Encode query
            query_embedding = model.encode([query])[0]
            
            # Get document embeddings
            doc_texts = [d['content'][:1000] for d in LocalKnowledgeTool._documents]
            doc_embeddings = model.encode(doc_texts)
            
            # Calculate similarities
            similarities = np.dot(doc_embeddings, query_embedding) / (
                np.linalg.norm(doc_embeddings, axis=1) * np.linalg.norm(query_embedding)
            )
            
            # Get top results
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            results = []
            for idx in top_indices:
                doc = LocalKnowledgeTool._documents[idx]
                results.append({
                    "source": doc.get('source', 'unknown'),
                    "content": doc['content'][:500],
                    "score": float(similarities[idx])
                })
            
            return self._success_response({
                "query": query,
                "results": results
            })
        
        except ImportError:
            # Fallback to simple keyword search
            results = []
            query_lower = query.lower()
            
            for doc in LocalKnowledgeTool._documents:
                content_lower = doc['content'].lower()
                if query_lower in content_lower:
                    results.append({
                        "source": doc.get('source', 'unknown'),
                        "content": doc['content'][:500],
                        "score": 1.0 if query_lower in content_lower else 0.0
                    })
            
            return self._success_response({
                "query": query,
                "results": results[:top_k],
                "note": "Using keyword search (install sentence-transformers for semantic search)"
            })
    
    async def _add_document(self, doc_path: str) -> Dict[str, Any]:
        """Add document from file"""
        if not os.path.exists(doc_path):
            return self._error_response(f"File not found: {doc_path}")
        
        # Read file content
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return self._error_response(f"Failed to read file: {e}")
        
        # Add to documents
        LocalKnowledgeTool._documents.append({
            "source": doc_path,
            "content": content,
            "added_at": Path(doc_path).stat().st_mtime
        })
        
        return self._success_response({
            "message": f"Added document: {doc_path}",
            "total_documents": len(LocalKnowledgeTool._documents)
        })
    
    async def _add_content(self, content: str) -> Dict[str, Any]:
        """Add content directly"""
        LocalKnowledgeTool._documents.append({
            "source": "direct_input",
            "content": content,
            "added_at": None
        })
        
        return self._success_response({
            "message": "Content added",
            "total_documents": len(LocalKnowledgeTool._documents)
        })
    
    async def _list_documents(self) -> Dict[str, Any]:
        """List all documents"""
        docs = [
            {"source": d.get('source', 'unknown'), "length": len(d['content'])}
            for d in LocalKnowledgeTool._documents
        ]
        
        return self._success_response({
            "total": len(docs),
            "documents": docs
        })
    
    async def _clear(self) -> Dict[str, Any]:
        """Clear the knowledge base"""
        count = len(LocalKnowledgeTool._documents)
        LocalKnowledgeTool._documents = []
        LocalKnowledgeTool._index = None
        
        return self._success_response({
            "message": f"Cleared {count} documents"
        })
