"""Tests for Sandbox Execution Engine module."""

import unittest
from unittest.mock import patch, MagicMock

from agentshell.sandbox import (
    DANGEROUS_COMMANDS,
    DANGEROUS_PATTERNS,
    DISK_WRITE_PATTERNS,
    NETWORK_ACCESS_PATTERNS,
    ExecutionResult,
    SafeExecutor,
)


class TestDangerousCommands(unittest.TestCase):
    """Tests for dangerous command constants."""

    def test_dangerous_commands_not_empty(self):
        """Test that dangerous commands list is not empty."""
        self.assertGreater(len(DANGEROUS_COMMANDS), 0)

    def test_dangerous_patterns_not_empty(self):
        """Test that dangerous patterns list is not empty."""
        self.assertGreater(len(DANGEROUS_PATTERNS), 0)

    def test_disk_write_patterns_not_empty(self):
        """Test that disk write patterns list is not empty."""
        self.assertGreater(len(DISK_WRITE_PATTERNS), 0)

    def test_network_patterns_not_empty(self):
        """Test that network access patterns list is not empty."""
        self.assertGreater(len(NETWORK_ACCESS_PATTERNS), 0)


class TestExecutionResult(unittest.TestCase):
    """Tests for ExecutionResult dataclass."""

    def test_success_property(self):
        """Test success property with exit code 0."""
        result = ExecutionResult(code=0, stdout="ok", stderr="", duration=0.1)
        self.assertTrue(result.success)

    def test_failure_property(self):
        """Test success property with non-zero exit code."""
        result = ExecutionResult(code=1, stdout="", stderr="error", duration=0.1)
        self.assertFalse(result.success)

    def test_to_dict(self):
        """Test converting result to dictionary."""
        result = ExecutionResult(
            code=0,
            stdout="output",
            stderr="errors",
            duration=1.5,
            safety_report={"has_disk_write": False},
            command="echo hello",
        )
        d = result.to_dict()
        self.assertEqual(d["code"], 0)
        self.assertEqual(d["stdout"], "output")
        self.assertEqual(d["stderr"], "errors")
        self.assertEqual(d["duration"], 1.5)
        self.assertEqual(d["command"], "echo hello")
        self.assertIn("has_disk_write", d["safety_report"])

    def test_default_safety_report(self):
        """Test default safety report is empty dict."""
        result = ExecutionResult(code=0, stdout="", stderr="", duration=0.0)
        self.assertEqual(result.safety_report, {})


class TestSafeExecutor(unittest.TestCase):
    """Tests for SafeExecutor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.executor = SafeExecutor(default_timeout=10)

    def test_validate_safe_command(self):
        """Test validating a safe command."""
        is_safe, warnings = self.executor.validate_command("echo hello")
        self.assertTrue(is_safe)
        self.assertEqual(len(warnings), 0)

    def test_validate_dangerous_rm_rf(self):
        """Test that rm -rf / is detected as dangerous."""
        is_safe, warnings = self.executor.validate_command("rm -rf /")
        self.assertFalse(is_safe)
        self.assertGreater(len(warnings), 0)

    def test_validate_dangerous_shutdown(self):
        """Test that shutdown is detected as dangerous."""
        is_safe, warnings = self.executor.validate_command("shutdown -h now")
        self.assertFalse(is_safe)
        self.assertGreater(len(warnings), 0)

    def test_validate_dangerous_mkfs(self):
        """Test that mkfs is detected as dangerous."""
        is_safe, warnings = self.executor.validate_command("mkfs.ext4 /dev/sda1")
        self.assertFalse(is_safe)
        self.assertGreater(len(warnings), 0)

    def test_validate_dangerous_dd(self):
        """Test that dd to /dev/ is detected as dangerous."""
        is_safe, warnings = self.executor.validate_command("dd if=/dev/zero of=/dev/sda")
        self.assertFalse(is_safe)
        self.assertGreater(len(warnings), 0)

    def test_validate_blocked_command(self):
        """Test custom blocked commands."""
        executor = SafeExecutor(blocked_commands=["custom_danger"])
        is_safe, warnings = executor.validate_command("custom_danger --force")
        self.assertFalse(is_safe)
        self.assertGreater(len(warnings), 0)

    def test_validate_allowed_command(self):
        """Test allowlist mode."""
        executor = SafeExecutor(allowed_commands=["echo", "ls"])
        is_safe, warnings = executor.validate_command("echo hello")
        self.assertTrue(is_safe)

    def test_validate_not_allowed_command(self):
        """Test that non-allowed command is rejected in allowlist mode."""
        executor = SafeExecutor(allowed_commands=["echo", "ls"])
        is_safe, warnings = executor.validate_command("rm file.txt")
        self.assertFalse(is_safe)
        self.assertGreater(len(warnings), 0)

    def test_check_disk_write_redirect(self):
        """Test detecting disk write via redirect."""
        self.assertTrue(self.executor.check_disk_write("echo hello > /tmp/test.txt"))

    def test_check_disk_write_append(self):
        """Test detecting disk write via append redirect."""
        self.assertTrue(self.executor.check_disk_write("echo hello >> /tmp/test.txt"))

    def test_check_disk_write_touch(self):
        """Test detecting disk write via touch."""
        self.assertTrue(self.executor.check_disk_write("touch /tmp/newfile.txt"))

    def test_check_disk_write_cp(self):
        """Test detecting disk write via cp."""
        self.assertTrue(self.executor.check_disk_write("cp a.txt b.txt"))

    def test_check_disk_write_safe(self):
        """Test that read-only command is not flagged as disk write."""
        self.assertFalse(self.executor.check_disk_write("cat /tmp/file.txt"))

    def test_check_network_curl(self):
        """Test detecting network access via curl."""
        self.assertTrue(self.executor.check_network_access("curl https://example.com"))

    def test_check_network_wget(self):
        """Test detecting network access via wget."""
        self.assertTrue(self.executor.check_network_access("wget https://example.com"))

    def test_check_network_ssh(self):
        """Test detecting network access via ssh."""
        self.assertTrue(self.executor.check_network_access("ssh user@host"))

    def test_check_network_safe(self):
        """Test that local command is not flagged as network access."""
        self.assertFalse(self.executor.check_network_access("cat /tmp/file.txt"))

    def test_execute_safe_command(self):
        """Test executing a safe command."""
        result = self.executor.execute("echo hello")
        self.assertTrue(result.success)
        self.assertEqual(result.code, 0)
        self.assertIn("hello", result.stdout)
        self.assertGreater(result.duration, 0)

    def test_execute_dangerous_command_blocked(self):
        """Test that dangerous command is blocked."""
        result = self.executor.execute("rm -rf /")
        self.assertFalse(result.success)
        self.assertEqual(result.code, -1)
        self.assertIn("blocked", result.stderr.lower())

    def test_execute_timeout(self):
        """Test command timeout."""
        result = self.executor.execute("sleep 10", timeout=1)
        self.assertFalse(result.success)
        self.assertEqual(result.code, -2)
        self.assertIn("timed out", result.stderr.lower())

    def test_execute_with_env_vars(self):
        """Test executing command with custom environment variables."""
        result = self.executor.execute("echo $MY_TEST_VAR", env_vars={"MY_TEST_VAR": "test_value"})
        self.assertTrue(result.success)
        self.assertIn("test_value", result.stdout)

    def test_execute_safety_report(self):
        """Test that safety report is populated."""
        result = self.executor.execute("echo hello")
        self.assertIn("has_disk_write", result.safety_report)
        self.assertIn("has_network_access", result.safety_report)
        self.assertIn("dangerous_patterns_found", result.safety_report)
        self.assertIn("blocked_patterns_found", result.safety_report)

    def test_execute_network_detection_in_report(self):
        """Test that network access is detected in safety report."""
        result = self.executor.execute("echo test")  # no network
        self.assertFalse(result.safety_report["has_network_access"])

    def test_extract_base_command(self):
        """Test base command extraction."""
        self.assertEqual(SafeExecutor._extract_base_command("ls -la"), "ls")
        self.assertEqual(SafeExecutor._extract_base_command("/usr/bin/python3 script.py"), "python3")
        self.assertEqual(SafeExecutor._extract_base_command("echo 'hello world'"), "echo")

    def test_execute_with_blocked_override(self):
        """Test execute with per-execution blocked commands."""
        result = self.executor.execute("echo test", blocked_commands=["echo"])
        self.assertFalse(result.success)
        self.assertEqual(result.code, -1)

    def test_execute_invalid_command(self):
        """Test executing a non-existent command."""
        result = self.executor.execute("nonexistent_command_xyz_12345")
        self.assertFalse(result.success)
        self.assertNotEqual(result.code, 0)


if __name__ == "__main__":
    unittest.main()
