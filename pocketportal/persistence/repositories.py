"""
Abstract Repository Interfaces
================================

Defines contracts for all persistence operations.
Implementations can use any backend (SQLite, PostgreSQL, Redis, etc.).
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class Message:
    """Represents a conversation message"""
    role: str
    content: str
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class Conversation:
    """Represents a conversation thread"""
    chat_id: str
    messages: List[Message]
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class Document:
    """Represents a knowledge base document"""
    id: str
    content: str
    embedding: Optional[List[float]] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None


class ConversationRepository(ABC):
    """
    Abstract interface for conversation persistence.

    Implementations:
    - SQLiteConversationRepository: Local SQLite database
    - PostgreSQLConversationRepository: Scalable PostgreSQL
    - RedisConversationRepository: Fast in-memory cache
    """

    @abstractmethod
    async def create_conversation(self, chat_id: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Create a new conversation"""
        pass

    @abstractmethod
    async def add_message(
        self,
        chat_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a message to a conversation"""
        pass

    @abstractmethod
    async def get_messages(
        self,
        chat_id: str,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Message]:
        """Retrieve messages from a conversation"""
        pass

    @abstractmethod
    async def get_conversation(self, chat_id: str) -> Optional[Conversation]:
        """Get full conversation details"""
        pass

    @abstractmethod
    async def delete_conversation(self, chat_id: str) -> bool:
        """Delete a conversation and all its messages"""
        pass

    @abstractmethod
    async def list_conversations(
        self,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Conversation]:
        """List all conversations"""
        pass

    @abstractmethod
    async def search_messages(
        self,
        query: str,
        chat_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Message]:
        """Search messages by content"""
        pass

    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """Get repository statistics"""
        pass


class KnowledgeRepository(ABC):
    """
    Abstract interface for knowledge/vector storage.

    Implementations:
    - SQLiteKnowledgeRepository: Local SQLite with FTS5
    - PostgreSQLKnowledgeRepository: PostgreSQL with pgvector
    - PineconeKnowledgeRepository: Cloud vector database
    - WeaviateKnowledgeRepository: Semantic search engine
    """

    @abstractmethod
    async def add_document(
        self,
        content: str,
        embedding: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add a document to knowledge base.
        Returns document ID.
        """
        pass

    @abstractmethod
    async def add_documents_batch(
        self,
        documents: List[Dict[str, Any]],
    ) -> List[str]:
        """
        Add multiple documents in batch.
        Returns list of document IDs.
        """
        pass

    @abstractmethod
    async def search(
        self,
        query: str,
        limit: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Document]:
        """
        Search documents by semantic similarity and/or full-text search.
        """
        pass

    @abstractmethod
    async def search_by_embedding(
        self,
        embedding: List[float],
        limit: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Document]:
        """
        Search documents by vector similarity.
        """
        pass

    @abstractmethod
    async def get_document(self, document_id: str) -> Optional[Document]:
        """Retrieve a specific document by ID"""
        pass

    @abstractmethod
    async def update_document(
        self,
        document_id: str,
        content: Optional[str] = None,
        embedding: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Update an existing document"""
        pass

    @abstractmethod
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document"""
        pass

    @abstractmethod
    async def delete_all(self) -> bool:
        """Clear all documents"""
        pass

    @abstractmethod
    async def count_documents(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count documents, optionally filtered"""
        pass

    @abstractmethod
    async def list_documents(
        self,
        limit: Optional[int] = None,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Document]:
        """List documents with pagination"""
        pass

    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """Get repository statistics"""
        pass
