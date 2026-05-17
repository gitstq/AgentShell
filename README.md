# ShellForge

ShellForge - Lightweight Terminal Command Agent Wrapping Engine

A zero-dependency Python CLI tool that wraps terminal commands into structured tool descriptions compatible with MCP/OpenAI function calling.

## Features

- **CLI Analyzer**: Automatically analyze CLI tools by parsing their help output
- **Safe Sandbox**: Execute commands with safety validation and timeout control
- **Template System**: Built-in templates for 11+ common CLI tools
- **MCP Server**: Lightweight HTTP-based MCP-compatible server
- **Execution History**: Track and search command execution history

## Installation

```bash
pip install -e .
```

## Usage

```bash
# Analyze a CLI tool
shellforge analyze git

# Safely execute a command
shellforge run ls -la

# List available templates
shellforge template list

# Show template details
shellforge template show git

# Generate tool schema
shellforge schema curl

# Start MCP server
shellforge serve --port 8765

# View execution history
shellforge history
shellforge history --stats
```

## Requirements

- Python 3.8+
- No external dependencies

## License

MIT
