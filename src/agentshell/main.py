"""
AgentShell CLI - Main entry point for the AgentShell command-line interface.

Provides subcommands for analyzing CLI tools, executing commands safely,
managing templates, running the MCP server, and viewing execution history.
"""

import argparse
import json
import sys
from typing import List, Optional

from agentshell import __version__
from agentshell.cli_analyzer import analyze_command, command_exists, generate_tool_schema
from agentshell.sandbox import SafeExecutor
from agentshell.template_engine import TemplateManager
from agentshell.history import HistoryManager


# ANSI color codes for terminal output
class Colors:
    """ANSI color code constants for terminal output."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"


def colorize(text: str, color: str) -> str:
    """Wrap text with ANSI color codes.

    Args:
        text: The text to colorize.
        color: ANSI color code string.

    Returns:
        Colorized text string.
    """
    return f"{color}{text}{Colors.RESET}"


def print_json(data: object) -> None:
    """Print data as formatted JSON.

    Args:
        data: The data object to serialize and print.
    """
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_analyze(args: argparse.Namespace) -> int:
    """Handle the 'analyze' subcommand.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    cmd_name = args.command

    if not command_exists(cmd_name):
        print(colorize(f"Error: Command '{cmd_name}' not found on PATH.", Colors.RED), file=sys.stderr)
        return 1

    result = analyze_command(cmd_name, timeout=args.timeout)

    if args.json:
        print_json(result.to_dict())
        return 0

    # Pretty print analysis
    print(colorize(f"=== Analysis of '{result.command_name}' ===", Colors.BOLD + Colors.CYAN))
    print()

    if result.description:
        print(colorize("Description:", Colors.BOLD))
        print(f"  {result.description}")
        print()

    if result.subcommands:
        print(colorize(f"Subcommands ({len(result.subcommands)}):", Colors.BOLD))
        for sc in result.subcommands:
            print(f"  {colorize(sc['name'], Colors.GREEN):20s} {sc['description']}")
        print()

    if result.arguments:
        print(colorize(f"Arguments ({len(result.arguments)}):", Colors.BOLD))
        for arg in result.arguments:
            req = colorize("required", Colors.RED) if arg.get("required") else colorize("optional", Colors.DIM)
            print(f"  {colorize(arg['name'], Colors.YELLOW):20s} [{req}] {arg['description']}")
        print()

    if result.options:
        print(colorize(f"Options ({len(result.options)}):", Colors.BOLD))
        for opt in result.options:
            flags = ", ".join(opt.get("flags", []))
            param = f" <{opt['parameter']}>" if opt.get("parameter") else ""
            type_info = f" ({opt['type']})" if opt.get("type") else ""
            print(f"  {colorize(flags + param, Colors.GREEN):30s} {type_info} {opt['description']}")
        print()

    return 0


def cmd_run(args: argparse.Namespace) -> int:
    """Handle the 'run' subcommand.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    command = " ".join(args.command_args)

    if not command.strip():
        print(colorize("Error: No command specified.", Colors.RED), file=sys.stderr)
        return 1

    executor = SafeExecutor(
        blocked_commands=args.block or [],
        default_timeout=args.timeout,
    )

    if args.json:
        result = executor.execute(command)
        print_json(result.to_dict())
        return 0

    # Show safety info
    has_disk_write = executor.check_disk_write(command)
    has_network = executor.check_network_access(command)

    if has_disk_write:
        print(colorize("  [!] Disk write detected", Colors.YELLOW))
    if has_network:
        print(colorize("  [!] Network access detected", Colors.YELLOW))

    print(colorize(f"  $ {command}", Colors.BOLD + Colors.CYAN))
    print()

    result = executor.execute(command)

    if result.stdout:
        print(result.stdout, end="")

    if result.stderr:
        print(colorize(result.stderr, Colors.RED), end="", file=sys.stderr)

    print()
    status_color = Colors.GREEN if result.success else Colors.RED
    status_text = "OK" if result.success else f"FAILED (code: {result.code})"
    print(colorize(f"  [{status_text}] ({result.duration:.3f}s)", status_color))

    # Record to history
    try:
        history = HistoryManager()
        history.record(
            command=command,
            exit_code=result.code,
            duration=result.duration,
            stdout=result.stdout[:500],
            stderr=result.stderr[:500],
            safety_report=result.safety_report,
        )
    except Exception:
        pass  # History recording is best-effort

    return 0 if result.success else 1


def cmd_template(args: argparse.Namespace) -> int:
    """Handle the 'template' subcommand.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    manager = TemplateManager()

    if args.template_action == "list":
        templates = manager.list_templates()
        if args.json:
            print_json({"templates": templates})
            return 0

        print(colorize("=== Available Templates ===", Colors.BOLD + Colors.CYAN))
        print()
        for name in templates:
            template = manager.load_template(name)
            desc = template.get("description", "") if template else ""
            print(f"  {colorize(name, Colors.GREEN):12s} {desc}")
        print()
        print(f"  Total: {len(templates)} templates")

    elif args.template_action == "show":
        name = args.name
        template = manager.load_template(name)
        if template is None:
            print(colorize(f"Error: Template '{name}' not found.", Colors.RED), file=sys.stderr)
            return 1

        if args.json:
            print_json(template)
            return 0

        print(colorize(f"=== Template: {template['name']} ===", Colors.BOLD + Colors.CYAN))
        print()
        print(colorize("Description:", Colors.BOLD))
        print(f"  {template.get('description', 'N/A')}")
        print()

        if template.get("common_commands"):
            print(colorize(f"Common Commands ({len(template['common_commands'])}):", Colors.BOLD))
            for cmd_info in template["common_commands"]:
                print(f"  {colorize(cmd_info['command'], Colors.GREEN):40s} {cmd_info['description']}")
            print()

        if template.get("parameters"):
            print(colorize(f"Parameters ({len(template['parameters'])}):", Colors.BOLD))
            for param in template["parameters"]:
                print(f"  {colorize(param['name'], Colors.YELLOW):20s} {param['description']}")
            print()

        if template.get("examples"):
            print(colorize(f"Examples ({len(template['examples'])}):", Colors.BOLD))
            for example in template["examples"]:
                print(f"  {colorize('$ ' + example, Colors.DIM)}")
            print()

    elif args.template_action == "search":
        query = args.query
        results = manager.search_templates(query)

        if args.json:
            print_json({"query": query, "results": [t["name"] for t in results]})
            return 0

        print(colorize(f"=== Search Results for '{query}' ===", Colors.BOLD + Colors.CYAN))
        print()
        if not results:
            print("  No matching templates found.")
        else:
            for template in results:
                print(f"  {colorize(template['name'], Colors.GREEN):12s} {template.get('description', '')}")
        print()

    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    """Handle the 'serve' subcommand.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    from agentshell.mcp_server import MCPServer
    from agentshell.sandbox import SafeExecutor

    port = args.port
    server = MCPServer(host="127.0.0.1", port=port)

    # Expose built-in templates as tools
    manager = TemplateManager()
    executor = SafeExecutor()

    for name in manager.list_templates():
        template = manager.load_template(name)
        if template is None:
            continue

        schema = manager.get_template_schema(name)

        def make_handler(tmpl_name: str) -> callable:
            """Create a closure for the tool handler."""
            def handler(arguments: dict) -> dict:
                cmd = arguments.get("subcommand", "")
                result = executor.execute(f"{tmpl_name} {cmd}", timeout=30)
                return {
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "exit_code": result.code,
                }
            return handler

        server.expose_tool(
            tool_name=f"shell_{name}",
            tool_schema=schema,
            handler=make_handler(name),
            description=template.get("description", ""),
        )

    print(colorize(f"AgentShell MCP Server starting on http://127.0.0.1:{port}", Colors.BOLD + Colors.CYAN))
    print(colorize(f"  Tools exposed: {len(server.list_tools())}", Colors.DIM))
    print(colorize("  Endpoints:", Colors.DIM))
    print("    GET  /tools   - List all tools")
    print("    POST /tools/<name> - Call a tool")
    print("    GET  /config  - Get MCP configuration")
    print("    GET  /health  - Health check")
    print()
    print("Press Ctrl+C to stop.")
    print()

    try:
        server.start(blocking=True)
    except KeyboardInterrupt:
        print()
        print(colorize("Server stopped.", Colors.YELLOW))
        server.stop()

    return 0


def cmd_history(args: argparse.Namespace) -> int:
    """Handle the 'history' subcommand.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    manager = HistoryManager()

    if args.json:
        if args.search_query:
            records = manager.search(args.search_query)
            print_json([r.to_dict() for r in records])
        else:
            stats = manager.stats()
            print_json(stats)
        return 0

    if args.stats:
        stats = manager.stats()
        print(colorize("=== Execution Statistics ===", Colors.BOLD + Colors.CYAN))
        print()
        print(f"  Total executions:  {colorize(str(stats['total_executions']), Colors.GREEN)}")
        print(f"  Successful:        {colorize(str(stats['successful']), Colors.GREEN)}")
        print(f"  Failed:            {colorize(str(stats['failed']), Colors.RED)}")
        rate_str = str(stats['success_rate']) + "%"
        dur_str = str(stats['avg_duration']) + "s"
        print(f"  Success rate:      {colorize(rate_str, Colors.GREEN)}")
        print(f"  Avg duration:      {colorize(dur_str, Colors.CYAN)}")
        print()

        if stats.get("most_used_commands"):
            print(colorize("Most Used Commands:", Colors.BOLD))
            for item in stats["most_used_commands"]:
                print(f"  {colorize(item['command'], Colors.GREEN):20s} ({item['count']} times)")
            print()
        return 0

    if args.export:
        try:
            content = manager.export(format=args.export)
            print(content)
        except ValueError as e:
            print(colorize(f"Error: {e}", Colors.RED), file=sys.stderr)
            return 1
        return 0

    if args.clear:
        manager.clear()
        print(colorize("History cleared.", Colors.YELLOW))
        return 0

    # Default: show recent history or search
    if args.search_query:
        records = manager.search(args.search_query)
        print(colorize(f"=== Search Results for '{args.search_query}' ===", Colors.BOLD + Colors.CYAN))
    else:
        records = list(reversed(manager.records[-20:]))
        print(colorize("=== Recent History ===", Colors.BOLD + Colors.CYAN))

    print()
    if not records:
        print("  No records found.")
    else:
        from datetime import datetime
        for record in records:
            dt = datetime.fromtimestamp(record.timestamp).strftime("%Y-%m-%d %H:%M:%S")
            status = colorize("OK", Colors.GREEN) if record.exit_code == 0 else colorize(f"FAIL({record.exit_code})", Colors.RED)
            cmd_display = record.command[:60] + "..." if len(record.command) > 60 else record.command
            print(f"  [{dt}] [{status}] {cmd_display}")
            if record.duration > 0:
                print(f"    Duration: {record.duration:.3f}s")
    print()

    return 0


def cmd_schema(args: argparse.Namespace) -> int:
    """Handle the 'schema' subcommand.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    cmd_name = args.command

    if not command_exists(cmd_name):
        print(colorize(f"Error: Command '{cmd_name}' not found on PATH.", Colors.RED), file=sys.stderr)
        return 1

    schema = generate_tool_schema(cmd_name)
    print_json(schema)
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the AgentShell CLI.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog="agentshell",
        description="AgentShell - Lightweight Terminal Command Agent Wrapping Engine",
        epilog="Examples:\n"
               "  agentshell analyze git\n"
               "  agentshell run ls -la\n"
               "  agentshell template list\n"
               "  agentshell schema curl\n"
               "  agentshell serve --port 9000\n"
               "  agentshell history --stats\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"AgentShell v{__version__}",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Output in JSON format",
    )

    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")

    # analyze subcommand
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a CLI tool")
    analyze_parser.add_argument("command", help="Command name to analyze")
    analyze_parser.add_argument("--timeout", type=int, default=10, help="Help command timeout (seconds)")

    # run subcommand
    run_parser = subparsers.add_parser("run", help="Safely execute a command")
    run_parser.add_argument("command_args", nargs="+", help="Command and arguments to execute")
    run_parser.add_argument("--timeout", type=int, default=30, help="Execution timeout (seconds)")
    run_parser.add_argument("--block", nargs="*", default=[], help="Additional blocked command patterns")

    # template subcommand
    template_parser = subparsers.add_parser("template", help="Manage command templates")
    template_subparsers = template_parser.add_subparsers(dest="template_action", help="Template actions")

    # template list
    template_subparsers.add_parser("list", help="List all available templates")

    # template show
    template_show_parser = template_subparsers.add_parser("show", help="Show template details")
    template_show_parser.add_argument("name", help="Template name")

    # template search
    template_search_parser = template_subparsers.add_parser("search", help="Search templates")
    template_search_parser.add_argument("query", help="Search query")

    # serve subcommand
    serve_parser = subparsers.add_parser("serve", help="Start MCP server")
    serve_parser.add_argument("--port", type=int, default=8765, help="Server port (default: 8765)")

    # history subcommand
    history_parser = subparsers.add_parser("history", help="View execution history")
    history_parser.add_argument("search_query", nargs="?", default=None, help="Search query")
    history_parser.add_argument("--stats", action="store_true", help="Show statistics")
    history_parser.add_argument("--export", choices=["json", "text"], help="Export history in format")
    history_parser.add_argument("--clear", action="store_true", help="Clear all history")

    # schema subcommand
    schema_parser = subparsers.add_parser("schema", help="Generate tool schema for a command")
    schema_parser.add_argument("command", help="Command name to generate schema for")

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for the AgentShell CLI.

    Args:
        argv: Command-line arguments (defaults to sys.argv).

    Returns:
        Exit code (0 for success, non-zero for error).
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.subcommand is None:
        parser.print_help()
        return 0

    # Dispatch to subcommand handlers
    handlers = {
        "analyze": cmd_analyze,
        "run": cmd_run,
        "template": cmd_template,
        "serve": cmd_serve,
        "history": cmd_history,
        "schema": cmd_schema,
    }

    handler = handlers.get(args.subcommand)
    if handler is None:
        parser.print_help()
        return 1

    return handler(args)


if __name__ == "__main__":
    sys.exit(main())
