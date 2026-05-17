"""
Execution History - Records and manages command execution history.

Provides persistent storage of execution records with search, statistics,
and export capabilities. History is stored in ~/.agentshell/history.json.
"""

import json
import os
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class ExecutionRecord:
    """A single command execution record.

    Attributes:
        id: Unique identifier for the record.
        timestamp: Unix timestamp when the command was executed.
        command: The command that was executed.
        exit_code: Exit code of the command.
        duration: Execution duration in seconds.
        stdout: Standard output (truncated for storage).
        stderr: Standard error (truncated for storage).
        safety_report: Safety analysis report.
        working_dir: Working directory where the command was run.
        tags: Optional tags for categorization.
    """
    id: str = ""
    timestamp: float = 0.0
    command: str = ""
    exit_code: int = 0
    duration: float = 0.0
    stdout: str = ""
    stderr: str = ""
    safety_report: Dict = field(default_factory=dict)
    working_dir: str = ""
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert record to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExecutionRecord":
        """Create an ExecutionRecord from a dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


class HistoryManager:
    """Manages command execution history with persistent storage.

    Stores execution records in ~/.agentshell/history.json and provides
    search, statistics, and export functionality.
    """

    def __init__(self, history_dir: Optional[str] = None) -> None:
        """Initialize the HistoryManager.

        Args:
            history_dir: Custom directory for history storage.
                Defaults to ~/.agentshell/
        """
        if history_dir:
            self._history_dir = history_dir
        else:
            home = os.path.expanduser("~")
            self._history_dir = os.path.join(home, ".agentshell")

        self._history_file = os.path.join(self._history_dir, "history.json")
        self._records: List[ExecutionRecord] = []
        self._load()

    def _ensure_dir(self) -> None:
        """Ensure the history directory exists."""
        os.makedirs(self._history_dir, exist_ok=True)

    def _load(self) -> None:
        """Load history from disk."""
        if not os.path.exists(self._history_file):
            self._records = []
            return

        try:
            with open(self._history_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._records = [ExecutionRecord.from_dict(r) for r in data]
        except (json.JSONDecodeError, IOError, KeyError):
            self._records = []

    def _save(self) -> None:
        """Save history to disk."""
        self._ensure_dir()
        data = [r.to_dict() for r in self._records]
        try:
            with open(self._history_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError:
            pass

    def record(
        self,
        command: str,
        exit_code: int = 0,
        duration: float = 0.0,
        stdout: str = "",
        stderr: str = "",
        safety_report: Optional[Dict] = None,
        working_dir: str = "",
        tags: Optional[List[str]] = None,
    ) -> ExecutionRecord:
        """Record a command execution.

        Args:
            command: The command that was executed.
            exit_code: Exit code of the command.
            duration: Execution duration in seconds.
            stdout: Standard output (will be truncated if too long).
            stderr: Standard error (will be truncated if too long).
            safety_report: Safety analysis report dictionary.
            working_dir: Working directory where the command was run.
            tags: Optional tags for categorization.

        Returns:
            The created ExecutionRecord.
        """
        # Generate a unique ID based on timestamp and command
        record_id = f"{int(time.time() * 1000)}_{hash(command) & 0xFFFFFFFF:08x}"

        # Truncate long outputs for storage
        max_output_length = 10000
        truncated_stdout = stdout[:max_output_length]
        truncated_stderr = stderr[:max_output_length]

        record = ExecutionRecord(
            id=record_id,
            timestamp=time.time(),
            command=command,
            exit_code=exit_code,
            duration=duration,
            stdout=truncated_stdout,
            stderr=truncated_stderr,
            safety_report=safety_report or {},
            working_dir=working_dir,
            tags=tags or [],
        )

        self._records.append(record)
        self._save()
        return record

    def search(self, query: str, limit: int = 50) -> List[ExecutionRecord]:
        """Search execution history by query string.

        Searches command strings, stdout, and stderr for the query.

        Args:
            query: Search query string.
            limit: Maximum number of results to return.

        Returns:
            List of matching ExecutionRecords, most recent first.
        """
        query_lower = query.lower()
        matching: List[ExecutionRecord] = []

        for record in reversed(self._records):
            if query_lower in record.command.lower():
                matching.append(record)
            elif query_lower in record.stdout.lower():
                matching.append(record)
            elif query_lower in record.stderr.lower():
                matching.append(record)
            elif any(query_lower in tag.lower() for tag in record.tags):
                matching.append(record)

            if len(matching) >= limit:
                break

        return matching

    def stats(self) -> Dict[str, Any]:
        """Generate statistics about execution history.

        Returns:
            Dictionary with statistics including total count, success rate,
            average duration, most used commands, etc.
        """
        if not self._records:
            return {
                "total_executions": 0,
                "successful": 0,
                "failed": 0,
                "success_rate": 0.0,
                "avg_duration": 0.0,
                "most_used_commands": [],
            }

        total = len(self._records)
        successful = sum(1 for r in self._records if r.exit_code == 0)
        failed = total - successful
        durations = [r.duration for r in self._records if r.duration > 0]
        avg_duration = sum(durations) / len(durations) if durations else 0.0

        # Count command usage (base command only)
        cmd_counts: Dict[str, int] = {}
        for record in self._records:
            base_cmd = record.command.split()[0] if record.command else "unknown"
            cmd_counts[base_cmd] = cmd_counts.get(base_cmd, 0) + 1

        most_used = sorted(cmd_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        return {
            "total_executions": total,
            "successful": successful,
            "failed": failed,
            "success_rate": round(successful / total * 100, 1) if total > 0 else 0.0,
            "avg_duration": round(avg_duration, 4),
            "most_used_commands": [
                {"command": cmd, "count": count} for cmd, count in most_used
            ],
            "first_execution": datetime.fromtimestamp(
                self._records[0].timestamp
            ).isoformat() if self._records else None,
            "last_execution": datetime.fromtimestamp(
                self._records[-1].timestamp
            ).isoformat() if self._records else None,
        }

    def export(self, format: str = "json") -> str:
        """Export execution history in the specified format.

        Args:
            format: Export format. Currently supports 'json' and 'text'.

        Returns:
            String representation of the history.

        Raises:
            ValueError: If the format is not supported.
        """
        if format == "json":
            data = [r.to_dict() for r in self._records]
            return json.dumps(data, indent=2, ensure_ascii=False)
        elif format == "text":
            lines: List[str] = []
            for record in self._records:
                dt = datetime.fromtimestamp(record.timestamp).strftime("%Y-%m-%d %H:%M:%S")
                status = "OK" if record.exit_code == 0 else f"FAIL({record.exit_code})"
                lines.append(f"[{dt}] [{status}] {record.command}")
                if record.duration > 0:
                    lines.append(f"  Duration: {record.duration:.3f}s")
                if record.stderr:
                    lines.append(f"  Error: {record.stderr[:200]}")
            return "\n".join(lines)
        else:
            raise ValueError(f"Unsupported export format: {format}. Use 'json' or 'text'.")

    def clear(self) -> None:
        """Clear all execution history."""
        self._records = []
        self._save()

    @property
    def records(self) -> List[ExecutionRecord]:
        """Get all execution records."""
        return list(self._records)

    @property
    def count(self) -> int:
        """Get the number of execution records."""
        return len(self._records)
