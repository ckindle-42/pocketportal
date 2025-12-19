# Known Issues & TODO Items

**Last Updated:** 2025-12-18
**Status:** All critical issues resolved, only enhancements remain

---

## ✅ Recently Resolved (Don't Re-Investigate)

These issues were identified in previous audits but have been **FIXED**. Don't waste time investigating these:

### 1. ✅ CLI Import Errors (RESOLVED 2025-12-18)
- **Issue:** Wrong import paths causing `ModuleNotFoundError`
- **Fixed In:** `claude/codebase-quality-review-vGUBA` commit `14cfea1`
- **Files:** `src/pocketportal/cli.py` lines 93, 112
- **Verification:** `pocketportal start --interface telegram` now works

### 2. ✅ Tool Loading Failures (RESOLVED 2025-12-18)
- **Issue:** Only 17/33 tools loading (ToolParameter API mismatch)
- **Status:** All 33 tools now load successfully
- **Verification:** `pocketportal list-tools` shows "33 loaded, 0 failed"

### 3. ✅ Documentation Drift (RESOLVED 2025-12-18)
- **Issue:** Docs claimed 25 tools, referenced non-existent commands
- **Fixed:** All tool counts updated, non-existent commands removed
- **Files:** README.md, docs/setup.md

### 4. ✅ Configuration Variable Names (RESOLVED 2025-12-18)
- **Issue:** Docs used wrong env var names (missing POCKETPORTAL_ prefix)
- **Fixed:** All config examples corrected in docs/setup.md
- **Verification:** Check docs/setup.md lines 462-467

---

## 🔧 Known Limitations (Documented, Not Critical)

These are architectural limitations that are **known, documented, and have workarounds**:

### 1. Web Interface Not CLI-Integrated
**Status:** Known limitation, documented workaround available
**Impact:** Low - Users can still run web interface
**Workaround:** `uvicorn pocketportal.interfaces.web.server:app --port 8000`
**Root Cause:** Web interface is FastAPI app, not BaseInterface wrapper
**Tracked In:**
- `src/pocketportal/cli.py:101,122` (TODO comments)
- `docs/setup.md:371-387` (documented)
- `README.md:31-32` (documented)

**Future Enhancement:**
```python
# TODO: Create WebInterface wrapper class that implements BaseInterface
# This would enable: pocketportal start --interface web
```

### 2. MCP Server Not CLI-Accessible
**Status:** Known limitation, Python API available
**Impact:** Low - MCP server functionality exists
**Workaround:** Use Python API (see docs/PLUGIN_DEVELOPMENT.md)
**Tracked In:** `docs/setup.md:446-448`

**Future Enhancement:**
```bash
# TODO: Implement CLI command
# pocketportal mcp-server --port 3000
```

### 3. No Dedicated Health Check Command
**Status:** Known limitation, alternative available
**Impact:** Low - `verify` command works for health checks
**Workaround:** Use `pocketportal verify` (more comprehensive)
**Tracked In:** Docker healthcheck uses `verify` instead

**Future Enhancement:**
```bash
# TODO: Add lightweight health check
# pocketportal health  # Quick yes/no check for Docker/K8s
```

---

## 📋 Future Enhancements (Non-Blocking)

### High Priority
1. **WebInterface BaseInterface Wrapper**
   - **Why:** Enable `pocketportal start --interface web` command
   - **Effort:** Medium (2-4 hours)
   - **Files:** Create `src/pocketportal/interfaces/web/interface.py`
   - **Benefit:** Unified CLI for all interfaces

2. **Run Full Test Suite**
   - **Why:** Ensure no regressions after fixes
   - **Effort:** Low (install pytest, run tests)
   - **Command:** `pip install -e ".[dev]" && pytest tests/ -v`

### Medium Priority
3. **MCP Server CLI Command**
   - **Why:** Easier for users than Python API
   - **Effort:** Medium (3-5 hours)
   - **Files:** Add to `src/pocketportal/cli.py`

4. **Health Check Command**
   - **Why:** Lightweight alternative to `verify`
   - **Effort:** Low (1-2 hours)
   - **Files:** Add to `src/pocketportal/cli.py`

5. **Example .env File**
   - **Why:** Show users all available config variables
   - **Effort:** Low (30 mins)
   - **File:** Create `.env.example`

### Low Priority
6. **Pre-Commit Hooks**
   - Lint checks
   - Import validation
   - Documentation link checker

7. **Integration Tests**
   - Test actual Telegram startup
   - Test actual web interface startup
   - Test tool execution end-to-end

---

## 🚫 Non-Issues (Don't Report These)

These are **intentional design decisions**, not bugs:

### 1. Telegram Interface Requires Config
**Not a Bug:** Telegram requires bot token from BotFather
**Expected:** `pocketportal start` fails without config
**See:** docs/setup.md for configuration instructions

### 2. Web Interface Starts via uvicorn
**Not a Bug:** Intentional separation until BaseInterface wrapper exists
**Expected:** `pocketportal start --interface web` shows error with uvicorn command
**See:** "Known Limitations" section above

### 3. Config Validation Fails on Fresh Install
**Not a Bug:** Requires at least one interface and one model configured
**Expected:** `pocketportal verify` shows config check failure
**See:** docs/setup.md for configuration

---

## 📝 How to Use This Document

### For Reviewers
1. **Check "Recently Resolved"** - Don't re-investigate these
2. **Check "Known Limitations"** - These are documented and have workarounds
3. **Check "Non-Issues"** - Don't report these as bugs
4. **Update this document** when you fix or discover new issues

### For Contributors
1. **Before reporting a bug** - Check "Known Limitations" and "Non-Issues"
2. **Before fixing something** - Check "Recently Resolved" to avoid duplicate work
3. **After fixing an issue** - Move it from "Future Enhancements" to "Recently Resolved"

### Updating This Document
When you fix an issue:
1. Add entry to "Recently Resolved" with date, commit, and verification
2. Remove from "Known Limitations" or "Future Enhancements"
3. Update "Last Updated" date at top

---

## 🔗 Related Documents

- **FIXES_APPLIED.md** - Detailed report of 2025-12-18 review fixes
- **AUDIT_REPORT.md** - Original audit findings (see STATUS UPDATE section)
- **CHANGELOG.md** - Version history and release notes
- **docs/GOVERNANCE.md** - Contribution and versioning rules

---

**Maintained By:** PocketPortal Contributors
**Questions:** Check related documents above or open GitHub issue
