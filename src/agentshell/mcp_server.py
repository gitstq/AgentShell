"""
MCP Server - Lightweight HTTP-based MCP-compatible server for exposing
shell tools to AI agents.

Implements a simple HTTP server using Python's built-in http.server module
that provides MCP-compatible endpoints for tool discovery and invocation.
"""

import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any, Callable, Dict, List, Optional


class MCPTool:
    """Represents a tool exposed by the MCP server.

    Attributes:
        name: Unique tool name.
        schema: JSON Schema describing the tool's parameters.
        handler: Callable that executes the tool.
        description: Human-readable description of the tool.
    """

    def __init__(
        self,
        name: str,
        schema: Dict[str, Any],
        handler: Callable,
        description: str = "",
    ) -> None:
        self.name = name
        self.schema = schema
        self.handler = handler
        self.description = description

    def to_dict(self) -> Dict[str, Any]:
        """Convert tool to dictionary representation."""
        return {
            "name": self.name,
            "description": self.description,
            "schema": self.schema,
        }


class MCPServer:
    """Lightweight MCP-compatible HTTP server.

    Exposes shell tools to AI agents via HTTP endpoints compatible with
    the Model Context Protocol (MCP).

    Endpoints:
        GET /tools - List all exposed tools
        POST /tools/{name} - Call a specific tool
        GET /config - Get MCP configuration
        GET /health - Health check endpoint
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 8765) -> None:
        """Initialize the MCP server.

        Args:
            host: Host address to bind to.
            port: Port number to listen on.
        """
        self.host = host
        self.port = port
        self._tools: Dict[str, MCPTool] = {}
        self._server: Optional[HTTPServer] = None
        self._thread: Optional[threading.Thread] = None

    def expose_tool(
        self,
        tool_name: str,
        tool_schema: Dict[str, Any],
        handler: Callable,
        description: str = "",
    ) -> None:
        """Expose a tool to AI agents.

        Args:
            tool_name: Unique name for the tool.
            tool_schema: JSON Schema describing tool parameters.
            handler: Callable that implements the tool logic.
                Should accept a single dict argument (parameters) and return a dict result.
            description: Human-readable description of the tool.
        """
        tool = MCPTool(
            name=tool_name,
            schema=tool_schema,
            handler=handler,
            description=description,
        )
        self._tools[tool_name] = tool

    def list_tools(self) -> List[Dict[str, Any]]:
        """List all exposed tools.

        Returns:
            List of tool dictionaries with name, description, and schema.
        """
        return [tool.to_dict() for tool in self._tools.values()]

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call an exposed tool by name.

        Args:
            tool_name: Name of the tool to call.
            arguments: Dictionary of arguments to pass to the tool handler.

        Returns:
            Dictionary with 'success', 'result', and optional 'error' keys.
        """
        tool = self._tools.get(tool_name)
        if tool is None:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found",
                "available_tools": list(self._tools.keys()),
            }

        try:
            result = tool.handler(arguments)
            return {
                "success": True,
                "result": result,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def generate_mcp_config(self) -> Dict[str, Any]:
        """Generate MCP configuration file content.

        Returns:
            Dictionary containing MCP server configuration.
        """
        return {
            "mcpServers": {
                "agentshell": {
                    "command": "agentshell",
                    "args": ["serve", "--port", str(self.port)],
                    "transport": "stdio",
                    "tools": [
                        {
                            "name": tool.name,
                            "description": tool.description,
                            "schema": tool.schema,
                        }
                        for tool in self._tools.values()
                    ],
                }
            },
            "server_info": {
                "name": "ShellForge MCP Server",
                "version": "1.0.0",
                "host": self.host,
                "port": self.port,
            },
        }

    def start(self, blocking: bool = True) -> None:
        """Start the MCP server.

        Args:
            blocking: If True, block the current thread. If False, run in background.
        """
        # Create a custom handler class with reference to the server
        server_ref = self

        class MCPRequestHandler(BaseHTTPRequestHandler):
            """HTTP request handler for MCP endpoints."""

            def log_message(self, format: str, *args: Any) -> None:
                """Override to suppress default logging."""
                pass

            def _send_json_response(self, data: Any, status_code: int = 200) -> None:
                """Send a JSON response."""
                self.send_response(status_code)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8"))

            def _read_request_body(self) -> bytes:
                """Read the request body."""
                content_length = int(self.headers.get("Content-Length", 0))
                return self.rfile.read(content_length)

            def do_GET(self) -> None:
                """Handle GET requests."""
                if self.path == "/tools":
                    self._send_json_response({
                        "tools": server_ref.list_tools(),
                    })
                elif self.path == "/config":
                    self._send_json_response(server_ref.generate_mcp_config())
                elif self.path == "/health":
                    self._send_json_response({
                        "status": "ok",
                        "tools_count": len(server_ref._tools),
                    })
                else:
                    self._send_json_response({
                        "error": "Not found",
                        "available_endpoints": ["/tools", "/config", "/health"],
                    }, status_code=404)

            def do_POST(self) -> None:
                """Handle POST requests."""
                # Handle /tools/{name} endpoint
                if self.path.startswith("/tools/"):
                    tool_name = self.path[len("/tools/"):]
                    try:
                        body = self._read_request_body()
                        arguments = json.loads(body) if body else {}
                    except json.JSONDecodeError:
                        self._send_json_response({
                            "error": "Invalid JSON in request body",
                        }, status_code=400)
                        return

                    result = server_ref.call_tool(tool_name, arguments)
                    status_code = 200 if result.get("success") else 400
                    self._send_json_response(result, status_code)
                else:
                    self._send_json_response({
                        "error": "Not found",
                    }, status_code=404)

        self._server = HTTPServer((self.host, self.port), MCPRequestHandler)

        if blocking:
            self._server.serve_forever()
        else:
            self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
            self._thread.start()

    def stop(self) -> None:
        """Stop the MCP server."""
        if self._server:
            self._server.shutdown()
            self._server = None
