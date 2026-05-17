"""Tests for CLI Analyzer module."""

import unittest
from unittest.mock import patch, MagicMock

from agentshell.cli_analyzer import (
    CLIAnalysisResult,
    command_exists,
    parse_help_output,
    generate_tool_schema,
    _parse_option_string,
)


class TestCommandExists(unittest.TestCase):
    """Tests for command_exists function."""

    @patch("agentshell.cli_analyzer.shutil.which")
    def test_command_exists_found(self, mock_which):
        """Test that existing command returns True."""
        mock_which.return_value = "/usr/bin/ls"
        self.assertTrue(command_exists("ls"))

    @patch("agentshell.cli_analyzer.shutil.which")
    def test_command_exists_not_found(self, mock_which):
        """Test that missing command returns False."""
        mock_which.return_value = None
        self.assertFalse(command_exists("nonexistent_cmd_xyz"))

    @patch("agentshell.cli_analyzer.shutil.which")
    def test_command_exists_empty(self, mock_which):
        """Test that empty command returns False."""
        mock_which.return_value = None
        self.assertFalse(command_exists(""))


class TestParseHelpOutput(unittest.TestCase):
    """Tests for parse_help_output function."""

    def test_parse_git_help(self):
        """Test parsing git-style help output."""
        help_text = """\
usage: git [--version] [--help] [-C <path>] [-c <name>=<value>]

These are common Git commands used in various situations:

start a working area (see also: git help tutorial)
   clone      Clone a repository into a new directory
   init       Create an empty Git repository or reinitialize an existing one

work on the current change (see also: git help everyday)
   add        Add file contents to the index
   mv         Move or rename a file, a directory, or a symlink
   reset      Reset current HEAD to the specified state

options:
   -v, --verbose         be more verbose
   -q, --quiet           be more quiet
   --cached              only show the cached changes
"""
        result = parse_help_output(help_text, "git")

        self.assertEqual(result.command_name, "git")
        self.assertIsInstance(result.subcommands, list)
        self.assertGreater(len(result.subcommands), 0)
        # Check that common subcommands are detected
        sub_names = [sc["name"] for sc in result.subcommands]
        self.assertIn("clone", sub_names)
        self.assertIn("init", sub_names)
        self.assertIn("add", sub_names)

        # Check options
        self.assertGreater(len(result.options), 0)
        opt_names = [opt["name"] for opt in result.options]
        self.assertIn("verbose", opt_names)
        self.assertIn("quiet", opt_names)

    def test_parse_ls_help(self):
        """Test parsing ls-style help output."""
        help_text = """\
Usage: ls [OPTION]... [FILE]...
List information about the FILEs (the current directory by default).

Mandatory arguments to long options are mandatory for short options too.
  -a, --all                  do not ignore entries starting with .
  -A, --almost-all           do not list implied . and ..
  -l                         use a long listing format
  -h, --human-readable       with -l, print sizes in human readable format
  -t                         sort by modification time, newest first
"""
        result = parse_help_output(help_text, "ls")

        self.assertEqual(result.command_name, "ls")
        self.assertGreater(len(result.options), 0)

    def test_parse_empty_help(self):
        """Test parsing empty help text."""
        result = parse_help_output("", "test")
        self.assertEqual(result.command_name, "test")
        self.assertEqual(result.description, "")
        self.assertEqual(result.subcommands, [])
        self.assertEqual(result.options, [])

    def test_parse_minimal_help(self):
        """Test parsing minimal help text."""
        help_text = "mytool - does something useful"
        result = parse_help_output(help_text, "mytool")
        self.assertEqual(result.command_name, "mytool")
        self.assertIn("mytool", result.description)

    def test_parse_with_arguments(self):
        """Test parsing help text with positional arguments."""
        help_text = """\
Usage: cp [OPTION]... SOURCE DEST
Copy SOURCE to DEST.

  -r     copy directories recursively
  -v     explain what is being done
"""
        result = parse_help_output(help_text, "cp")
        self.assertEqual(result.command_name, "cp")
        self.assertGreater(len(result.options), 0)


class TestParseOptionString(unittest.TestCase):
    """Tests for _parse_option_string helper function."""

    def test_short_option(self):
        """Test parsing a short option."""
        result = _parse_option_string("-v", "be verbose")
        self.assertEqual(result["name"], "v")
        self.assertEqual(result["flags"], ["-v"])
        self.assertEqual(result["type"], "boolean")

    def test_long_option(self):
        """Test parsing a long option."""
        result = _parse_option_string("--verbose", "be verbose")
        self.assertEqual(result["name"], "verbose")
        self.assertEqual(result["flags"], ["--verbose"])
        self.assertEqual(result["type"], "boolean")

    def test_combined_option(self):
        """Test parsing combined short and long options."""
        result = _parse_option_string("-f, --file FILE", "output file")
        self.assertEqual(result["name"], "file")
        self.assertIn("-f", result["flags"])
        self.assertIn("--file", result["flags"])
        self.assertEqual(result["parameter"], "FILE")
        self.assertEqual(result["type"], "string")

    def test_option_with_port(self):
        """Test parsing option with port parameter."""
        result = _parse_option_string("--port PORT", "server port")
        self.assertEqual(result["name"], "port")
        self.assertEqual(result["parameter"], "PORT")
        self.assertEqual(result["type"], "integer")

    def test_option_with_file(self):
        """Test parsing option with file parameter."""
        result = _parse_option_string("--config FILE", "config file path")
        self.assertEqual(result["name"], "config")
        self.assertEqual(result["parameter"], "FILE")
        self.assertEqual(result["type"], "string")


class TestGenerateToolSchema(unittest.TestCase):
    """Tests for generate_tool_schema function."""

    def test_schema_from_analysis_result(self):
        """Test generating schema from a pre-computed analysis result."""
        analysis = CLIAnalysisResult(
            command_name="testcmd",
            description="A test command for unit testing",
            subcommands=[
                {"name": "run", "description": "Run something"},
                {"name": "stop", "description": "Stop something"},
            ],
            options=[
                {
                    "name": "verbose",
                    "flags": ["-v", "--verbose"],
                    "parameter": "",
                    "description": "Enable verbose output",
                    "type": "boolean",
                },
                {
                    "name": "output",
                    "flags": ["-o", "--output"],
                    "parameter": "FILE",
                    "description": "Output file path",
                    "type": "string",
                },
            ],
        )

        schema = generate_tool_schema("testcmd", analysis)

        self.assertEqual(schema["type"], "function")
        self.assertEqual(schema["function"]["name"], "shell_testcmd")
        self.assertEqual(schema["function"]["description"], "A test command for unit testing")

        params = schema["function"]["parameters"]
        self.assertEqual(params["type"], "object")
        self.assertIn("subcommand", params["properties"])
        self.assertIn("verbose", params["properties"])
        self.assertIn("output", params["properties"])

    def test_schema_structure(self):
        """Test that schema has correct MCP/OpenAI function calling structure."""
        analysis = CLIAnalysisResult(
            command_name="mytool",
            description="My tool description",
        )

        schema = generate_tool_schema("mytool", analysis)

        # Verify top-level structure
        self.assertIn("type", schema)
        self.assertIn("function", schema)
        self.assertIn("name", schema["function"])
        self.assertIn("description", schema["function"])
        self.assertIn("parameters", schema["function"])

        # Verify parameters structure
        params = schema["function"]["parameters"]
        self.assertEqual(params["type"], "object")
        self.assertIn("properties", params)
        self.assertIn("required", params)


class TestCLIAnalysisResult(unittest.TestCase):
    """Tests for CLIAnalysisResult class."""

    def test_to_dict(self):
        """Test converting result to dictionary."""
        result = CLIAnalysisResult(
            command_name="test",
            description="Test description",
            subcommands=[{"name": "sub", "description": "Sub command"}],
            options=[{"name": "opt", "flags": ["-o"], "parameter": "", "description": "An option", "type": "boolean"}],
        )

        d = result.to_dict()
        self.assertEqual(d["command_name"], "test")
        self.assertEqual(d["description"], "Test description")
        self.assertEqual(len(d["subcommands"]), 1)
        self.assertEqual(len(d["options"]), 1)

    def test_default_values(self):
        """Test default values of CLIAnalysisResult."""
        result = CLIAnalysisResult(command_name="test")
        self.assertEqual(result.command_name, "test")
        self.assertEqual(result.description, "")
        self.assertEqual(result.subcommands, [])
        self.assertEqual(result.arguments, [])
        self.assertEqual(result.options, [])
        self.assertEqual(result.raw_help, "")

    def test_repr(self):
        """Test string representation."""
        result = CLIAnalysisResult(command_name="test", subcommands=[{"name": "a", "description": "b"}], options=[])
        repr_str = repr(result)
        self.assertIn("test", repr_str)
        self.assertIn("subcommands=1", repr_str)


if __name__ == "__main__":
    unittest.main()
