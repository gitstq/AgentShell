"""
Sandbox Execution Engine - Provides safe execution of shell commands
with security validation, timeout control, and resource monitoring.
"""

import os
import re
import shlex
import subprocess
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# Dangerous command patterns that should be blocked by default
DANGEROUS_COMMANDS: List[str] = [
    "rm -rf /",
    "rm -rf /*",
    "mkfs",
    "dd if=",
    "> /dev/sda",
    "> /dev/sdb",
    ":(){ :|:& };:",
    "chmod -R 777 /",
    "chown -R",
    "mv / /dev",
    "shutdown",
    "reboot",
    "halt",
    "poweroff",
    "init 0",
    "init 6",
]

# Patterns for detecting dangerous commands using regex
DANGEROUS_PATTERNS: List[re.Pattern] = [
    re.compile(r"rm\s+(-[a-zA-Z]*f[a-zA-Z]*\s+)?(-[a-zA-Z]*r[a-zA-Z]*\s+)?/\s*$", re.IGNORECASE),
    re.compile(r"rm\s+(-[a-zA-Z]*r[a-zA-Z]*\s+)?(-[a-zA-Z]*f[a-zA-Z]*\s+)?/\s*$", re.IGNORECASE),
    re.compile(r"mkfs\b", re.IGNORECASE),
    re.compile(r"dd\s+.*of=/dev/", re.IGNORECASE),
    re.compile(r">\s*/dev/sd[a-z]", re.IGNORECASE),
    re.compile(r"chmod\s+(-[a-zA-Z]*R[a-zA-Z]*\s+)?777\s+/", re.IGNORECASE),
    re.compile(r"shutdown\b", re.IGNORECASE),
    re.compile(r"\breboot\b", re.IGNORECASE),
    re.compile(r"\bhalt\b", re.IGNORECASE),
    re.compile(r"\bpoweroff\b", re.IGNORECASE),
    re.compile(r">\s*/dev/null\s*;\s*rm\s+", re.IGNORECASE),
    re.compile(r"fork\s*bomb", re.IGNORECASE),
    re.compile(r":\(\)\s*\{", re.IGNORECASE),
]

# Patterns indicating disk write operations
DISK_WRITE_PATTERNS: List[re.Pattern] = [
    re.compile(r">\s*\S"),           # Redirect output to file
    re.compile(r">>\s*\S"),          # Append output to file
    re.compile(r"\btee\b", re.IGNORECASE),
    re.compile(r"\bcp\b", re.IGNORECASE),
    re.compile(r"\bmv\b", re.IGNORECASE),
    re.compile(r"\btouch\b", re.IGNORECASE),
    re.compile(r"\bmkdir\b", re.IGNORECASE),
    re.compile(r"\binstall\b", re.IGNORECASE),
    re.compile(r"\bln\b", re.IGNORECASE),
    re.compile(r"\bmv\b", re.IGNORECASE),
]

# Patterns indicating network access
NETWORK_ACCESS_PATTERNS: List[re.Pattern] = [
    re.compile(r"\bcurl\b", re.IGNORECASE),
    re.compile(r"\bwget\b", re.IGNORECASE),
    re.compile(r"\bnc\b\s", re.IGNORECASE),
    re.compile(r"\bnetcat\b", re.IGNORECASE),
    re.compile(r"\bping\b", re.IGNORECASE),
    re.compile(r"\bssh\b", re.IGNORECASE),
    re.compile(r"\bscp\b", re.IGNORECASE),
    re.compile(r"\bsftp\b", re.IGNORECASE),
    re.compile(r"\bftp\b", re.IGNORECASE),
    re.compile(r"\btelnet\b", re.IGNORECASE),
    re.compile(r"\bnslookup\b", re.IGNORECASE),
    re.compile(r"\bdig\b", re.IGNORECASE),
    re.compile(r"\bpython\s.*-m\s+http", re.IGNORECASE),
    re.compile(r"\bncat\b", re.IGNORECASE),
    re.compile(r"\bsocat\b", re.IGNORECASE),
]


@dataclass
class ExecutionResult:
    """Result of a command execution in the sandbox.

    Attributes:
        code: Exit code of the command.
        stdout: Standard output captured from the command.
        stderr: Standard error captured from the command.
        duration: Execution time in seconds.
        safety_report: Report on safety checks performed.
        command: The original command that was executed.
    """
    code: int
    stdout: str
    stderr: str
    duration: float
    safety_report: Dict = field(default_factory=dict)
    command: str = ""

    def to_dict(self) -> Dict:
        """Convert result to dictionary."""
        return {
            "command": self.command,
            "code": self.code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "duration": round(self.duration, 4),
            "safety_report": self.safety_report,
        }

    @property
    def success(self) -> bool:
        """Whether the command executed successfully (exit code 0)."""
        return self.code == 0


class SafeExecutor:
    """Secure sandbox executor for running shell commands.

    Provides safety validation, timeout control, and execution
    environment management for shell commands.
    """

    def __init__(
        self,
        blocked_commands: Optional[List[str]] = None,
        allowed_commands: Optional[List[str]] = None,
        default_timeout: int = 30,
        working_dir: Optional[str] = None,
    ) -> None:
        """Initialize the SafeExecutor.

        Args:
            blocked_commands: Additional commands to block (on top of defaults).
            allowed_commands: If set, only these commands are allowed (whitelist mode).
            default_timeout: Default timeout in seconds for command execution.
            working_dir: Default working directory for command execution.
        """
        self.blocked_commands = blocked_commands or []
        self.allowed_commands = allowed_commands
        self.default_timeout = default_timeout
        self.working_dir = working_dir

    def validate_command(self, command: str) -> Tuple[bool, List[str]]:
        """Validate a command against safety rules.

        Checks the command against dangerous patterns, blocked commands,
        and optionally an allowlist.

        Args:
            command: The shell command string to validate.

        Returns:
            Tuple of (is_safe, list_of_warnings).
        """
        warnings: List[str] = []

        # Check against dangerous patterns
        for pattern in DANGEROUS_PATTERNS:
            if pattern.search(command):
                warnings.append(
                    f"DANGEROUS: Command matches dangerous pattern: {pattern.pattern}"
                )

        # Check against dangerous command list
        for dangerous in DANGEROUS_COMMANDS:
            if dangerous.lower() in command.lower():
                warnings.append(
                    f"DANGEROUS: Command contains dangerous string: '{dangerous}'"
                )

        # Check against custom blocked commands
        for blocked in self.blocked_commands:
            if blocked.lower() in command.lower():
                warnings.append(f"BLOCKED: Command matches blocked pattern: '{blocked}'")

        # If allowlist is set, check against it
        if self.allowed_commands:
            base_cmd = self._extract_base_command(command)
            if base_cmd not in self.allowed_commands:
                warnings.append(
                    f"NOT_ALLOWED: Command '{base_cmd}' is not in the allowed commands list."
                )

        is_safe = len(warnings) == 0
        return is_safe, warnings

    def check_disk_write(self, command: str) -> bool:
        """Check if a command may perform disk write operations.

        Args:
            command: The shell command string to check.

        Returns:
            True if the command may write to disk.
        """
        for pattern in DISK_WRITE_PATTERNS:
            if pattern.search(command):
                return True
        return False

    def check_network_access(self, command: str) -> bool:
        """Check if a command may access the network.

        Args:
            command: The shell command string to check.

        Returns:
            True if the command may access the network.
        """
        for pattern in NETWORK_ACCESS_PATTERNS:
            if pattern.search(command):
                return True
        return False

    def execute(
        self,
        command: str,
        timeout: Optional[int] = None,
        allowed_commands: Optional[List[str]] = None,
        blocked_commands: Optional[List[str]] = None,
        working_dir: Optional[str] = None,
        env_vars: Optional[Dict[str, str]] = None,
    ) -> ExecutionResult:
        """Execute a command in the sandbox with safety checks.

        Args:
            command: The shell command to execute.
            timeout: Execution timeout in seconds (overrides default).
            allowed_commands: Override allowed commands for this execution.
            blocked_commands: Additional blocked commands for this execution.
            working_dir: Working directory for this execution.
            env_vars: Additional environment variables.

        Returns:
            ExecutionResult with exit code, output, and safety report.
        """
        effective_timeout = timeout if timeout is not None else self.default_timeout
        effective_working_dir = working_dir or self.working_dir

        # Build safety report
        safety_report: Dict = {
            "has_disk_write": self.check_disk_write(command),
            "has_network_access": self.check_network_access(command),
            "dangerous_patterns_found": [],
            "blocked_patterns_found": [],
        }

        # Validate command
        original_blocked = self.blocked_commands
        original_allowed = self.allowed_commands

        if blocked_commands is not None:
            self.blocked_commands = original_blocked + blocked_commands
        if allowed_commands is not None:
            self.allowed_commands = allowed_commands

        is_safe, warnings = self.validate_command(command)

        self.blocked_commands = original_blocked
        self.allowed_commands = original_allowed

        for w in warnings:
            if w.startswith("DANGEROUS:"):
                safety_report["dangerous_patterns_found"].append(w)
            elif w.startswith("BLOCKED:") or w.startswith("NOT_ALLOWED:"):
                safety_report["blocked_patterns_found"].append(w)

        # Refuse to execute dangerous commands
        if safety_report["dangerous_patterns_found"]:
            return ExecutionResult(
                code=-1,
                stdout="",
                stderr=f"Command blocked by safety checks: {'; '.join(safety_report['dangerous_patterns_found'])}",
                duration=0.0,
                safety_report=safety_report,
                command=command,
            )

        if safety_report["blocked_patterns_found"]:
            return ExecutionResult(
                code=-1,
                stdout="",
                stderr=f"Command blocked: {'; '.join(safety_report['blocked_patterns_found'])}",
                duration=0.0,
                safety_report=safety_report,
                command=command,
            )

        # Prepare environment
        env = None
        if env_vars:
            env = os.environ.copy()
            env.update(env_vars)

        # Execute the command
        start_time = time.time()
        try:
            # Use shell=True to support pipes and redirections
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=effective_timeout,
                cwd=effective_working_dir,
                env=env,
            )
            duration = time.time() - start_time
            return ExecutionResult(
                code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                duration=duration,
                safety_report=safety_report,
                command=command,
            )
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return ExecutionResult(
                code=-2,
                stdout="",
                stderr=f"Command timed out after {effective_timeout} seconds",
                duration=duration,
                safety_report=safety_report,
                command=command,
            )
        except Exception as e:
            duration = time.time() - start_time
            return ExecutionResult(
                code=-3,
                stdout="",
                stderr=f"Execution error: {str(e)}",
                duration=duration,
                safety_report=safety_report,
                command=command,
            )

    @staticmethod
    def _extract_base_command(command: str) -> str:
        """Extract the base command name from a command string.

        Args:
            command: The shell command string.

        Returns:
            The base command name (first word).
        """
        try:
            parts = shlex.split(command)
            if parts:
                return os.path.basename(parts[0])
        except ValueError:
            # Fall back to simple split if shlex fails
            parts = command.split()
            if parts:
                return os.path.basename(parts[0])
        return ""
