# 🔄 Phase 2.5 Migration Guide

**Upgrading to Production Enhancements**

This guide walks you through migrating from Phase 1/2 to Phase 2.5 with minimal downtime.

---

## 📋 Pre-Migration Checklist

- [ ] Phase 1/2 is installed and working
- [ ] You have a recent backup
- [ ] Docker is installed (for sandbox feature)
- [ ] All users are notified of planned maintenance
- [ ] You have 60-90 minutes available

---

## 🎯 Migration Path

You have two options:

### Option A: Full Migration (Recommended)
Install all three enhancements at once (60-90 minutes)

### Option B: Incremental Migration
Install enhancements one at a time over multiple sessions

---

## 🚀 Option A: Full Migration

### Step 1: Backup (5 minutes)

```bash
cd ~/your-project

# Create backup
BACKUP_NAME="backup_$(date +%Y%m%d_%H%M%S).tar.gz"
tar -czf ~/$BACKUP_NAME .
echo "✅ Backup created: ~/$BACKUP_NAME"

# Also backup knowledge base
cp -r ~/.telegram_agent/knowledge_base/ ~/.telegram_agent/knowledge_base.backup/
echo "✅ Knowledge base backed up"
```

### Step 2: Stop Services (2 minutes)

```bash
# Stop all running interfaces
pkill -f "python.*telegram_interface"
pkill -f "python.*web_interface"
pkill -f "python.*slack_interface"
pkill -f "python.*rest_api"

# Verify stopped
ps aux | grep "python.*interface" || echo "✅ All services stopped"
```

### Step 3: Install Dependencies (5 minutes)

```bash
cd ~/your-project
source venv/bin/activate

# Install Docker SDK
pip install docker

# Verify
python3 << 'EOF'
try:
    import docker
    client = docker.from_env()
    print("✅ Docker SDK installed and Docker is running")
except:
    print("❌ Docker not available - install Docker first")
EOF
```

### Step 4: Copy Enhancement Files (3 minutes)

```bash
# Extract enhancements
tar -xzf pocketportal_enhancements.tar.gz

# Copy to your project
cp -r pocketportal_enhancements/tools/* telegram_agent_tools/
cp -r pocketportal_enhancements/interfaces/* interfaces/
cp -r pocketportal_enhancements/security/* security/

# Verify structure
tree -L 2 telegram_agent_tools/ | grep -E "(knowledge_base_sqlite|docker_sandbox)"
```

### Step 5: Migrate Knowledge Base (10 minutes)

```bash
# Run migration
python << 'EOF'
import asyncio
import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path.cwd()))

from telegram_agent_tools.knowledge_tools.knowledge_base_sqlite import EnhancedKnowledgeTool

async def migrate():
    print("=" * 60)
    print("Starting Knowledge Base Migration")
    print("=" * 60)
    
    tool = EnhancedKnowledgeTool()
    
    # Migrate
    result = await tool.execute({
        "action": "migrate",
        "path": "~/.telegram_agent/knowledge_base/knowledge_base.json"
    })
    
    if result['success']:
        stats = result['result']
        print(f"\n✅ Migration successful!")
        print(f"   Migrated: {stats['migrated']} documents")
        print(f"   Failed: {stats['failed']} documents")
        print(f"   Total: {stats['total']} documents")
        
        # Get stats
        stats_result = await tool.execute({"action": "stats"})
        if stats_result['success']:
            db_stats = stats_result['result']
            print(f"\nDatabase Statistics:")
            print(f"   Total documents: {db_stats['total_documents']}")
            print(f"   Database size: {db_stats['database_size_mb']:.2f} MB")
            print(f"   Embeddings: {'Enabled' if db_stats['embeddings_enabled'] else 'Disabled'}")
    else:
        print(f"\n❌ Migration failed: {result['error']}")
        sys.exit(1)

asyncio.run(migrate())
EOF

# Verify migration
python << 'EOF'
import asyncio
from telegram_agent_tools.knowledge_tools.knowledge_base_sqlite import EnhancedKnowledgeTool

async def test():
    tool = EnhancedKnowledgeTool()
    
    # Test search
    result = await tool.execute({
        "action": "search",
        "query": "test",
        "limit": 1
    })
    
    if result['success']:
        print("✅ SQLite knowledge base working")
    else:
        print(f"❌ Search failed: {result['error']}")

asyncio.run(test())
EOF
```

### Step 6: Integrate Telegram UI (15 minutes)

```bash
# Backup current telegram_interface.py
cp interfaces/telegram_interface.py interfaces/telegram_interface.py.backup

# Edit telegram_interface.py
cat >> interfaces/telegram_interface.py << 'INTEGRATION_MARKER'

# ============================================================================
# ENHANCEMENT: Inline Keyboards
# ============================================================================

from enhanced_telegram_ui import EnhancedTelegramBot

# In TelegramInterface.__init__, add:
# self.enhanced_ui = EnhancedTelegramBot(self)

# In _register_handlers, add:
# self.enhanced_ui.register_handlers(application)

INTEGRATION_MARKER

echo "⚠️  Manual step required:"
echo "Edit interfaces/telegram_interface.py and add the lines shown above"
echo "See docs/INTEGRATION_EXAMPLE.md for detailed instructions"
```

**Manual Integration Steps:**

1. Open `interfaces/telegram_interface.py`
2. Add import at top:
   ```python
   from enhanced_telegram_ui import EnhancedTelegramBot
   ```
3. In `__init__` method, after existing initialization:
   ```python
   # Enhanced UI
   self.enhanced_ui = EnhancedTelegramBot(self)
   ```
4. In `_register_handlers` method, after existing handlers:
   ```python
   # Register enhanced handlers
   self.enhanced_ui.register_handlers(application)
   ```

### Step 7: Build Docker Sandbox (10 minutes)

```bash
# Build sandbox image
python << 'EOF'
import asyncio
from security.docker_sandbox import DockerPythonSandbox

async def setup():
    print("=" * 60)
    print("Building Docker Sandbox")
    print("=" * 60)
    
    try:
        sandbox = DockerPythonSandbox()
        print("\n✅ Sandbox initialized")
        
        # Test execution
        print("\nTesting sandbox...")
        result = await sandbox.execute_code("""
print("Hello from Docker!")
import sys
print(f"Python {sys.version.split()[0]}")
import numpy as np
print(f"NumPy {np.__version__}")
""")
        
        if result['success']:
            print("✅ Sandbox test passed")
            print(f"\nOutput:\n{result['stdout']}")
        else:
            print(f"❌ Sandbox test failed: {result['stderr']}")
        
        sandbox.cleanup()
    
    except Exception as e:
        print(f"❌ Sandbox setup failed: {e}")
        print("\nTroubleshooting:")
        print("1. Is Docker running? Check with: docker ps")
        print("2. Is Docker SDK installed? Check with: pip list | grep docker")
        print("3. Do you have permissions? May need: sudo usermod -aG docker $USER")

asyncio.run(setup())
EOF
```

### Step 8: Update Tool Registry (5 minutes)

```bash
# Verify tools are discoverable
python << 'EOF'
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from telegram_agent_tools import registry

# Refresh registry
registry.discover_tools()

# Check for new tools
tools = registry.list_tools()
tool_names = [t['name'] for t in tools]

expected_new = ['knowledge_base_enhanced', 'python_sandbox']
found_new = [t for t in expected_new if t in tool_names]

print(f"✅ Found {len(found_new)}/{len(expected_new)} new tools:")
for tool in found_new:
    print(f"   - {tool}")

if len(found_new) < len(expected_new):
    missing = [t for t in expected_new if t not in found_new]
    print(f"\n⚠️  Missing tools: {missing}")
EOF
```

### Step 9: Run Tests (10 minutes)

```bash
# Test 1: SQLite Knowledge Base
python << 'EOF'
import asyncio
from telegram_agent_tools.knowledge_tools.knowledge_base_sqlite import EnhancedKnowledgeTool

async def test_kb():
    print("Testing SQLite Knowledge Base...")
    tool = EnhancedKnowledgeTool()
    
    # Add test document
    result = await tool.execute({
        "action": "add",
        "content": "Test document for migration",
        "metadata": {"test": True}
    })
    assert result['success'], f"Add failed: {result}"
    doc_id = result['result']['doc_id']
    print(f"✅ Add document: ID {doc_id}")
    
    # Search
    result = await tool.execute({
        "action": "search",
        "query": "migration",
        "limit": 5
    })
    assert result['success'], f"Search failed: {result}"
    print(f"✅ Search: Found {len(result['result'])} documents")
    
    # Delete
    result = await tool.execute({
        "action": "delete",
        "doc_id": doc_id
    })
    assert result['success'], f"Delete failed: {result}"
    print(f"✅ Delete: Removed ID {doc_id}")
    
    print("\n✅ Knowledge Base tests passed!")

asyncio.run(test_kb())
EOF

# Test 2: Docker Sandbox
python << 'EOF'
import asyncio
from security.docker_sandbox import DockerPythonSandbox

async def test_sandbox():
    print("\nTesting Docker Sandbox...")
    sandbox = DockerPythonSandbox()
    
    # Test 1: Basic execution
    result = await sandbox.execute_code("print('Hello')")
    assert result['success'], f"Basic exec failed: {result}"
    assert 'Hello' in result['stdout'], f"Output incorrect: {result['stdout']}"
    print("✅ Basic execution")
    
    # Test 2: Network isolation
    result = await sandbox.execute_code("""
import socket
try:
    socket.create_connection(("google.com", 80), timeout=1)
    print("NETWORK_ENABLED")
except:
    print("NETWORK_DISABLED")
""")
    assert 'NETWORK_DISABLED' in result['stdout'], "Network not isolated!"
    print("✅ Network isolation")
    
    # Test 3: Timeout
    import time
    start = time.time()
    result = await sandbox.execute_code("import time; time.sleep(100)", timeout=2)
    elapsed = time.time() - start
    assert elapsed < 5, f"Timeout not enforced: {elapsed}s"
    print("✅ Timeout enforcement")
    
    sandbox.cleanup()
    print("\n✅ Sandbox tests passed!")

asyncio.run(test_sandbox())
EOF

# Test 3: Telegram UI (manual)
echo ""
echo "⚠️  Manual test required for Telegram UI:"
echo "1. Start the bot: python interfaces/telegram_interface.py"
echo "2. Send: /tools_menu"
echo "3. Verify buttons appear"
echo "4. Click a button and verify response"
```

### Step 10: Start Services (5 minutes)

```bash
# Start Telegram bot
python interfaces/telegram_interface.py &
TELEGRAM_PID=$!
sleep 3

# Verify started
if ps -p $TELEGRAM_PID > /dev/null; then
    echo "✅ Telegram bot started (PID: $TELEGRAM_PID)"
else
    echo "❌ Telegram bot failed to start"
    cat logs/agent.log | tail -20
fi

# Start other interfaces if needed
# python interfaces/web_interface.py &
# python interfaces/slack_interface.py &
# python interfaces/rest_api.py &
```

### Step 11: Verify in Production (5 minutes)

```bash
# Check Telegram bot
echo "Send a message to your bot and verify response"
echo "Try: /tools_menu"

# Check knowledge base
echo "Try: Search the knowledge base for [your topic]"

# Check logs
tail -f logs/agent.log
```

---

## 🔄 Option B: Incremental Migration

### Week 1: SQLite Knowledge Base
```bash
# Install only knowledge base
cp pocketportal_enhancements/tools/knowledge_base_sqlite.py telegram_agent_tools/knowledge_tools/
python telegram_agent_tools/knowledge_tools/knowledge_base_sqlite.py  # Migrate

# Test for a week, monitor performance
```

### Week 2: Telegram UI
```bash
# Install inline keyboards
cp pocketportal_enhancements/interfaces/enhanced_telegram_ui.py interfaces/
# Integrate with telegram_interface.py

# Test for a week, gather user feedback
```

### Week 3: Docker Sandbox
```bash
# Install Docker sandbox
pip install docker
cp pocketportal_enhancements/security/docker_sandbox.py security/
python security/docker_sandbox.py  # Build image

# Test for a week, monitor security
```

---

## 🐛 Rollback Procedure

If something goes wrong:

### Rollback Step 1: Stop Services
```bash
pkill -f "python.*interface"
```

### Rollback Step 2: Restore Backup
```bash
cd ~
tar -xzf backup_*.tar.gz
cd your-project
```

### Rollback Step 3: Restore Knowledge Base
```bash
cp -r ~/.telegram_agent/knowledge_base.backup/* ~/.telegram_agent/knowledge_base/
```

### Rollback Step 4: Restart Services
```bash
source venv/bin/activate
python interfaces/telegram_interface.py
```

---

## ✅ Post-Migration Checklist

- [ ] All tests passed
- [ ] Telegram bot responds
- [ ] Inline keyboards work
- [ ] Knowledge base searches are faster
- [ ] Docker sandbox executes code
- [ ] No errors in logs
- [ ] Users can interact normally
- [ ] Backup is safe
- [ ] Performance improved

---

## 📊 Validation

### Performance Validation

**Knowledge Base:**
```bash
python << 'EOF'
import asyncio
import time
from telegram_agent_tools.knowledge_tools.knowledge_base_sqlite import EnhancedKnowledgeTool

async def benchmark():
    tool = EnhancedKnowledgeTool()
    
    # Benchmark search
    start = time.time()
    result = await tool.execute({
        "action": "search",
        "query": "test",
        "limit": 10
    })
    elapsed = time.time() - start
    
    print(f"Search time: {elapsed:.3f}s")
    print(f"Expected: <0.200s for 100+ docs")
    
    if elapsed < 0.2:
        print("✅ Performance excellent")
    elif elapsed < 0.5:
        print("⚠️  Performance acceptable")
    else:
        print("❌ Performance poor - check indexes")

asyncio.run(benchmark())
EOF
```

**Docker Sandbox:**
```bash
python << 'EOF'
import asyncio
import time
from security.docker_sandbox import DockerPythonSandbox

async def benchmark():
    sandbox = DockerPythonSandbox()
    
    # Warmup
    await sandbox.execute_code("print('warmup')")
    
    # Benchmark
    times = []
    for i in range(5):
        start = time.time()
        await sandbox.execute_code("print('test')")
        times.append(time.time() - start)
    
    avg = sum(times) / len(times)
    print(f"Avg execution time: {avg:.3f}s")
    print(f"Expected: <1.0s")
    
    if avg < 1.0:
        print("✅ Performance excellent")
    else:
        print("⚠️  Performance slow - check Docker")
    
    sandbox.cleanup()

asyncio.run(benchmark())
EOF
```

---

## 📝 Summary

**Migration Complete!**

You now have:
- ✅ SQLite knowledge base (10-100x faster)
- ✅ Telegram inline keyboards (better UX)
- ✅ Docker sandbox (secure execution)

**Total time:** 60-90 minutes  
**Downtime:** ~10 minutes  
**Risk level:** Low (full backup + rollback plan)

**Next steps:**
1. Monitor performance for 24-48 hours
2. Collect user feedback
3. Optimize based on usage patterns
4. Celebrate! 🎉
