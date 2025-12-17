#!/bin/bash
# PocketPortal 4.1 - Complete Installation Script
# Installs everything needed for a fresh deployment

set -e  # Exit on error

echo "========================================================================"
echo "🤖 PocketPortal 4.1 - Installation"
echo "========================================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on macOS or Linux
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
    echo "✅ Detected: macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    echo "✅ Detected: Linux"
else
    echo "❌ Unsupported OS: $OSTYPE"
    exit 1
fi

echo ""

# Function to check command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python version
echo "📋 Checking Python version..."
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 11 ]; then
        echo "✅ Python $PYTHON_VERSION (OK)"
    else
        echo "❌ Python 3.11+ required, found $PYTHON_VERSION"
        exit 1
    fi
else
    echo "❌ Python 3 not found. Please install Python 3.11 or 3.12"
    exit 1
fi

# Check Homebrew (macOS only)
if [ "$OS" = "macos" ]; then
    echo ""
    echo "📋 Checking Homebrew..."
    if command_exists brew; then
        echo "✅ Homebrew installed"
    else
        echo "⚠️  Homebrew not found. Installing..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
fi

# Install Ollama
echo ""
echo "📋 Checking Ollama..."
if command_exists ollama; then
    echo "✅ Ollama installed"
else
    echo "⚠️  Ollama not found. Installing..."
    if [ "$OS" = "macos" ]; then
        brew install ollama
    else
        curl -fsSL https://ollama.ai/install.sh | sh
    fi
fi

# Start Ollama service
echo ""
echo "🚀 Starting Ollama service..."
if [ "$OS" = "macos" ]; then
    brew services start ollama 2>/dev/null || true
else
    sudo systemctl start ollama 2>/dev/null || true
fi

sleep 3  # Give Ollama time to start

# Pull default model
echo ""
echo "📥 Downloading default model (this may take 5-10 minutes)..."
ollama pull qwen2.5:7b-instruct-q4_K_M || echo "⚠️  Model download failed, will retry later"

# Create virtual environment
echo ""
echo "🐍 Creating Python virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment exists, skipping..."
else
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "❓ Install with all features? (MCP, Git, Docker, OCR, etc.)"
read -p "   This adds ~500MB of packages [Y/n]: " install_all

if [[ $install_all =~ ^[Nn]$ ]]; then
    echo "📦 Installing core dependencies..."
    pip install -e .
    echo "✅ Core dependencies installed"
else
    echo "📦 Installing all dependencies..."

    # Install Node.js for MCP (if not present)
    if ! command_exists node; then
        echo "📦 Installing Node.js (required for MCP)..."
        if [ "$OS" = "macos" ]; then
            brew install node
        else
            curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
            sudo apt-get install -y nodejs
        fi
    fi

    # Install Tesseract for PDF OCR (if not present)
    if ! command_exists tesseract; then
        echo "📦 Installing Tesseract (required for PDF OCR)..."
        if [ "$OS" = "macos" ]; then
            brew install tesseract
        else
            sudo apt-get install -y tesseract-ocr
        fi
    fi

    pip install -e ".[all]"
    echo "✅ All dependencies installed"
fi

# Install Playwright browsers (for web automation)
echo ""
echo "🌐 Installing Playwright browsers..."
python -m playwright install chromium || echo "⚠️  Playwright install failed"

# Create necessary directories
echo ""
echo "📁 Creating necessary directories..."
mkdir -p logs screenshots browser_data data credentials
echo "✅ Directories created"

# Create .env from example if it doesn't exist
echo ""
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists, not overwriting"
else
    echo "📝 Creating .env from template..."
    cp .env.example .env
    echo "✅ .env created - YOU MUST EDIT THIS FILE"
fi

# Set executable permissions
echo ""
echo "🔧 Setting executable permissions..."
chmod +x scripts/*.sh 2>/dev/null || true
chmod +x scripts/*.py 2>/dev/null || true

# Run verification
echo ""
echo "🔍 Verifying system setup..."
python verify_system.py || echo "⚠️  Some checks failed, review output above"

# Summary
echo ""
echo "========================================================================"
echo "✅ Installation Complete!"
echo "========================================================================"
echo ""
echo "📋 What was installed:"
echo "   ✅ Python virtual environment"
echo "   ✅ PocketPortal package"
echo "   ✅ Ollama LLM runtime"
echo "   ✅ Default model (qwen2.5:7b)"
if [[ ! $install_all =~ ^[Nn]$ ]]; then
    echo "   ✅ All features (MCP, Git, Docker, etc.)"
fi
echo ""
echo "🎯 Next Steps:"
echo "   1. Get Telegram bot token from @BotFather"
echo "   2. Edit .env file and add your bot token"
echo "   3. Add your Telegram user ID to .env"
echo "   4. Run: source venv/bin/activate"
echo "   5. Run: pocketportal start --interface telegram"
echo "   6. Message your bot on Telegram!"
echo ""
echo "📖 Documentation:"
echo "   - README.md - Overview"
echo "   - docs/setup.md - Installation guide"
echo "   - docs/architecture.md - Architecture documentation"
echo ""
echo "🆘 Need help? Check docs/TROUBLESHOOTING.md"
echo ""
echo "========================================================================"
