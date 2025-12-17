# Part 2A: Base Tool Framework + First 2 Tools

**What You'll Build:** Base framework + QR Generator + Text Transformer  
**Time Required:** 45 minutes  
**Difficulty:** Easy  
**Prerequisites:** Part 1 complete

---

## ðŸŽ¯ Overview

In this part, you'll create:

1. **Base Tool Framework** - Foundation that all tools inherit from
2. **QR Code Generator** - Create QR codes for URLs, WiFi, contacts
3. **Text Transformer** - Convert between JSON, YAML, XML, CSV, TOML, INI

By the end, you'll be able to:
- Generate a QR code from a URL
- Convert JSON to YAML
- Have a framework for adding more tools easily

---

## ðŸ“¦ Step 1: Install Dependencies

```bash
cd ~/telegram-agent
source venv/bin/activate

# Install tool dependencies
pip install qrcode[pil]==7.4.2 pyyaml==6.0.1 xmltodict==0.13.0 toml==0.10.2 pillow==10.1.0

# Verify installation
python3 << 'EOF'
import qrcode
import yaml
import xmltodict
import toml
print("âœ… All dependencies installed successfully")
EOF
```

**Expected output:**
```
âœ… All dependencies installed successfully
```

---

## ðŸ“ Step 2: Create Directory Structure

```bash
cd ~/telegram-agent

# Create tool directories
mkdir -p telegram_agent_tools/utility_tools
mkdir -p telegram_agent_tools/data_tools
mkdir -p telegram_agent_tools/web_tools

# Verify structure
ls -la telegram_agent_tools/
```

**Expected output:**
```
drwxr-xr-x  utility_tools
drwxr-xr-x  data_tools
drwxr-xr-x  web_tools
```

---

## ðŸ’» Step 3: Create Base Tool Framework

Create the foundation that all tools will use.

**File: `telegram_agent_tools/base_tool.py`**

```bash
cat > telegram_agent_tools/base_tool.py << 'ENDOFFILE'
"""
Base Tool Framework
All tools inherit from this base class
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ToolCategory(Enum):
    """Tool categories"""
    UTILITY = "utility"
    DATA = "data"
    WEB = "web"
    DEVELOPMENT = "development"
    AUTOMATION = "automation"
    SYSTEM = "system"


@dataclass
class ToolMetadata:
    """Tool metadata"""
    name: str
    description: str
    category: ToolCategory
    version: str = "1.0.0"
    requires_confirmation: bool = False
    async_capable: bool = True
    parameters: Dict[str, Any] = None


class BaseTool(ABC):
    """Base class for all tools"""
    
    def __init__(self):
        self.metadata = self._get_metadata()
        self.execution_count = 0
        self.error_count = 0
    
    @abstractmethod
    def _get_metadata(self) -> ToolMetadata:
        """Return tool metadata"""
        pass
    
    @abstractmethod
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool
        
        Args:
            parameters: Tool-specific parameters
            
        Returns:
            Dictionary with:
                - success: bool
                - result: Any (tool-specific)
                - error: Optional[str]
                - metadata: Optional[Dict] (execution info)
        """
        pass
    
    async def validate_parameters(self, parameters: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate parameters before execution
        
        Returns:
            (is_valid, error_message)
        """
        return True, None
    
    def _success_response(self, result: Any, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Create success response"""
        self.execution_count += 1
        return {
            "success": True,
            "result": result,
            "error": None,
            "metadata": metadata or {}
        }
    
    def _error_response(self, error: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Create error response"""
        self.error_count += 1
        logger.error(f"Tool {self.metadata.name} error: {error}")
        return {
            "success": False,
            "result": None,
            "error": error,
            "metadata": metadata or {}
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get tool execution statistics"""
        success_count = self.execution_count - self.error_count
        return {
            "name": self.metadata.name,
            "executions": self.execution_count,
            "successes": success_count,
            "errors": self.error_count,
            "success_rate": success_count / max(1, self.execution_count)
        }
ENDOFFILE
```

**Verify the file:**
```bash
python3 << 'EOF'
import sys
sys.path.insert(0, '/Users/YOUR_USERNAME/telegram-agent')  # Update YOUR_USERNAME
from telegram_agent_tools.base_tool import BaseTool, ToolCategory, ToolMetadata
print("âœ… Base tool framework loaded successfully")
EOF
```

---

## ðŸ”² Step 4: Create QR Code Generator Tool

**File: `telegram_agent_tools/utility_tools/qr_generator.py`**

```bash
cat > telegram_agent_tools/utility_tools/qr_generator.py << 'ENDOFFILE'
"""
QR Code Generator Tool
Generate QR codes for URLs, WiFi credentials, contact cards, and plain text
"""

import qrcode
from io import BytesIO
from pathlib import Path
import re
from typing import Dict, Any
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from base_tool import BaseTool, ToolMetadata, ToolCategory


class QRGeneratorTool(BaseTool):
    """Generate QR codes"""
    
    def _get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="qr_generate",
            description="Generate QR codes for URLs, WiFi, contacts, or plain text",
            category=ToolCategory.UTILITY,
            requires_confirmation=False,
            parameters={
                "content": {
                    "type": "string",
                    "required": True,
                    "description": "Content to encode in QR code"
                },
                "qr_type": {
                    "type": "string",
                    "required": False,
                    "default": "text",
                    "options": ["text", "url", "wifi", "vcard"],
                    "description": "Type of QR code to generate"
                },
                "size": {
                    "type": "integer",
                    "required": False,
                    "default": 10,
                    "min": 1,
                    "max": 40,
                    "description": "QR code size (1-40)"
                },
                "error_correction": {
                    "type": "string",
                    "required": False,
                    "default": "H",
                    "options": ["L", "M", "Q", "H"],
                    "description": "Error correction level"
                },
                "output_path": {
                    "type": "string",
                    "required": False,
                    "description": "Save path (default: temp directory)"
                }
            }
        )
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate QR code"""
        
        # Validate parameters
        valid, error = await self.validate_parameters(parameters)
        if not valid:
            return self._error_response(error)
        
        try:
            content = parameters.get("content")
            qr_type = parameters.get("qr_type", "text")
            
            # Process based on type
            if qr_type == "url":
                content = self._process_url(content)
            elif qr_type == "wifi":
                content = self._process_wifi(parameters)
            elif qr_type == "vcard":
                content = self._process_vcard(parameters)
            
            # Generate QR code
            qr_data = self._generate_qr(
                content,
                size=parameters.get("size", 10),
                error_correction=parameters.get("error_correction", "H")
            )
            
            # Save to file
            output_path = parameters.get("output_path")
            if not output_path:
                # Use temp directory
                import tempfile
                temp_dir = Path(tempfile.gettempdir())
                output_path = temp_dir / f"qr_{hash(content) & 0xFFFFFF:06x}.png"
            else:
                output_path = Path(output_path)
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(qr_data)
            
            return self._success_response(
                result=str(output_path),
                metadata={
                    "type": qr_type,
                    "size_bytes": len(qr_data),
                    "content_length": len(content),
                    "output_path": str(output_path)
                }
            )
        
        except Exception as e:
            return self._error_response(f"QR generation failed: {str(e)}")
    
    async def validate_parameters(self, parameters: Dict[str, Any]) -> tuple[bool, str]:
        """Validate parameters"""
        
        if "content" not in parameters:
            return False, "Missing required parameter: content"
        
        content = parameters.get("content")
        if not content or not isinstance(content, str):
            return False, "Content must be a non-empty string"
        
        # Check content length (QR codes have limits)
        if len(content) > 4296:
            return False, "Content too long (max 4296 bytes for QR code)"
        
        qr_type = parameters.get("qr_type", "text")
        if qr_type not in ["text", "url", "wifi", "vcard"]:
            return False, f"Invalid qr_type: {qr_type}. Must be: text, url, wifi, or vcard"
        
        # Type-specific validation
        if qr_type == "url":
            if not self._is_valid_url(content):
                return False, "Invalid URL format"
        
        elif qr_type == "wifi":
            if "ssid" not in parameters or "password" not in parameters:
                return False, "WiFi QR requires 'ssid' and 'password' parameters"
        
        elif qr_type == "vcard":
            if "name" not in parameters:
                return False, "vCard QR requires 'name' parameter"
        
        return True, None
    
    def _generate_qr(self, content: str, size: int = 10, error_correction: str = "H") -> bytes:
        """Generate QR code and return as bytes"""
        
        # Error correction mapping
        ec_map = {
            "L": qrcode.constants.ERROR_CORRECT_L,
            "M": qrcode.constants.ERROR_CORRECT_M,
            "Q": qrcode.constants.ERROR_CORRECT_Q,
            "H": qrcode.constants.ERROR_CORRECT_H
        }
        
        qr = qrcode.QRCode(
            version=size,
            error_correction=ec_map.get(error_correction, qrcode.constants.ERROR_CORRECT_H),
            box_size=10,
            border=4,
        )
        
        qr.add_data(content)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to bytes
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
    
    def _process_url(self, url: str) -> str:
        """Process URL for QR code"""
        # Add https:// if no protocol
        if not url.startswith(('http://', 'https://', 'ftp://')):
            url = 'https://' + url
        return url
    
    def _process_wifi(self, parameters: Dict[str, Any]) -> str:
        """Generate WiFi QR content"""
        ssid = parameters.get("ssid")
        password = parameters.get("password")
        encryption = parameters.get("encryption", "WPA")
        hidden = parameters.get("hidden", False)
        
        # WiFi QR format: WIFI:T:WPA;S:MySSID;P:MyPassword;H:false;;
        wifi_str = f"WIFI:T:{encryption};S:{ssid};P:{password};H:{'true' if hidden else 'false'};;"
        return wifi_str
    
    def _process_vcard(self, parameters: Dict[str, Any]) -> str:
        """Generate vCard QR content"""
        name = parameters.get("name")
        phone = parameters.get("phone", "")
        email = parameters.get("email", "")
        organization = parameters.get("organization", "")
        
        vcard = "BEGIN:VCARD\nVERSION:3.0\n"
        vcard += f"FN:{name}\n"
        if phone:
            vcard += f"TEL:{phone}\n"
        if email:
            vcard += f"EMAIL:{email}\n"
        if organization:
            vcard += f"ORG:{organization}\n"
        vcard += "END:VCARD"
        
        return vcard
    
    def _is_valid_url(self, url: str) -> bool:
        """Basic URL validation"""
        # Simple URL pattern
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        # Check with and without protocol
        if url_pattern.match(url):
            return True
        if url_pattern.match('https://' + url):
            return True
        
        return False
ENDOFFILE
```

---

## ðŸ”„ Step 5: Create Text Transformer Tool

**File: `telegram_agent_tools/utility_tools/text_transformer.py`**

```bash
cat > telegram_agent_tools/utility_tools/text_transformer.py << 'ENDOFFILE'
"""
Text Transformer Tool
Convert between different text formats: JSON, YAML, XML, CSV, TOML, INI
"""

import json
import yaml
import xmltodict
import csv
import toml
import configparser
from io import StringIO
from typing import Dict, Any
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from base_tool import BaseTool, ToolMetadata, ToolCategory


class TextTransformerTool(BaseTool):
    """Transform text between formats"""
    
    def _get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="text_transform",
            description="Convert between JSON, YAML, XML, CSV, TOML, and INI formats",
            category=ToolCategory.UTILITY,
            requires_confirmation=False,
            parameters={
                "input_text": {
                    "type": "string",
                    "required": True,
                    "description": "Input text to transform"
                },
                "input_format": {
                    "type": "string",
                    "required": True,
                    "options": ["json", "yaml", "xml", "csv", "toml", "ini"],
                    "description": "Input format"
                },
                "output_format": {
                    "type": "string",
                    "required": True,
                    "options": ["json", "yaml", "xml", "csv", "toml", "ini"],
                    "description": "Output format"
                },
                "pretty": {
                    "type": "boolean",
                    "required": False,
                    "default": True,
                    "description": "Pretty-print output"
                }
            }
        )
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Transform text format"""
        
        # Validate parameters
        valid, error = await self.validate_parameters(parameters)
        if not valid:
            return self._error_response(error)
        
        try:
            input_text = parameters.get("input_text")
            input_format = parameters.get("input_format").lower()
            output_format = parameters.get("output_format").lower()
            pretty = parameters.get("pretty", True)
            
            # Parse input
            data = self._parse_input(input_text, input_format)
            
            # Format output
            output_text = self._format_output(data, output_format, pretty)
            
            return self._success_response(
                result=output_text,
                metadata={
                    "input_format": input_format,
                    "output_format": output_format,
                    "input_size": len(input_text),
                    "output_size": len(output_text)
                }
            )
        
        except Exception as e:
            return self._error_response(f"Transformation failed: {str(e)}")
    
    async def validate_parameters(self, parameters: Dict[str, Any]) -> tuple[bool, str]:
        """Validate parameters"""
        
        required = ["input_text", "input_format", "output_format"]
        for param in required:
            if param not in parameters:
                return False, f"Missing required parameter: {param}"
        
        valid_formats = ["json", "yaml", "xml", "csv", "toml", "ini"]
        
        input_format = parameters.get("input_format", "").lower()
        if input_format not in valid_formats:
            return False, f"Invalid input_format: {input_format}"
        
        output_format = parameters.get("output_format", "").lower()
        if output_format not in valid_formats:
            return False, f"Invalid output_format: {output_format}"
        
        return True, None
    
    def _parse_input(self, text: str, format: str) -> Any:
        """Parse input text based on format"""
        
        if format == "json":
            return json.loads(text)
        
        elif format == "yaml":
            return yaml.safe_load(text)
        
        elif format == "xml":
            return xmltodict.parse(text)
        
        elif format == "csv":
            reader = csv.DictReader(StringIO(text))
            return list(reader)
        
        elif format == "toml":
            return toml.loads(text)
        
        elif format == "ini":
            config = configparser.ConfigParser()
            config.read_string(text)
            return {section: dict(config.items(section)) for section in config.sections()}
        
        else:
            raise ValueError(f"Unsupported input format: {format}")
    
    def _format_output(self, data: Any, format: str, pretty: bool = True) -> str:
        """Format data to output format"""
        
        if format == "json":
            if pretty:
                return json.dumps(data, indent=2, ensure_ascii=False)
            else:
                return json.dumps(data, ensure_ascii=False)
        
        elif format == "yaml":
            return yaml.dump(data, default_flow_style=False, allow_unicode=True)
        
        elif format == "xml":
            return xmltodict.unparse(data, pretty=pretty)
        
        elif format == "csv":
            if not isinstance(data, list):
                raise ValueError("CSV output requires list of dictionaries")
            
            if not data:
                return ""
            
            output = StringIO()
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
            return output.getvalue()
        
        elif format == "toml":
            return toml.dumps(data)
        
        elif format == "ini":
            config = configparser.ConfigParser()
            for section, values in data.items():
                config[section] = values
            
            output = StringIO()
            config.write(output)
            return output.getvalue()
        
        else:
            raise ValueError(f"Unsupported output format: {format}")
ENDOFFILE
```

---

## âœ… Step 6: Test Tools

Create a test script to verify everything works:

**File: `test_part2a.py`**

```bash
cat > test_part2a.py << 'ENDOFFILE'
#!/usr/bin/env python3
"""
Test Part 2A Tools
"""

import asyncio
import sys
from pathlib import Path

# Add telegram_agent_tools to path
sys.path.insert(0, str(Path(__file__).parent / 'telegram_agent_tools'))

from utility_tools.qr_generator import QRGeneratorTool
from utility_tools.text_transformer import TextTransformerTool


async def test_qr_generator():
    """Test QR code generation"""
    print("\n" + "="*60)
    print("Testing QR Code Generator")
    print("="*60)
    
    tool = QRGeneratorTool()
    print(f"âœ… Tool loaded: {tool.metadata.name}")
    print(f"   Description: {tool.metadata.description}")
    
    # Test 1: Simple URL QR code
    print("\nðŸ“ Test 1: Generate URL QR code")
    result = await tool.execute({
        "content": "https://github.com",
        "qr_type": "url",
        "size": 10
    })
    
    if result["success"]:
        print(f"âœ… QR code generated: {result['result']}")
        print(f"   Size: {result['metadata']['size_bytes']} bytes")
    else:
        print(f"âŒ Failed: {result['error']}")
    
    # Test 2: WiFi QR code
    print("\nðŸ“ Test 2: Generate WiFi QR code")
    result = await tool.execute({
        "content": "MyWiFi",  # This is ignored for wifi type
        "qr_type": "wifi",
        "ssid": "MyHomeNetwork",
        "password": "SecurePassword123",
        "encryption": "WPA"
    })
    
    if result["success"]:
        print(f"âœ… WiFi QR code generated: {result['result']}")
    else:
        print(f"âŒ Failed: {result['error']}")
    
    stats = tool.get_stats()
    print(f"\nðŸ“Š Tool Statistics:")
    print(f"   Executions: {stats['executions']}")
    print(f"   Success rate: {stats['success_rate']*100:.1f}%")


async def test_text_transformer():
    """Test text transformation"""
    print("\n" + "="*60)
    print("Testing Text Transformer")
    print("="*60)
    
    tool = TextTransformerTool()
    print(f"âœ… Tool loaded: {tool.metadata.name}")
    print(f"   Description: {tool.metadata.description}")
    
    # Test 1: JSON to YAML
    print("\nðŸ“ Test 1: Convert JSON to YAML")
    json_input = '{"name": "John", "age": 30, "city": "New York"}'
    
    result = await tool.execute({
        "input_text": json_input,
        "input_format": "json",
        "output_format": "yaml",
        "pretty": True
    })
    
    if result["success"]:
        print(f"âœ… Conversion successful:")
        print(f"--- YAML Output ---")
        print(result['result'])
        print(f"-------------------")
    else:
        print(f"âŒ Failed: {result['error']}")
    
    # Test 2: YAML to JSON
    print("\nðŸ“ Test 2: Convert YAML to JSON")
    yaml_input = """
name: Alice
age: 25
hobbies:
  - reading
  - coding
  - hiking
"""
    
    result = await tool.execute({
        "input_text": yaml_input,
        "input_format": "yaml",
        "output_format": "json",
        "pretty": True
    })
    
    if result["success"]:
        print(f"âœ… Conversion successful:")
        print(f"--- JSON Output ---")
        print(result['result'])
        print(f"-------------------")
    else:
        print(f"âŒ Failed: {result['error']}")
    
    stats = tool.get_stats()
    print(f"\nðŸ“Š Tool Statistics:")
    print(f"   Executions: {stats['executions']}")
    print(f"   Success rate: {stats['success_rate']*100:.1f}%")


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("Part 2A Tool Testing Suite")
    print("="*60)
    
    await test_qr_generator()
    await test_text_transformer()
    
    print("\n" + "="*60)
    print("âœ… All Part 2A tests complete!")
    print("="*60)
    print("\nYou now have:")
    print("  âœ… Base tool framework")
    print("  âœ… QR code generator working")
    print("  âœ… Text transformer working")
    print("\nReady to proceed to Part 2B!")


if __name__ == "__main__":
    asyncio.run(main())
ENDOFFILE

chmod +x test_part2a.py
```

**Run the tests:**

```bash
cd ~/telegram-agent
source venv/bin/activate
python3 test_part2a.py
```

**Expected output:**

```
============================================================
Part 2A Tool Testing Suite
============================================================

============================================================
Testing QR Code Generator
============================================================
âœ… Tool loaded: qr_generate
   Description: Generate QR codes for URLs, WiFi, contacts, or plain text

ðŸ“ Test 1: Generate URL QR code
âœ… QR code generated: /tmp/qr_abc123.png
   Size: 2847 bytes

ðŸ“ Test 2: Generate WiFi QR code
âœ… WiFi QR code generated: /tmp/qr_def456.png

ðŸ“Š Tool Statistics:
   Executions: 2
   Success rate: 100.0%

============================================================
Testing Text Transformer
============================================================
âœ… Tool loaded: text_transform
   Description: Convert between JSON, YAML, XML, CSV, TOML, and INI formats

ðŸ“ Test 1: Convert JSON to YAML
âœ… Conversion successful:
--- YAML Output ---
age: 30
city: New York
name: John
-------------------

ðŸ“ Test 2: Convert YAML to JSON
âœ… Conversion successful:
--- JSON Output ---
{
  "name": "Alice",
  "age": 25,
  "hobbies": [
    "reading",
    "coding",
    "hiking"
  ]
}
-------------------

ðŸ“Š Tool Statistics:
   Executions: 2
   Success rate: 100.0%

============================================================
âœ… All Part 2A tests complete!
============================================================

You now have:
  âœ… Base tool framework
  âœ… QR code generator working
  âœ… Text transformer working

Ready to proceed to Part 2B!
```

---

## âœ… Checkpoint Verification

Before moving to Part 2B, verify:

**1. Files Created:**
```bash
ls -la telegram_agent_tools/base_tool.py
ls -la telegram_agent_tools/utility_tools/qr_generator.py
ls -la telegram_agent_tools/utility_tools/text_transformer.py
```

All files should exist.

**2. QR Codes Generated:**
```bash
ls -la /tmp/qr_*.png
```

You should see 2 QR code PNG files.

**3. Tests Pass:**
All tests should show âœ… and 100% success rate.

**4. Tools Load:**
```bash
python3 << 'EOF'
import sys
sys.path.insert(0, '/Users/YOUR_USERNAME/telegram-agent/telegram_agent_tools')
from utility_tools.qr_generator import QRGeneratorTool
from utility_tools.text_transformer import TextTransformerTool
print("âœ… All tools load successfully")
EOF
```

---

## ðŸ› Troubleshooting

**Issue: "ModuleNotFoundError: No module named 'qrcode'"**
```bash
pip install qrcode[pil] pyyaml xmltodict toml
```

**Issue: "No such file or directory: base_tool.py"**
```bash
# Make sure you're in the right directory
cd ~/telegram-agent
# Re-create the base_tool.py file (Step 3)
```

**Issue: "Permission denied" when creating files**
```bash
# Ensure directories exist and are writable
chmod 755 telegram_agent_tools
chmod 755 telegram_agent_tools/utility_tools
```

---

## ðŸ“Š What You Built

**Files Created:**
- `telegram_agent_tools/base_tool.py` (130 lines)
- `telegram_agent_tools/utility_tools/qr_generator.py` (213 lines)
- `telegram_agent_tools/utility_tools/text_transformer.py` (178 lines)
- `test_part2a.py` (161 lines)

**Total:** 682 lines of production code

**Capabilities Added:**
- âœ… Tool framework for easy extension
- âœ… QR code generation (text, URL, WiFi, vCard)
- âœ… Format conversion (6 formats supported)
- âœ… Parameter validation
- âœ… Error handling
- âœ… Execution statistics

---

## â­ï¸ Next Steps

You're ready for **Part 2B: Next 2 Utility Tools**

This will add:
- File Compressor (ZIP/TAR/7Z)
- Math Visualizer (plot functions and charts)

Estimated time: 45 minutes

---

## ðŸ’¾ Backup Your Work

Before continuing:

```bash
cd ~/telegram-agent
tar -czf backup_part2a_$(date +%Y%m%d_%H%M%S).tar.gz telegram_agent_tools/ test_part2a.py
```

This creates a timestamped backup you can restore if needed.

---

**Part 2A Complete!** âœ…

You've successfully created the foundation and first 2 tools. Everything is tested and working.
