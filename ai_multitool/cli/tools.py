"""Tool server for terminal AI integration.

This module provides a tool server that can be used by terminal AI tools
(Claude Code, Devin, OpenCode, Gemini CLI, Qwen CLI) to execute ai-multitool
capabilities as tools.
"""

import json
import asyncio
from typing import Dict, Any, Optional, List
from pathlib import Path
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ai_multitool.adapters import (
    ClaudeCodeAdapter,
    DevinAdapter,
    OpenCodeAdapter,
    GeminiAdapter,
    QwenAdapter,
    create_claude_code_adapter,
    create_devin_adapter,
    create_opencode_adapter,
    create_gemini_adapter,
    create_qwen_adapter,
)
from ai_multitool.plugins import Provider, PluginConfig
from ai_multitool.config.settings import get_settings

console = Console()


class ToolServer:
    """Tool server for terminal AI integration."""

    def __init__(self, cli_tool: str):
        """Initialize the tool server for a specific CLI tool.

        Args:
            cli_tool: The CLI tool name (claude-code, devin, opencode, gemini, qwen)
        """
        self.cli_tool = cli_tool
        self.adapter = None
        self._initialize_adapter()

    def _initialize_adapter(self):
        """Initialize the appropriate adapter for the CLI tool."""
        settings = get_settings()

        adapter_map = {
            "claude-code": (create_claude_code_adapter, Provider.ANTHROPIC),
            "devin": (create_devin_adapter, Provider.ANTHROPIC),
            "opencode": (create_opencode_adapter, Provider.ANTHROPIC),
            "gemini": (create_gemini_adapter, Provider.ANTHROPIC),
            "qwen": (create_qwen_adapter, Provider.ANTHROPIC),
        }

        if self.cli_tool not in adapter_map:
            raise ValueError(f"Unsupported CLI tool: {self.cli_tool}")

        factory, default_provider = adapter_map[self.cli_tool]

        # Get API key based on provider
        api_key = settings.get_anthropic_key() if default_provider == Provider.ANTHROPIC else settings.get_openai_key()

        if not api_key:
            raise ValueError(f"API key not found for {default_provider}")

        # Create adapter
        self.adapter = factory(
            api_key=api_key,
            provider=str(default_provider),
            model=settings.default_model,
            enable_code_analysis=True,
            enable_git_integration=True,
        )

    def get_tools(self) -> List[Dict[str, Any]]:
        """Get tool definitions for the CLI tool.

        Returns:
            List of tool definitions in the appropriate format
        """
        return self.adapter.get_tool_definitions()

    def get_tools_schema(self) -> Dict[str, Any]:
        """Get tool definitions as a schema.

        Returns:
            Dictionary mapping tool names to their definitions
        """
        return self.adapter.get_tool_definitions_schema()

    def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """Execute a tool.

        Args:
            tool_name: Name of the tool to execute
            **kwargs: Tool arguments

        Returns:
            Tool execution result
        """
        return self.adapter.execute_tool(tool_name, **kwargs)

    async def chat(self, message: str, system_prompt: Optional[str] = None) -> str:
        """Chat with the AI.

        Args:
            message: User message
            system_prompt: Optional system prompt

        Returns:
            AI response
        """
        return await self.adapter.chat(message, system_prompt=system_prompt)


def list_available_tools(cli_tool: str):
    """List available tools for a CLI tool.

    Args:
        cli_tool: The CLI tool name
    """
    try:
        server = ToolServer(cli_tool)
        tools = server.get_tools()

        console.print(Panel(f"[bold cyan]Available Tools for {cli_tool}[/bold cyan]"))

        table = Table()
        table.add_column("Tool Name", style="cyan")
        table.add_column("Description", style="green")
        table.add_column("Category", style="yellow")

        for tool in tools:
            # Handle different tool formats
            if "name" in tool:
                name = tool["name"]
                description = tool.get("description", "No description")
                category = tool.get("category", "General")
            elif "function" in tool:
                name = tool["function"]["name"]
                description = tool["function"].get("description", "No description")
                category = tool["function"].get("category", "General")
            else:
                continue

            table.add_row(name, description, category)

        console.print(table)
        console.print(f"\n[dim]Total tools: {len(tools)}[/dim]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


def export_tools_schema(cli_tool: str, output_file: Optional[str] = None):
    """Export tools schema to JSON.

    Args:
        cli_tool: The CLI tool name
        output_file: Optional output file path
    """
    try:
        server = ToolServer(cli_tool)
        schema = server.get_tools_schema()

        if output_file:
            with open(output_file, 'w') as f:
                json.dump(schema, f, indent=2)
            console.print(f"[green]Schema exported to {output_file}[/green]")
        else:
            console.print(json.dumps(schema, indent=2))

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


def execute_tool_command(cli_tool: str, tool_name: str, **kwargs):
    """Execute a tool command.

    Args:
        cli_tool: The CLI tool name
        tool_name: Name of the tool to execute
        **kwargs: Tool arguments
    """
    try:
        server = ToolServer(cli_tool)
        result = server.execute_tool(tool_name, **kwargs)

        console.print(Panel(f"[bold cyan]Tool: {tool_name}[/bold cyan]"))
        console.print(json.dumps(result, indent=2) if isinstance(result, dict) else str(result))

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


def create_cli_app():
    """Create the CLI app for tool server."""
    app = typer.Typer(
        name="ai-multitool-tools",
        help="Tool server for terminal AI integration",
        add_completion=False,
    )

    @app.command()
    def list(
        cli_tool: str = typer.Argument(..., help="CLI tool (claude-code, devin, opencode, gemini, qwen)")
    ):
        """List available tools for a CLI tool"""
        list_available_tools(cli_tool)

    @app.command()
    def schema(
        cli_tool: str = typer.Argument(..., help="CLI tool (claude-code, devin, opencode, gemini, qwen)"),
        output: str = typer.Option(None, "--output", "-o", help="Output file path")
    ):
        """Export tools schema as JSON"""
        export_tools_schema(cli_tool, output)

    @app.command()
    def execute(
        cli_tool: str = typer.Argument(..., help="CLI tool (claude-code, devin, opencode, gemini, qwen)"),
        tool_name: str = typer.Argument(..., help="Tool name to execute"),
        args: List[str] = typer.Option(None, "--arg", "-a", help="Tool arguments (key=value)")
    ):
        """Execute a tool"""
        # Parse arguments
        kwargs = {}
        if args:
            for arg in args:
                if "=" in arg:
                    key, value = arg.split("=", 1)
                    kwargs[key] = value

        execute_tool_command(cli_tool, tool_name, **kwargs)

    @app.command()
    def chat(
        cli_tool: str = typer.Argument(..., help="CLI tool (claude-code, devin, opencode, gemini, qwen)"),
        message: str = typer.Argument(..., help="Message to send")
    ):
        """Chat with the AI using the CLI tool's adapter"""
        async def run_chat():
            try:
                server = ToolServer(cli_tool)
                response = await server.chat(message)
                console.print(Panel(response, title="AI Response"))
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                raise typer.Exit(1)

        asyncio.run(run_chat())

    return app


if __name__ == "__main__":
    app = create_cli_app()
    app()

# Export app for CLI entry point
app = create_cli_app()
