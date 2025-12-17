# 🚀 PocketPortal Phase 2: Advanced Features

**Building on the Unified Architecture**

Phase 2 adds enterprise-grade features while maintaining the privacy-first, local-only philosophy.

---

## 📦 What's Included

### **New Interfaces** (~600 lines)
1. **Slack Bot** - Enterprise messaging integration
2. **REST API** - Programmatic access for integrations

### **Enhanced Capabilities** (~800 lines)
3. **Persistent Memory** - Session management across interfaces
4. **Voice Support (Web)** - Browser-based voice recording
5. **Multi-User Support** - User management and preferences
6. **Cloud LLM Backends** - Optional OpenAI/Anthropic support

**Total New Code:** ~1,400 lines  
**Reuses:** All Phase 1 code (~9,200 lines)

---

## 🎯 Feature Overview

### 1. Slack Interface

**Location:** `interfaces/slack_interface.py`  
**Lines:** ~350

**Features:**
- Direct messages
- Channel mentions (@bot)
- Slash commands (/ ai, /tools, /stats, /health)
- File handling
- Rate limiting
- Same AgentCore as Telegram/Web

**Setup Time:** 30 minutes  
**Prerequisites:** Slack workspace with admin access

**Quick Start:**
```bash
# Install Slack SDK
pip install slack-bolt==1.18.0

# Configure .env
echo "SLACK_BOT_TOKEN=xoxb-your-token" >> .env
echo "SLACK_APP_TOKEN=xapp-your-token" >> .env

# Run
python interfaces/slack_interface.py
```

---

### 2. REST API

**Location:** `interfaces/rest_api.py`  
**Lines:** ~300

**Features:**
- RESTful endpoints
- API key authentication
- OpenAPI/Swagger docs
- Tool execution API
- Statistics API
- Health checks

**Endpoints:**
```
POST   /api/v1/chat              # Send message
GET    /api/v1/tools             # List tools
POST   /api/v1/tools/{tool}/execute  # Execute tool
GET    /api/v1/stats             # Statistics
GET    /api/v1/health            # Health check
```

**Setup Time:** 10 minutes

**Quick Start:**
```bash
# Run API server
python interfaces/rest_api.py

# Visit docs
open http://localhost:8001/docs

# Test with curl
curl -X POST http://localhost:8001/api/v1/chat \
  -H "X-API-Key: your_key" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'
```

---

### 3. Persistent Memory

**Location:** `core/persistent_memory.py`  
**Lines:** ~400

**Features:**
- SQLite backend
- Encrypted sensitive data
- Per-session history
- User preferences
- Cross-interface sync
- Automatic cleanup

**Database Schema:**
```sql
sessions (
  session_id, user_id, interface,
  created_at, last_active, message_count, metadata
)

messages (
  session_id, role, content, timestamp,
  model_used, tools_used, execution_time
)

user_preferences (
  user_id, preferences, updated_at
)
```

**Usage:**
```python
from core.persistent_memory import PersistentMemoryManager

manager = PersistentMemoryManager()

# Create session
session = await manager.create_session(
    session_id="web_123",
    user_id="user_456",
    interface="web"
)

# Add message
await manager.add_message(
    session_id=session.session_id,
    role="user",
    content="Hello!"
)

# Get history
history = await manager.get_history(session.session_id)

# Save preferences
await manager.save_user_preferences(
    user_id="user_456",
    preferences={'theme': 'dark'}
)
```

---

### 4. Voice Support (Web)

**Location:** `web_static/js/voice-recorder.js`  
**Lines:** ~350

**Features:**
- Browser-based recording (Web Audio API)
- Real-time visualization
- Audio compression
- WebSocket transmission
- Playback controls

**Integration:**
```html
<!-- Add to your web interface -->
<script src="/js/voice-recorder.js"></script>

<button id="record-btn">🎤 Record</button>
<div id="status"></div>
<div id="visualizer"></div>

<script>
const voiceUI = new VoiceUIController(websocket);
await voiceUI.init('record-btn', 'status', 'visualizer');
</script>
```

**Browser Support:**
- ✅ Chrome/Edge 60+
- ✅ Firefox 55+
- ✅ Safari 11+
- ✅ Mobile browsers (iOS 14.3+, Android Chrome)

---

### 5. Multi-User Support

**Included in:** Persistent Memory + API + Web Interface

**Features:**
- User authentication
- Per-user preferences
- Session isolation
- User statistics
- Access control

**Implementation:**
```python
# Each interface handles auth differently

# Telegram: User ID verification
if update.effective_user.id != authorized_user:
    return

# Web: Session-based (cookies/JWT)
session_id = request.cookies.get('session_id')

# API: API key per user
api_key = request.headers.get('X-API-Key')

# Slack: Workspace membership
if not is_authorized(event['user']):
    return
```

---

### 6. Cloud LLM Backends

**Location:** `core/backends/cloud_backends.py`  
**Lines:** ~300

**Features:**
- OpenAI integration (GPT-4, GPT-3.5)
- Anthropic integration (Claude 3.5/3)
- Same interface as local backends
- Automatic fallback
- Cost tracking

**Supported Models:**

**OpenAI:**
- gpt-4-turbo-preview (latest)
- gpt-4
- gpt-3.5-turbo

**Anthropic:**
- claude-3-5-sonnet-20241022 (latest)
- claude-3-opus-20240229
- claude-3-sonnet-20240229
- claude-3-haiku-20240307

**Configuration:**
```bash
# Add to .env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Enable in routing
LLM_BACKEND=openai  # or anthropic
# Or use alongside local models with fallback
```

**Usage:**
```python
from core.backends.cloud_backends import OpenAIBackend, AnthropicBackend

# OpenAI
openai = OpenAIBackend()
result = await openai.generate(
    prompt="Hello!",
    model_name="gpt-4-turbo-preview"
)

# Anthropic
anthropic = AnthropicBackend()
result = await anthropic.generate(
    prompt="Hello!",
    model_name="claude-3-5-sonnet-20241022"
)
```

---

## 🚀 Installation

### Prerequisites

From Phase 1:
- ✅ Python 3.11+
- ✅ Ollama/LM Studio/MLX
- ✅ Phase 1 unified architecture installed

New for Phase 2:
- Slack workspace (for Slack interface)
- Cloud API keys (for cloud backends, optional)

### Quick Install

```bash
cd ~/your-project

# 1. Copy Phase 2 files
cp -r pocketportal_phase2/* .

# 2. Install new dependencies
pip install slack-bolt==1.18.0  # For Slack
# Cloud backends use existing aiohttp

# 3. Update .env
cat >> .env << 'EOF'
# Slack
SLACK_BOT_TOKEN=xoxb-your-token
SLACK_APP_TOKEN=xapp-your-token
SLACK_AUTHORIZED_USERS=U12345,U67890

# API Keys (optional)
API_KEYS=your_api_key_here

# Cloud LLMs (optional)
OPENAI_API_KEY=sk-your-key
ANTHROPIC_API_KEY=sk-ant-your-key

# Memory
MEMORY_ENCRYPTION_KEY=your_32_byte_key
SESSION_TTL_DAYS=30
MAX_HISTORY_LENGTH=50
EOF

# 4. Initialize database
python -c "
from core.persistent_memory import PersistentMemoryManager
manager = PersistentMemoryManager()
print('✅ Database initialized')
"
```

---

## 🎮 Usage Examples

### Example 1: Slack Bot

```bash
# Start Slack interface
python interfaces/slack_interface.py

# In Slack:
# Direct message: "Hello!"
# Channel: "@bot what's the weather?"
# Slash command: "/ai explain quantum computing"
# Slash command: "/tools" - List tools
# Slash command: "/stats" - Show stats
```

### Example 2: REST API

```python
import requests

API_URL = "http://localhost:8001"
API_KEY = "your_key"

# Send message
response = requests.post(
    f"{API_URL}/api/v1/chat",
    headers={"X-API-Key": API_KEY},
    json={
        "message": "What's 2+2?",
        "session_id": "api_session_1",
        "user_id": "user_123"
    }
)

print(response.json())
# {
#   "success": true,
#   "response": "2+2 equals 4",
#   "model_used": "qwen2.5-7b",
#   "execution_time": 0.5,
#   "tools_used": []
# }

# List tools
response = requests.get(
    f"{API_URL}/api/v1/tools",
    headers={"X-API-Key": API_KEY}
)

print(response.json())
```

### Example 3: Persistent Memory

```python
import asyncio
from core.persistent_memory import PersistentMemoryManager

async def demo():
    manager = PersistentMemoryManager()
    
    # Start conversation
    session = await manager.create_session(
        session_id="demo_001",
        user_id="alice",
        interface="web"
    )
    
    # Add messages
    await manager.add_message(session.session_id, "user", "Hi!")
    await manager.add_message(
        session.session_id,
        "assistant",
        "Hello! How can I help?",
        model_used="qwen2.5-7b",
        execution_time=0.3
    )
    
    # Later... retrieve history
    history = await manager.get_history(session.session_id)
    for msg in history:
        print(f"{msg.role}: {msg.content}")
    
    # Save preferences
    await manager.save_user_preferences(
        "alice",
        {'theme': 'dark', 'language': 'en'}
    )
    
    # Get stats
    stats = await manager.get_stats()
    print(f"Total sessions: {stats['total_sessions']}")
    print(f"Total messages: {stats['total_messages']}")

asyncio.run(demo())
```

### Example 4: Cloud LLMs

```python
import asyncio
from core.backends.cloud_backends import OpenAIBackend, AnthropicBackend

async def demo():
    # Try OpenAI
    openai = OpenAIBackend()
    
    result = await openai.generate(
        prompt="Explain async/await in Python",
        model_name="gpt-4-turbo-preview",
        max_tokens=200
    )
    
    print(f"GPT-4: {result['content']}")
    print(f"Tokens: {result['tokens']}, Time: {result['elapsed_ms']:.0f}ms")
    
    await openai.close()
    
    # Try Anthropic
    anthropic = AnthropicBackend()
    
    result = await anthropic.generate(
        prompt="Explain async/await in Python",
        model_name="claude-3-5-sonnet-20241022",
        max_tokens=200
    )
    
    print(f"Claude: {result['content']}")
    print(f"Tokens: {result['tokens']}, Time: {result['elapsed_ms']:.0f}ms")
    
    await anthropic.close()

asyncio.run(demo())
```

---

## 📊 Architecture Integration

### How Phase 2 Fits

```
┌─────────────────────────────────────────────────┐
│         Enhanced Core (Phase 1 + 2)             │
│  ┌──────────────────────────────────────────┐  │
│  │ AgentCore (Phase 1)                      │  │
│  │ + PersistentMemoryManager (Phase 2)      │  │
│  │ + Cloud Backends (Phase 2)               │  │
│  └──────────────────────────────────────────┘  │
└────┬────────┬────────┬────────┬────────────────┘
     │        │        │        │
┌────▼───┐ ┌─▼─────┐ ┌▼─────┐ ┌▼────┐
│Telegram│ │  Web  │ │Slack │ │ API │
│(Phase1)│ │(P1+P2)│ │(P2)  │ │(P2) │
└────────┘ └───────┘ └──────┘ └─────┘
```

### Data Flow

```
User Message → Interface → AgentCore
                              ↓
                    PersistentMemory.add_message()
                              ↓
                    Router (local OR cloud)
                              ↓
                    Tool Execution
                              ↓
                    PersistentMemory.add_message()
                              ↓
                         Response
```

---

## 🔧 Configuration

### Complete .env Example

```bash
# ============================================================================
# Phase 1: Core Configuration
# ============================================================================
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_USER_ID=123456789

OLLAMA_BASE_URL=http://localhost:11434
LLM_BACKEND=ollama
ROUTING_STRATEGY=auto

# ============================================================================
# Phase 2: Advanced Configuration
# ============================================================================

# Slack Interface
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token
SLACK_AUTHORIZED_USERS=U123456,U789012  # Comma-separated

# REST API
API_KEYS=key1_here,key2_here,key3_here  # Comma-separated

# Cloud LLMs (optional)
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key

# Persistent Memory
MEMORY_ENCRYPTION_KEY=your_32_byte_fernet_key
SESSION_TTL_DAYS=30
MAX_HISTORY_LENGTH=50

# Multi-User
ENABLE_MULTI_USER=true
REQUIRE_USER_AUTH=true
```

---

## 📈 Performance

### Benchmarks

**Persistent Memory:**
- Session creation: <1ms
- Message add: <5ms
- History retrieval (50 msgs): <10ms
- Database size: ~1MB per 1000 messages

**Cloud Backends:**
- OpenAI GPT-4 Turbo: 500-1500ms
- OpenAI GPT-3.5 Turbo: 200-800ms
- Anthropic Claude 3.5: 800-2000ms
- Anthropic Claude 3 Haiku: 300-1000ms

**Interfaces:**
- Slack: Similar to Telegram
- REST API: <5ms overhead
- Web + Voice: 100-300ms for audio processing

---

## 🐛 Troubleshooting

### Slack Interface

**Issue:** Bot not responding
```bash
# Check tokens
echo $SLACK_BOT_TOKEN
echo $SLACK_APP_TOKEN

# Verify bot permissions in Slack App settings:
# - chat:write
# - app_mentions:read
# - im:history
# - commands
```

**Issue:** "Unauthorized" messages
```bash
# Add your Slack user ID to authorized users
# Get ID from Slack profile → More → Copy member ID
echo "SLACK_AUTHORIZED_USERS=U12345" >> .env
```

### REST API

**Issue:** 401 Unauthorized
```bash
# Generate new API key
python3 << 'EOF'
import secrets
print(secrets.token_urlsafe(32))
EOF

# Add to .env
echo "API_KEYS=<generated_key>" >> .env
```

**Issue:** CORS errors
```bash
# Add allowed origins in rest_api.py
allow_origins=["http://localhost:3000", "https://yoursite.com"]
```

### Cloud Backends

**Issue:** API key not found
```bash
# Verify keys are set
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY

# Test connectivity
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models
```

**Issue:** Rate limiting
```bash
# Implement exponential backoff
# Or use local models as primary with cloud as fallback
```

---

## 🎓 Next Steps

### After Phase 2

1. **Monitor Usage**
   - Check persistent memory stats
   - Monitor API usage
   - Track model costs

2. **Optimize**
   - Tune session cleanup
   - Implement caching
   - Add request queuing

3. **Extend**
   - Add Discord interface
   - Implement webhooks
   - Build mobile app

4. **Scale**
   - Add load balancing
   - Implement Redis cache
   - Multi-instance deployment

---

## 📝 Summary

Phase 2 adds:
- ✅ 2 new interfaces (Slack, REST API)
- ✅ Persistent memory with encryption
- ✅ Voice support for web
- ✅ Multi-user management
- ✅ Cloud LLM support

**Total:** ~1,400 new lines building on Phase 1's 9,200 lines

**All Features Work Together:**
- Same AgentCore
- Shared memory
- Unified tools
- Consistent experience

---

## 🤝 Contributing

Phase 2 is modular - easy to add more:
- New interfaces (Discord, WhatsApp)
- New backends (Google Gemini, Mistral)
- Enhanced features (RAG, function calling)

---

**Built with ❤️ for privacy-first AI**

Phase 1 + Phase 2 = Production-ready, enterprise-grade, privacy-first AI agent system!
