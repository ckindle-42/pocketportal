# 📋 Migration Guide: Existing → Unified Architecture

**From:** telegram_agent_v3.py (monolithic)  
**To:** Unified core + multiple interfaces

**Time Required:** 30-60 minutes  
**Difficulty:** Easy (mostly copying files)

---

## 🎯 What You're Doing

You're extracting the core AI logic into a reusable engine that can serve multiple interfaces (Telegram, Web, Slack, API) while keeping all your existing routing, tools, and security intact.

**Nothing breaks** - your Telegram bot will work identically, but now you'll also have a web interface!

---

## 📋 Pre-Migration Checklist

- [ ] Current `telegram_agent_v3.py` is working
- [ ] Ollama is running
- [ ] You have a backup: `cp -r ~/telegram-agent ~/telegram-agent.backup`
- [ ] Python 3.11+ is installed
- [ ] Virtual environment is active

---

## 🚀 Migration Steps

### Step 1: Backup Current Setup (2 minutes)

```bash
# Full backup
cd ~
tar -czf telegram-agent-backup-$(date +%Y%m%d).tar.gz telegram-agent/

# Verify backup
ls -lh telegram-agent-backup-*.tar.gz
```

---

### Step 2: Create New Directories (1 minute)

```bash
cd ~/telegram-agent

# Create new directories
mkdir -p core
mkdir -p interfaces
mkdir -p web_static

# Verify structure
tree -L 1
```

Expected output:
```
.
├── core/               # NEW
├── interfaces/         # NEW
├── web_static/         # NEW
├── routing/            # Existing
├── telegram_agent_tools/  # Existing
├── security/           # Existing
├── telegram_agent_v3.py   # Existing (will be replaced)
└── ...
```

---

### Step 3: Copy New Core Files (5 minutes)

**Option A: From the files I just created**

```bash
cd ~/telegram-agent

# Copy core engine
cp /tmp/pocketportal_unified/core/* core/

# Copy interfaces
cp /tmp/pocketportal_unified/interfaces/* interfaces/

# Copy web frontend
cp /tmp/pocketportal_unified/web_static/* web_static/

# Copy README
cp /tmp/pocketportal_unified/README.md UNIFIED_README.md
```

**Option B: Manual creation**

If the files aren't in /tmp, create them manually using the content I provided:
- `core/agent_engine.py`
- `core/__init__.py`
- `interfaces/telegram_interface.py`
- `interfaces/web_interface.py`
- `interfaces/__init__.py`
- `web_static/index.html`

---

### Step 4: Update Dependencies (5 minutes)

```bash
cd ~/telegram-agent
source venv/bin/activate

# Install new web dependencies
pip install fastapi==0.104.1
pip install "uvicorn[standard]==0.24.0"
pip install websockets==12.0

# Verify installation
python -c "import fastapi, uvicorn, websockets; print('✅ Web dependencies installed')"
```

---

### Step 5: Verify Existing Modules (2 minutes)

Your existing modules should be unchanged. Verify they're all present:

```bash
cd ~/telegram-agent

# Check routing
ls -la routing/
# Should see: model_registry.py, model_backends.py, etc.

# Check tools
ls -la telegram_agent_tools/
# Should see: utility_tools/, data_tools/, web_tools/, etc.

# Check security
ls -la security/
# Should see: security_module.py

# Check config validator
ls -la config_validator.py
```

If any are missing, you need to copy them from your backup.

---

### Step 6: Test Core Engine (5 minutes)

```bash
cd ~/telegram-agent
source venv/bin/activate

# Test the core
python core/agent_engine.py
```

Expected output:
```
============================================================
Initializing AgentCore (Unified Engine)
============================================================
Loading routing system...
Loading tool registry...
Tools loaded: 11 success, 0 failed
Initializing security module...
============================================================
AgentCore initialized successfully!
  Routing: AUTO
  Tools: 11
  Models: 10
============================================================
Processing message from test | chat_id=test_001 | length=30
Completed processing | model=ollama_qwen25_7b | time=1.23s | tools=0
============================================================
TEST RESULT:
============================================================
Success: True
Model: ollama_qwen25_7b
Time: 1.23s
Response: [Your agent's response]
============================================================
```

✅ **Checkpoint:** If this works, your core is good!

---

### Step 7: Test Telegram Interface (10 minutes)

```bash
cd ~/telegram-agent
source venv/bin/activate

# Run new Telegram interface
python interfaces/telegram_interface.py
```

Expected output:
```
============================================================
Initializing Telegram Interface
============================================================
Initializing AgentCore...
============================================================
AgentCore initialized successfully!
  Routing: AUTO
  Tools: 11
  Models: 10
============================================================
Telegram Interface ready!
============================================================
🚀 Telegram Bot Starting!
============================================================
```

**Test on Telegram:**
1. Open your bot in Telegram
2. Send: `/start`
3. Send: `/health`
4. Send: `Hello!`
5. Send: `What tools do you have?`

✅ **Checkpoint:** If responses work identically to before, migration successful!

---

### Step 8: Test Web Interface (10 minutes)

```bash
# In a NEW terminal (keep Telegram running if you want)
cd ~/telegram-agent
source venv/bin/activate

# Run web interface
python interfaces/web_interface.py
```

Expected output:
```
============================================================
Starting PocketPortal Web Interface
============================================================
Initializing AgentCore...
============================================================
Web interface ready!
Open http://localhost:8000 in your browser
============================================================
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Test in Browser:**
1. Open http://localhost:8000
2. Should see "PocketPortal" interface
3. Type: "Hello!"
4. Should get response with model info
5. Try: "What's 2+2?"
6. Try: "List your tools"

✅ **Checkpoint:** If web chat works, you're done!

---

### Step 9: Run Both Simultaneously (Optional)

```bash
# Terminal 1: Telegram
cd ~/telegram-agent && source venv/bin/activate
python interfaces/telegram_interface.py

# Terminal 2: Web
cd ~/telegram-agent && source venv/bin/activate
python interfaces/web_interface.py
```

Now you can chat via both Telegram AND web browser! 🎉

---

## 🔄 Rollback Plan

If something goes wrong:

```bash
# Stop everything
pkill -f telegram_interface
pkill -f web_interface

# Restore backup
cd ~
rm -rf telegram-agent
cp -r telegram-agent.backup telegram-agent

# Or restore from tar
tar -xzf telegram-agent-backup-YYYYMMDD.tar.gz

# Test old version
cd telegram-agent
source venv/bin/activate
python telegram_agent_v3.py
```

---

## 📊 Verification Checklist

After migration, verify:

- [ ] Telegram bot responds to messages
- [ ] All commands work (`/start`, `/help`, `/tools`, `/health`, `/stats`)
- [ ] Tools execute correctly (test QR generator, math, etc.)
- [ ] Web interface loads at http://localhost:8000
- [ ] Web chat responds to messages
- [ ] Model selection works (fast models for simple queries)
- [ ] Security features work (rate limiting, input sanitization)
- [ ] Logs appear in `logs/` directory

---

## 🐛 Troubleshooting

### "Module not found" errors

```bash
# Make sure you're in the right directory
cd ~/telegram-agent

# Make sure venv is activated
source venv/bin/activate

# Verify Python path includes current directory
python -c "import sys; print(sys.path)"
# Should include '/Users/you/telegram-agent'
```

### Core can't find routing/tools

```bash
# The imports should work if you're in the project root
# Check your directory structure:
ls -la
# Should see: core/, routing/, telegram_agent_tools/, security/

# If routing/ is missing, copy from backup:
cp -r ~/telegram-agent.backup/routing/ .
```

### Web interface won't start

```bash
# Check if port 8000 is in use
lsof -i :8000

# Use different port
uvicorn interfaces.web_interface:app --host 127.0.0.1 --port 8001
```

### Telegram bot won't connect

```bash
# Verify your .env has correct token
cat .env | grep TELEGRAM_BOT_TOKEN

# Test token with curl
curl -X GET "https://api.telegram.org/bot<YOUR_TOKEN>/getMe"
```

---

## 📈 Performance Comparison

### Before (Monolithic)
- Single interface (Telegram only)
- ~800 lines in main file
- Hard to add new features
- No web access

### After (Unified)
- Multiple interfaces (Telegram + Web)
- Core: 300 lines (reusable)
- Each interface: ~350 lines
- Easy to add Slack, API, etc.
- Web browser access ✅

**Same performance, better architecture!**

---

## 🎓 What Changed?

### File Changes

**Removed:**
- ❌ `telegram_agent_v3.py` (replaced by interface adapter)

**Added:**
- ✅ `core/agent_engine.py` (unified brain)
- ✅ `core/__init__.py`
- ✅ `interfaces/telegram_interface.py` (Telegram adapter)
- ✅ `interfaces/web_interface.py` (Web adapter)
- ✅ `interfaces/__init__.py`
- ✅ `web_static/index.html` (Web UI)

**Unchanged:**
- ✅ `routing/` (all files)
- ✅ `telegram_agent_tools/` (all files)
- ✅ `security/` (all files)
- ✅ `config_validator.py`
- ✅ `.env`

### Code Changes

**Before:**
```python
# telegram_agent_v3.py - Everything in one file
class TelegramAgent:
    def __init__(self):
        # Initialize routing
        # Initialize tools
        # Initialize Telegram
        # All logic here
    
    def handle_message(self, update, context):
        # Process message
        # Call LLM
        # Format response
```

**After:**
```python
# core/agent_engine.py - Reusable brain
class AgentCore:
    async def process_message(self, chat_id, message, interface):
        # Same logic, interface-agnostic
        return result

# interfaces/telegram_interface.py - Thin adapter
class TelegramInterface:
    def __init__(self):
        self.agent_core = AgentCore(config)  # Use core
    
    async def handle_message(self, update, context):
        result = await self.agent_core.process_message(...)  # Delegate
        await update.message.reply_text(result.response)  # Format

# interfaces/web_interface.py - Another thin adapter
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket, session_id):
    result = await agent_core.process_message(...)  # Same core!
    await websocket.send_json(result)  # Different format
```

---

## ✅ Success Criteria

Your migration is successful when:

1. ✅ Telegram bot works identically to before
2. ✅ Web interface loads and responds
3. ✅ Both can run simultaneously
4. ✅ Statistics are tracked across both
5. ✅ All 11 tools work in both interfaces
6. ✅ No errors in logs

---

## 🎉 Next Steps

After successful migration:

1. **Test thoroughly** - Use both interfaces for a day
2. **Monitor logs** - Check for any issues
3. **Add features** - Now it's easy to extend!
4. **Consider Slack** - Add another interface in ~2 hours
5. **Build API** - Expose core via REST API

---

## 📞 Need Help?

If stuck:
1. Check logs in `logs/` directory
2. Enable verbose logging: `LOG_LEVEL=DEBUG` in `.env`
3. Test core independently: `python core/agent_engine.py`
4. Test each interface separately
5. Restore from backup if needed

---

**Migration Complete! 🎊**

You now have a unified architecture that's easier to maintain and extend!
