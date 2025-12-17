#!/usr/bin/env python3
"""
Complete System Verification Script
Runs all verification checks for the Telegram AI Agent
"""

import sys
import subprocess
from pathlib import Path
import importlib.util


class Colors:
    """Terminal colors"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Print section header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")


def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}Ã¢Å“â€¦ {text}{Colors.END}")


def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}Ã¢ÂÅ’ {text}{Colors.END}")


def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}Ã¢Å¡Â Ã¯Â¸Â  {text}{Colors.END}")


def check_python_version():
    """Check Python version"""
    major, minor = sys.version_info[:2]
    if major == 3 and minor in [11, 12]:
        print_success(f"Python {major}.{minor}.{sys.version_info.micro}")
        return True
    else:
        print_error(f"Python {major}.{minor} - Need 3.11 or 3.12")
        return False


def check_virtual_env():
    """Check if running in virtual environment"""
    if sys.prefix != sys.base_prefix:
        print_success(f"Virtual environment: {sys.prefix}")
        return True
    else:
        print_error("Not in virtual environment")
        return False


def check_directories():
    """Check required directories"""
    required_dirs = [
        'routing',
        'security',
        'telegram_agent_tools',
        'telegram_agent_tools/utility_tools',
        'telegram_agent_tools/data_tools',
        'telegram_agent_tools/web_tools',
        'telegram_agent_tools/audio_tools',
        'telegram_agent_tools/dev_tools',
        'telegram_agent_tools/automation_tools',
        'telegram_agent_tools/knowledge_tools',
        'logs',
        'screenshots',
        'browser_data',
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists() and path.is_dir():
            pass  # Silent success
        else:
            print_error(f"Missing directory: {dir_path}")
            all_exist = False
    
    if all_exist:
        print_success(f"All {len(required_dirs)} directories exist")
    
    return all_exist


def check_core_dependencies():
    """Check core Python dependencies"""
    deps = [
        ('telegram', 'python-telegram-bot'),
        ('dotenv', 'python-dotenv'),
        ('pydantic', 'pydantic'),
        ('aiohttp', 'aiohttp'),
        ('cryptography', 'cryptography'),
        ('qrcode', 'qrcode'),
        ('yaml', 'PyYAML'),
        ('pandas', 'pandas'),
        ('matplotlib', 'matplotlib'),
    ]
    
    all_installed = True
    installed_count = 0
    
    for module_name, package_name in deps:
        try:
            __import__(module_name)
            installed_count += 1
        except ImportError:
            print_error(f"Missing: {package_name}")
            all_installed = False
    
    if all_installed:
        print_success(f"All {len(deps)} core dependencies installed")
    else:
        print_warning(f"Only {installed_count}/{len(deps)} dependencies installed")
    
    return all_installed


def check_config_file():
    """Check .env file"""
    env_path = Path('.env')
    if not env_path.exists():
        print_error(".env file not found")
        return False
    
    print_success(".env file exists")
    
    # Check required keys
    env_content = env_path.read_text()
    required_keys = ['TELEGRAM_BOT_TOKEN', 'TELEGRAM_USER_ID']
    
    missing = []
    empty = []
    
    for key in required_keys:
        if f"{key}=" not in env_content:
            missing.append(key)
        else:
            # Check if value is filled
            for line in env_content.split('\n'):
                line = line.strip()
                if line.startswith(f"{key}="):
                    value = line.split('=', 1)[1].strip()
                    if not value or value.startswith('your_') or value == '':
                        empty.append(key)
    
    if missing:
        print_error(f"Missing keys: {', '.join(missing)}")
        return False
    
    if empty:
        print_warning(f"Empty values: {', '.join(empty)}")
        print_warning("Please edit .env and fill in these values")
        return False
    
    print_success("Configuration validated")
    return True


def check_routing_system():
    """Check routing system files"""
    routing_files = [
        'routing/__init__.py',
        'routing/model_registry.py',
        'routing/model_backends.py',
        'routing/task_classifier.py',
        'routing/intelligent_router.py',
        'routing/execution_engine.py',
        'routing/response_formatter.py',
    ]
    
    all_exist = True
    for file_path in routing_files:
        if not Path(file_path).exists():
            print_error(f"Missing: {file_path}")
            all_exist = False
    
    if all_exist:
        print_success(f"All {len(routing_files)} routing files exist")
        
        # Try to import
        try:
            from routing import ModelRegistry, IntelligentRouter
            print_success("Routing system imports successfully")
        except ImportError as e:
            print_error(f"Routing import error: {e}")
            return False
    
    return all_exist


def check_security_module():
    """Check security module"""
    security_files = [
        'security/__init__.py',
        'security/security_module.py',
    ]
    
    all_exist = True
    for file_path in security_files:
        if not Path(file_path).exists():
            print_error(f"Missing: {file_path}")
            all_exist = False
    
    if all_exist:
        print_success("Security module files exist")
        
        # Try to import
        try:
            from security import RateLimiter, InputSanitizer
            print_success("Security module imports successfully")
        except ImportError as e:
            print_error(f"Security import error: {e}")
            return False
    
    return all_exist


def check_tool_system():
    """Check tool system"""
    tool_files = [
        'telegram_agent_tools/__init__.py',
        'telegram_agent_tools/base_tool.py',
    ]
    
    all_exist = True
    for file_path in tool_files:
        if not Path(file_path).exists():
            print_error(f"Missing: {file_path}")
            all_exist = False
    
    if all_exist:
        print_success("Tool framework files exist")
        
        # Try to import and load tools
        try:
            from telegram_agent_tools import registry
            loaded, failed = registry.discover_and_load()
            
            if loaded > 0:
                print_success(f"Tools loaded: {loaded} loaded, {failed} failed")
                if loaded == 11:
                    print_success("All 11 tools loaded successfully!")
                elif loaded > 0:
                    print_warning(f"Partial: {loaded}/11 tools loaded")
            else:
                print_warning("No tools loaded yet (expected if not built)")
        except Exception as e:
            print_error(f"Tool system error: {e}")
            return False
    
    return all_exist


def check_config_validator():
    """Check configuration validator"""
    if not Path('config_validator.py').exists():
        print_error("config_validator.py not found")
        return False
    
    print_success("config_validator.py exists")
    
    try:
        from config_validator import load_and_validate_config
        config = load_and_validate_config()
        if config:
            print_success(f"Configuration valid: {config.llm_backend} backend")
            return True
        else:
            print_error("Configuration validation failed")
            return False
    except Exception as e:
        print_error(f"Config validator error: {e}")
        return False


def check_main_agent():
    """Check main agent file"""
    if not Path('telegram_agent_v3.py').exists():
        print_warning("telegram_agent_v3.py not found (created in Part 6)")
        return None  # Not an error, might not be built yet
    
    print_success("telegram_agent_v3.py exists")
    return True


def check_ollama():
    """Check Ollama service"""
    try:
        import subprocess
        result = subprocess.run(
            ['curl', '-s', 'http://localhost:11434/api/tags'],
            capture_output=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print_success("Ollama service running")
            
            # Check for models
            try:
                result = subprocess.run(
                    ['ollama', 'list'],
                    capture_output=True,
                    text=True
                )
                lines = result.stdout.strip().split('\n')
                model_count = len(lines) - 1  # Subtract header
                if model_count > 0:
                    print_success(f"Ollama models: {model_count} installed")
                else:
                    print_warning("No Ollama models installed")
            except:
                pass
            
            return True
        else:
            print_warning("Ollama not running")
            return False
    except Exception as e:
        print_warning(f"Ollama check failed: {e}")
        return False


def check_disk_space():
    """Check available disk space"""
    try:
        import shutil
        total, used, free = shutil.disk_usage(Path.home())
        free_gb = free // (2**30)
        
        if free_gb > 50:
            print_success(f"Disk space: {free_gb}GB free")
            return True
        else:
            print_warning(f"Low disk space: {free_gb}GB free (recommend 50GB+)")
            return False
    except Exception as e:
        print_warning(f"Disk space check failed: {e}")
        return True  # Don't fail on this


def check_memory():
    """Check system memory"""
    try:
        import psutil
        mem = psutil.virtual_memory()
        total_gb = mem.total // (2**30)
        available_gb = mem.available // (2**30)
        
        print_success(f"Memory: {available_gb}GB available / {total_gb}GB total")
        return True
    except ImportError:
        # psutil not installed yet
        print_warning("psutil not installed (memory check skipped)")
        return True
    except Exception as e:
        print_warning(f"Memory check failed: {e}")
        return True


def main():
    """Run all checks"""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}Telegram AI Agent - Complete System Verification{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}")
    
    checks = [
        ("Python Version", check_python_version),
        ("Virtual Environment", check_virtual_env),
        ("Directory Structure", check_directories),
        ("Core Dependencies", check_core_dependencies),
        ("Configuration File", check_config_file),
        ("Routing System", check_routing_system),
        ("Security Module", check_security_module),
        ("Tool System", check_tool_system),
        ("Configuration Validator", check_config_validator),
        ("Main Agent", check_main_agent),
        ("Ollama Service", check_ollama),
        ("Disk Space", check_disk_space),
        ("System Memory", check_memory),
    ]
    
    results = []
    for name, check_func in checks:
        print_header(name)
        result = check_func()
        results.append(result)
    
    # Summary
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}Summary{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}\n")
    
    passed = sum(1 for r in results if r is True)
    failed = sum(1 for r in results if r is False)
    skipped = sum(1 for r in results if r is None)
    
    print(f"Total checks: {len(checks)}")
    print_success(f"Passed: {passed}")
    if failed > 0:
        print_error(f"Failed: {failed}")
    if skipped > 0:
        print_warning(f"Skipped: {skipped}")
    
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    if failed == 0:
        print_success("ALL CRITICAL CHECKS PASSED!")
        if skipped > 0:
            print_warning(f"({skipped} optional checks skipped)")
        print(f"\n{Colors.GREEN}System ready for next deployment step{Colors.END}")
    else:
        print_error("SOME CHECKS FAILED")
        print(f"\n{Colors.YELLOW}Please fix the issues above before proceeding{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}\n")
    
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
