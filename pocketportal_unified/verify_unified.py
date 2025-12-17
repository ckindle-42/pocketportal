#!/usr/bin/env python3
"""
PocketPortal Unified - System Verification Script
=================================================

This script tests all components of the unified architecture:
- Core engine
- Telegram interface (structure)
- Web interface (structure)
- Dependencies
- Configuration

Run this after migration to verify everything is working.
"""

import sys
import os
from pathlib import Path
import importlib.util

# ANSI colors
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")


# ============================================================================
# CHECKS
# ============================================================================

def check_directory_structure():
    """Check if all required directories exist"""
    print_info("Checking directory structure...")
    
    required_dirs = [
        'core',
        'interfaces',
        'web_static',
        'routing',
        'telegram_agent_tools',
        'security'
    ]
    
    all_good = True
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print_success(f"Directory exists: {dir_name}/")
        else:
            print_error(f"Directory missing: {dir_name}/")
            all_good = False
    
    return all_good


def check_core_files():
    """Check if core files exist"""
    print_info("Checking core files...")
    
    required_files = [
        'core/__init__.py',
        'core/agent_engine.py',
    ]
    
    all_good = True
    for file_path in required_files:
        if Path(file_path).exists():
            print_success(f"File exists: {file_path}")
        else:
            print_error(f"File missing: {file_path}")
            all_good = False
    
    return all_good


def check_interface_files():
    """Check if interface files exist"""
    print_info("Checking interface files...")
    
    required_files = [
        'interfaces/__init__.py',
        'interfaces/telegram_interface.py',
        'interfaces/web_interface.py',
        'web_static/index.html'
    ]
    
    all_good = True
    for file_path in required_files:
        if Path(file_path).exists():
            print_success(f"File exists: {file_path}")
        else:
            print_error(f"File missing: {file_path}")
            all_good = False
    
    return all_good


def check_dependencies():
    """Check if required Python packages are installed"""
    print_info("Checking Python dependencies...")
    
    required_packages = [
        ('telegram', 'python-telegram-bot'),
        ('fastapi', 'fastapi'),
        ('uvicorn', 'uvicorn'),
        ('websockets', 'websockets'),
        ('pydantic', 'pydantic'),
        ('aiohttp', 'aiohttp'),
        ('dotenv', 'python-dotenv'),
    ]
    
    all_good = True
    for module_name, package_name in required_packages:
        try:
            __import__(module_name)
            print_success(f"Package installed: {package_name}")
        except ImportError:
            print_error(f"Package missing: {package_name}")
            print_warning(f"  Install with: pip install {package_name}")
            all_good = False
    
    return all_good


def check_core_import():
    """Try importing the core module"""
    print_info("Testing core module import...")
    
    try:
        from core import AgentCore, ProcessingResult
        print_success("Core module imports successfully")
        print_success(f"  - AgentCore class available")
        print_success(f"  - ProcessingResult class available")
        return True
    except Exception as e:
        print_error(f"Core module import failed: {e}")
        return False


def check_routing_system():
    """Check routing system"""
    print_info("Checking routing system...")
    
    required_files = [
        'routing/__init__.py',
        'routing/model_registry.py',
        'routing/model_backends.py',
        'routing/task_classifier.py',
        'routing/intelligent_router.py',
        'routing/execution_engine.py'
    ]
    
    all_good = True
    for file_path in required_files:
        if Path(file_path).exists():
            print_success(f"Routing file exists: {Path(file_path).name}")
        else:
            print_error(f"Routing file missing: {file_path}")
            all_good = False
    
    return all_good


def check_tools():
    """Check tool system"""
    print_info("Checking tool system...")
    
    required_files = [
        'telegram_agent_tools/__init__.py',
        'telegram_agent_tools/base_tool.py'
    ]
    
    all_good = True
    for file_path in required_files:
        if Path(file_path).exists():
            print_success(f"Tool file exists: {Path(file_path).name}")
        else:
            print_error(f"Tool file missing: {file_path}")
            all_good = False
    
    # Check for tool directories
    tool_dirs = [
        'telegram_agent_tools/utility_tools',
        'telegram_agent_tools/data_tools',
        'telegram_agent_tools/web_tools'
    ]
    
    for dir_path in tool_dirs:
        if Path(dir_path).exists():
            tool_count = len(list(Path(dir_path).glob('*.py'))) - 1  # Exclude __init__.py
            print_success(f"Tool directory exists: {Path(dir_path).name} ({tool_count} tools)")
        else:
            print_warning(f"Tool directory missing: {dir_path}")
    
    return all_good


def check_security():
    """Check security module"""
    print_info("Checking security module...")
    
    required_files = [
        'security/__init__.py',
        'security/security_module.py'
    ]
    
    all_good = True
    for file_path in required_files:
        if Path(file_path).exists():
            print_success(f"Security file exists: {Path(file_path).name}")
        else:
            print_error(f"Security file missing: {file_path}")
            all_good = False
    
    return all_good


def check_configuration():
    """Check configuration files"""
    print_info("Checking configuration...")
    
    if Path('.env').exists():
        print_success("Configuration file exists: .env")
        
        # Check for required variables
        with open('.env', 'r') as f:
            content = f.read()
            
        required_vars = [
            'TELEGRAM_BOT_TOKEN',
            'TELEGRAM_USER_ID',
            'OLLAMA_BASE_URL'
        ]
        
        for var in required_vars:
            if var in content and not content.split(var)[1].split('\n')[0].strip().endswith('here'):
                print_success(f"  Variable configured: {var}")
            else:
                print_warning(f"  Variable not configured: {var}")
    else:
        print_warning("Configuration file missing: .env")
        print_info("  Copy .env.example to .env and configure")
        return False
    
    if Path('config_validator.py').exists():
        print_success("Config validator exists: config_validator.py")
    else:
        print_error("Config validator missing: config_validator.py")
        return False
    
    return True


def check_ollama():
    """Check if Ollama is running"""
    print_info("Checking Ollama service...")
    
    try:
        import aiohttp
        import asyncio
        
        async def check():
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get('http://localhost:11434/api/tags', timeout=aiohttp.ClientTimeout(total=3)) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            models = data.get('models', [])
                            print_success(f"Ollama is running ({len(models)} models available)")
                            for model in models[:3]:  # Show first 3
                                print_success(f"  - {model['name']}")
                            return True
                        else:
                            print_warning("Ollama is running but returned unexpected status")
                            return False
            except Exception as e:
                print_warning(f"Cannot connect to Ollama: {e}")
                print_info("  Make sure Ollama is running: ollama serve")
                return False
        
        return asyncio.run(check())
        
    except Exception as e:
        print_warning(f"Cannot check Ollama: {e}")
        return False


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Run all checks"""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}PocketPortal Unified - System Verification{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}")
    
    checks = [
        ("Directory Structure", check_directory_structure),
        ("Core Files", check_core_files),
        ("Interface Files", check_interface_files),
        ("Python Dependencies", check_dependencies),
        ("Core Module Import", check_core_import),
        ("Routing System", check_routing_system),
        ("Tool System", check_tools),
        ("Security Module", check_security),
        ("Configuration", check_configuration),
        ("Ollama Service", check_ollama),
    ]
    
    results = []
    for name, check_func in checks:
        print_header(name)
        result = check_func()
        results.append((name, result))
    
    # Summary
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}Summary{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}\n")
    
    passed = sum(1 for _, r in results if r is True)
    failed = sum(1 for _, r in results if r is False)
    
    print(f"Total checks: {len(checks)}")
    print_success(f"Passed: {passed}")
    if failed > 0:
        print_error(f"Failed: {failed}")
    
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    if failed == 0:
        print_success("ALL CHECKS PASSED! ✨")
        print()
        print_info("You're ready to run:")
        print_info("  Telegram: python interfaces/telegram_interface.py")
        print_info("  Web: python interfaces/web_interface.py")
    else:
        print_error("SOME CHECKS FAILED")
        print()
        print_warning("Fix the issues above before running the system")
        print()
        print_info("Common fixes:")
        print_info("  - Missing directories: Follow migration guide")
        print_info("  - Missing packages: pip install -r requirements.txt")
        print_info("  - Config issues: Copy .env.example to .env and configure")
        print_info("  - Ollama not running: ollama serve")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}\n")
    
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
