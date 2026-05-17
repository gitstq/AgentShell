"""
CLI Tool Analyzer - Analyzes CLI tools by parsing their help output
and generating structured tool schemas compatible with MCP/OpenAI function calling.
"""

import re
import shutil
import subprocess
import json
from typing import Dict, List, Optional, Any


class CLIAnalysisResult:
    """Result of analyzing a CLI command's help output."""

    def __init__(
        self,
        command_name: str,
        description: str = "",
        subcommands: Optional[List[Dict[str, str]]] = None,
        arguments: Optional[List[Dict[str, Any]]] = None,
        options: Optional[List[Dict[str, Any]]] = None,
        raw_help: str = "",
    ) -> None:
        self.command_name = command_name
        self.description = description
        self.subcommands = subcommands or []
        self.arguments = arguments or []
        self.options = options or []
        self.raw_help = raw_help

    def to_dict(self) -> Dict[str, Any]:
        """Convert analysis result to dictionary."""
        return {
            "command_name": self.command_name,
            "description": self.description,
            "subcommands": self.subcommands,
            "arguments": self.arguments,
            "options": self.options,
        }

    def __repr__(self) -> str:
        return f"CLIAnalysisResult(command={self.command_name!r}, subcommands={len(self.subcommands)}, options={len(self.options)})"


def command_exists(cmd_name: str) -> bool:
    """Check if a command exists on the system PATH.

    Args:
        cmd_name: Name of the command to check.

    Returns:
        True if the command is found on PATH, False otherwise.
    """
    return shutil.which(cmd_name) is not None


def analyze_command(cmd_name: str, timeout: int = 10) -> CLIAnalysisResult:
    """Analyze a CLI tool by executing its help command and parsing the output.

    Attempts to run `cmd --help` and `cmd -h`, then parses the output
    to extract structured information about the tool.

    Args:
        cmd_name: Name of the CLI command to analyze.
        timeout: Maximum time in seconds to wait for the help command.

    Returns:
        CLIAnalysisResult with parsed information about the command.
    """
    if not command_exists(cmd_name):
        return CLIAnalysisResult(
            command_name=cmd_name,
            description=f"Command '{cmd_name}' not found on system PATH.",
        )

    help_text = ""
    for help_flag in ["--help", "-h"]:
        try:
            result = subprocess.run(
                [cmd_name, help_flag],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            # Prefer stdout; fall back to stderr if stdout is empty
            help_text = result.stdout or result.stderr
            if help_text.strip():
                break
        except (subprocess.TimeoutExpired, OSError, FileNotFoundError):
            continue

    if not help_text.strip():
        return CLIAnalysisResult(
            command_name=cmd_name,
            description=f"Could not retrieve help output for '{cmd_name}'.",
        )

    return parse_help_output(help_text, cmd_name)


def parse_help_output(help_text: str, cmd_name: str = "") -> CLIAnalysisResult:
    """Parse CLI help text and extract structured information.

    Extracts command name, description, subcommands, positional arguments,
    and options from typical CLI help output formats.

    Args:
        help_text: The raw help output text.
        cmd_name: Optional command name override.

    Returns:
        CLIAnalysisResult with parsed information.
    """
    lines = help_text.split("\n")
    description = ""
    subcommands: List[Dict[str, str]] = []
    arguments: List[Dict[str, Any]] = []
    options: List[Dict[str, Any]] = []

    # Extract description from first non-empty, non-usage lines
    desc_lines: List[str] = []
    in_usage = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if desc_lines:
                break
            continue
        if stripped.lower().startswith("usage:") or stripped.lower().startswith("usage"):
            in_usage = True
            continue
        if in_usage:
            if not stripped:
                in_usage = False
            continue
        # Skip lines that look like usage or command name headers
        if stripped.lower() == cmd_name.lower():
            continue
        if stripped.startswith("-") or stripped.startswith("["):
            break
        desc_lines.append(stripped)

    description = " ".join(desc_lines).strip()

    # Extract subcommands - lines like "  command    Description of command"
    subcommand_pattern = re.compile(
        r"^\s{2,}(\S+)\s{2,}(.+)$"
    )
    # Extract options - lines like "  -f, --file FILE    Description"
    option_pattern = re.compile(
        r"^\s{2,}(-[a-zA-Z](?:,\s--[a-zA-Z][\w-]*)?(?:\s[<\[]?\w+[\]>]?)?)\s{2,}(.+)$"
    )
    # Extract arguments - lines like "  ARG    Description"
    argument_pattern = re.compile(
        r"^\s{2,}([A-Z_]{2,}(?:\.\.\.)?)\s{2,}(.+)$"
    )

    known_option_prefixes = {"-", "--"}
    known_subcommands: List[str] = []

    # First pass: identify subcommands and options
    for line in lines:
        stripped = line.strip()

        # Try option pattern
        opt_match = option_pattern.match(line)
        if opt_match:
            opt_str = opt_match.group(1).strip()
            opt_desc = opt_match.group(2).strip()
            opt_info = _parse_option_string(opt_str, opt_desc)
            options.append(opt_info)
            continue

        # Try subcommand pattern (must not start with -)
        sub_match = subcommand_pattern.match(line)
        if sub_match and not sub_match.group(1).startswith("-"):
            sub_name = sub_match.group(1)
            sub_desc = sub_match.group(2).strip()
            # Filter out things that look like options or arguments
            if sub_name.upper() == sub_name and len(sub_name) > 2:
                # Likely an argument placeholder
                arguments.append({
                    "name": sub_name.lower(),
                    "description": sub_desc,
                    "required": not sub_name.endswith("..."),
                })
            else:
                subcommands.append({
                    "name": sub_name,
                    "description": sub_desc,
                })
                known_subcommands.append(sub_name)
            continue

        # Try argument pattern
        arg_match = argument_pattern.match(line)
        if arg_match:
            arg_name = arg_match.group(1)
            arg_desc = arg_match.group(2).strip()
            arguments.append({
                "name": arg_name.lower().rstrip("."),
                "description": arg_desc,
                "required": not arg_name.endswith("..."),
            })

    if not cmd_name:
        # Try to extract command name from first usage line
        for line in lines:
            usage_match = re.match(r"\s*usage:\s*(\S+)", line, re.IGNORECASE)
            if usage_match:
                cmd_name = usage_match.group(1)
                break
        if not cmd_name:
            cmd_name = "unknown"

    return CLIAnalysisResult(
        command_name=cmd_name,
        description=description,
        subcommands=subcommands,
        arguments=arguments,
        options=options,
        raw_help=help_text,
    )


def _parse_option_string(opt_str: str, opt_desc: str) -> Dict[str, Any]:
    """Parse an option string like '-f, --file FILE' into a structured dict.

    Args:
        opt_str: The option flags and parameter string.
        opt_desc: The description of the option.

    Returns:
        Dictionary with name, flags, parameter, description, and type info.
    """
    parts = opt_str.split(",")
    flags: List[str] = []
    param: str = ""
    name: str = ""

    for part in parts:
        part = part.strip()
        if not part:
            continue
        # Check if there's a parameter attached
        tokens = part.split(None, 1)
        flags.append(tokens[0])
        if len(tokens) > 1:
            param = tokens[1].strip("[]<>")

    # Determine the canonical name
    for f in flags:
        if f.startswith("--"):
            name = f[2:].split("[")[0].split("=")[0]
            break
    if not name and flags:
        name = flags[0].lstrip("-")

    # Determine type
    opt_type = "boolean"
    if param:
        param_lower = param.lower()
        if param_lower in ("file", "path", "dir", "directory"):
            opt_type = "string"
        elif param_lower in ("int", "num", "count", "number", "port", "seconds"):
            opt_type = "integer"
        elif param_lower in ("float",):
            opt_type = "number"
        else:
            opt_type = "string"

    return {
        "name": name,
        "flags": flags,
        "parameter": param,
        "description": opt_desc,
        "type": opt_type,
    }


def generate_tool_schema(cmd_name: str, analysis_result: Optional[CLIAnalysisResult] = None) -> Dict[str, Any]:
    """Generate a JSON Schema tool description compatible with MCP/OpenAI function calling.

    If analysis_result is not provided, the command will be analyzed automatically.

    Args:
        cmd_name: Name of the CLI command.
        analysis_result: Optional pre-computed analysis result.

    Returns:
        Dictionary in OpenAI function calling / MCP tool format.
    """
    if analysis_result is None:
        analysis_result = analyze_command(cmd_name)

    properties: Dict[str, Any] = {}
    required: List[str] = []

    # Add subcommand as a property if present
    if analysis_result.subcommands:
        properties["subcommand"] = {
            "type": "string",
            "enum": [sc["name"] for sc in analysis_result.subcommands],
            "description": "The subcommand to execute.",
        }

    # Add options as properties
    for opt in analysis_result.options:
        prop_name = opt["name"].replace("-", "_")
        prop_schema: Dict[str, Any] = {
            "type": opt["type"],
            "description": opt["description"],
        }
        if opt["parameter"]:
            prop_schema["default"] = None
        properties[prop_name] = prop_schema

    # Add arguments as properties
    for arg in analysis_result.arguments:
        arg_name = arg["name"]
        properties[arg_name] = {
            "type": "string",
            "description": arg["description"],
        }
        if arg.get("required", False):
            required.append(arg_name)

    schema: Dict[str, Any] = {
        "type": "function",
        "function": {
            "name": f"shell_{cmd_name}",
            "description": analysis_result.description or f"Execute {cmd_name} command",
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        },
    }

    return schema
