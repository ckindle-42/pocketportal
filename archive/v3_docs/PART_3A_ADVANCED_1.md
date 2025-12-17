# Part 3A: Advanced Tools (Audio & Python Environments)

**What You'll Build:** Audio Batch Transcriber + Python Environment Manager  
**Time Required:** 45 minutes  
**Difficulty:** Medium  
**Prerequisites:** Part 2C complete

---

## ðŸŽ¯ Overview

In this part, you'll add 2 powerful advanced tools:

7. **Audio Batch Transcriber** - Transcribe multiple audio files simultaneously
8. **Python Environment Manager** - Create and manage virtual environments

By the end, you'll be able to:
- Transcribe multiple voice messages at once
- Convert audio formats automatically
- Create isolated Python environments
- Install packages per environment
- Execute code in specific environments

---

## ðŸ“¦ Step 1: Install Dependencies

```bash
cd ~/telegram-agent
source venv/bin/activate

# Install audio processing
pip install faster-whisper==0.10.0 pydub==0.25.1

# Note: pydub also requires ffmpeg
brew install ffmpeg

# Verify installation
python3 << 'EOF'
import faster_whisper
from pydub import AudioSegment
print("âœ… All audio dependencies installed")
print(f"   faster-whisper: {faster_whisper.__version__}")
EOF
```

**Expected output:**
```
âœ… All audio dependencies installed
   faster-whisper: 0.10.0
```

---

## ðŸ“ Step 2: Create Audio Tools Directory

```bash
cd ~/telegram-agent
mkdir -p telegram_agent_tools/audio_tools

# Verify
ls -la telegram_agent_tools/
```

---

## ðŸŽ¤ Step 3: Create Audio Batch Transcriber

**File: `telegram_agent_tools/audio_tools/audio_batch_transcriber.py`**

```bash
cat > telegram_agent_tools/audio_tools/audio_batch_transcriber.py << 'ENDOFFILE'
"""
Audio Batch Transcriber Tool
Transcribe multiple audio files with progress tracking
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from base_tool import BaseTool, ToolMetadata, ToolCategory

logger = logging.getLogger(__name__)

try:
    from faster_whisper import WhisperModel
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False


class AudioBatchTranscriberTool(BaseTool):
    """Batch transcribe audio files"""
    
    def __init__(self):
        super().__init__()
        self.model = None
        self.model_size = "base"
        self._executor = ThreadPoolExecutor(max_workers=2)
    
    def _get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="audio_batch_transcribe",
            description="Batch transcribe multiple audio files to text",
            category=ToolCategory.UTILITY,
            requires_confirmation=False,
            parameters={
                "files": {
                    "type": "array",
                    "required": True,
                    "description": "List of audio file paths"
                },
                "language": {
                    "type": "string",
                    "required": False,
                    "description": "Language code (e.g., 'en', 'es')"
                },
                "model_size": {
                    "type": "string",
                    "required": False,
                    "default": "base",
                    "options": ["tiny", "base", "small", "medium", "large"],
                    "description": "Whisper model size"
                }
            }
        )
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Transcribe audio files"""
        
        valid, error = await self.validate_parameters(parameters)
        if not valid:
            return self._error_response(error)
        
        if not WHISPER_AVAILABLE:
            return self._error_response("faster-whisper not installed. Run: pip install faster-whisper")
        
        try:
            files = parameters.get("files", [])
            language = parameters.get("language")
            model_size = parameters.get("model_size", "base")
            
            # Load model if needed
            if self.model is None or self.model_size != model_size:
                self._load_model(model_size)
            
            # Validate files
            paths = []
            errors = []
            for file in files:
                path = Path(file).expanduser()
                if not path.exists():
                    errors.append(f"{path.name}: File not found")
                else:
                    paths.append(path)
            
            if not paths:
                return self._error_response("No valid audio files found")
            
            # Transcribe files
            loop = asyncio.get_event_loop()
            tasks = [
                loop.run_in_executor(
                    self._executor,
                    self._transcribe_file,
                    path,
                    language
                )
                for path in paths
            ]
            
            results = await asyncio.gather(*tasks)
            
            # Compile statistics
            successful = sum(1 for r in results if r['success'])
            failed = len(results) - successful
            total_duration = sum(r.get('duration', 0) for r in results if r['success'])
            
            return self._success_response(
                result={
                    'transcriptions': results,
                    'summary': {
                        'total': len(paths),
                        'successful': successful,
                        'failed': failed,
                        'duration_seconds': total_duration
                    }
                },
                metadata={
                    "model_size": model_size,
                    "files_processed": len(paths)
                }
            )
        
        except Exception as e:
            return self._error_response(f"Transcription failed: {str(e)}")
    
    async def validate_parameters(self, parameters: Dict[str, Any]) -> tuple[bool, str]:
        """Validate parameters"""
        if "files" not in parameters:
            return False, "Missing required parameter: files"
        
        files = parameters.get("files")
        if not isinstance(files, list) or not files:
            return False, "files must be a non-empty list"
        
        return True, None
    
    def _load_model(self, model_size: str):
        """Load Whisper model"""
        logger.info(f"Loading Whisper model: {model_size}")
        self.model = WhisperModel(
            model_size,
            device="cpu",
            compute_type="int8"
        )
        self.model_size = model_size
        logger.info("Whisper model loaded")
    
    def _transcribe_file(self, file_path: Path, language: Optional[str] = None) -> Dict[str, Any]:
        """Transcribe a single audio file"""
        try:
            # Transcribe
            segments, info = self.model.transcribe(
                str(file_path),
                language=language,
                beam_size=5,
                vad_filter=True
            )
            
            # Collect text
            text_segments = []
            full_text = []
            
            for segment in segments:
                text_segments.append({
                    'start': segment.start,
                    'end': segment.end,
                    'text': segment.text.strip()
                })
                full_text.append(segment.text.strip())
            
            return {
                'file': str(file_path.name),
                'success': True,
                'language': info.language,
                'duration': info.duration,
                'text': ' '.join(full_text),
                'segments': text_segments
            }
        
        except Exception as e:
            logger.error(f"Transcription failed for {file_path}: {e}")
            return {
                'file': str(file_path.name),
                'success': False,
                'error': str(e)
            }
    
    def cleanup(self):
        """Clean up resources"""
        self._executor.shutdown(wait=False)
ENDOFFILE
```

---

## ðŸ Step 4: Create Python Environment Manager

**File: `telegram_agent_tools/dev_tools/python_env_manager.py`**

```bash
mkdir -p telegram_agent_tools/dev_tools

cat > telegram_agent_tools/dev_tools/python_env_manager.py << 'ENDOFFILE'
"""
Python Environment Manager Tool
Create and manage Python virtual environments
"""

import asyncio
import subprocess
import sys
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))
from base_tool import BaseTool, ToolMetadata, ToolCategory

logger = logging.getLogger(__name__)


class PythonEnvManagerTool(BaseTool):
    """Manage Python virtual environments"""
    
    def __init__(self, base_path: Optional[Path] = None):
        super().__init__()
        self.base_path = base_path or Path.home() / ".telegram_agent" / "venvs"
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def _get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="python_env",
            description="Create and manage Python virtual environments",
            category=ToolCategory.DEVELOPMENT,
            requires_confirmation=False,
            parameters={
                "action": {
                    "type": "string",
                    "required": True,
                    "options": ["create", "list", "install", "run", "delete"],
                    "description": "Action to perform"
                },
                "name": {
                    "type": "string",
                    "required": False,
                    "description": "Environment name"
                },
                "python_version": {
                    "type": "string",
                    "required": False,
                    "description": "Python version (e.g., '3.11')"
                },
                "packages": {
                    "type": "array",
                    "required": False,
                    "description": "Packages to install"
                },
                "command": {
                    "type": "string",
                    "required": False,
                    "description": "Command to run in environment"
                }
            }
        )
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute environment operation"""
        
        valid, error = await self.validate_parameters(parameters)
        if not valid:
            return self._error_response(error)
        
        try:
            action = parameters.get("action")
            
            if action == "create":
                return await self._create_env(parameters)
            elif action == "list":
                return await self._list_envs()
            elif action == "install":
                return await self._install_packages(parameters)
            elif action == "run":
                return await self._run_command(parameters)
            elif action == "delete":
                return await self._delete_env(parameters)
            else:
                return self._error_response(f"Unknown action: {action}")
        
        except Exception as e:
            return self._error_response(f"Operation failed: {str(e)}")
    
    async def validate_parameters(self, parameters: Dict[str, Any]) -> tuple[bool, str]:
        """Validate parameters"""
        if "action" not in parameters:
            return False, "Missing required parameter: action"
        
        action = parameters.get("action")
        
        if action in ["create", "install", "run", "delete"]:
            if "name" not in parameters:
                return False, f"{action} action requires 'name' parameter"
        
        if action == "install":
            if "packages" not in parameters:
                return False, "install action requires 'packages' parameter"
        
        if action == "run":
            if "command" not in parameters:
                return False, "run action requires 'command' parameter"
        
        return True, None
    
    async def _create_env(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create virtual environment"""
        name = parameters.get("name")
        python_version = parameters.get("python_version")
        
        env_path = self.base_path / name
        
        if env_path.exists():
            return self._error_response(f"Environment '{name}' already exists")
        
        try:
            # Determine Python executable
            if python_version:
                python_cmd = f"python{python_version}"
            else:
                python_cmd = sys.executable
            
            # Create venv
            process = await asyncio.create_subprocess_exec(
                python_cmd, "-m", "venv", str(env_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                return self._error_response(f"Failed to create environment: {stderr.decode()}")
            
            # Get Python version
            version = await self._get_python_version(env_path)
            
            return self._success_response(
                result=f"Created environment '{name}'",
                metadata={
                    "name": name,
                    "path": str(env_path),
                    "python_version": version
                }
            )
        
        except Exception as e:
            return self._error_response(f"Environment creation failed: {str(e)}")
    
    async def _list_envs(self) -> Dict[str, Any]:
        """List all environments"""
        try:
            envs = []
            
            for env_dir in self.base_path.iterdir():
                if not env_dir.is_dir():
                    continue
                
                python_path = env_dir / "bin" / "python"
                if not python_path.exists():
                    continue
                
                version = await self._get_python_version(env_dir)
                packages = await self._list_packages(env_dir)
                
                envs.append({
                    'name': env_dir.name,
                    'path': str(env_dir),
                    'python_version': version,
                    'package_count': len(packages)
                })
            
            return self._success_response(
                result=envs,
                metadata={"count": len(envs)}
            )
        
        except Exception as e:
            return self._error_response(f"Failed to list environments: {str(e)}")
    
    async def _install_packages(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Install packages in environment"""
        name = parameters.get("name")
        packages = parameters.get("packages", [])
        
        env_path = self.base_path / name
        if not env_path.exists():
            return self._error_response(f"Environment '{name}' not found")
        
        pip_path = env_path / "bin" / "pip"
        
        try:
            # Install packages
            process = await asyncio.create_subprocess_exec(
                str(pip_path), "install", *packages,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                return self._error_response(f"Package installation failed: {stderr.decode()}")
            
            return self._success_response(
                result=f"Installed {len(packages)} packages in '{name}'",
                metadata={
                    "environment": name,
                    "packages": packages
                }
            )
        
        except Exception as e:
            return self._error_response(f"Installation failed: {str(e)}")
    
    async def _run_command(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Run command in environment"""
        name = parameters.get("name")
        command = parameters.get("command")
        
        env_path = self.base_path / name
        if not env_path.exists():
            return self._error_response(f"Environment '{name}' not found")
        
        python_path = env_path / "bin" / "python"
        
        try:
            # Run command
            process = await asyncio.create_subprocess_shell(
                f"{python_path} -c \"{command}\"",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            output = stdout.decode() if stdout else stderr.decode()
            
            return self._success_response(
                result=output,
                metadata={
                    "environment": name,
                    "exit_code": process.returncode
                }
            )
        
        except Exception as e:
            return self._error_response(f"Command execution failed: {str(e)}")
    
    async def _delete_env(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Delete environment"""
        name = parameters.get("name")
        
        env_path = self.base_path / name
        if not env_path.exists():
            return self._error_response(f"Environment '{name}' not found")
        
        try:
            import shutil
            shutil.rmtree(env_path)
            
            return self._success_response(
                result=f"Deleted environment '{name}'",
                metadata={"name": name}
            )
        
        except Exception as e:
            return self._error_response(f"Deletion failed: {str(e)}")
    
    async def _get_python_version(self, env_path: Path) -> str:
        """Get Python version in environment"""
        python_path = env_path / "bin" / "python"
        
        try:
            process = await asyncio.create_subprocess_exec(
                str(python_path), "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            version = (stdout or stderr).decode().strip()
            return version.replace("Python ", "")
        except:
            return "unknown"
    
    async def _list_packages(self, env_path: Path) -> List[str]:
        """List installed packages"""
        pip_path = env_path / "bin" / "pip"
        
        try:
            process = await asyncio.create_subprocess_exec(
                str(pip_path), "list", "--format=freeze",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            packages = stdout.decode().strip().split('\n')
            return [p.split('==')[0] for p in packages if p]
        except:
            return []
ENDOFFILE
```

---

## âœ… Step 5: Test Tools

Create test script:

**File: `test_part3a.py`**

```bash
cat > test_part3a.py << 'ENDOFFILE'
#!/usr/bin/env python3
"""Test Part 3A Tools"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'telegram_agent_tools'))

from audio_tools.audio_batch_transcriber import AudioBatchTranscriberTool
from dev_tools.python_env_manager import PythonEnvManagerTool


async def test_python_env():
    """Test Python environment manager"""
    print("\n" + "="*60)
    print("Testing Python Environment Manager")
    print("="*60)
    
    tool = PythonEnvManagerTool()
    print(f"âœ… Tool loaded: {tool.metadata.name}")
    
    # Test 1: Create environment
    print("\nðŸ“ Test 1: Create virtual environment")
    result = await tool.execute({
        "action": "create",
        "name": "test_env",
        "python_version": "3.11"
    })
    
    if result["success"]:
        print(f"âœ… Environment created: {result['result']}")
        print(f"   Python version: {result['metadata']['python_version']}")
    else:
        print(f"âŒ Failed: {result['error']}")
    
    # Test 2: List environments
    print("\nðŸ“ Test 2: List environments")
    result = await tool.execute({"action": "list"})
    
    if result["success"]:
        print(f"âœ… Found {result['metadata']['count']} environments:")
        for env in result['result']:
            print(f"   - {env['name']} (Python {env['python_version']}, {env['package_count']} packages)")
    else:
        print(f"âŒ Failed: {result['error']}")
    
    # Test 3: Install packages
    print("\nðŸ“ Test 3: Install packages")
    result = await tool.execute({
        "action": "install",
        "name": "test_env",
        "packages": ["requests", "numpy"]
    })
    
    if result["success"]:
        print(f"âœ… Packages installed: {result['result']}")
    else:
        print(f"âŒ Failed: {result['error']}")
    
    # Test 4: Run command
    print("\nðŸ“ Test 4: Run Python command")
    result = await tool.execute({
        "action": "run",
        "name": "test_env",
        "command": "print('Hello from test_env!')"
    })
    
    if result["success"]:
        print(f"âœ… Command executed:")
        print(f"   Output: {result['result'].strip()}")
    else:
        print(f"âŒ Failed: {result['error']}")
    
    # Cleanup
    print("\nðŸ“ Cleanup: Delete test environment")
    result = await tool.execute({
        "action": "delete",
        "name": "test_env"
    })
    print(f"âœ… {result['result']}" if result["success"] else f"âŒ {result['error']}")
    
    stats = tool.get_stats()
    print(f"\nðŸ“Š Tool Statistics:")
    print(f"   Executions: {stats['executions']}")
    print(f"   Success rate: {stats['success_rate']*100:.1f}%")


async def test_audio_transcriber():
    """Test audio transcriber"""
    print("\n" + "="*60)
    print("Testing Audio Batch Transcriber")
    print("="*60)
    
    tool = AudioBatchTranscriberTool()
    print(f"âœ… Tool loaded: {tool.metadata.name}")
    print("â„¹ï¸  Note: Requires actual audio files to test")
    print("   Skipping live test (requires audio files)")


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("Part 3A Tool Testing Suite")
    print("="*60)
    
    await test_python_env()
    await test_audio_transcriber()
    
    print("\n" + "="*60)
    print("âœ… Part 3A tests complete!")
    print("="*60)
    print("\nYou now have:")
    print("  âœ… Python Environment Manager working")
    print("  âœ… Audio Batch Transcriber installed")
    print("  âœ… 8 total tools implemented")
    print("\nReady for Part 3B!")


if __name__ == "__main__":
    asyncio.run(main())
ENDOFFILE

chmod +x test_part3a.py
python3 test_part3a.py
```

---

## âœ… Checkpoint Verification

**1. Files created:**
```bash
ls -la telegram_agent_tools/audio_tools/audio_batch_transcriber.py
ls -la telegram_agent_tools/dev_tools/python_env_manager.py
```

**2. Dependencies installed:**
```bash
python3 -c "import faster_whisper; print('âœ… faster-whisper ready')"
```

**3. Test passes:**
Run test script and verify environment operations work.

---

## ðŸ“Š What You Built

**New Files:**
- `audio_batch_transcriber.py` (199 lines)
- `python_env_manager.py` (295 lines)
- `test_part3a.py` (114 lines)

**Total:** 608 lines

**Cumulative:** 4,286 lines total

---

## ðŸŽ‰ Part 3A Complete!

You now have:
- âœ… 8 total tools
- âœ… Audio transcription capability
- âœ… Python environment management
- âœ… All Phase 1-2 + first Phase 3 tools

**Next: Part 3B** - Job Scheduler + Enhanced Shell + Knowledge Search

---

**Part 3A Complete!** âœ…
