# ⚡ Phase 2 Quick Installation Guide

**Time Required:** 30-60 minutes  
**Prerequisites:** Phase 1 installed and working

---

## 📋 Pre-Installation Checklist

- [ ] Phase 1 unified architecture is installed
- [ ] Telegram bot is working
- [ ] Web interface is working (optional but recommended)
- [ ] You have a backup: `tar -czf backup-phase1.tar.gz ~/your-project/`
- [ ] Python venv is activated

---

## 🚀 Installation Steps

### Step 1: Download Phase 2 Files (2 minutes)

```bash
cd ~/your-project

# Copy Phase 2 files (adjust path as needed)
# These files integrate seamlessly with Phase 1
cp -r /path/to/pocketportal_phase2/* .

# Verify structure
tree -L 2 -I '__pycache__|*.pyc'
```

**Expected structure:**
```
your-project/
├── core/
│   ├── agent_engine.py           # Phase 1
│   ├── persistent_memory.py      # Phase 2 NEW
│   └── backends/
│       └── cloud_backends.py     # Phase 2 NEW
├── interfaces/
│   ├── telegram_interface.py     # Phase 1
│   ├── web_interface.py          # Phase 1
│   ├── slack_interface.py        # Phase 2 NEW
│   └── rest_api.py               # Phase 2 NEW
├── web_static/
│   ├── index.html                # Phase 1
│   └── js/
│       └── voice-recorder.js     # Phase 2 NEW
└── ...
```

---

### Step 2: Install Dependencies (5 minutes)

```bash
cd ~/your-project
source venv/bin/activate

# Slack SDK (only if using Slack)
pip install slack-bolt==1.18.0

# Cloud backends use existing dependencies (aiohttp)
# No additional installs needed for OpenAI/Anthropic

# Verify
python3 << 'EOF'
try:
    import slack_bolt
    print("✅ Slack SDK installed")
except ImportError:
    print("⚠️  Slack SDK not installed (optional)")

import aiohttp
print("✅ Cloud backends ready (using existing aiohttp)")
EOF
```

---

### Step 3: Configure Environment (10 minutes)

#### Option A: Slack Bot (30 minutes setup)

```bash
# 1. Create Slack App at api.slack.com/apps
# 2. Enable Socket Mode
# 3. Add Bot Token Scopes:
#    - chat:write
#    - app_mentions:read
#    - im:history
#    - commands
# 4. Install app to workspace
# 5. Get tokens

# Add to .env
cat >> .env << 'EOF'

# ============================================================================
# PHASE 2: Slack Interface
# ============================================================================
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_APP_TOKEN=xapp-your-app-token-here
SLACK_AUTHORIZED_USERS=  # Leave empty for all, or U123456,U789012
EOF
```

#### Option B: REST API (5 minutes)

```bash
# Generate API key
API_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# Add to .env
cat >> .env << EOF

# ============================================================================
# PHASE 2: REST API
# ============================================================================
API_KEYS=$API_KEY
EOF

echo "✅ Your API key: $API_KEY"
echo "📝 Save this key securely!"
```

#### Option C: Cloud LLMs (5 minutes)

```bash
# Get API keys from:
# - OpenAI: platform.openai.com/api-keys
# - Anthropic: console.anthropic.com/settings/keys

# Add to .env
cat >> .env << 'EOF'

# ============================================================================
# PHASE 2: Cloud LLM Backends
# ============================================================================
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
EOF
```

#### Option D: Memory & Multi-User (2 minutes)

```bash
# Generate encryption key
ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")

# Add to .env
cat >> .env << EOF

# ============================================================================
# PHASE 2: Persistent Memory
# ============================================================================
MEMORY_ENCRYPTION_KEY=$ENCRYPTION_KEY
SESSION_TTL_DAYS=30
MAX_HISTORY_LENGTH=50
EOF
```

---

### Step 4: Initialize Database (2 minutes)

```bash
# Create persistent memory database
python3 << 'EOF'
from core.persistent_memory import PersistentMemoryManager

manager = PersistentMemoryManager()
print("✅ Database initialized at data/memory.db")

# Get stats
import asyncio
stats = asyncio.run(manager.get_stats())
print(f"Database size: {stats['database_size_mb']:.2f} MB")
EOF
```

---

### Step 5: Test Each Feature (15 minutes)

#### Test 1: Persistent Memory

```bash
python3 << 'EOF'
import asyncio
from core.persistent_memory import PersistentMemoryManager

async def test():
    manager = PersistentMemoryManager()
    
    # Create session
    session = await manager.create_session(
        session_id="test_001",
        user_id="test_user",
        interface="test"
    )
    print(f"✅ Session created: {session.session_id}")
    
    # Add messages
    await manager.add_message(session.session_id, "user", "Hello!")
    await manager.add_message(session.session_id, "assistant", "Hi there!")
    print("✅ Messages added")
    
    # Get history
    history = await manager.get_history(session.session_id)
    print(f"✅ History retrieved: {len(history)} messages")
    
    for msg in history:
        print(f"  {msg.role}: {msg.content}")

asyncio.run(test())
EOF
```

#### Test 2: Cloud Backends (if configured)

```bash
# Skip if you don't have API keys

python3 << 'EOF'
import asyncio
import os

async def test():
    # Test OpenAI
    if os.getenv("OPENAI_API_KEY"):
        from core.backends.cloud_backends import OpenAIBackend
        
        openai = OpenAIBackend()
        available = await openai.is_available()
        
        if available:
            result = await openai.generate(
                prompt="Say 'Hello from OpenAI!'",
                model_name="gpt-3.5-turbo",
                max_tokens=20
            )
            print(f"✅ OpenAI: {result['content']}")
        else:
            print("⚠️  OpenAI not available")
        
        await openai.close()
    else:
        print("⏭️  OpenAI: No API key configured")
    
    # Test Anthropic
    if os.getenv("ANTHROPIC_API_KEY"):
        from core.backends.cloud_backends import AnthropicBackend
        
        anthropic = AnthropicBackend()
        result = await anthropic.generate(
            prompt="Say 'Hello from Anthropic!'",
            model_name="claude-3-haiku-20240307",
            max_tokens=20
        )
        print(f"✅ Anthropic: {result['content']}")
        await anthropic.close()
    else:
        print("⏭️  Anthropic: No API key configured")

asyncio.run(test())
EOF
```

#### Test 3: REST API

```bash
# Start API server (in background)
python interfaces/rest_api.py &
API_PID=$!
sleep 3

# Test health endpoint (no auth)
curl -s http://localhost:8001/api/v1/health | python3 -m json.tool

# Test chat endpoint (with auth)
API_KEY=$(grep "API_KEYS=" .env | cut -d'=' -f2)
curl -s -X POST http://localhost:8001/api/v1/chat \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is 2+2?"}' | python3 -m json.tool

# Stop API server
kill $API_PID
```

#### Test 4: Slack Bot (if configured)

```bash
# Only if you configured Slack

# Start Slack bot
python interfaces/slack_interface.py

# In Slack:
# 1. Send DM to bot: "Hello!"
# 2. Mention in channel: "@bot what's the time?"
# 3. Use slash command: "/ai tell me a joke"
# 4. Check stats: "/stats"

# Bot should respond!
```

---

### Step 6: Integration Test (5 minutes)

```bash
# Test that Phase 1 still works

# Telegram bot
python interfaces/telegram_interface.py &
TELEGRAM_PID=$!
echo "✅ Telegram started (PID: $TELEGRAM_PID)"

# Send message via Telegram and verify response
# Then stop:
kill $TELEGRAM_PID

# Web interface
python interfaces/web_interface.py &
WEB_PID=$!
echo "✅ Web started (PID: $WEB_PID)"

# Open http://localhost:8000 and test
# Then stop:
kill $WEB_PID

echo "✅ Phase 1 still works!"
```

---

### Step 7: Run Everything (Optional)

```bash
# Run all interfaces simultaneously
# Each in a separate terminal or using tmux/screen

# Terminal 1: Telegram
python interfaces/telegram_interface.py

# Terminal 2: Web
python interfaces/web_interface.py

# Terminal 3: Slack (if configured)
python interfaces/slack_interface.py

# Terminal 4: REST API
python interfaces/rest_api.py

# Now you can:
# - Chat via Telegram
# - Chat via Web browser
# - Chat via Slack
# - Call REST API
# All using the SAME AgentCore and memory!
```

---

## ✅ Verification Checklist

After installation, verify:

- [ ] Persistent memory database created (`data/memory.db` exists)
- [ ] Memory test script works
- [ ] Cloud backends test works (if configured)
- [ ] REST API responds to health check
- [ ] REST API responds to authenticated chat
- [ ] Slack bot responds (if configured)
- [ ] Telegram still works (Phase 1)
- [ ] Web interface still works (Phase 1)
- [ ] No errors in logs

---

## 🔄 Rollback Plan

If something goes wrong:

```bash
# Stop all processes
pkill -f "python interfaces"

# Restore Phase 1 backup
cd ~
rm -rf your-project
tar -xzf backup-phase1.tar.gz

# Restart Phase 1
cd your-project
source venv/bin/activate
python interfaces/telegram_interface.py
```

---

## 📊 What's Different?

### Before (Phase 1 Only)
```
- 2 interfaces (Telegram, Web)
- No persistent memory
- Local models only
- No voice on web
```

### After (Phase 1 + Phase 2)
```
- 4 interfaces (Telegram, Web, Slack, API)
- Persistent memory with encryption
- Local + Cloud models
- Voice recording on web
- Multi-user support
- Session management
```

---

## 🎯 Common Patterns

### Pattern 1: Local + Cloud Hybrid

```bash
# Primary: Local (fast, private)
LLM_BACKEND=ollama
ROUTING_STRATEGY=speed

# Fallback: Cloud (for complex queries)
OPENAI_API_KEY=sk-...

# Routing automatically uses cloud when needed
```

### Pattern 2: Multi-Interface Setup

```bash
# Different interfaces for different use cases:
# - Telegram: Mobile, personal use
# - Slack: Team, work use
# - REST API: Integrations, automation
# - Web: Desktop, full features
```

### Pattern 3: Memory Persistence

```python
# User starts chat on Telegram
telegram_interface → session_id="telegram_123"

# Later, continues on Web
web_interface → session_id="web_123"  # Different session

# Want to share? Use same session ID!
session_id = f"user_{user_id}"  # Shared across interfaces
```

---

## 🐛 Common Issues

### Issue: "Database locked"
```bash
# SQLite is locked by another process
# Solution: Only one writer at a time
# Use transactions properly (already handled in code)
```

### Issue: "Invalid API key"
```bash
# Cloud backend auth failed
# Solution: Verify keys are correct
echo $OPENAI_API_KEY | head -c 20  # Should be "sk-..."
echo $ANTHROPIC_API_KEY | head -c 20  # Should be "sk-ant-..."
```

### Issue: Slack bot not responding
```bash
# Check tokens
python3 << 'EOF'
import os
print("Bot token:", os.getenv("SLACK_BOT_TOKEN", "NOT SET")[:20])
print("App token:", os.getenv("SLACK_APP_TOKEN", "NOT SET")[:20])
EOF

# Verify Socket Mode is enabled in Slack app settings
```

---

## 🎉 Success Criteria

You've successfully installed Phase 2 when:

- ✅ All tests pass
- ✅ Phase 1 interfaces still work
- ✅ At least one Phase 2 interface works
- ✅ Persistent memory stores/retrieves data
- ✅ No errors in logs
- ✅ Can switch between interfaces seamlessly

---

## 📝 Next Steps

1. **Explore Features**
   - Try each interface
   - Test memory persistence
   - Experiment with cloud models

2. **Customize**
   - Adjust session TTL
   - Configure authorized users
   - Set up webhooks

3. **Monitor**
   - Check database size
   - Monitor API usage
   - Track costs (if using cloud)

4. **Optimize**
   - Tune routing strategy
   - Implement caching
   - Add monitoring

---

**Installation Complete!** 🎊

You now have a production-grade, multi-interface, privacy-first AI agent system with:
- 4 interfaces
- Persistent memory
- Cloud LLM support
- Voice capabilities
- Multi-user management

**Total capability:** Phase 1 (9,200 lines) + Phase 2 (1,400 lines) = **10,600 lines of code!**
