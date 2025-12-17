# ⚡ Phase 2.5 Quick Reference

**Production Enhancements - Cheat Sheet**

---

## 📦 Installation (5 Minutes)

```bash
# 1. Install dependencies
pip install docker

# 2. Copy files
tar -xzf pocketportal_enhancements.tar.gz
cp -r pocketportal_enhancements/* ~/your-project/

# 3. Migrate knowledge base
python telegram_agent_tools/knowledge_tools/knowledge_base_sqlite.py

# 4. Build sandbox
python security/docker_sandbox.py

# 5. Restart
python interfaces/telegram_interface.py
```

---

## 🗂️ SQLite Knowledge Base

### Commands
```python
# Add document
{"action": "add", "path": "/path/to/file.txt"}

# Search
{"action": "search", "query": "containers", "limit": 5}

# List all
{"action": "list", "limit": 10}

# Delete
{"action": "delete", "doc_id": 123}

# Stats
{"action": "stats"}

# Migrate from JSON
{"action": "migrate", "path": "path/to/knowledge_base.json"}
```

### Performance
| Documents | Search Time |
|-----------|-------------|
| 10        | 20ms        |
| 100       | 50ms        |
| 1000      | 150ms       |

---

## 🎯 Telegram Inline Keyboards

### New Commands
```
/tools_menu   - Interactive tool selection
/settings     - Toggle settings with buttons
/models       - Select preferred model
```

### Integration
```python
from enhanced_telegram_ui import EnhancedTelegramBot

# In __init__
self.enhanced_ui = EnhancedTelegramBot(self)

# In _register_handlers
self.enhanced_ui.register_handlers(application)
```

### Custom Keyboards
```python
from enhanced_telegram_ui import InlineKeyboardHelper

# Confirmation
keyboard = InlineKeyboardHelper.confirmation_keyboard(
    action="confirm_delete",
    data="doc_123"
)

# Tool selection
keyboard = InlineKeyboardHelper.tool_selection_keyboard(tools)

# Settings
keyboard = InlineKeyboardHelper.settings_keyboard(settings)
```

---

## 🐳 Docker Python Sandbox

### Basic Usage
```python
from security.docker_sandbox import DockerPythonSandbox

sandbox = DockerPythonSandbox()
result = await sandbox.execute_code("print('Hello')")
sandbox.cleanup()
```

### Configuration
```python
from security.docker_sandbox import SandboxConfig

config = SandboxConfig(
    memory_limit="512m",
    cpu_quota=100000,
    timeout_seconds=60,
    network_disabled=False
)

sandbox = DockerPythonSandbox(config)
```

### Security
- ✅ Isolated container
- ✅ No host filesystem access
- ✅ Network disabled by default
- ✅ Resource limits enforced
- ✅ Auto-cleanup

---

## 🚨 Troubleshooting

### SQLite
```bash
# Check database
sqlite3 ~/.telegram_agent/knowledge_base/knowledge_base.db "SELECT COUNT(*) FROM documents;"

# Rebuild indexes
sqlite3 ~/.telegram_agent/knowledge_base/knowledge_base.db "REINDEX;"
```

### Docker
```bash
# Check Docker running
docker ps

# Check image exists
docker images | grep python-sandbox

# Rebuild image
docker rmi python-sandbox:3.11
python security/docker_sandbox.py
```

### Telegram UI
```bash
# Verify integration
grep -n "EnhancedTelegramBot" interfaces/telegram_interface.py

# Check logs
tail -f logs/agent.log | grep callback
```

---

## 📊 Performance Benchmarks

### Expected Performance
- Knowledge Base: 50-150ms (100-1000 docs)
- Docker Sandbox: 200-800ms (including overhead)
- Telegram UI: Instant (button clicks)

### Optimization Tips
```bash
# SQLite: Analyze regularly
sqlite3 knowledge_base.db "ANALYZE;"

# Docker: Pre-build images
docker build -t python-sandbox:3.11 .

# Telegram: Cache keyboards
# (Reuse keyboard instances)
```

---

## 🔐 Security Validation

### Test Network Isolation
```python
result = await sandbox.execute_code("""
import socket
try:
    socket.create_connection(("google.com", 80), timeout=1)
    print("FAIL")
except:
    print("PASS")
""")
# Should print: PASS
```

### Test Filesystem Isolation
```python
result = await sandbox.execute_code("""
import os
print(f"Write /tmp: {os.access('/tmp', os.W_OK)}")  # True
print(f"Write /: {os.access('/', os.W_OK)}")        # False
""")
```

---

## 📈 Monitoring

### Knowledge Base Stats
```python
tool = EnhancedKnowledgeTool()
result = await tool.execute({"action": "stats"})
print(result['result'])
# {
#   'total_documents': 100,
#   'database_size_mb': 5.2,
#   'recent_additions_7d': 10
# }
```

### Docker Stats
```bash
# Container count
docker ps -a | grep sandbox | wc -l

# Image size
docker images python-sandbox:3.11 --format "{{.Size}}"

# Clean old containers
docker container prune -f
```

---

## 🎯 Common Patterns

### Pattern 1: Search with Confirmation
```python
# 1. Search knowledge base
results = await kb.execute({"action": "search", "query": "topic"})

# 2. Show results with buttons
await enhanced_ui.send_knowledge_base_results(chat_id, results['result'])

# 3. User clicks delete button
# 4. Show confirmation
# 5. Execute deletion
```

### Pattern 2: Safe Code Execution
```python
# 1. User requests code execution
# 2. Confirm with button
# 3. Execute in Docker sandbox
result = await sandbox.execute_code(code, timeout=30)

# 4. Return output safely
if result['success']:
    return result['stdout']
```

### Pattern 3: Interactive Tool Selection
```python
# 1. User sends /tools_menu
# 2. Show paginated tool list with buttons
# 3. User clicks tool button
# 4. Show tool details
# 5. User describes task
# 6. Execute tool
```

---

## 🔄 Update Workflow

```bash
# 1. Backup
tar -czf backup.tar.gz ~/your-project

# 2. Update files
cp -r new_files/* ~/your-project/

# 3. Rebuild Docker image if needed
docker rmi python-sandbox:3.11
python security/docker_sandbox.py

# 4. Restart
pkill -f telegram_interface
python interfaces/telegram_interface.py
```

---

## 📞 Support

### Documentation
- Full docs: `docs/README_ENHANCEMENTS.md`
- Migration: `docs/MIGRATION_GUIDE.md`
- This card: `docs/QUICK_REFERENCE.md`

### Common Issues
1. Docker not available → Install Docker Desktop / daemon
2. Migration failed → Check JSON file path
3. Buttons not working → Verify integration code
4. Slow searches → Run `ANALYZE` on SQLite database

---

## ✅ Quick Validation

```bash
# Test everything
python << 'EOF'
import asyncio

async def test_all():
    # 1. Knowledge Base
    from telegram_agent_tools.knowledge_tools.knowledge_base_sqlite import EnhancedKnowledgeTool
    kb = EnhancedKnowledgeTool()
    kb_result = await kb.execute({"action": "stats"})
    print(f"✅ KB: {kb_result['result']['total_documents']} docs")
    
    # 2. Docker Sandbox
    from security.docker_sandbox import DockerPythonSandbox
    sandbox = DockerPythonSandbox()
    exec_result = await sandbox.execute_code("print('test')")
    print(f"✅ Sandbox: {exec_result['success']}")
    sandbox.cleanup()
    
    # 3. UI (manual test)
    print("⚠️  Telegram UI: Send /tools_menu to test")

asyncio.run(test_all())
EOF
```

---

**Quick Reference v2.5** | [Full Docs](docs/README_ENHANCEMENTS.md)
