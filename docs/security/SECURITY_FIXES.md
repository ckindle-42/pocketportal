# PocketPortal Security & Critical Fixes

**Canonical Source** — This is the single source of truth for all security fixes and critical improvements in PocketPortal.

**Last Updated:** 2025-12-18
**Current Version:** 4.7.4
**Status:** All fixes implemented and verified

---

## Table of Contents

1. [Current Architecture Fixes (v4.x)](#current-architecture-fixes-v4x)
2. [Historical Fixes (v3.x Legacy)](#historical-fixes-v3x-legacy)
3. [Testing & Verification](#testing--verification)
4. [Security Principles](#security-principles)

---

## Current Architecture Fixes (v4.x)

These fixes apply to the current modular, interface-agnostic PocketPortal architecture (v4.0+).

### 1. Data Corruption Risk Fix (Atomic Writes)

**Applicable:** v4.x modular architecture
**Files:** Knowledge base and persistent storage components

#### Problem
The knowledge base was using direct file writes with `json.dump()`, which could lead to:
- **Data corruption** if the process crashed during write
- **Race conditions** with concurrent writes
- **Complete data loss** in case of power failure during save

#### Solution
Implemented atomic write pattern with the following protections:

1. **Atomic Writes**: Write to temporary file first, then atomic rename
   ```python
   # Write to temp file
   temp_fd, temp_path = tempfile.mkstemp(...)
   # Write data with fsync
   # Atomic rename (guaranteed by OS)
   shutil.move(temp_path, self.DB_PATH)
   ```

2. **File Locking**: Prevents concurrent write conflicts
   ```python
   fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
   ```

3. **Automatic Backup**: Creates backup before each write
   - Enables recovery if something goes wrong
   - Located at `{DB_PATH}.backup`

4. **Crash Recovery**: Automatically restores from backup on failure

#### Impact
- ✅ Zero data loss even if process crashes mid-write
- ✅ No race conditions with concurrent access
- ✅ Automatic recovery from failures

#### Files Changed
- `src/pocketportal/tools/knowledge_tools/local_knowledge.py`

---

### 2. Persistent Rate Limiting

**Applicable:** v4.x modular architecture
**Files:** `src/pocketportal/security/`

#### Problem
Rate limiter stored data in memory, which reset on every restart:
- **Security vulnerability**: Malicious users could bypass rate limits by forcing restarts
- **No abuse tracking**: Violation history lost on restart
- **Easy to exploit**: Simple crash triggers full quota reset

#### Solution
Implemented persistent storage for rate limit data:

1. **Disk Persistence**: Rate limit data saved to disk
   ```python
   self.persist_path = Path('data/rate_limits.json')
   self._save_state()  # Called after each check
   ```

2. **Atomic Writes**: Same atomic write pattern as knowledge base
   - No corruption risk
   - Safe concurrent access

3. **Automatic Loading**: State restored on startup
   ```python
   def __init__(self, ...):
       self._load_state()  # Load existing limits
   ```

4. **Old Data Cleanup**: Expired requests automatically removed

#### Impact
- ✅ Rate limits survive restarts (prevents bypass attacks)
- ✅ Violation tracking persists
- ✅ Malicious users cannot reset quotas by crashing the bot

#### Files Changed
- `src/pocketportal/security/rate_limiter.py`

---

### 3. Circuit Breaker Pattern (LLM Reliability)

**Applicable:** v4.x modular architecture
**Version:** Introduced in v4.6.0
**Files:** `src/pocketportal/routing/execution_engine.py`

#### Problem
When a backend (e.g., Ollama) failed, the system would:
- **Repeatedly retry** the same failing backend
- **Waste time** waiting for timeouts
- **No failover strategy** for persistent failures
- **Poor user experience** with slow responses

#### Solution
Implemented circuit breaker pattern:

1. **Failure Tracking**: Monitors backend health
   ```python
   class CircuitState:
       CLOSED      # Normal operation
       OPEN        # Too many failures, reject requests
       HALF_OPEN   # Testing recovery
   ```

2. **Automatic Failover**: After 3 failures, circuit opens
   - Blocks requests for 60 seconds
   - Prevents hammering failed backend
   - Falls back to other backends immediately

3. **Smart Recovery**: Half-open state for testing
   ```python
   # After timeout, allow 1 test request
   # If success → Close circuit
   # If failure → Reopen circuit
   ```

4. **Health Monitoring**: Expose circuit state via health check
   ```python
   await engine.health_check()
   # Returns: {
   #   'ollama': {
   #     'available': False,
   #     'circuit_state': 'open',
   #     'failure_count': 5
   #   }
   # }
   ```

#### Impact
- ✅ No wasted time on failing backends
- ✅ Automatic recovery when backend comes back
- ✅ Better user experience (faster failures)
- ✅ Resource efficiency (no timeout wastage)

#### Configuration
```python
# In config dict or settings:
config = {
    'circuit_breaker_threshold': 3,       # Failures before opening
    'circuit_breaker_timeout': 60,        # Seconds before retry
    'circuit_breaker_half_open_calls': 1  # Test calls in half-open
}
```

#### Monitoring
```python
# Get detailed status
status = engine.get_circuit_breaker_status()

# Manually reset if needed
engine.reset_circuit_breaker('ollama')
```

---

### 4. Input Sanitization (v4.x)

**Applicable:** v4.x modular architecture
**Files:** `src/pocketportal/security/input_sanitizer.py`

#### Protections Implemented
- ✅ Path traversal prevention (`../../../etc/passwd`)
- ✅ Dangerous command detection (`rm -rf /`, `dd`, etc.)
- ✅ SQL injection prevention (`DROP TABLE`, `DELETE FROM`)
- ✅ XSS prevention in responses (`<script>`, `onclick=`)

#### Integration
All user input is sanitized before execution:
```python
# Security: Sanitize user input before execution
sanitized_query, warnings = self.input_sanitizer.sanitize_command(user_message)

if warnings:
    logger.warning(f"Security warnings: {warnings}")
    await interface.send_warning(warnings)

result = await engine.execute(query=sanitized_query)
```

---

## Historical Fixes (v3.x Legacy)

These fixes were applied to the legacy v3.x monolithic architecture. They are documented here for historical reference only. **The v3.x architecture has been completely replaced by v4.x.**

### v3.x Critical Security Issue (December 2025)

**⚠️ Historical Reference Only — v3.x is deprecated**

#### 🔴 CRITICAL: Security Module Not Integrated (v3.0.0)

**Issue:** Input sanitization module was initialized but never called in v3.x
**Severity:** HIGH
**Impact:** User messages passed directly to execution without sanitization

**v3.x Vulnerable Code (Fixed in v3.0.1):**
```python
# BEFORE (VULNERABLE):
result = await self.execution_engine.execute(
    query=user_message,  # ❌ Unsanitized input!
    system_prompt=self._build_system_prompt()
)

# AFTER (SECURE):
sanitized_query, warnings = self.input_sanitizer.sanitize_command(user_message)
result = await self.execution_engine.execute(
    query=sanitized_query,  # ✅ Sanitized input
    system_prompt=self._build_system_prompt()
)
```

**Resolution:** Fixed in v3.0.1, then superseded by v4.x modular architecture

---

### v3.x Code Quality Fixes

**⚠️ Historical Reference Only — v3.x is deprecated**

#### Missing Import in `local_knowledge.py` (v3.x)
- **Issue:** Missing `from datetime import datetime`
- **Impact:** Potential runtime errors
- **Status:** Fixed in v3.0.1, refactored in v4.x

#### Hardcoded Paths (v3.x)
- **Issue:** Hardcoded `data/knowledge_base.json` ignored `KNOWLEDGE_BASE_DIR`
- **Impact:** Configuration ignored, deployment inflexibility
- **Fix:** Respect environment variables
- **Status:** Fixed in v3.0.1, refactored in v4.x with proper config management

#### Tool Registry (v3.x)
- **Issue:** Manual tool registration, inconsistent naming
- **Fix:** Auto-discovery, validation, statistics
- **Status:** Completely redesigned in v4.x with plugin architecture

---

## Testing & Verification

### Current v4.x Test Suite

Comprehensive test coverage in `tests/`:

#### Data Integrity Tests
```bash
pytest tests/unit/test_data_integrity.py -v
```

**Coverage:**
- ✅ Atomic write backup creation
- ✅ Crash survival testing
- ✅ No partial data corruption
- ✅ Concurrent write safety

#### Security Tests
```bash
pytest tests/unit/test_security.py -v
```

**Coverage:**
- ✅ Input sanitization (path traversal, command injection, SQL injection)
- ✅ Rate limiting persistence across restarts
- ✅ Rate limit bypass prevention
- ✅ XSS prevention

#### Circuit Breaker Tests
```bash
pytest tests/integration/test_circuit_breaker.py -v
```

**Coverage:**
- ✅ Opens after threshold failures
- ✅ Prevents repeated failures
- ✅ Transitions to half-open state
- ✅ Closes on successful recovery

### Manual Security Testing

**Input Sanitization:**
```bash
# Test dangerous patterns (should be blocked/sanitized):
pocketportal test-security "../../../etc/passwd"       # Path traversal
pocketportal test-security "rm -rf /"                  # Dangerous command
pocketportal test-security "DROP TABLE users"          # SQL injection
```

**Rate Limiting:**
```bash
# Send rapid requests (should trigger rate limit):
for i in {1..50}; do pocketportal query "test $i"; done
```

**Circuit Breaker:**
```bash
# Check circuit state:
pocketportal health-check --verbose
```

---

## Performance Impact

All fixes designed for minimal performance overhead:

| Fix | Performance Impact | Notes |
|-----|-------------------|-------|
| Atomic Writes | ~1-2ms overhead | One-time cost per save operation |
| Rate Limiter Persistence | ~0.5-1ms overhead | Amortized across requests |
| Circuit Breaker | <0.1ms overhead | **Reduces** total latency by skipping failures |
| Input Sanitization | ~0.2-0.5ms overhead | Pattern matching on input strings |

**Net Result:** Improved overall performance due to circuit breaker preventing timeout waste

---

## Security Principles

PocketPortal implements defense-in-depth security:

### Before Fixes
- ❌ Data could be lost/corrupted on crash
- ❌ Rate limits could be bypassed via restarts
- ❌ Failed backends caused cascading slowdowns
- ❌ User input not sanitized (v3.x critical issue)

### After Fixes
- ✅ **Data Integrity Guaranteed**: Atomic writes, automatic backups
- ✅ **Rate Limits Enforced**: Persistent across restarts
- ✅ **Failed Backends Isolated**: Circuit breaker auto-recovery
- ✅ **All State Changes Atomic**: No partial updates
- ✅ **Input Sanitization**: Defense against injection attacks
- ✅ **Structured Exception Handling**: Type-safe error management

### Standards Alignment

- **OWASP Top 10**: Addresses A03:2021 (Injection)
- **CWE-78**: Command injection prevention
- **CWE-22**: Path traversal prevention
- **CWE-89**: SQL injection prevention
- **GDPR Compliant**: Local processing, no data leakage
- **POSIX Standards**: Atomic operations for file integrity

---

## Migration Notes

### For v4.x Deployments

All fixes are **automatically integrated** — no manual migration required:

1. **Atomic Writes**: Apply on next save (existing data readable)
2. **Rate Limiter Persistence**: Starts with clean state, persists going forward
3. **Circuit Breaker**: Automatically active in execution engine
4. **Input Sanitization**: Integrated in all interface implementations

### Configuration

**`.env` Settings:**
```bash
# Rate Limiting
RATE_LIMIT_REQUESTS_PER_MINUTE=30
RATE_LIMIT_WINDOW=60
RATE_LIMIT_PERSIST_PATH=data/rate_limits.json

# Circuit Breaker
CIRCUIT_BREAKER_THRESHOLD=3
CIRCUIT_BREAKER_TIMEOUT=60
CIRCUIT_BREAKER_HALF_OPEN_CALLS=1

# Security
ENABLE_INPUT_SANITIZATION=true
SANITIZATION_LOG_WARNINGS=true
```

---

## Future Enhancements

Potential improvements under consideration:

### Knowledge Base
- Write-ahead logging (WAL) for transaction safety
- Incremental backups instead of full copies
- Compression for large datasets

### Rate Limiter
- Distributed rate limiting (Redis backend)
- Per-endpoint and per-tool granularity
- Dynamic limit adjustment based on user reputation

### Circuit Breaker
- OpenTelemetry integration for metrics/alerting
- Adaptive thresholds based on SLA requirements
- Circuit state persistence (survive process restarts)

### Input Sanitization
- Machine learning-based anomaly detection
- Context-aware sanitization rules
- Configurable severity levels per pattern

---

## References & Further Reading

- **Atomic Writes**: [POSIX Atomic Operations](https://pubs.opengroup.org/onlinepubs/9699919799/)
- **Circuit Breaker Pattern**: [Martin Fowler's Circuit Breaker](https://martinfowler.com/bliki/CircuitBreaker.html)
- **Rate Limiting Algorithms**: Token Bucket, Sliding Window, Leaky Bucket
- **OWASP Top 10**: [Injection Prevention](https://owasp.org/Top10/A03_2021-Injection/)
- **Security Best Practices**: [CWE Top 25](https://cwe.mitre.org/top25/)

---

## Related Documentation

- **Architecture Guide**: [docs/architecture.md](../architecture.md)
- **Setup Guide**: [docs/setup.md](../setup.md)
- **Testing Guide**: [docs/TESTING.md](../TESTING.md)
- **Changelog**: [CHANGELOG.md](../../CHANGELOG.md)
- **Migration Guide**: [docs/archive/MIGRATION_TO_4.0.md](../archive/MIGRATION_TO_4.0.md)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| **4.7.4** | 2025-12-18 | Documentation consolidation (this document created as SSOT) |
| **4.6.0** | 2025-12-17 | Circuit breaker pattern implemented |
| **4.5.1** | 2025-12-17 | Interface consolidation, error codes |
| **4.4.1** | 2025-12-17 | Atomic writes, persistent rate limiting |
| **3.0.1** | 2025-12-17 | Security module integration fix (v3.x legacy) |
| **3.0.0** | 2025-12-17 | Initial v3.x release (deprecated, replaced by v4.x) |

---

**Status:** ✅ All fixes implemented and tested
**Governance:** Single Source of Truth (SSOT) for security documentation
**License:** MIT
**Maintained By:** PocketPortal Development Team
