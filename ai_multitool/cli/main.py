"""Main CLI entry point for ai-multitool"""

import asyncio
import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from ai_multitool.core.llm_client import ClientFactory
from ai_multitool.core.models import Message, MessageRole, ChatHistory
from ai_multitool.config.settings import get_settings
from ai_multitool.utils.file_utils import read_file, read_directory, is_code_file
from ai_multitool.parsers.code_parser import get_parser
from ai_multitool.utils.git_utils import get_git_helper

app = typer.Typer(
    name="ai-multitool",
    help="AI-powered CLI multitool for developers",
    add_completion=False,
)

console = Console()


@app.command()
def hello(name: str = typer.Option("World", help="Name to greet")):
    """Say hello to someone"""
    console.print(f"[bold green]Hello, {name}![/bold green]")


@app.command()
def version():
    """Show version information"""
    from ai_multitool import __version__
    console.print(f"ai-multitool version: [bold]{__version__}[/bold]")


@app.command()
def chat(
    prompt: str = typer.Argument(..., help="Your prompt to the AI"),
    model: str = typer.Option(None, help="AI model to use (default from config)"),
    provider: str = typer.Option(None, help="AI provider (anthropic or openai)"),
    stream: bool = typer.Option(False, help="Stream the response"),
    temperature: float = typer.Option(0.7, help="Temperature for generation"),
):
    """Chat with an AI model"""
    settings = get_settings()

    # Use config defaults if not specified
    provider = provider or "anthropic"
    model = model or settings.default_model
    api_key = settings.anthropic_api_key if provider == "anthropic" else settings.openai_api_key

    if not api_key:
        console.print("[red]Error: API key not found. Set ANTHROPIC_API_KEY or OPENAI_API_KEY in .env[/red]")
        raise typer.Exit(1)

    async def run_chat():
        console.print(Panel(f"[bold cyan]Chatting with {provider}/{model}[/bold cyan]"))
        console.print(f"[dim]Prompt: {prompt}[/dim]\n")

        # Create client
        client = ClientFactory.create_client(provider, api_key, model)

        # Create message
        message = Message(role=MessageRole.USER, content=prompt)

        # Make API call
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Thinking...", total=None)

            if stream:
                # Streaming response
                response_text = ""
                async for chunk in client.stream_chat([message], temperature=temperature):
                    console.print(chunk, end="")
                    response_text += chunk
                console.print()  # New line
            else:
                # Non-streaming response
                response = await client.chat([message], temperature=temperature)
                console.print(Panel(response.content, title="AI Response"))

                # Show metadata
                console.print(
                    f"[dim]Tokens: {response.tokens_used} | "
                    f"Latency: {response.latency_ms:.0f}ms | "
                    f"Cached: {'Yes' if response.cached else 'No'}[/dim]"
                )

    asyncio.run(run_chat())


@app.command()
def analyze(
    path: str = typer.Argument(..., help="File or directory to analyze"),
    model: str = typer.Option(None, help="AI model to use (default from config)"),
    provider: str = typer.Option(None, help="AI provider (anthropic or openai)"),
    structure: bool = typer.Option(False, help="Show code structure without AI analysis"),
    git: bool = typer.Option(True, help="Include git repository context"),
):
    """Analyze code with AI"""
    from pathlib import Path

    settings = get_settings()
    provider = provider or "anthropic"
    model = model or settings.default_model
    api_key = settings.anthropic_api_key if provider == "anthropic" else settings.openai_api_key

    if not api_key and not structure:
        console.print("[red]Error: API key not found. Set ANTHROPIC_API_KEY or OPENAI_API_KEY in .env[/red]")
        raise typer.Exit(1)

    # Get code parser and git helper
    parser = get_parser()
    git_helper = get_git_helper()

    async def run_analyze():
        console.print(Panel(f"[bold cyan]Analyzing: {path}[/bold cyan]"))
        console.print(f"[dim]Provider: {provider} | Model: {model}[/dim]\n")

        # Check if path is file or directory
        path_obj = Path(path)
        if not path_obj.exists():
            console.print(f"[red]Error: Path not found: {path}[/red]")
            raise typer.Exit(1)

        # Get git context
        git_context_str = ""
        if git:
            git_context = git_helper.get_context(str(path_obj.absolute()) if path_obj.is_file() else str(path_obj.absolute()))
            git_context_str = git_helper.context_to_string(git_context)
            if git_context.is_repo:
                console.print(f"[dim]Git: {git_context.branch} | {git_context.status}[/dim]\n")

        # Parse code structure
        if path_obj.is_file():
            structure_obj = parser.parse_file(path)
            if not structure_obj:
                console.print(f"[yellow]Could not parse file: {path}[/yellow]")
                return
            
            structures = [structure_obj]
            console.print(f"[dim]Language: {structure_obj.language}[/dim]")
            console.print(f"[dim]Functions: {len(structure_obj.functions)}[/dim]")
            console.print(f"[dim]Classes: {len(structure_obj.classes)}[/dim]")
            console.print(f"[dim]Complexity: {structure_obj.complexity_score}[/dim]\n")
            
            if structure:
                # Show structure only
                console.print(Panel(parser.structure_to_context(structure_obj), title="Code Structure"))
                if git and git_context.is_repo:
                    console.print(Panel(git_context_str, title="Git Context"))
                return
            
            # Read actual content for AI analysis
            content = read_file(path)
            file_info = f"File: {path_obj.name} ({len(content)} chars)"
            structure_context = parser.structure_to_context(structure_obj)
            
        elif path_obj.is_dir():
            # For directories, parse all code files
            structures = parser.parse_directory(path, max_files=50)
            if not structures:
                console.print("[yellow]No code files found in directory[/yellow]")
                return
            
            summary = parser.get_summary(structures)
            console.print(f"[dim]{summary}[/dim]\n")
            
            if structure:
                # Show structures only
                for s in structures[:10]:
                    console.print(Panel(parser.structure_to_context(s), title=f"{s.file_path}"))
                if len(structures) > 10:
                    console.print(f"[dim]... and {len(structures) - 10} more files[/dim]")
                if git and git_context.is_repo:
                    console.print(Panel(git_context_str, title="Git Context"))
                return
            
            # Read actual content for AI analysis
            content = ""
            for file_path in [s.file_path for s in structures[:10]]:
                try:
                    file_content = read_file(file_path)
                    content += f"\n\n# File: {file_path}\n{file_content}"
                except Exception as e:
                    console.print(f"[yellow]Warning: Could not read {file_path}: {e}[/yellow]")

            file_info = f"Directory: {len(structures)} files analyzed"
            structure_context = summary
        else:
            console.print(f"[red]Error: Not a file or directory: {path}[/red]")
            raise typer.Exit(1)

        # Create client
        client = ClientFactory.create_client(provider, api_key, model)

        # Build prompt with structure and git context
        prompt_parts = [
            f"Analyze the following code:\n\n{file_info}",
        ]
        
        if git_context_str:
            prompt_parts.append(f"\n{git_context_str}")
        
        prompt_parts.extend([
            f"\nCode Structure:\n{structure_context}",
            f"\n```python\n{content[:10000]}\n```",
            "\nPlease provide:",
            "1. A summary of what this code does",
            "2. Any potential issues or improvements",
            "3. Best practices that could be applied",
        ])
        
        prompt = "\n".join(prompt_parts)

        # Make API call
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Analyzing...", total=None)

            response = await client.chat([Message(role=MessageRole.USER, content=prompt)])

        # Display analysis
        console.print(Panel(response.content, title="AI Analysis"))
        console.print(
            f"[dim]Tokens: {response.tokens_used} | "
            f"Latency: {response.latency_ms:.0f}ms[/dim]"
        )

    asyncio.run(run_analyze())


@app.command()
def list_models():
    """List available AI models"""
    console.print("[bold cyan]Available AI Models[/bold cyan]\n")

    models = [
        ("Anthropic", [
            ("claude-3-opus-20240229", "Most capable model", 200000),
            ("claude-3-sonnet-20240229", "Balanced performance", 200000),
            ("claude-3-haiku-20240307", "Fast and efficient", 200000),
        ]),
        ("OpenAI", [
            ("gpt-4-turbo-preview", "Latest GPT-4", 128000),
            ("gpt-4", "Original GPT-4", 8192),
            ("gpt-3.5-turbo", "Fast and cost-effective", 16385),
        ]),
    ]

    for provider, provider_models in models:
        console.print(f"[bold]{provider}:[/bold]")
        for model, description, context in provider_models:
            console.print(f"  - {model}")
            console.print(f"    {description} | Context: {context} tokens")
        console.print()


@app.command()
def config(
    key: str = typer.Argument(None, help="Configuration key to view or set"),
    value: str = typer.Argument(None, help="Value to set (if setting)"),
):
    """View or set configuration"""
    settings = get_settings()

    if key is None:
        # Show all configuration
        console.print("[bold cyan]Current Configuration:[/bold cyan]\n")
        for field_name, field_value in settings.model_dump().items():
            if "api_key" in field_name and field_value:
                # Mask API keys
                masked = field_value[:4] + "*" * (len(field_value) - 4)
                console.print(f"  {field_name}: {masked}")
            else:
                console.print(f"  {field_name}: {field_value}")
    elif value is None:
        # Show specific configuration
        value = getattr(settings, key, None)
        if value is None:
            console.print(f"[yellow]Configuration key '{key}' not found[/yellow]")
        elif "api_key" in key and value:
            masked = value[:4] + "*" * (len(value) - 4)
            console.print(f"{key}: {masked}")
        else:
            console.print(f"{key}: {value}")
    else:
        # Set configuration (would need to update .env file)
        console.print(f"[yellow]Setting configuration is not yet implemented.[/yellow]")
        console.print(f"[dim]To set {key}={value}, edit your .env file directly.[/dim]")


if __name__ == "__main__":
    app()
