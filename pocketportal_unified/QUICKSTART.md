# ⚡ Ultra-Quick Start (5 Minutes)

**Too busy to read? Here's the fastest path to a working system.**

---

## Prerequisites

- ✅ Python 3.11+
- ✅ Ollama running (`ollama serve`)
- ✅ Telegram bot token
- ✅ 5 minutes

---

## Step 1: Setup (2 minutes)

```bash
# Copy files to your existing telegram-agent directory
cd ~/telegram-agent
cp -r /path/to/pocketportal_unified/* .

# Install web dependencies
source venv/bin/activate
pip install fastapi uvicorn websockets

# Configure
cp .env.example .env
nano .env  # Add your TELEGRAM_BOT_TOKEN and TELEGRAM_USER_ID
```

---

## Step 2: Test Core (1 minute)

```bash
python core/agent_engine.py
```

Should see:
```
✅ AgentCore initialized successfully!
  Tools: 11
  Models: 10
```

---

## Step 3: Run Telegram (1 minute)

```bash
python interfaces/telegram_interface.py
```

Test on phone:
- `/start` → Welcome message
- `Hello!` → Response
- ✅ Works? Great!

---

## Step 4: Run Web (1 minute)

```bash
# New terminal
python interfaces/web_interface.py
```

Open: http://localhost:8000

Test in browser:
- Type: "Hello!"
- Get response
- ✅ Works? Done!

---

## That's It!

You now have:
- ✅ Telegram bot working
- ✅ Web interface working
- ✅ Same AI brain powering both
- ✅ Ready to chat from phone or browser

---

## Troubleshooting

**"Module not found"**
```bash
# You're not in the right directory or venv not activated
cd ~/telegram-agent
source venv/bin/activate
```

**"Can't connect to Ollama"**
```bash
ollama serve  # In another terminal
```

**"Port 8000 in use"**
```bash
python interfaces/web_interface.py --port 8001
# Or: uvicorn interfaces.web_interface:app --port 8001
```

---

## Next Steps

- Read [README.md](README.md) for full details
- Read [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for step-by-step migration
- Run `python verify_unified.py` for comprehensive checks

---

**Questions?** Check the logs in `logs/` directory.

**Success?** 🎉 Now add Slack, API, or whatever interface you want!
