"""Main CLI entry point for ai-multitool"""

import asyncio
import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from ai_multitool.core.llm_client import ClientFactory
from ai_multitool.core.models import Message, MessageRole, ChatHistory
from ai_multitool.config.settings import get_settings

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
):
    """Analyze code with AI"""
    console.print(Panel(f"[bold cyan]Analyzing: {path}[/bold cyan]"))
    console.print(f"[dim]Using model: {model or 'default'}[/dim]")
    console.print("\n[yellow]Analysis will appear here...[/yellow]")
    # TODO: Implement analyze command


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
