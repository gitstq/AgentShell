"""
Template Engine - Built-in command templates for common CLI tools.

Provides pre-defined tool templates with descriptions, common commands,
parameter explanations, and usage examples. Templates are stored as
Python dictionaries (no YAML dependency required).
"""

from typing import Dict, List, Optional


# Template format: each template is a dict with structured metadata
BUILTIN_TEMPLATES: Dict[str, Dict] = {
    "git": {
        "name": "git",
        "description": "Distributed version control system for tracking changes in source code.",
        "common_commands": [
            {
                "command": "git init",
                "description": "Initialize a new Git repository",
            },
            {
                "command": "git clone <url>",
                "description": "Clone a remote repository",
            },
            {
                "command": "git add <path>",
                "description": "Stage file changes for commit",
            },
            {
                "command": "git commit -m <message>",
                "description": "Commit staged changes with a message",
            },
            {
                "command": "git push [remote] [branch]",
                "description": "Push commits to a remote repository",
            },
            {
                "command": "git pull [remote] [branch]",
                "description": "Fetch and merge changes from a remote",
            },
            {
                "command": "git branch [name]",
                "description": "List or create branches",
            },
            {
                "command": "git checkout <branch>",
                "description": "Switch to a branch or restore files",
            },
            {
                "command": "git merge <branch>",
                "description": "Merge a branch into the current branch",
            },
            {
                "command": "git log [--oneline]",
                "description": "Show commit history",
            },
            {
                "command": "git status",
                "description": "Show working tree status",
            },
            {
                "command": "git diff [path]",
                "description": "Show changes between commits or working tree",
            },
            {
                "command": "git stash",
                "description": "Stash current changes temporarily",
            },
            {
                "command": "git remote -v",
                "description": "List remote repositories",
            },
            {
                "command": "git tag <name>",
                "description": "Create, list, or delete tags",
            },
        ],
        "parameters": [
            {"name": "url", "description": "Remote repository URL (https:// or git://)"},
            {"name": "branch", "description": "Branch name to operate on"},
            {"name": "path", "description": "File or directory path"},
            {"name": "message", "description": "Commit message string"},
            {"name": "remote", "description": "Remote name (default: origin)"},
        ],
        "examples": [
            "git init",
            "git clone https://github.com/user/repo.git",
            "git add .",
            "git commit -m 'feat: add new feature'",
            "git push origin main",
            "git log --oneline -10",
        ],
    },
    "docker": {
        "name": "docker",
        "description": "Platform for building, running, and managing containerized applications.",
        "common_commands": [
            {"command": "docker build -t <image> <path>", "description": "Build an image from a Dockerfile"},
            {"command": "docker run [options] <image> [command]", "description": "Run a command in a new container"},
            {"command": "docker ps", "description": "List running containers"},
            {"command": "docker ps -a", "description": "List all containers"},
            {"command": "docker stop <container>", "description": "Stop a running container"},
            {"command": "docker rm <container>", "description": "Remove a container"},
            {"command": "docker images", "description": "List Docker images"},
            {"command": "docker pull <image>", "description": "Pull an image from a registry"},
            {"command": "docker push <image>", "description": "Push an image to a registry"},
            {"command": "docker logs <container>", "description": "View container logs"},
            {"command": "docker exec -it <container> <cmd>", "description": "Execute command in a running container"},
            {"command": "docker-compose up", "description": "Start multi-container services"},
            {"command": "docker-compose down", "description": "Stop and remove containers"},
            {"command": "docker system prune", "description": "Remove unused data"},
        ],
        "parameters": [
            {"name": "image", "description": "Docker image name (e.g., nginx:latest)"},
            {"name": "container", "description": "Container ID or name"},
            {"name": "path", "description": "Build context path"},
            {"name": "command", "description": "Command to run inside container"},
        ],
        "examples": [
            "docker build -t myapp:1.0 .",
            "docker run -d -p 8080:80 nginx",
            "docker ps -a",
            "docker logs -f my_container",
            "docker exec -it my_container /bin/bash",
        ],
    },
    "npm": {
        "name": "npm",
        "description": "Node.js package manager for installing and managing JavaScript dependencies.",
        "common_commands": [
            {"command": "npm init", "description": "Create a new package.json"},
            {"command": "npm install [package]", "description": "Install dependencies"},
            {"command": "npm install -g <package>", "description": "Install a package globally"},
            {"command": "npm uninstall <package>", "description": "Uninstall a package"},
            {"command": "npm update", "description": "Update dependencies"},
            {"command": "npm run <script>", "description": "Run a script from package.json"},
            {"command": "npm test", "description": "Run tests"},
            {"command": "npm publish", "description": "Publish a package to the registry"},
            {"command": "npm list", "description": "List installed packages"},
            {"command": "npm audit", "description": "Check for vulnerabilities"},
            {"command": "npm cache clean", "description": "Clean the package cache"},
        ],
        "parameters": [
            {"name": "package", "description": "Package name to install/uninstall"},
            {"name": "script", "description": "Script name defined in package.json"},
            {"name": "version", "description": "Package version specifier"},
        ],
        "examples": [
            "npm init -y",
            "npm install express",
            "npm install -g typescript",
            "npm run build",
            "npm test",
        ],
    },
    "pip": {
        "name": "pip",
        "description": "Python package installer for managing Python packages and dependencies.",
        "common_commands": [
            {"command": "pip install <package>", "description": "Install a package"},
            {"command": "pip install -r requirements.txt", "description": "Install from requirements file"},
            {"command": "pip uninstall <package>", "description": "Uninstall a package"},
            {"command": "pip list", "description": "List installed packages"},
            {"command": "pip show <package>", "description": "Show package details"},
            {"command": "pip freeze", "description": "Output installed packages in requirements format"},
            {"command": "pip search <query>", "description": "Search PyPI for packages"},
            {"command": "pip check", "description": "Verify installed packages have compatible dependencies"},
            {"command": "pip cache purge", "description": "Clear the pip cache"},
            {"command": "pip install --upgrade <package>", "description": "Upgrade a package"},
        ],
        "parameters": [
            {"name": "package", "description": "Package name to install/uninstall"},
            {"name": "version", "description": "Package version specifier (e.g., >=1.0.0)"},
            {"name": "index_url", "description": "Custom package index URL"},
        ],
        "examples": [
            "pip install requests",
            "pip install -r requirements.txt",
            "pip list --format=columns",
            "pip show numpy",
            "pip freeze > requirements.txt",
        ],
    },
    "python": {
        "name": "python",
        "description": "Python interpreter for running Python scripts and modules.",
        "common_commands": [
            {"command": "python <script.py>", "description": "Run a Python script"},
            {"command": "python -m <module>", "description": "Run a Python module"},
            {"command": "python -c <code>", "description": "Execute Python code inline"},
            {"command": "python -V", "description": "Print Python version"},
            {"command": "python -m venv <dir>", "description": "Create a virtual environment"},
            {"command": "python -m pip install <pkg>", "description": "Install a package via pip module"},
            {"command": "python -m http.server [port]", "description": "Start a simple HTTP server"},
            {"command": "python -m json.tool", "description": "Format JSON input"},
        ],
        "parameters": [
            {"name": "script", "description": "Path to Python script file"},
            {"name": "module", "description": "Python module name"},
            {"name": "code", "description": "Inline Python code to execute"},
            {"name": "port", "description": "Port number for HTTP server"},
        ],
        "examples": [
            "python app.py",
            "python -m venv .venv",
            "python -c \"print('Hello')\"",
            "python -m http.server 8000",
            "echo '{\"key\": \"value\"}' | python -m json.tool",
        ],
    },
    "curl": {
        "name": "curl",
        "description": "Command-line tool for transferring data with URL syntax, supporting HTTP, HTTPS, FTP, and more.",
        "common_commands": [
            {"command": "curl <url>", "description": "Fetch content from a URL"},
            {"command": "curl -o <file> <url>", "description": "Save output to a file"},
            {"command": "curl -X POST -d <data> <url>", "description": "Send POST request with data"},
            {"command": "curl -H <header> <url>", "description": "Send request with custom header"},
            {"command": "curl -L <url>", "description": "Follow redirects"},
            {"command": "curl -s <url>", "description": "Silent mode (no progress)"},
            {"command": "curl -u <user:pass> <url>", "description": "Authenticate with username/password"},
            {"command": "curl -F <file=@path> <url>", "description": "Upload a file"},
            {"command": "curl -x <proxy> <url>", "description": "Use a proxy"},
            {"command": "curl -I <url>", "description": "Fetch only HTTP headers"},
        ],
        "parameters": [
            {"name": "url", "description": "Target URL"},
            {"name": "data", "description": "POST data string"},
            {"name": "header", "description": "HTTP header in 'Key: Value' format"},
            {"name": "file", "description": "Path to file for upload or output"},
            {"name": "proxy", "description": "Proxy URL (e.g., http://proxy:8080)"},
        ],
        "examples": [
            "curl https://api.example.com/data",
            "curl -X POST -H 'Content-Type: application/json' -d '{\"key\":\"val\"}' https://api.example.com",
            "curl -L -o page.html https://example.com",
            "curl -I https://example.com",
        ],
    },
    "jq": {
        "name": "jq",
        "description": "Command-line JSON processor for filtering, transforming, and querying JSON data.",
        "common_commands": [
            {"command": "jq '.' <file>", "description": "Pretty-print JSON file"},
            {"command": "jq '.key' <file>", "description": "Extract a field from JSON"},
            {"command": "jq '.[]' <file>", "description": "Extract array elements"},
            {"command": "jq '.key1.key2' <file>", "description": "Extract nested field"},
            {"command": "jq 'select(.key > 10)' <file>", "description": "Filter array elements"},
            {"command": "jq 'map(.key)' <file>", "description": "Map over array elements"},
            {"command": "jq 'keys' <file>", "description": "Get object keys"},
            {"command": "jq 'length' <file>", "description": "Get array length"},
            {"command": "jq -s '.' <file>", "description": "Slurp input into an array"},
        ],
        "parameters": [
            {"name": "filter", "description": "jq filter expression"},
            {"name": "file", "description": "Path to JSON file (or use stdin)"},
        ],
        "examples": [
            "echo '{\"name\":\"John\"}' | jq '.'",
            "cat data.json | jq '.items[] | select(.price > 100)'",
            "jq 'keys' config.json",
            "jq -s '.[0] + .[1]' file1.json file2.json",
        ],
    },
    "grep": {
        "name": "grep",
        "description": "Search for patterns in text using regular expressions.",
        "common_commands": [
            {"command": "grep <pattern> <file>", "description": "Search for pattern in file"},
            {"command": "grep -r <pattern> <dir>", "description": "Recursively search in directory"},
            {"command": "grep -i <pattern> <file>", "description": "Case-insensitive search"},
            {"command": "grep -n <pattern> <file>", "description": "Show line numbers"},
            {"command": "grep -v <pattern> <file>", "description": "Invert match (exclude pattern)"},
            {"command": "grep -c <pattern> <file>", "description": "Count matching lines"},
            {"command": "grep -l <pattern> <dir>", "description": "List files with matches"},
            {"command": "grep -A<N> <pattern> <file>", "description": "Show N lines after match"},
            {"command": "grep -B<N> <pattern> <file>", "description": "Show N lines before match"},
            {"command": "grep -e <p1> -e <p2> <file>", "description": "Match multiple patterns"},
        ],
        "parameters": [
            {"name": "pattern", "description": "Regular expression or text pattern to search"},
            {"name": "file", "description": "File path to search in"},
            {"name": "dir", "description": "Directory to search recursively"},
        ],
        "examples": [
            "grep 'error' app.log",
            "grep -rn 'TODO' src/",
            "grep -i 'warning' *.log",
            "grep -v 'debug' app.log | grep 'error'",
        ],
    },
    "find": {
        "name": "find",
        "description": "Search for files and directories in a directory hierarchy.",
        "common_commands": [
            {"command": "find <dir>", "description": "List all files in directory"},
            {"command": "find <dir> -name <pattern>", "description": "Find files by name pattern"},
            {"command": "find <dir> -type f", "description": "Find only files"},
            {"command": "find <dir> -type d", "description": "Find only directories"},
            {"command": "find <dir> -size +<N>", "description": "Find files larger than N"},
            {"command": "find <dir> -mtime -<N>", "description": "Find files modified in last N days"},
            {"command": "find <dir> -exec <cmd> {} \\;", "description": "Execute command on found files"},
            {"command": "find <dir> -perm <mode>", "description": "Find files by permissions"},
            {"command": "find <dir> -empty", "description": "Find empty files or directories"},
        ],
        "parameters": [
            {"name": "dir", "description": "Starting directory for search"},
            {"name": "pattern", "description": "File name pattern (supports wildcards)"},
            {"name": "N", "description": "Numeric value for size/time filters"},
            {"name": "mode", "description": "Permission mode (e.g., 755)"},
        ],
        "examples": [
            "find . -name '*.py'",
            "find /tmp -type f -mtime -7",
            "find . -size +100M",
            "find . -name '*.log' -exec rm {} \\;",
        ],
    },
    "tar": {
        "name": "tar",
        "description": "Archiving utility for creating and extracting tar archives.",
        "common_commands": [
            {"command": "tar -czf <archive.tar.gz> <files>", "description": "Create a gzipped archive"},
            {"command": "tar -xzf <archive.tar.gz>", "description": "Extract a gzipped archive"},
            {"command": "tar -tf <archive.tar.gz>", "description": "List contents of an archive"},
            {"command": "tar -cf <archive.tar> <files>", "description": "Create an uncompressed archive"},
            {"command": "tar -xf <archive.tar>", "description": "Extract an uncompressed archive"},
            {"command": "tar -czf - <dir> | ssh user@host 'tar -xzf -'", "description": "Archive and transfer over SSH"},
            {"command": "tar --exclude=<pattern> -czf <archive> <dir>", "description": "Create archive excluding files"},
        ],
        "parameters": [
            {"name": "archive", "description": "Path to the archive file"},
            {"name": "files", "description": "Files or directories to archive"},
            {"name": "dir", "description": "Directory to extract to or archive from"},
            {"name": "pattern", "description": "Exclude pattern"},
        ],
        "examples": [
            "tar -czf backup.tar.gz /data/project",
            "tar -xzf archive.tar.gz -C /target/dir",
            "tar -tf archive.tar.gz",
            "tar --exclude='*.pyc' -czf src.tar.gz src/",
        ],
    },
    "ssh": {
        "name": "ssh",
        "description": "Secure shell client for remote login and command execution.",
        "common_commands": [
            {"command": "ssh user@host", "description": "Connect to a remote host"},
            {"command": "ssh user@host <command>", "description": "Execute command on remote host"},
            {"command": "ssh -p <port> user@host", "description": "Connect using a specific port"},
            {"command": "ssh -i <keyfile> user@host", "description": "Connect using a specific identity key"},
            {"command": "ssh -L <local>:<remote>:<remote_port> user@host", "description": "Create local port forwarding"},
            {"command": "ssh -R <remote>:<local>:<local_port> user@host", "description": "Create remote port forwarding"},
            {"command": "ssh-copy-id user@host", "description": "Copy SSH key to remote host"},
            {"command": "ssh-keygen -t rsa -b 4096", "description": "Generate a new SSH key pair"},
        ],
        "parameters": [
            {"name": "user", "description": "Remote username"},
            {"name": "host", "description": "Remote hostname or IP address"},
            {"name": "port", "description": "SSH port number (default: 22)"},
            {"name": "keyfile", "description": "Path to SSH private key file"},
            {"name": "command", "description": "Command to execute on remote host"},
        ],
        "examples": [
            "ssh user@example.com",
            "ssh -p 2222 user@example.com",
            "ssh user@host 'ls -la /tmp'",
            "ssh -L 8080:localhost:80 user@host",
        ],
    },
}


class TemplateManager:
    """Manager for loading, searching, and registering command templates.

    Templates provide pre-defined tool descriptions for common CLI utilities,
    enabling quick integration with AI agent systems.
    """

    def __init__(self) -> None:
        """Initialize TemplateManager with built-in templates."""
        self._templates: Dict[str, Dict] = {}
        # Load all built-in templates
        for name, template in BUILTIN_TEMPLATES.items():
            self._templates[name] = template

    def load_template(self, name: str) -> Optional[Dict]:
        """Load a template by name.

        Args:
            name: Name of the template to load.

        Returns:
            Template dictionary if found, None otherwise.
        """
        return self._templates.get(name)

    def list_templates(self) -> List[str]:
        """List all available template names.

        Returns:
            Sorted list of template names.
        """
        return sorted(self._templates.keys())

    def search_templates(self, query: str) -> List[Dict]:
        """Search templates by keyword in name, description, and commands.

        Args:
            query: Search keyword or phrase.

        Returns:
            List of matching template dictionaries.
        """
        query_lower = query.lower()
        results: List[Dict] = []

        for name, template in self._templates.items():
            # Search in name
            if query_lower in name.lower():
                results.append(template)
                continue

            # Search in description
            if query_lower in template.get("description", "").lower():
                results.append(template)
                continue

            # Search in common commands
            for cmd_info in template.get("common_commands", []):
                if query_lower in cmd_info.get("command", "").lower() or \
                   query_lower in cmd_info.get("description", "").lower():
                    results.append(template)
                    break

            # Search in parameters
            for param in template.get("parameters", []):
                if query_lower in param.get("name", "").lower() or \
                   query_lower in param.get("description", "").lower():
                    results.append(template)
                    break

        return results

    def register_template(self, name: str, template: Dict) -> None:
        """Register a custom template.

        Args:
            name: Name for the template.
            template: Template dictionary with required fields:
                - description: str
                - common_commands: list of dicts with 'command' and 'description'
                - parameters: list of dicts with 'name' and 'description'
                - examples: list of example command strings
        """
        template["name"] = name
        self._templates[name] = template

    def get_template_schema(self, name: str) -> Optional[Dict]:
        """Get a tool schema for a template, compatible with MCP/OpenAI format.

        Args:
            name: Template name.

        Returns:
            Tool schema dictionary if template exists, None otherwise.
        """
        template = self.load_template(name)
        if template is None:
            return None

        properties: Dict = {}
        required: List[str] = []

        # Add subcommand property if there are common commands
        if template.get("common_commands"):
            properties["subcommand"] = {
                "type": "string",
                "description": "The subcommand or action to perform.",
            }

        # Add parameters as properties
        for param in template.get("parameters", []):
            param_name = param["name"]
            properties[param_name] = {
                "type": "string",
                "description": param.get("description", ""),
            }

        return {
            "type": "function",
            "function": {
                "name": f"shell_{name}",
                "description": template.get("description", f"Execute {name} command"),
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }

    def get_all_schemas(self) -> Dict[str, Dict]:
        """Get tool schemas for all registered templates.

        Returns:
            Dictionary mapping template names to their schemas.
        """
        schemas: Dict[str, Dict] = {}
        for name in self.list_templates():
            schema = self.get_template_schema(name)
            if schema is not None:
                schemas[name] = schema
        return schemas
