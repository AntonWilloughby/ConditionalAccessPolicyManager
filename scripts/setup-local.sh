#!/bin/bash
# CA Policy Manager - Local Setup Script (Linux/macOS)
# Run this script to quickly set up the app for local testing

set -e

echo "🚀 CA Policy Manager - Local Setup"
echo ""

# Check Python
echo "1️⃣  Checking Python installation..."
PYTHON_CMD=""
UNSUPPORTED_PYTHONS=()

for cmd in python3.12 python3.11 python3 python; do
    if command -v $cmd &> /dev/null; then
        VERSION=$($cmd --version 2>&1)
        if [[ $VERSION =~ Python\ ([0-9]+)\.([0-9]+)\.([0-9]+) ]]; then
            MAJOR=${BASH_REMATCH[1]}
            MINOR=${BASH_REMATCH[2]}
            if [[ "$MAJOR" == "3" && ( "$MINOR" == "11" || "$MINOR" == "12" ) ]]; then
                PYTHON_CMD=$cmd
                echo "✅ Found supported $VERSION via $cmd"
                break
            else
                UNSUPPORTED_PYTHONS+=("$VERSION via $cmd")
            fi
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    if [ ${#UNSUPPORTED_PYTHONS[@]} -gt 0 ]; then
        echo "⚠️  Detected Python installations that are not supported by this tool:"
        for entry in "${UNSUPPORTED_PYTHONS[@]}"; do
            echo "   - $entry"
        done
        echo ""
    fi

    echo "❌ Python 3.11 or 3.12 not found!"
    echo ""
    echo "📥 Please install Python:"
    echo "   Ubuntu/Debian: sudo apt install python3.11 python3.11-venv"
    echo "   macOS: brew install python@3.11"
    echo "   Or download from: https://www.python.org/downloads/"
    echo ""
    exit 1
fi

echo ""

# Create virtual environment
echo "2️⃣  Creating virtual environment..."
if [ -d .venv ]; then
    echo "⚠️  Existing .venv found - cleaning..."
    rm -rf .venv
fi

$PYTHON_CMD -m venv .venv
echo "✅ Virtual environment created"

echo ""

# Activate virtual environment
echo "3️⃣  Activating virtual environment..."
source .venv/bin/activate
echo "✅ Virtual environment activated"

echo ""

# Install dependencies
echo "4️⃣  Installing dependencies..."
cd CA_Policy_Manager_Web

echo "   Upgrading pip..."
pip install --upgrade pip setuptools wheel --quiet --disable-pip-version-check

echo "   Installing packages (this may take 2-3 minutes)..."
pip install -r requirements.txt --quiet --disable-pip-version-check

echo "✅ All dependencies installed successfully"

echo ""

# Check for .env
echo "5️⃣  Checking environment configuration..."
if [ ! -f .env ]; then
    echo "⚠️  .env file not found"
    echo "   Creating from template..."

    $PYTHON_CMD - <<'PY'
import pathlib
import re
import secrets

secret = secrets.token_hex(32)
content = pathlib.Path('.env.example').read_text()
content = re.sub(r'SECRET_KEY=.*', f'SECRET_KEY={secret}', content)
content = re.sub(r'#DEMO_MODE=.*', 'DEMO_MODE=true', content)
pathlib.Path('.env').write_text(content)
PY

    echo "✅ .env file created with auto-generated SECRET_KEY"
    echo ""
    echo "📝 IMPORTANT: Edit .env file and set:"
    echo "   - MSAL_CLIENT_ID (from Azure App Registration)"
    echo "   - MSAL_CLIENT_SECRET (optional unless you use client-credential auth)"
    echo "   - DEMO_MODE=false (after you add real credentials)"
    echo ""
    echo "   See docs/QUICK_SETUP.md for Azure setup instructions"
else
    echo "✅ .env file exists"

    DEMO_MODE_VALUE=$(grep -E '^DEMO_MODE=' .env | tail -n 1 | cut -d '=' -f2 | tr '[:upper:]' '[:lower:]')
    CLIENT_ID_VALUE=$(grep -E '^MSAL_CLIENT_ID=' .env | tail -n 1 | cut -d '=' -f2)
    CLIENT_SECRET_VALUE=$(grep -E '^MSAL_CLIENT_SECRET=' .env | tail -n 1 | cut -d '=' -f2)

    if [ -z "$CLIENT_ID_VALUE" ] || [[ "$CLIENT_ID_VALUE" == your_* ]]; then
        if [[ "$DEMO_MODE_VALUE" == "true" ]]; then
            echo "ℹ️  MSAL_CLIENT_ID is still a placeholder. Demo mode is enabled, so sign-in is disabled until you set a real client ID."
        else
            echo "❗ MSAL_CLIENT_ID is missing but DEMO_MODE=false. Authentication will fail until you set a real client ID."
        fi
    fi

    if [ -z "$CLIENT_SECRET_VALUE" ] || [[ "$CLIENT_SECRET_VALUE" == your_* ]]; then
        echo "ℹ️  MSAL_CLIENT_SECRET is still a placeholder. Optional for delegated sign-in but required for client credential flows."
    fi
fi

echo ""
echo "============================================================"
echo "✅ Setup complete!"
echo "============================================================"

echo ""
echo "🚀 To start the app, run:"
echo "   source .venv/bin/activate"
echo "   cd CA_Policy_Manager_Web"
echo "   python app.py"

echo ""
echo "🌐 Then open in browser:"
echo "   http://localhost:5000"

echo ""
echo "📚 For more details, see:"
echo "   LOCAL_TESTING_GUIDE.md"

echo ""
echo "🔁 If you change values in .env later (especially DEMO_MODE), fully stop running python processes so Flask reloads the new environment."
echo "   Example: pkill -f \"python app.py\""
echo ""
