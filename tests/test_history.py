"""Tests for Execution History module."""

import json
import os
import tempfile
import unittest

from agentshell.history import ExecutionRecord, HistoryManager


class TestExecutionRecord(unittest.TestCase):
    """Tests for ExecutionRecord dataclass."""

    def test_create_record(self):
        """Test creating a basic execution record."""
        record = ExecutionRecord(
            id="test_001",
            timestamp=1000000.0,
            command="echo hello",
            exit_code=0,
            duration=0.05,
            stdout="hello\n",
            stderr="",
        )
        self.assertEqual(record.id, "test_001")
        self.assertEqual(record.command, "echo hello")
        self.assertEqual(record.exit_code, 0)
        self.assertTrue(record.stdout, "hello\n")

    def test_to_dict(self):
        """Test converting record to dictionary."""
        record = ExecutionRecord(
            id="test_002",
            timestamp=2000000.0,
            command="ls",
            exit_code=0,
            duration=0.1,
            stdout="file1\nfile2\n",
            stderr="",
            tags=["test"],
        )
        d = record.to_dict()
        self.assertEqual(d["id"], "test_002")
        self.assertEqual(d["command"], "ls")
        self.assertEqual(d["tags"], ["test"])

    def test_from_dict(self):
        """Test creating record from dictionary."""
        data = {
            "id": "test_003",
            "timestamp": 3000000.0,
            "command": "pwd",
            "exit_code": 0,
            "duration": 0.01,
            "stdout": "/home\n",
            "stderr": "",
            "safety_report": {"has_disk_write": False},
            "working_dir": "/home",
            "tags": [],
        }
        record = ExecutionRecord.from_dict(data)
        self.assertEqual(record.id, "test_003")
        self.assertEqual(record.command, "pwd")
        self.assertEqual(record.safety_report["has_disk_write"], False)

    def test_default_values(self):
        """Test default values of ExecutionRecord."""
        record = ExecutionRecord()
        self.assertEqual(record.id, "")
        self.assertEqual(record.timestamp, 0.0)
        self.assertEqual(record.command, "")
        self.assertEqual(record.exit_code, 0)
        self.assertEqual(record.duration, 0.0)
        self.assertEqual(record.stdout, "")
        self.assertEqual(record.stderr, "")
        self.assertEqual(record.safety_report, {})
        self.assertEqual(record.working_dir, "")
        self.assertEqual(record.tags, [])


class TestHistoryManager(unittest.TestCase):
    """Tests for HistoryManager class."""

    def setUp(self):
        """Set up test fixtures with a temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = HistoryManager(history_dir=self.temp_dir)

    def tearDown(self):
        """Clean up temporary directory."""
        # Remove history file and directory
        history_file = os.path.join(self.temp_dir, "history.json")
        if os.path.exists(history_file):
            os.remove(history_file)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)

    def test_initial_empty_history(self):
        """Test that new manager starts with empty history."""
        self.assertEqual(self.manager.count, 0)
        self.assertEqual(self.manager.records, [])

    def test_record_execution(self):
        """Test recording a command execution."""
        record = self.manager.record(
            command="echo hello",
            exit_code=0,
            duration=0.05,
            stdout="hello\n",
        )
        self.assertIsNotNone(record.id)
        self.assertGreater(record.timestamp, 0)
        self.assertEqual(record.command, "echo hello")
        self.assertEqual(self.manager.count, 1)

    def test_record_multiple(self):
        """Test recording multiple executions."""
        self.manager.record("echo a", exit_code=0)
        self.manager.record("echo b", exit_code=0)
        self.manager.record("echo c", exit_code=1)
        self.assertEqual(self.manager.count, 3)

    def test_record_with_tags(self):
        """Test recording with tags."""
        record = self.manager.record(
            command="npm install",
            tags=["npm", "install"],
        )
        self.assertEqual(record.tags, ["npm", "install"])

    def test_record_with_safety_report(self):
        """Test recording with safety report."""
        report = {"has_disk_write": True, "has_network_access": False}
        record = self.manager.record(
            command="touch file.txt",
            safety_report=report,
        )
        self.assertEqual(record.safety_report, report)

    def test_search_by_command(self):
        """Test searching history by command string."""
        self.manager.record("git status")
        self.manager.record("git log")
        self.manager.record("npm install")

        results = self.manager.search("git")
        self.assertEqual(len(results), 2)

    def test_search_by_stdout(self):
        """Test searching history by stdout content."""
        self.manager.record("echo hello", stdout="hello\n")
        self.manager.record("echo world", stdout="world\n")

        results = self.manager.search("hello")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].command, "echo hello")

    def test_search_by_tag(self):
        """Test searching history by tag."""
        self.manager.record("npm install", tags=["npm"])
        self.manager.record("pip install", tags=["pip"])

        results = self.manager.search("npm")
        self.assertEqual(len(results), 1)

    def test_search_no_results(self):
        """Test searching with no matching results."""
        self.manager.record("echo hello")
        results = self.manager.search("nonexistent_xyz")
        self.assertEqual(len(results), 0)

    def test_search_limit(self):
        """Test search result limit."""
        for i in range(10):
            self.manager.record(f"echo test{i}")

        results = self.manager.search("echo", limit=3)
        self.assertEqual(len(results), 3)

    def test_search_most_recent_first(self):
        """Test that search returns most recent results first."""
        self.manager.record("echo first")
        self.manager.record("echo second")
        self.manager.record("echo third")

        results = self.manager.search("echo")
        self.assertEqual(results[0].command, "echo third")
        self.assertEqual(results[1].command, "echo second")
        self.assertEqual(results[2].command, "echo first")

    def test_stats_empty(self):
        """Test statistics with empty history."""
        stats = self.manager.stats()
        self.assertEqual(stats["total_executions"], 0)
        self.assertEqual(stats["successful"], 0)
        self.assertEqual(stats["failed"], 0)
        self.assertEqual(stats["success_rate"], 0.0)

    def test_stats_with_records(self):
        """Test statistics with recorded executions."""
        self.manager.record("echo ok", exit_code=0)
        self.manager.record("echo ok2", exit_code=0)
        self.manager.record("false", exit_code=1)

        stats = self.manager.stats()
        self.assertEqual(stats["total_executions"], 3)
        self.assertEqual(stats["successful"], 2)
        self.assertEqual(stats["failed"], 1)
        self.assertAlmostEqual(stats["success_rate"], 66.7, places=0)

    def test_stats_most_used_commands(self):
        """Test most used commands in statistics."""
        self.manager.record("git status")
        self.manager.record("git log")
        self.manager.record("git diff")
        self.manager.record("npm install")

        stats = self.manager.stats()
        most_used = stats["most_used_commands"]
        self.assertEqual(most_used[0]["command"], "git")
        self.assertEqual(most_used[0]["count"], 3)

    def test_export_json(self):
        """Test exporting history as JSON."""
        self.manager.record("echo hello", exit_code=0)
        self.manager.record("echo world", exit_code=0)

        exported = self.manager.export(format="json")
        data = json.loads(exported)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["command"], "echo hello")
        self.assertEqual(data[1]["command"], "echo world")

    def test_export_text(self):
        """Test exporting history as text."""
        self.manager.record("echo hello", exit_code=0, duration=0.1)

        exported = self.manager.export(format="text")
        self.assertIn("echo hello", exported)
        self.assertIn("OK", exported)

    def test_export_invalid_format(self):
        """Test exporting with invalid format raises ValueError."""
        with self.assertRaises(ValueError):
            self.manager.export(format="xml")

    def test_clear_history(self):
        """Test clearing all history."""
        self.manager.record("echo a")
        self.manager.record("echo b")
        self.assertEqual(self.manager.count, 2)

        self.manager.clear()
        self.assertEqual(self.manager.count, 0)

    def test_persistence(self):
        """Test that history persists across manager instances."""
        self.manager.record("echo persistent", exit_code=0)

        # Create a new manager with the same directory
        new_manager = HistoryManager(history_dir=self.temp_dir)
        self.assertEqual(new_manager.count, 1)
        self.assertEqual(new_manager.records[0].command, "echo persistent")

    def test_long_output_truncation(self):
        """Test that long outputs are truncated in records."""
        long_output = "x" * 20000
        record = self.manager.record("echo long", stdout=long_output)
        self.assertLessEqual(len(record.stdout), 10000)


if __name__ == "__main__":
    unittest.main()
