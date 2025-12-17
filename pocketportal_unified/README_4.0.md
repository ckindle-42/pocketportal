# PocketPortal 4.0 - Unified Modular Architecture

**The truly interface-agnostic AI agent platform**

## 🎯 What Changed in 4.0

PocketPortal 4.0 represents a fundamental architectural shift from "Telegram-first" to **"Core-first, Interface-agnostic"**. The core is now completely decoupled from any specific interface, making it trivial to add new interfaces (Web, Slack, Discord, API, CLI, etc.) without touching the core logic.

### Executive Summary

```
Before (3.x):  Telegram Bot → [Monolithic Logic]
After (4.0):   Any Interface → Security → AgentCore → Router → LLM
                                             ├─ ContextManager
                                             ├─ EventBus
                                             └─ PromptManager
```

## ✨ Key Improvements

### 1. ✅ Dependency Injection
**Before:**
```python
class AgentCore:
    def __init__(self, config):
        self.model_registry = ModelRegistry()  # Hard to test!
        self.router = IntelligentRouter(...)
```

**After:**
```python
class AgentCoreV2:
    def __init__(self, model_registry, router, execution_engine, ...):
        self.model_registry = model_registry  # Injected! Easy to mock!
        self.router = router
```

**Benefit:** Easy unit testing with mock dependencies. No more loading heavy LLMs in tests.

---

### 2. ✅ Structured Error Handling
**Before:**
```python
return ProcessingResult(
    success=False,
    response=f"⚠️ Error: {str(e)}"  # String error!
)
```

**After:**
```python
raise RateLimitError(
    "Rate limit exceeded",
    retry_after=60,
    details={'user_id': 123}
)
```

**Benefit:** Interfaces can handle errors appropriately. Web UI shows red toast, Telegram shows message, API returns proper status code.

---

### 3. ✅ Externalized Prompts
**Before:**
```python
base_prompt = (
    "You are a helpful AI assistant..."  # Hardcoded!
)
```

**After:**
```python
# prompts/base_system.md
base_prompt = prompt_manager.load_template('base_system')
```

**Benefit:** Change prompts without redeploying. Hot-reload in production.

---

### 4. ✅ SQLite Rate Limiting
**Before:**
```python
# JSON file with potential race conditions
self.requests: Dict[int, List[float]] = defaultdict(list)
```

**After:**
```python
# SQLite with ACID guarantees
with conn.execute("BEGIN IMMEDIATE"):  # Proper locking!
    conn.execute("INSERT INTO rate_limit_requests...")
```

**Benefit:** No race conditions under concurrent load. Proper transaction isolation.

---

### 5. ✅ Context Management
**Before:**
- Each interface managed its own context
- No history sharing between Telegram and Web

**After:**
```python
# Unified context across ALL interfaces
context_manager.get_history(chat_id="user_123")
# Works whether from Telegram, Web, or Slack!
```

**Benefit:** Seamless experience when switching interfaces. Conversation continues.

---

### 6. ✅ Event Bus for Real-Time Feedback
**Before:**
- Request → Wait → Response (no intermediate feedback)

**After:**
```python
await event_bus.publish(EventType.TOOL_STARTED, chat_id, {'tool': 'git_status'})
# Telegram shows: "🔧 Running git tool..."
# Web shows: Spinner on git icon
```

**Benefit:** Better UX with intermediate feedback. Users know what's happening.

---

### 7. ✅ Security Middleware
**Before:**
```python
# Security checks scattered throughout code
sanitized, warnings = input_sanitizer.sanitize(message)
# Core processes message
```

**After:**
```python
Interface → SecurityMiddleware → AgentCore
            ↓ (no bypass path!)
            Sanitize + Rate Limit + Validate
```

**Benefit:** No data reaches core without passing security. Single enforcement point.

---

### 8. ✅ Structured Logging with Trace IDs
**Before:**
```
INFO: Processing message
INFO: Selected model qwen2.5-7b
INFO: Execution completed
# Where did this request go? 🤷
```

**After:**
```json
{"trace_id": "a3f8", "component": "AgentCore", "message": "Processing message"}
{"trace_id": "a3f8", "component": "Router", "message": "Selected qwen2.5-7b"}
{"trace_id": "a3f8", "component": "ExecutionEngine", "message": "Completed"}
```

**Benefit:** Follow a single request through the entire system. Debug complex failures easily.

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    INTERFACE LAYER                      │
│  (Telegram, Web, Slack, API, CLI)                      │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│                  SECURITY MIDDLEWARE                     │
│  • Rate Limiting                                        │
│  • Input Sanitization                                   │
│  • Policy Enforcement                                   │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│                    AGENT CORE V2                        │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐ │
│  │  Context    │  │   Event      │  │    Prompt     │ │
│  │  Manager    │  │   Bus        │  │    Manager    │ │
│  └─────────────┘  └──────────────┘  └───────────────┘ │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│                  ROUTING & EXECUTION                     │
│  • Intelligent Router                                   │
│  • Circuit Breaker                                      │
│  • Model Backends (Ollama, LMStudio, MLX)              │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│                      TOOLS LAYER                        │
│  (11+ tools: Git, Docker, Web, Data, System...)        │
└─────────────────────────────────────────────────────────┘
```

## 📦 Core Components

### AgentCoreV2
The brain. Orchestrates everything. Interface-agnostic.

```python
from pocketportal_unified.core import create_agent_core

config = {
    'ollama_base_url': 'http://localhost:11434',
    'routing_strategy': 'AUTO',
    'model_preferences': {...}
}

agent_core = create_agent_core(config)
```

### SecurityMiddleware
The protective wrapper. Nothing reaches core without validation.

```python
from pocketportal_unified.core import SecurityMiddleware
from security.sqlite_rate_limiter import SQLiteRateLimiter

rate_limiter = SQLiteRateLimiter(max_requests=30, window_seconds=60)
secure_core = SecurityMiddleware(
    agent_core,
    rate_limiter=rate_limiter,
    enable_rate_limiting=True,
    enable_input_sanitization=True
)
```

### ContextManager
Unified conversation history across all interfaces.

```python
from pocketportal_unified.core import ContextManager

context_manager = ContextManager(max_context_messages=50)

# User switches from Telegram to Web
context_manager.get_history("user_123")  # Same history!
```

### EventBus
Real-time event system for intermediate feedback.

```python
from pocketportal_unified.core import EventBus, EventType

event_bus = EventBus()

async def on_tool_started(event):
    print(f"Tool started: {event.data['tool']}")

event_bus.subscribe(EventType.TOOL_STARTED, on_tool_started)
```

### PromptManager
External prompt templates. No more hardcoded strings.

```python
from pocketportal_unified.core import PromptManager

prompt_manager = PromptManager()
system_prompt = prompt_manager.build_system_prompt(
    interface='telegram',
    user_preferences={'verbose': True}
)
```

## 🚀 Quick Start

### 1. Using the Unified Core Directly

```python
import asyncio
from pocketportal_unified.core import create_agent_core, SecurityMiddleware

async def main():
    # Create core
    config = {
        'ollama_base_url': 'http://localhost:11434',
        'routing_strategy': 'AUTO'
    }
    agent_core = create_agent_core(config)

    # Wrap with security
    secure_core = SecurityMiddleware(agent_core)

    # Process message
    result = await secure_core.process_message(
        chat_id="user_123",
        message="Hello! What tools do you have?",
        interface="cli"
    )

    print(result.response)

asyncio.run(main())
```

### 2. Creating a New Interface

**Example: Slack Interface**

```python
from pocketportal_unified.core import create_agent_core, SecurityMiddleware

class SlackInterface:
    def __init__(self):
        # Create core
        agent_core = create_agent_core(config)
        self.secure_core = SecurityMiddleware(agent_core)

    async def handle_message(self, slack_message):
        # Map Slack format to core format
        result = await self.secure_core.process_message(
            chat_id=f"slack_{slack_message.user_id}",
            message=slack_message.text,
            interface="slack"
        )

        # Map core response back to Slack format
        await slack_client.send_message(result.response)
```

**That's it!** The core handles:
- Routing
- Model selection
- Tool execution
- Context management
- Security
- Logging

You just map your interface's format to/from the core.

## 🔧 Migration from 3.x to 4.0

### For Telegram Users

**Old way (telegram_agent_v3.py):**
```python
# Monolithic file with everything mixed in
```

**New way (telegram_interface.py):**
```python
from pocketportal_unified.core import create_agent_core, SecurityMiddleware

class TelegramInterface:
    def __init__(self):
        agent_core = create_agent_core(config)
        self.secure_core = SecurityMiddleware(agent_core)

    async def handle_message(self, update, context):
        result = await self.secure_core.process_message(...)
        await update.message.reply_text(result.response)
```

### Adding New Models

Just update the model registry! The routing system automatically uses them.

```python
# In routing/model_registry.py
self.register(ModelMetadata(
    model_id="ollama_custom_model",
    backend="ollama",
    display_name="My Custom Model",
    capabilities=[ModelCapability.GENERAL, ModelCapability.CODE],
    ...
))
```

### Custom Prompts

Edit files in `pocketportal_unified/prompts/`:
- `base_system.md` - Base prompt for all interfaces
- `telegram_interface.md` - Telegram-specific additions
- `web_interface.md` - Web-specific additions
- `preferences/verbose.md` - Verbose mode prompt
- `preferences/terse.md` - Terse mode prompt

Changes take effect immediately (cache TTL: 5 minutes).

## 📊 Monitoring & Observability

### Structured Logs

All logs are JSON with trace IDs:

```json
{
  "timestamp": "2025-12-17T10:30:45",
  "level": "INFO",
  "trace_id": "a3f8",
  "component": "AgentCore",
  "message": "Processing message",
  "chat_id": "telegram_123",
  "interface": "telegram"
}
```

**Query by trace ID:**
```python
from pocketportal_unified.core import LogParser

entries = LogParser.parse_log_file('logs/pocketportal.log')
timeline = LogParser.get_trace_timeline(entries, 'a3f8')
print(timeline)
```

### Event History

```python
# Get recent events
events = event_bus.get_event_history(chat_id="user_123", limit=50)

# Get stats
stats = event_bus.get_stats()
print(stats['total_events'])
print(stats['event_counts'])
```

### Circuit Breaker Status

```python
# Check backend health
status = execution_engine.get_circuit_breaker_status()

# Example output:
# {
#     'ollama': {'state': 'closed', 'failure_count': 0},
#     'lmstudio': {'state': 'open', 'failure_count': 3}  # Failed!
# }

# Manually reset
execution_engine.reset_circuit_breaker('ollama')
```

## 🧪 Testing

### Unit Tests (Easy with Dependency Injection!)

```python
from unittest.mock import Mock
from pocketportal_unified.core import AgentCoreV2

def test_agent_core():
    # Create mock dependencies
    mock_registry = Mock()
    mock_router = Mock()
    mock_engine = Mock()
    mock_context = Mock()
    mock_events = Mock()
    mock_prompts = Mock()

    # Inject mocks
    core = AgentCoreV2(
        model_registry=mock_registry,
        router=mock_router,
        execution_engine=mock_engine,
        context_manager=mock_context,
        event_bus=mock_events,
        prompt_manager=mock_prompts,
        config={}
    )

    # Test without loading any real LLMs!
    assert core.model_registry == mock_registry
```

## 📈 Performance Considerations

### Context Window Management

The ContextManager limits messages to avoid overwhelming LLMs:

```python
context_manager = ContextManager(max_context_messages=50)
# Only last 50 messages included in context
```

### Event Bus

Events are non-blocking. Failed subscribers don't affect others:

```python
# Subscriber 1 fails → Subscriber 2 still gets event
event_bus.subscribe(EventType.TOOL_STARTED, faulty_callback)
event_bus.subscribe(EventType.TOOL_STARTED, good_callback)
```

### Rate Limiting

SQLite WAL mode allows concurrent reads:

```python
rate_limiter = SQLiteRateLimiter(...)
# Multiple interfaces can check limits simultaneously
```

## 🔐 Security

### Defense in Depth

1. **SecurityMiddleware** - First line of defense
2. **InputSanitizer** - Detects dangerous patterns
3. **RateLimiter** - Prevents abuse
4. **Tool Confirmation** - Critical tools require approval

### Custom Security Policies

Add your own in `SecurityMiddleware._validate_security_policies()`:

```python
async def _validate_security_policies(self, sec_ctx):
    # Example: Block messages containing certain keywords
    if 'forbidden_word' in sec_ctx.sanitized_input:
        raise PolicyViolationError("Forbidden content")
```

## 🎓 Best Practices

### 1. Always Use SecurityMiddleware

```python
# ✅ Good
secure_core = SecurityMiddleware(agent_core)
result = await secure_core.process_message(...)

# ❌ Bad
result = await agent_core.process_message(...)  # No security!
```

### 2. Use Trace Context

```python
# ✅ Good
from pocketportal_unified.core import TraceContext

with TraceContext() as trace_id:
    result = await secure_core.process_message(...)
    # All logs have the same trace_id!
```

### 3. Subscribe to Events for UX

```python
# Show users what's happening
async def on_tool_started(event):
    await send_message(f"🔧 Using {event.data['tool']}...")

event_bus.subscribe(EventType.TOOL_STARTED, on_tool_started)
```

### 4. Clean Up Old Data

```python
# Periodic cleanup (e.g., daily cron job)
context_manager.cleanup_old_conversations(days_to_keep=30)
rate_limiter.cleanup_old_data(days_to_keep=7)
```

## 🚧 Roadmap

- [ ] Hot-reloading configuration (no restart needed)
- [ ] Interface Registry (single main.py for all interfaces)
- [ ] Metrics export (Prometheus/Grafana integration)
- [ ] Admin interface (manage users, rate limits, models)
- [ ] Multi-tenancy support
- [ ] Cloud backend support (OpenAI, Anthropic, etc.)

## 📝 License

MIT License - See LICENSE file

## 🤝 Contributing

Contributions welcome! The modular architecture makes it easy to:
- Add new interfaces
- Add new model backends
- Add new tools
- Improve security
- Enhance monitoring

## 📞 Support

- Issues: GitHub Issues
- Docs: `/docs` directory
- Architecture: This README

---

**PocketPortal 4.0** - *Truly modular. Truly production-ready.*
