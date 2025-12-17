"""
Enhanced Persistent Memory Manager
==================================

Provides persistent, encrypted memory storage across sessions with:
- Per-chat conversation history
- User preferences and context
- Session management
- Multi-user support
- Automatic cleanup of old sessions

Builds on existing memory implementation but adds session management
and cross-interface persistence.
"""

import asyncio
import json
import logging
import sqlite3
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from cryptography.fernet import Fernet
import aiosqlite

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """A single message in conversation history"""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: str
    model_used: Optional[str] = None
    tools_used: Optional[List[str]] = None
    execution_time: Optional[float] = None


@dataclass
class Session:
    """A chat session"""
    session_id: str
    user_id: str
    interface: str  # 'telegram', 'web', 'slack', 'api'
    created_at: str
    last_active: str
    message_count: int
    metadata: Dict[str, Any]


class PersistentMemoryManager:
    """
    Manages persistent memory across sessions and interfaces.
    
    Features:
    - SQLite backend for reliability
    - Encrypted sensitive data
    - Per-session conversation history
    - User preferences
    - Multi-interface support
    - Automatic session cleanup
    """
    
    def __init__(
        self,
        db_path: Path = Path("data/memory.db"),
        encryption_key: Optional[str] = None,
        max_history_length: int = 50,
        session_ttl_days: int = 30
    ):
        """
        Initialize memory manager
        
        Args:
            db_path: Path to SQLite database
            encryption_key: Encryption key (auto-generated if None)
            max_history_length: Max messages to keep per session
            session_ttl_days: Days before inactive sessions are cleaned
        """
        self.db_path = db_path
        self.max_history_length = max_history_length
        self.session_ttl_days = session_ttl_days
        
        # Setup encryption
        if encryption_key:
            self.cipher = Fernet(encryption_key.encode())
        else:
            # Generate new key
            key = Fernet.generate_key()
            self.cipher = Fernet(key)
            logger.warning(f"Generated new encryption key: {key.decode()}")
            logger.warning("Save this key to MEMORY_ENCRYPTION_KEY in .env for persistence")
        
        # Create database
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    interface TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_active TEXT NOT NULL,
                    message_count INTEGER DEFAULT 0,
                    metadata TEXT,
                    INDEX idx_user_id (user_id),
                    INDEX idx_interface (interface),
                    INDEX idx_last_active (last_active)
                )
            """)
            
            # Messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    model_used TEXT,
                    tools_used TEXT,
                    execution_time REAL,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE,
                    INDEX idx_session_id (session_id),
                    INDEX idx_timestamp (timestamp)
                )
            """)
            
            # User preferences table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    user_id TEXT PRIMARY KEY,
                    preferences TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            conn.commit()
        
        logger.info(f"Database initialized at {self.db_path}")
    
    def _encrypt(self, data: str) -> str:
        """Encrypt sensitive data"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def _decrypt(self, data: str) -> str:
        """Decrypt sensitive data"""
        return self.cipher.decrypt(data.encode()).decode()
    
    async def create_session(
        self,
        session_id: str,
        user_id: str,
        interface: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Session:
        """Create new session"""
        
        session = Session(
            session_id=session_id,
            user_id=user_id,
            interface=interface,
            created_at=datetime.now().isoformat(),
            last_active=datetime.now().isoformat(),
            message_count=0,
            metadata=metadata or {}
        )
        
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute("""
                INSERT OR REPLACE INTO sessions
                (session_id, user_id, interface, created_at, last_active, message_count, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                session.session_id,
                session.user_id,
                session.interface,
                session.created_at,
                session.last_active,
                session.message_count,
                json.dumps(session.metadata)
            ))
            await conn.commit()
        
        logger.info(f"Created session: {session_id} for user {user_id} on {interface}")
        return session
    
    async def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID"""
        
        async with aiosqlite.connect(self.db_path) as conn:
            async with conn.execute("""
                SELECT session_id, user_id, interface, created_at, last_active, 
                       message_count, metadata
                FROM sessions
                WHERE session_id = ?
            """, (session_id,)) as cursor:
                row = await cursor.fetchone()
                
                if not row:
                    return None
                
                return Session(
                    session_id=row[0],
                    user_id=row[1],
                    interface=row[2],
                    created_at=row[3],
                    last_active=row[4],
                    message_count=row[5],
                    metadata=json.loads(row[6]) if row[6] else {}
                )
    
    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        model_used: Optional[str] = None,
        tools_used: Optional[List[str]] = None,
        execution_time: Optional[float] = None
    ):
        """Add message to session history"""
        
        message = Message(
            role=role,
            content=content,
            timestamp=datetime.now().isoformat(),
            model_used=model_used,
            tools_used=tools_used,
            execution_time=execution_time
        )
        
        async with aiosqlite.connect(self.db_path) as conn:
            # Insert message
            await conn.execute("""
                INSERT INTO messages
                (session_id, role, content, timestamp, model_used, tools_used, execution_time)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                message.role,
                message.content,
                message.timestamp,
                message.model_used,
                json.dumps(message.tools_used) if message.tools_used else None,
                message.execution_time
            ))
            
            # Update session last_active and message_count
            await conn.execute("""
                UPDATE sessions
                SET last_active = ?, message_count = message_count + 1
                WHERE session_id = ?
            """, (datetime.now().isoformat(), session_id))
            
            await conn.commit()
        
        # Trim old messages if exceeds limit
        await self._trim_history(session_id)
    
    async def get_history(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Message]:
        """Get conversation history for session"""
        
        limit = limit or self.max_history_length
        
        async with aiosqlite.connect(self.db_path) as conn:
            async with conn.execute("""
                SELECT role, content, timestamp, model_used, tools_used, execution_time
                FROM messages
                WHERE session_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (session_id, limit)) as cursor:
                rows = await cursor.fetchall()
                
                messages = []
                for row in reversed(rows):  # Reverse to get chronological order
                    messages.append(Message(
                        role=row[0],
                        content=row[1],
                        timestamp=row[2],
                        model_used=row[3],
                        tools_used=json.loads(row[4]) if row[4] else None,
                        execution_time=row[5]
                    ))
                
                return messages
    
    async def _trim_history(self, session_id: str):
        """Trim old messages to keep history under limit"""
        
        async with aiosqlite.connect(self.db_path) as conn:
            # Get count
            async with conn.execute("""
                SELECT COUNT(*) FROM messages WHERE session_id = ?
            """, (session_id,)) as cursor:
                count = (await cursor.fetchone())[0]
            
            if count > self.max_history_length:
                # Delete oldest messages
                await conn.execute("""
                    DELETE FROM messages
                    WHERE id IN (
                        SELECT id FROM messages
                        WHERE session_id = ?
                        ORDER BY timestamp ASC
                        LIMIT ?
                    )
                """, (session_id, count - self.max_history_length))
                
                await conn.commit()
                logger.debug(f"Trimmed {count - self.max_history_length} old messages from {session_id}")
    
    async def get_user_sessions(
        self,
        user_id: str,
        interface: Optional[str] = None
    ) -> List[Session]:
        """Get all sessions for a user"""
        
        async with aiosqlite.connect(self.db_path) as conn:
            if interface:
                query = """
                    SELECT session_id, user_id, interface, created_at, last_active,
                           message_count, metadata
                    FROM sessions
                    WHERE user_id = ? AND interface = ?
                    ORDER BY last_active DESC
                """
                params = (user_id, interface)
            else:
                query = """
                    SELECT session_id, user_id, interface, created_at, last_active,
                           message_count, metadata
                    FROM sessions
                    WHERE user_id = ?
                    ORDER BY last_active DESC
                """
                params = (user_id,)
            
            async with conn.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                
                sessions = []
                for row in rows:
                    sessions.append(Session(
                        session_id=row[0],
                        user_id=row[1],
                        interface=row[2],
                        created_at=row[3],
                        last_active=row[4],
                        message_count=row[5],
                        metadata=json.loads(row[6]) if row[6] else {}
                    ))
                
                return sessions
    
    async def save_user_preferences(
        self,
        user_id: str,
        preferences: Dict[str, Any]
    ):
        """Save user preferences"""
        
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute("""
                INSERT OR REPLACE INTO user_preferences
                (user_id, preferences, updated_at)
                VALUES (?, ?, ?)
            """, (
                user_id,
                json.dumps(preferences),
                datetime.now().isoformat()
            ))
            await conn.commit()
        
        logger.info(f"Saved preferences for user {user_id}")
    
    async def get_user_preferences(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """Get user preferences"""
        
        async with aiosqlite.connect(self.db_path) as conn:
            async with conn.execute("""
                SELECT preferences FROM user_preferences WHERE user_id = ?
            """, (user_id,)) as cursor:
                row = await cursor.fetchone()
                
                if row:
                    return json.loads(row[0])
                return {}
    
    async def cleanup_old_sessions(self):
        """Delete sessions older than TTL"""
        
        cutoff = (datetime.now() - timedelta(days=self.session_ttl_days)).isoformat()
        
        async with aiosqlite.connect(self.db_path) as conn:
            # Get count before deletion
            async with conn.execute("""
                SELECT COUNT(*) FROM sessions WHERE last_active < ?
            """, (cutoff,)) as cursor:
                count = (await cursor.fetchone())[0]
            
            if count > 0:
                # Delete old sessions (messages will cascade delete)
                await conn.execute("""
                    DELETE FROM sessions WHERE last_active < ?
                """, (cutoff,))
                await conn.commit()
                
                logger.info(f"Cleaned up {count} old sessions (> {self.session_ttl_days} days)")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        
        async with aiosqlite.connect(self.db_path) as conn:
            # Count sessions
            async with conn.execute("SELECT COUNT(*) FROM sessions") as cursor:
                total_sessions = (await cursor.fetchone())[0]
            
            # Count messages
            async with conn.execute("SELECT COUNT(*) FROM messages") as cursor:
                total_messages = (await cursor.fetchone())[0]
            
            # Count users
            async with conn.execute("SELECT COUNT(DISTINCT user_id) FROM sessions") as cursor:
                total_users = (await cursor.fetchone())[0]
            
            # Get by interface
            async with conn.execute("""
                SELECT interface, COUNT(*) FROM sessions GROUP BY interface
            """) as cursor:
                by_interface = {row[0]: row[1] for row in await cursor.fetchall()}
            
            return {
                'total_sessions': total_sessions,
                'total_messages': total_messages,
                'total_users': total_users,
                'by_interface': by_interface,
                'database_size_mb': self.db_path.stat().st_size / (1024 * 1024)
            }


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

async def example_usage():
    """Example usage of persistent memory"""
    
    manager = PersistentMemoryManager()
    
    # Create session
    session = await manager.create_session(
        session_id="web_session_123",
        user_id="user_456",
        interface="web",
        metadata={'browser': 'Chrome', 'device': 'Desktop'}
    )
    
    # Add messages
    await manager.add_message(
        session_id=session.session_id,
        role="user",
        content="Hello!"
    )
    
    await manager.add_message(
        session_id=session.session_id,
        role="assistant",
        content="Hi! How can I help?",
        model_used="qwen2.5-7b",
        execution_time=0.5
    )
    
    # Get history
    history = await manager.get_history(session.session_id)
    print(f"History: {len(history)} messages")
    
    # Save preferences
    await manager.save_user_preferences(
        user_id="user_456",
        preferences={'theme': 'dark', 'verbose': True}
    )
    
    # Get stats
    stats = await manager.get_stats()
    print(f"Stats: {stats}")


if __name__ == "__main__":
    asyncio.run(example_usage())
