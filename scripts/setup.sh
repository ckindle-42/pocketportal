#!/bin/bash
# =============================================================================
# Telegram AI Agent v3.1 - Automated Setup
# =============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║        Telegram AI Agent v3.1 - Setup                      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check Python version
echo -e "${YELLOW}[1/8] Checking Python version...${NC}"
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || [ "$PYTHON_MINOR" -lt 10 ]; then
    echo -e "${RED}✗ Python 3.10+ required (found $PYTHON_VERSION)${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python $PYTHON_VERSION${NC}"

# Create virtual environment
echo -e "${YELLOW}[2/8] Creating virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment exists${NC}"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo -e "${YELLOW}[3/8] Upgrading pip...${NC}"
pip install --upgrade pip -q
echo -e "${GREEN}✓ pip upgraded${NC}"

# Install dependencies
echo -e "${YELLOW}[4/8] Installing dependencies...${NC}"
pip install -r requirements.txt -q
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Install Playwright browsers
echo -e "${YELLOW}[5/8] Installing Playwright browsers...${NC}"
playwright install chromium 2>/dev/null || echo -e "${YELLOW}⚠ Playwright browser installation skipped (optional)${NC}"
echo -e "${GREEN}✓ Browser setup complete${NC}"

# Create directories
echo -e "${YELLOW}[6/8] Creating directories...${NC}"
mkdir -p logs data screenshots
echo -e "${GREEN}✓ Directories created${NC}"

# Check Ollama
echo -e "${YELLOW}[7/8] Checking Ollama...${NC}"
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Ollama is running${NC}"
    
    # List available models
    MODELS=$(curl -s http://localhost:11434/api/tags | python3 -c "import sys, json; models = json.load(sys.stdin).get('models', []); print(', '.join([m['name'] for m in models[:5]]))" 2>/dev/null || echo "none")
    echo -e "  Available models: ${BLUE}$MODELS${NC}"
else
    echo -e "${YELLOW}⚠ Ollama not running. Start with: ollama serve${NC}"
fi

# Configuration check
echo -e "${YELLOW}[8/8] Checking configuration...${NC}"
if [ -f ".env" ]; then
    echo -e "${GREEN}✓ .env file exists${NC}"
    
    # Validate required fields
    if grep -q "TELEGRAM_BOT_TOKEN=your_" .env 2>/dev/null; then
        echo -e "${YELLOW}⚠ Please update TELEGRAM_BOT_TOKEN in .env${NC}"
    fi
    if grep -q "TELEGRAM_USER_ID=your_" .env 2>/dev/null; then
        echo -e "${YELLOW}⚠ Please update TELEGRAM_USER_ID in .env${NC}"
    fi
else
    echo -e "${YELLOW}⚠ No .env file found. Creating from template...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}⚠ Please edit .env with your credentials${NC}"
fi

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    Setup Complete!                         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Next steps:${NC}"
echo -e "  1. Edit .env with your Telegram credentials"
echo -e "  2. Ensure Ollama is running: ${BLUE}ollama serve${NC}"
echo -e "  3. Pull a model: ${BLUE}ollama pull qwen2.5:7b${NC}"
echo -e "  4. Start the agent: ${BLUE}source venv/bin/activate && python telegram_agent_v3.py${NC}"
echo ""
echo -e "${GREEN}Optional - Auto-start on boot (macOS):${NC}"
echo -e "  ${BLUE}cp com.telegram.agent.plist ~/Library/LaunchAgents/${NC}"
echo -e "  ${BLUE}launchctl load ~/Library/LaunchAgents/com.telegram.agent.plist${NC}"
echo ""
echo -e "${GREEN}Verify installation:${NC}"
echo -e "  ${BLUE}python verify_system.py${NC}"
