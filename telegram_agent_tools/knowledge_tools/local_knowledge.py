"""Local Knowledge Tool - RAG-based document search"""

import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

try:
    import aiofiles
    HAS_AIOFILES = True
except ImportError:
    HAS_AIOFILES = False

from ..base_tool import BaseTool, ToolMetadata, ToolParameter, ToolCategory


class LocalKnowledgeTool(BaseTool):
    """Search and retrieve from local knowledge base"""

    _index: Optional[Any] = None
    _documents: List[Dict[str, Any]] = []
    _embeddings_model: Optional[Any] = None
    _db_loaded: bool = False

    DB_PATH = Path("data/knowledge_base.json")

    def __init__(self):
        super().__init__()
        # Load database only once
        if not LocalKnowledgeTool._db_loaded:
            self._load_db()
            LocalKnowledgeTool._db_loaded = True
    
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
    
    def _get_embedding(self, text: str) -> List[float]:
        """Generate embedding for text (cached in model)"""
        try:
            if LocalKnowledgeTool._embeddings_model is None:
                from sentence_transformers import SentenceTransformer
                LocalKnowledgeTool._embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')

            # Generate embedding and convert to list for JSON serialization
            embedding = LocalKnowledgeTool._embeddings_model.encode([text])[0]
            return embedding.tolist()
        except Exception as e:
            print(f"Warning: Could not generate embedding: {e}")
            return []

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
        """Search the knowledge base using cached embeddings"""
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
                LocalKnowledgeTool._embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')

            model = LocalKnowledgeTool._embeddings_model

            # Encode query once
            query_embedding = model.encode([query])[0]

            # Use cached embeddings from documents
            results = []
            for doc in LocalKnowledgeTool._documents:
                # Skip documents without embeddings
                if 'embedding' not in doc or not doc['embedding']:
                    continue

                # Use stored embedding (much faster than recalculating!)
                doc_emb = np.array(doc['embedding'])

                # Calculate cosine similarity
                score = np.dot(doc_emb, query_embedding) / (
                    np.linalg.norm(doc_emb) * np.linalg.norm(query_embedding)
                )

                results.append({
                    "source": doc.get('source', 'unknown'),
                    "content": doc['content'][:500],
                    "score": float(score)
                })

            # Sort by score and return top_k
            results.sort(key=lambda x: x['score'], reverse=True)

            return self._success_response({
                "query": query,
                "results": results[:top_k]
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
        """Add document from file with pre-computed embedding"""
        if not os.path.exists(doc_path):
            return self._error_response(f"File not found: {doc_path}")

        # Read file content asynchronously if aiofiles is available
        try:
            if HAS_AIOFILES:
                async with aiofiles.open(doc_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
            else:
                # Fallback to synchronous reading
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
        except Exception as e:
            return self._error_response(f"Failed to read file: {e}")

        # Generate embedding once at add time (not at search time!)
        embedding = self._get_embedding(content[:1000])

        # Add to documents with cached embedding
        LocalKnowledgeTool._documents.append({
            "source": doc_path,
            "content": content,
            "embedding": embedding,  # CACHED for fast search!
            "added_at": Path(doc_path).stat().st_mtime
        })

        # Save to disk
        self._save_db()

        return self._success_response({
            "message": f"Added document: {doc_path}",
            "total_documents": len(LocalKnowledgeTool._documents)
        })
    
    async def _add_content(self, content: str) -> Dict[str, Any]:
        """Add content directly with pre-computed embedding"""
        # Generate embedding once at add time (not at search time!)
        embedding = self._get_embedding(content[:1000])

        LocalKnowledgeTool._documents.append({
            "source": "direct_input",
            "content": content,
            "embedding": embedding,  # CACHED for fast search!
            "added_at": None
        })

        # Save to disk
        self._save_db()

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

        # Save the cleared state
        self._save_db()

        return self._success_response({
            "message": f"Cleared {count} documents"
        })

    def _load_db(self):
        """Load knowledge base from disk"""
        if self.DB_PATH.exists():
            try:
                with open(self.DB_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    LocalKnowledgeTool._documents = data.get('documents', [])
            except Exception as e:
                print(f"Error loading knowledge base: {e}")

    def _save_db(self):
        """Save knowledge base to disk"""
        try:
            self.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(self.DB_PATH, 'w', encoding='utf-8') as f:
                json.dump({'documents': LocalKnowledgeTool._documents}, f, indent=2)
        except Exception as e:
            print(f"Error saving knowledge base: {e}")
