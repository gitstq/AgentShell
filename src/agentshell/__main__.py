"""Allow running agentshell as a module: python -m agentshell."""

from agentshell.main import main
import sys

if __name__ == "__main__":
    sys.exit(main())
