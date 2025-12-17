# Migration Guide: PocketPortal 3.x → 4.0

This guide helps you migrate from the monolithic 3.x architecture to the modular 4.0 architecture.

## Overview

**TL;DR:** PocketPortal 4.0 is a major architectural refactor. The good news: **your existing setup still works!** The 3.x files remain in place for backwards compatibility during migration.

## What's New in 4.0?

See `pocketportal_unified/README_4.0.md` for the full list, but highlights include:
- 🏗️ Modular architecture with dependency injection
- 🔐 Security middleware enforced at all entry points
- 💾 SQLite-based rate limiting (no more JSON race conditions)
- 📝 Structured logging with request tracing
- 🎯 Interface-agnostic core (add Web/Slack/API easily)
- 📊 Event bus for real-time feedback
- 🧠 Unified context across all interfaces

## Migration Paths

### Path 1: Gradual Migration (Recommended)

**Timeline:** 1-2 weeks
**Risk:** Low
**Effort:** Medium

1. **Week 1: Run 3.x and 4.0 in parallel**
   - Keep using `telegram_agent_v3.py` for production
   - Test `pocketportal_unified/interfaces/telegram_interface.py` on a test bot
   - Verify feature parity

2. **Week 2: Switch to 4.0**
   - Update your systemd service or Docker Compose to use the new interface
   - Monitor logs for any issues
   - Keep 3.x as fallback for 1 week

3. **Week 3: Cleanup**
   - Remove 3.x files if everything works
   - Enjoy the new architecture!

### Path 2: Fresh Start (For New Deployments)

**Timeline:** 1 day
**Risk:** Low
**Effort:** Low

If you're setting up PocketPortal for the first time, just use 4.0:

```bash
# Use the new unified architecture
python pocketportal_unified/interfaces/telegram_interface.py
```

### Path 3: Hybrid (Custom Interfaces)

**Timeline:** Variable
**Risk:** Medium
**Effort:** High

If you've customized PocketPortal heavily:

1. Keep your custom code in 3.x
2. Gradually migrate custom tools to the new tool format
3. Build a new interface using `pocketportal_unified/core`

## Step-by-Step Migration

### Step 1: Update Dependencies

```bash
# Install new dependencies
pip install -r requirements_core.txt

# SQLite is built-in, no new dependencies needed for core features!
```

### Step 2: Test the New Core

```python
# test_core_v2.py
import asyncio
from pocketportal_unified.core import create_agent_core, SecurityMiddleware

async def test():
    config = {
        'ollama_base_url': 'http://localhost:11434',
        'routing_strategy': 'AUTO',
        'model_preferences': {}
    }

    agent_core = create_agent_core(config)
    secure_core = SecurityMiddleware(agent_core)

    result = await secure_core.process_message(
        chat_id="test_001",
        message="Hello! What can you do?",
        interface="cli"
    )

    print(f"✅ Response: {result.response[:100]}...")
    print(f"✅ Model: {result.model_used}")
    print(f"✅ Time: {result.execution_time:.2f}s")

asyncio.run(test())
```

Run it:
```bash
python test_core_v2.py
```

Expected output:
```
✅ Response: I'm an AI assistant with access to various tools. I can help with coding, data analysis...
✅ Model: Qwen2.5 7B
✅ Time: 2.34s
```

### Step 3: Migrate Configuration

**Old (.env for 3.x):**
```env
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_USER_ID=123456
OLLAMA_BASE_URL=http://localhost:11434
```

**New (.env for 4.0):**
```env
# Same! No changes needed!
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_USER_ID=123456
OLLAMA_BASE_URL=http://localhost:11434

# Optional new settings
MAX_CONTEXT_MESSAGES=50
RATE_LIMIT_DB_PATH=data/rate_limits.db
CONTEXT_DB_PATH=data/context.db
```

### Step 4: Migrate Custom Tools

**Old (3.x tool format):**
```python
from telegram_agent_tools.base_tool import BaseTool

class MyCustomTool(BaseTool):
    metadata = ToolMetadata(
        name="my_tool",
        description="Does something cool"
    )

    async def execute(self, params):
        # Your logic
        return {"success": True, "data": "..."}
```

**New (4.0 tool format):**
```python
# Same! Tool format is unchanged!
from telegram_agent_tools.base_tool import BaseTool

class MyCustomTool(BaseTool):
    metadata = ToolMetadata(
        name="my_tool",
        description="Does something cool"
    )

    async def execute(self, params):
        # Your logic
        return {"success": True, "data": "..."}
```

Tools are **100% compatible**! Just make sure they're in `telegram_agent_tools/`.

### Step 5: Update Your Startup Script

**Old:**
```bash
#!/bin/bash
python telegram_agent_v3.py
```

**New:**
```bash
#!/bin/bash
python pocketportal_unified/interfaces/telegram_interface.py
```

### Step 6: Test Telegram Interface

```bash
# Run the new Telegram interface
python pocketportal_unified/interfaces/telegram_interface.py
```

Send a message to your bot. You should see structured logs:

```json
{"timestamp": "2025-12-17T10:30:45", "level": "INFO", "component": "AgentCore", "message": "Processing message", "trace_id": "a3f8"}
{"timestamp": "2025-12-17T10:30:46", "level": "INFO", "component": "Router", "message": "Selected model", "model": "qwen2.5-7b"}
{"timestamp": "2025-12-17T10:30:48", "level": "INFO", "component": "AgentCore", "message": "Completed processing", "execution_time": 2.34}
```

## Breaking Changes

### 1. Import Paths Changed

**Old:**
```python
from core.agent_engine import AgentCore
```

**New:**
```python
from pocketportal_unified.core import create_agent_core, AgentCoreV2
```

### 2. Error Handling Changed

**Old:**
```python
result = await agent_core.process_message(...)
if not result.success:
    print(result.response)  # String error message
```

**New:**
```python
try:
    result = await secure_core.process_message(...)
except RateLimitError as e:
    print(f"Rate limited! Retry after {e.retry_after}s")
except ValidationError as e:
    print(f"Invalid input: {e.message}")
```

### 3. SecurityMiddleware Required

**Old:**
```python
# Security checks inside AgentCore
result = await agent_core.process_message(...)
```

**New:**
```python
# Security checks BEFORE AgentCore
secure_core = SecurityMiddleware(agent_core)
result = await secure_core.process_message(...)  # Must use wrapper!
```

### 4. Rate Limiter Storage Changed

**Old:**
```python
# data/rate_limits.json (file-based)
```

**New:**
```python
# data/rate_limits.db (SQLite-based)
```

**Migration:** Old rate limit data is **not** migrated. Rate limits will reset on first 4.0 run. This is safe and expected.

## Feature Parity Checklist

Verify your migration is complete:

- [ ] Bot responds to `/start` command
- [ ] Bot responds to regular messages
- [ ] Tools execute correctly
- [ ] Rate limiting works (try spamming)
- [ ] Context is preserved across messages
- [ ] Security warnings appear for dangerous commands
- [ ] Multiple interfaces can run simultaneously (if applicable)

## Rollback Plan

If something goes wrong:

```bash
# Stop 4.0
pkill -f "telegram_interface.py"

# Start 3.x
python telegram_agent_v3.py
```

Your old 3.x setup is **untouched**. Just switch back!

## Database Migration (Optional)

4.0 uses SQLite for:
- Rate limiting: `data/rate_limits.db`
- Context: `data/context.db`

These are created automatically on first run. **No manual migration needed.**

If you want to preserve old context, you'll need to write a custom migration script (or just start fresh).

## Performance Impact

### Before (3.x)
- Rate limiting: File I/O per request
- Context: In-memory only (lost on restart)
- Logging: Plain text

### After (4.0)
- Rate limiting: SQLite (faster, concurrent-safe)
- Context: SQLite (persistent, shared across interfaces)
- Logging: Structured JSON (better for analysis)

**Expected:** Slightly better performance under concurrent load.

## Testing Recommendations

### Unit Tests
```bash
# Test core functionality
pytest tests/test_agent_core_v2.py

# Test security middleware
pytest tests/test_security_middleware.py

# Test context management
pytest tests/test_context_manager.py
```

### Integration Tests
```bash
# Test full flow
pytest tests/test_integration_telegram.py
```

### Load Tests
```bash
# Test concurrent requests
python tests/load_test.py --concurrent 10 --requests 100
```

## Common Issues

### Issue 1: Import Errors

**Error:**
```
ModuleNotFoundError: No module named 'pocketportal_unified.core'
```

**Solution:**
```bash
# Make sure you're in the project root
cd /path/to/pocketportal

# Run from project root
python pocketportal_unified/interfaces/telegram_interface.py
```

### Issue 2: Database Locked

**Error:**
```
sqlite3.OperationalError: database is locked
```

**Solution:**
SQLite WAL mode should prevent this. If it happens:
```bash
# Check for zombie processes
ps aux | grep python

# Kill old processes
pkill -f telegram
```

### Issue 3: Rate Limit Not Working

**Symptom:** Can send unlimited messages

**Solution:**
Make sure you're using `SecurityMiddleware`:
```python
secure_core = SecurityMiddleware(agent_core, enable_rate_limiting=True)
```

## Getting Help

1. **Check logs:** `logs/pocketportal.log`
2. **Search by trace_id:** Find the trace_id in your logs and grep for it
3. **GitHub Issues:** Report bugs with trace_id and error logs
4. **Architecture docs:** `pocketportal_unified/README_4.0.md`

## Next Steps

After migration:

1. **Explore new features:**
   - Event bus for real-time UI updates
   - Multi-interface support (add a Web UI!)
   - Advanced monitoring with trace IDs

2. **Optimize:**
   - Adjust context window size
   - Tune rate limits
   - Customize prompts

3. **Extend:**
   - Add new interfaces (Web, Slack, Discord)
   - Add custom security policies
   - Add custom event handlers

---

**Questions?** Open an issue on GitHub with the `migration` label.

**Success!** Share your migration story in Discussions.
