"""Tests for Template Engine module."""

import unittest

from agentshell.template_engine import (
    BUILTIN_TEMPLATES,
    TemplateManager,
)


class TestBuiltinTemplates(unittest.TestCase):
    """Tests for built-in template constants."""

    def test_builtin_templates_not_empty(self):
        """Test that built-in templates are defined."""
        self.assertGreater(len(BUILTIN_TEMPLATES), 0)

    def test_required_templates_exist(self):
        """Test that all required templates are present."""
        required = ["git", "docker", "npm", "pip", "python", "curl", "jq", "grep", "find", "tar", "ssh"]
        for name in required:
            self.assertIn(name, BUILTIN_TEMPLATES, f"Missing template: {name}")

    def test_template_structure(self):
        """Test that each template has the required structure."""
        for name, template in BUILTIN_TEMPLATES.items():
            self.assertIn("name", template, f"Template '{name}' missing 'name'")
            self.assertIn("description", template, f"Template '{name}' missing 'description'")
            self.assertIn("common_commands", template, f"Template '{name}' missing 'common_commands'")
            self.assertIn("parameters", template, f"Template '{name}' missing 'parameters'")
            self.assertIn("examples", template, f"Template '{name}' missing 'examples'")

    def test_template_has_commands(self):
        """Test that each template has at least one common command."""
        for name, template in BUILTIN_TEMPLATES.items():
            self.assertGreater(
                len(template["common_commands"]),
                0,
                f"Template '{name}' has no common commands",
            )

    def test_template_has_examples(self):
        """Test that each template has at least one example."""
        for name, template in BUILTIN_TEMPLATES.items():
            self.assertGreater(
                len(template["examples"]),
                0,
                f"Template '{name}' has no examples",
            )


class TestTemplateManager(unittest.TestCase):
    """Tests for TemplateManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = TemplateManager()

    def test_list_templates(self):
        """Test listing all templates."""
        templates = self.manager.list_templates()
        self.assertGreater(len(templates), 10)
        # Should be sorted
        self.assertEqual(templates, sorted(templates))

    def test_load_existing_template(self):
        """Test loading an existing template."""
        template = self.manager.load_template("git")
        self.assertIsNotNone(template)
        self.assertEqual(template["name"], "git")
        self.assertIn("description", template)

    def test_load_nonexistent_template(self):
        """Test loading a non-existent template."""
        template = self.manager.load_template("nonexistent_tool_xyz")
        self.assertIsNone(template)

    def test_search_by_name(self):
        """Test searching templates by name."""
        results = self.manager.search_templates("git")
        self.assertGreater(len(results), 0)
        names = [r["name"] for r in results]
        self.assertIn("git", names)

    def test_search_by_description(self):
        """Test searching templates by description keyword."""
        results = self.manager.search_templates("version control")
        self.assertGreater(len(results), 0)

    def test_search_by_command(self):
        """Test searching templates by command keyword."""
        results = self.manager.search_templates("clone")
        self.assertGreater(len(results), 0)

    def test_search_no_results(self):
        """Test searching with no matching results."""
        results = self.manager.search_templates("xyznonexistent123")
        self.assertEqual(len(results), 0)

    def test_register_template(self):
        """Test registering a custom template."""
        custom_template = {
            "description": "A custom test tool",
            "common_commands": [
                {"command": "mytool run", "description": "Run the tool"},
            ],
            "parameters": [
                {"name": "mode", "description": "Operation mode"},
            ],
            "examples": ["mytool run --fast"],
        }
        self.manager.register_template("mytool", custom_template)

        loaded = self.manager.load_template("mytool")
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["name"], "mytool")
        self.assertEqual(loaded["description"], "A custom test tool")

        # Should appear in list
        self.assertIn("mytool", self.manager.list_templates())

    def test_register_overwrites(self):
        """Test that registering a template with existing name overwrites it."""
        original = self.manager.load_template("git")
        self.manager.register_template("git", {
            "description": "Overwritten git template",
            "common_commands": [],
            "parameters": [],
            "examples": [],
        })
        overwritten = self.manager.load_template("git")
        self.assertEqual(overwritten["description"], "Overwritten git template")

    def test_get_template_schema(self):
        """Test generating tool schema from template."""
        schema = self.manager.get_template_schema("git")
        self.assertIsNotNone(schema)
        self.assertEqual(schema["type"], "function")
        self.assertEqual(schema["function"]["name"], "shell_git")
        self.assertIn("parameters", schema["function"])

    def test_get_template_schema_nonexistent(self):
        """Test generating schema for non-existent template."""
        schema = self.manager.get_template_schema("nonexistent_xyz")
        self.assertIsNone(schema)

    def test_get_all_schemas(self):
        """Test getting all schemas."""
        schemas = self.manager.get_all_schemas()
        self.assertGreater(len(schemas), 10)
        for name, schema in schemas.items():
            self.assertEqual(schema["type"], "function")
            self.assertIn("function", schema)

    def test_template_command_structure(self):
        """Test that common commands have required fields."""
        for name, template in BUILTIN_TEMPLATES.items():
            for cmd in template["common_commands"]:
                self.assertIn("command", cmd, f"Template '{name}' command missing 'command' field")
                self.assertIn("description", cmd, f"Template '{name}' command missing 'description' field")

    def test_template_parameter_structure(self):
        """Test that parameters have required fields."""
        for name, template in BUILTIN_TEMPLATES.items():
            for param in template["parameters"]:
                self.assertIn("name", param, f"Template '{name}' parameter missing 'name' field")
                self.assertIn("description", param, f"Template '{name}' parameter missing 'description' field")


if __name__ == "__main__":
    unittest.main()
