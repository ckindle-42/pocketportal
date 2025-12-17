# Part 5: Testing & Production Deployment

**What You'll Build:** Test Suite + Production Deployment  
**Time Required:** 1 hour  
**Difficulty:** Medium  
**Prerequisites:** Part 4 complete (agent working)

---

## ðŸŽ¯ Overview

This part ensures your agent is production-ready:

- **Comprehensive Testing** - Verify all components work
- **Auto-start Setup** - Agent starts on boot
- **Monitoring** - Health checks and logging
- **Backup Strategy** - Protect your data

---

## ðŸ§ª Part 5A: Testing Suite

### Test 1: Component Tests

**File: `tests/test_components.py`**

```bash
mkdir -p tests

cat > tests/test_components.py << 'ENDOFFILE'
#!/usr/bin/env python3
"""Component Tests"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

async def test_routing():
    """Test routing system"""
    print("\nðŸ§ª Testing Routing System...")
    
    from routing import ModelRegistry, IntelligentRouter, ExecutionEngine, RoutingStrategy
    
    registry = ModelRegistry()
    router = IntelligentRouter(registry, RoutingStrategy.AUTO)
    
    config = {'ollama_base_url': 'http://localhost:11434'}
    engine = ExecutionEngine(registry, router, config)
    
    # Test query
    result = await engine.execute("Hello")
    
    assert result.success, "Routing execution failed"
    assert result.execution_time < 5.0, "Response too slow"
    print(f"âœ… Routing: {result.execution_time:.2f}s")
    

async def test_tools():
    """Test tool registry"""
    print("\nðŸ§ª Testing Tool Registry...")
    
    from telegram_agent_tools import registry
    
    loaded, failed = registry.discover_and_load()
    
    assert loaded == 11, f"Expected 11 tools, got {loaded}"
    assert failed == 0, f"Tool loading failed: {failed} errors"
    print(f"âœ… Tools: {loaded}/11 loaded")


async def test_tool_execution():
    """Test individual tool"""
    print("\nðŸ§ª Testing Tool Execution...")
    
    from telegram_agent_tools import registry
    registry.discover_and_load()
    
    # Test QR generator
    qr_tool = registry.get_tool('qr_generate')
    result = await qr_tool.execute({
        'content': 'https://github.com',
        'qr_type': 'url'
    })
    
    assert result['success'], f"Tool execution failed: {result.get('error')}"
    print(f"âœ… Tool execution: QR code generated")


async def main():
    """Run all tests"""
    print("="*60)
    print("Component Test Suite")
    print("="*60)
    
    tests = [
        test_routing,
        test_tools,
        test_tool_execution
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            await test()
            passed += 1
        except Exception as e:
            print(f"âŒ Test failed: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*60)
    
    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
ENDOFFILE

chmod +x tests/test_components.py
```

### Test 2: Integration Tests

**File: `tests/test_integration.py`**

```bash
cat > tests/test_integration.py << 'ENDOFFILE'
#!/usr/bin/env python3
"""Integration Tests"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

async def test_end_to_end():
    """Test complete message flow"""
    print("\nðŸ§ª Testing End-to-End Flow...")
    
    from routing import ModelRegistry, IntelligentRouter, ExecutionEngine, RoutingStrategy
    from telegram_agent_tools import registry
    
    # Setup
    model_registry = ModelRegistry()
    router = IntelligentRouter(model_registry, RoutingStrategy.AUTO)
    config = {'ollama_base_url': 'http://localhost:11434'}
    engine = ExecutionEngine(model_registry, router, config)
    
    # Load tools
    registry.discover_and_load()
    
    # Test query
    result = await engine.execute(
        "What is 2+2?",
        system_prompt="You are a helpful assistant."
    )
    
    assert result.success, "Execution failed"
    assert len(result.response) > 0, "Empty response"
    print(f"âœ… End-to-end: Response received ({len(result.response)} chars)")


async def test_performance():
    """Test performance benchmarks"""
    print("\nðŸ§ª Testing Performance...")
    
    from routing import ModelRegistry, IntelligentRouter, ExecutionEngine, RoutingStrategy
    import time
    
    registry = ModelRegistry()
    router = IntelligentRouter(registry, RoutingStrategy.SPEED)
    config = {'ollama_base_url': 'http://localhost:11434'}
    engine = ExecutionEngine(registry, router, config)
    
    # Benchmark
    start = time.time()
    result = await engine.execute("Hi")
    elapsed = time.time() - start
    
    assert elapsed < 2.0, f"Too slow: {elapsed:.2f}s"
    print(f"âœ… Performance: {elapsed:.2f}s (target: <2s)")


async def main():
    """Run integration tests"""
    print("="*60)
    print("Integration Test Suite")
    print("="*60)
    
    tests = [
        test_end_to_end,
        test_performance
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            await test()
            passed += 1
        except Exception as e:
            print(f"âŒ Test failed: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*60)
    
    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
ENDOFFILE

chmod +x tests/test_integration.py
```

### Run All Tests

```bash
cd ~/telegram-agent

# Run component tests
python3 tests/test_components.py

# Run integration tests
python3 tests/test_integration.py
```

---

## ðŸš€ Part 5B: Production Deployment

### Step 1: Create LaunchAgent (Auto-start on Boot)

**File: `~/Library/LaunchAgents/com.telegram.agent.plist`**

```bash
cat > ~/Library/LaunchAgents/com.telegram.agent.plist << 'ENDOFFILE'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.telegram.agent</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/Users/YOUR_USERNAME/telegram-agent/venv/bin/python3</string>
        <string>/Users/YOUR_USERNAME/telegram-agent/telegram_agent_v3.py</string>
    </array>
    
    <key>WorkingDirectory</key>
    <string>/Users/YOUR_USERNAME/telegram-agent</string>
    
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>
    
    <key>StandardOutPath</key>
    <string>/Users/YOUR_USERNAME/telegram-agent/logs/agent.out.log</string>
    
    <key>StandardErrorPath</key>
    <string>/Users/YOUR_USERNAME/telegram-agent/logs/agent.err.log</string>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>
    
    <key>ThrottleInterval</key>
    <integer>60</integer>
</dict>
</plist>
ENDOFFILE
```

**Important:** Replace `YOUR_USERNAME` with your actual macOS username!

### Step 2: Load LaunchAgent

```bash
# Load the agent
launchctl load ~/Library/LaunchAgents/com.telegram.agent.plist

# Verify it's running
launchctl list | grep telegram.agent

# Check logs
tail -f ~/telegram-agent/logs/agent.out.log
```

### Step 3: Control Commands

```bash
# Stop agent
launchctl unload ~/Library/LaunchAgents/com.telegram.agent.plist

# Start agent
launchctl load ~/Library/LaunchAgents/com.telegram.agent.plist

# Restart agent
launchctl unload ~/Library/LaunchAgents/com.telegram.agent.plist
launchctl load ~/Library/LaunchAgents/com.telegram.agent.plist
```

### Step 4: Health Monitoring

**File: `health_check.sh`**

```bash
cat > health_check.sh << 'ENDOFFILE'
#!/bin/bash

echo "ðŸ¥ Health Check"
echo "==============="

# Check if agent is running
if launchctl list | grep -q telegram.agent; then
    echo "âœ… Agent is running"
else
    echo "âŒ Agent is not running"
    exit 1
fi

# Check Ollama
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "âœ… Ollama is running"
else
    echo "âŒ Ollama is not running"
    exit 1
fi

# Check logs for errors
ERROR_COUNT=$(tail -100 ~/telegram-agent/logs/agent.err.log 2>/dev/null | wc -l)
if [ $ERROR_COUNT -gt 10 ]; then
    echo "âš ï¸  Warning: $ERROR_COUNT recent errors"
else
    echo "âœ… No recent errors"
fi

# Check disk space
DISK_USAGE=$(df -h ~ | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 90 ]; then
    echo "âš ï¸  Warning: Disk usage at ${DISK_USAGE}%"
else
    echo "âœ… Disk usage OK (${DISK_USAGE}%)"
fi

echo ""
echo "ðŸ“Š System Stats:"
echo "  Uptime: $(uptime | awk '{print $3, $4}')"
echo "  Memory: $(vm_stat | grep free | awk '{print $3}' | sed 's/\.//')KB free"

echo ""
echo "âœ… Health check complete"
ENDOFFILE

chmod +x health_check.sh
```

### Step 5: Backup Strategy

**File: `backup.sh`**

```bash
cat > backup.sh << 'ENDOFFILE'
#!/bin/bash

BACKUP_DIR=~/telegram-agent-backups
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="telegram_agent_backup_${DATE}.tar.gz"

echo "ðŸ’¾ Creating backup..."

# Create backup directory
mkdir -p $BACKUP_DIR

# Create backup
cd ~/telegram-agent
tar -czf "$BACKUP_DIR/$BACKUP_FILE" \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='logs/*.log' \
    --exclude='browser_data' \
    .

echo "âœ… Backup created: $BACKUP_FILE"
echo "   Size: $(du -h "$BACKUP_DIR/$BACKUP_FILE" | cut -f1)"

# Keep only last 7 backups
cd $BACKUP_DIR
ls -t telegram_agent_backup_* | tail -n +8 | xargs rm -f 2>/dev/null

echo "âœ… Backup complete"
ENDOFFILE

chmod +x backup.sh
```

### Step 6: Monitoring Dashboard

Create a simple status dashboard:

**File: `status.sh`**

```bash
cat > status.sh << 'ENDOFFILE'
#!/bin/bash

clear
echo "â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—"
echo "â•‘     Telegram AI Agent - Status Dashboard          â•‘"
echo "â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•"
echo ""

# Agent Status
if launchctl list | grep -q telegram.agent; then
    echo "ðŸ¤– Agent:      âœ… Running"
else
    echo "ðŸ¤– Agent:      âŒ Stopped"
fi

# Ollama Status
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "ðŸ§  Ollama:     âœ… Running"
else
    echo "ðŸ§  Ollama:     âŒ Stopped"
fi

# Tool Count
TOOL_COUNT=$(python3 -c "from telegram_agent_tools import registry; loaded, _ = registry.discover_and_load(); print(loaded)" 2>/dev/null)
echo "ðŸ”§ Tools:      $TOOL_COUNT loaded"

# Recent Activity
if [ -f ~/telegram-agent/logs/agent.out.log ]; then
    LAST_ACTIVITY=$(tail -1 ~/telegram-agent/logs/agent.out.log 2>/dev/null)
    echo "ðŸ“ Last Log:   ${LAST_ACTIVITY:0:50}..."
fi

# Uptime
if [ -f ~/telegram-agent/logs/agent.out.log ]; then
    START_TIME=$(stat -f %B ~/telegram-agent/logs/agent.out.log)
    CURRENT_TIME=$(date +%s)
    UPTIME=$((CURRENT_TIME - START_TIME))
    HOURS=$((UPTIME / 3600))
    echo "â±ï¸  Uptime:     ${HOURS}h"
fi

echo ""
echo "Press Ctrl+C to exit, or wait 30s for refresh..."
sleep 30
exec "$0"
ENDOFFILE

chmod +x status.sh
```

---

## âœ… Deployment Checklist

Before going to production:

- [ ] All tests pass (`tests/test_*.py`)
- [ ] LaunchAgent configured and loaded
- [ ] Health check script runs successfully
- [ ] Backup script tested
- [ ] Logs directory created with proper permissions
- [ ] `.env` file secured (chmod 600)
- [ ] Telegram bot token valid
- [ ] Authorized user ID correct
- [ ] Ollama models downloaded
- [ ] At least 50GB free disk space

**Run complete verification:**

```bash
cd ~/telegram-agent

# Run tests
python3 tests/test_components.py && python3 tests/test_integration.py

# Health check
./health_check.sh

# Create first backup
./backup.sh

# Start monitoring
./status.sh
```

---

## ðŸ“Š Monitoring & Maintenance

### Daily Tasks
- Check `./status.sh` for system health
- Review error logs if issues reported
- Test basic Telegram interactions

### Weekly Tasks
- Run `./backup.sh` to create backup
- Review `~/telegram-agent/logs/` for patterns
- Update Ollama models if needed
- Check disk space usage

### Monthly Tasks
- Full system test with all tools
- Review and rotate old logs
- Update dependencies: `pip install --upgrade -r requirements.txt`
- Test backup restoration

---

## ðŸ”§ Troubleshooting Production Issues

**Agent not starting:**
```bash
# Check LaunchAgent status
launchctl list | grep telegram

# View error log
tail -50 ~/telegram-agent/logs/agent.err.log

# Manually test
cd ~/telegram-agent
source venv/bin/activate
python3 telegram_agent_v3.py
```

**High memory usage:**
```bash
# Check process
ps aux | grep telegram_agent

# Restart agent
launchctl unload ~/Library/LaunchAgents/com.telegram.agent.plist
launchctl load ~/Library/LaunchAgents/com.telegram.agent.plist
```

**Bot not responding:**
```bash
# Check Ollama
curl http://localhost:11434/api/tags

# Check bot token
grep TELEGRAM_BOT_TOKEN ~/telegram-agent/.env

# Test bot directly
python3 << 'EOF'
from telegram import Bot
import os
from dotenv import load_dotenv

load_dotenv()
bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
print(bot.get_me())
EOF
```

---

## ðŸŽ‰ Part 5 Complete!

Your agent is now:
- âœ… Fully tested
- âœ… Auto-starts on boot
- âœ… Monitored and logged
- âœ… Backed up regularly
- âœ… Production-ready!

**System Stats:**
- **Total Lines of Code:** ~7,500
- **Tools Implemented:** 11
- **Test Coverage:** Component + Integration
- **Uptime Target:** 99.9%

---

## ðŸ“ˆ What's Next

**Optional: Part 6 - MCP Integration**

Add 400+ service connectors:
- Google Drive, Gmail, Calendar
- GitHub, GitLab
- Slack, Discord
- Notion, Airtable
- And 390+ more!

**Or: Customize Your Agent**

- Add more tools
- Create custom models
- Integrate with other services
- Build automation workflows

---

**Part 5 Complete!** âœ…

**Your Telegram AI Agent is now in production!** ðŸš€

The agent runs 24/7, handles your requests intelligently, and provides comprehensive tooling - all while keeping your data 100% local and private.
