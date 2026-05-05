"""Main CLI entry point for ai-multitool"""

import asyncio
import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from ai_multitool.core.llm_client import ClientFactory
from ai_multitool.core.models import Message, MessageRole, ChatHistory
from ai_multitool.core.exceptions import (
    AIMultitoolError,
    APIKeyError,
    APIError,
    ConfigurationError,
    FileOperationError,
    NetworkError,
    ValidationError,
)
from ai_multitool.config.settings import get_settings
from ai_multitool.utils.file_utils import read_file, read_directory, is_code_file
from ai_multitool.parsers.code_parser import get_parser
from ai_multitool.utils.git_utils import get_git_helper
from ai_multitool.utils.context_builder import get_context_builder
from ai_multitool.utils.key_manager import get_key_manager
from ai_multitool.utils.sanitizer import get_sanitizer
from ai_multitool.utils.metrics import get_metrics_collector, MetricsContext
from ai_multitool.utils.rag_helper import get_rag_context, check_rag_available

app = typer.Typer(
    name="ai-multitool",
    help="AI-powered CLI multitool for developers",
    add_completion=False,
)

console = Console()


def handle_error(error: Exception) -> None:
    """Handle and display errors nicely."""
    if isinstance(error, AIMultitoolError):
        # Custom exceptions with suggestions
        console.print(f"[bold red]Error:[/bold red] {error.message}")
        if error.suggestion:
            console.print(f"[cyan]💡 {error.suggestion}[/cyan]")
        if error.details:
            console.print(f"[dim]Details: {error.details}[/dim]")
    elif isinstance(error, KeyboardInterrupt):
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
    else:
        # Unexpected errors
        console.print(f"[bold red]Unexpected error:[/bold red] {error}")
        console.print(f"[dim]Error type: {type(error).__name__}[/dim]")
        console.print("[cyan]💡 If this persists, please report the issue at https://github.com/BlackWh1te/PyPi/issues[/cyan]")


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
    rag: bool = typer.Option(False, help="Use RAG to retrieve relevant context from indexed documents"),
    rag_index: str = typer.Option(None, help="Path to RAG index (default: ~/.ai-multitool/index)"),
    rag_top_k: int = typer.Option(3, help="Number of RAG results to include"),
):
    """Chat with an AI model"""
    settings = get_settings()

    # Use config defaults if not specified
    provider = provider or "anthropic"
    model = model or settings.default_model
    api_key = settings.get_anthropic_key() if provider == "anthropic" else settings.get_openai_key()

    if not api_key:
        console.print("[red]Error: API key not found. Set ANTHROPIC_API_KEY or OPENAI_API_KEY in .env, or use 'ai-multitool keys set'[/red]")
        raise typer.Exit(1)

    async def run_chat():
        try:
            console.print(Panel(f"[bold cyan]Chatting with {provider}/{model}[/bold cyan]"))
            console.print(f"[dim]Prompt: {prompt}[/dim]\n")

            # Get RAG context if enabled
            rag_context = ""
            if rag:
                if check_rag_available(rag_index):
                    console.print(f"[dim]Retrieving RAG context...[/dim]")
                    rag_context = get_rag_context(prompt, rag_index, rag_top_k)
                    if rag_context:
                        console.print(f"[dim]Found {rag_top_k} relevant documents[/dim]\n")
                    else:
                        console.print(f"[yellow]No relevant documents found[/yellow]\n")
                else:
                    console.print(f"[yellow]RAG index not found. Run 'ai-multitool rag index <path>' to create an index.[/yellow]\n")

            # Build enhanced prompt with RAG context
            if rag_context:
                enhanced_prompt = f"""Use the following retrieved context to answer the user's question:

{rag_context}

User Question: {prompt}

Please provide a helpful answer based on the retrieved context. If the context doesn't contain relevant information, say so and provide a general response."""
            else:
                enhanced_prompt = prompt

            # Create client
            client = ClientFactory.create_client(provider, api_key, model)

            # Create message
            message = Message(role=MessageRole.USER, content=enhanced_prompt)

            # Get metrics collector
            metrics_collector = get_metrics_collector()

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
                    with MetricsContext(metrics_collector, provider, model, "chat") as metrics_ctx:
                        async for chunk in client.stream_chat([message], temperature=temperature):
                            console.print(chunk, end="")
                            response_text += chunk
                    console.print()  # New line
                else:
                    # Non-streaming response
                    with MetricsContext(metrics_collector, provider, model, "chat") as metrics_ctx:
                        response = await client.chat([message], temperature=temperature)
                        metrics_ctx.tokens_used = response.tokens_used
                        metrics_ctx.cached = response.cached
                    
                    console.print(Panel(response.content, title="AI Response"))

                    # Show metadata
                    console.print(
                        f"[dim]Tokens: {response.tokens_used} | "
                        f"Latency: {response.latency_ms:.0f}ms | "
                        f"Cached: {'Yes' if response.cached else 'No'}[/dim]"
                    )
        except Exception as e:
            handle_error(e)
            raise typer.Exit(1)

    asyncio.run(run_chat())


@app.command()
def analyze(
    path: str = typer.Argument(..., help="File or directory to analyze"),
    model: str = typer.Option(None, help="AI model to use (default from config)"),
    provider: str = typer.Option(None, help="AI provider (anthropic or openai)"),
    structure: bool = typer.Option(False, help="Show code structure without AI analysis"),
    git: bool = typer.Option(True, help="Include git repository context"),
    context: bool = typer.Option(True, help="Use smart context builder for enhanced analysis"),
    sanitize: bool = typer.Option(True, help="Sanitize content for security (redact sensitive data)"),
    rag_context: bool = typer.Option(False, help="Use RAG to retrieve relevant documentation context"),
    rag_index: str = typer.Option(None, help="Path to RAG index (default: ~/.ai-multitool/index)"),
    rag_top_k: int = typer.Option(3, help="Number of RAG results to include"),
):
    """Analyze code with AI"""
    from pathlib import Path

    settings = get_settings()
    provider = provider or "anthropic"
    model = model or settings.default_model
    api_key = settings.get_anthropic_key() if provider == "anthropic" else settings.get_openai_key()

    if not api_key and not structure:
        console.print("[red]Error: API key not found. Set ANTHROPIC_API_KEY or OPENAI_API_KEY in .env, or use 'ai-multitool keys set'[/red]")
        raise typer.Exit(1)

    # Get helpers
    parser = get_parser()
    git_helper = get_git_helper()
    context_builder = get_context_builder()
    sanitizer = get_sanitizer()

    async def run_analyze():
        try:
            console.print(Panel(f"[bold cyan]Analyzing: {path}[/bold cyan]"))
            console.print(f"[dim]Provider: {provider} | Model: {model}[/dim]\n")

            # Check if path is file or directory
            path_obj = Path(path)
            if not path_obj.exists():
                raise FileOperationError(f"Path not found: {path}", path, suggestion="Check if the file/directory path is correct")

            # Build smart context
            if context:
                analysis_context = context_builder.build_context(
                    path,
                    include_git=git,
                    include_related=True,
                    max_related=5,
                    max_context_length=8000
                )
                
                if analysis_context.git_context and analysis_context.git_context.is_repo:
                    console.print(f"[dim]Git: {analysis_context.git_context.branch} | {analysis_context.git_context.status}[/dim]")
                
                if analysis_context.code_structure:
                    console.print(f"[dim]Language: {analysis_context.code_structure.language}[/dim]")
                    console.print(f"[dim]Functions: {len(analysis_context.code_structure.functions)}[/dim]")
                    console.print(f"[dim]Classes: {len(analysis_context.code_structure.classes)}[/dim]")
                    console.print(f"[dim]Complexity: {analysis_context.code_structure.complexity_score}[/dim]\n")
                
                if structure:
                    # Show context only
                    console.print(Panel(analysis_context.context_string, title="Analysis Context"))
                    return
                
                context_str = analysis_context.context_string
            else:
                # Use legacy approach
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
                    
                    content = read_file(path)
                    file_info = f"File: {path_obj.name} ({len(content)} chars)"
                    structure_context = parser.structure_to_context(structure_obj)
                    
                elif path_obj.is_dir():
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

                # Build prompt
                prompt_parts = [f"Analyze the following code:\n\n{file_info}"]
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
                context_str = "\n".join(prompt_parts)

            # Read content for AI analysis
            if path_obj.is_file():
                content = read_file(path)
                
                # Sanitize content if enabled
                if sanitize:
                    result = sanitizer.sanitize(content, path)
                    if result.issues_found:
                        console.print(f"[yellow]Security issues found: {', '.join(result.issues_found)}[/yellow]")
                    if result.warnings:
                        console.print(f"[dim]Warnings: {', '.join(result.warnings)}[/dim]")
                    content = result.sanitized_content
            else:
                structures = parser.parse_directory(path, max_files=10)
                content = ""
                for file_path in [s.file_path for s in structures[:10]]:
                    try:
                        file_content = read_file(file_path)
                        
                        # Check file safety
                        is_safe, warnings = sanitizer.check_file_safety(file_path)
                        if not is_safe:
                            console.print(f"[yellow]Skipping potentially unsafe file: {file_path}[/yellow]")
                            console.print(f"[dim]Reason: {warnings[0]}[/dim]")
                            continue
                        
                        # Sanitize content if enabled
                        if sanitize:
                            result = sanitizer.sanitize(file_content, file_path)
                            if result.issues_found:
                                console.print(f"[yellow]Security issues in {Path(file_path).name}: {', '.join(result.issues_found)}[/yellow]")
                            file_content = result.sanitized_content
                        
                        content += f"\n\n# File: {file_path}\n{file_content}"
                    except Exception as e:
                        console.print(f"[yellow]Warning: Could not read {file_path}: {e}[/yellow]")

            # Get RAG context if enabled
            rag_retrieved_context = ""
            if rag_context:
                # Build a query from the path for RAG
                rag_query = f"Analyze code in {path}"
                if check_rag_available(rag_index):
                    console.print(f"[dim]Retrieving RAG context...[/dim]")
                    rag_retrieved_context = get_rag_context(rag_query, rag_index, rag_top_k)
                    if rag_retrieved_context:
                        console.print(f"[dim]Found {rag_top_k} relevant documents[/dim]\n")
                    else:
                        console.print(f"[yellow]No relevant documentation found[/yellow]\n")
                else:
                    console.print(f"[yellow]RAG index not found. Run 'ai-multitool rag index <path>' to create an index.[/yellow]\n")

            # Build final prompt with smart context
            if context:
                # Build prompt with RAG context if available
                rag_section = ""
                if rag_retrieved_context:
                    rag_section = f"\n\nRelevant Documentation:\n{rag_retrieved_context}\n"
                
                prompt = f"""Analyze the following code with the provided context:

{context_str}
{rag_section}
Code Content:
```python
{content[:10000]}
```

Please provide:
1. A summary of what this code does
2. Any potential issues or improvements
3. Best practices that could be applied
"""
            else:
                prompt = context_str
                if rag_retrieved_context:
                    prompt = f"""{context_str}

Relevant Documentation:
{rag_retrieved_context}

Please analyze the code considering the documentation above."""

            # Create client
            client = ClientFactory.create_client(provider, api_key, model)

            # Get metrics collector
            metrics_collector = get_metrics_collector()

            # Make API call
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Analyzing...", total=None)

                with MetricsContext(metrics_collector, provider, model, "analyze") as metrics_ctx:
                    response = await client.chat([Message(role=MessageRole.USER, content=prompt)])
                    metrics_ctx.tokens_used = response.tokens_used
                    metrics_ctx.cached = response.cached

            # Display analysis
            console.print(Panel(response.content, title="AI Analysis"))
            console.print(
                f"[dim]Tokens: {response.tokens_used} | "
                f"Latency: {response.latency_ms:.0f}ms[/dim]"
            )
        except Exception as e:
            handle_error(e)
            raise typer.Exit(1)

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


# Create a sub-app for keys management
keys_app = typer.Typer(help="Manage API keys securely using system keyring")


@keys_app.command("set")
def keys_set(
    provider: str = typer.Argument(..., help="Provider (anthropic or openai)"),
    key: str = typer.Option(..., prompt=True, hide_input=True, help="API key to store"),
):
    """Store an API key securely in the system keyring"""
    key_manager = get_key_manager()
    
    if not key_manager.is_available():
        console.print("[red]Error: keyring library not installed. Install with: pip install keyring[/red]")
        raise typer.Exit(1)
    
    provider = provider.lower()
    
    if provider == "anthropic":
        success = key_manager.set_anthropic_key(key)
        if success:
            console.print("[bold green]✓[/bold green] Anthropic API key stored securely")
        else:
            console.print("[red]Error storing Anthropic API key[/red]")
            raise typer.Exit(1)
    elif provider == "openai":
        success = key_manager.set_openai_key(key)
        if success:
            console.print("[bold green]✓[/bold green] OpenAI API key stored securely")
        else:
            console.print("[red]Error storing OpenAI API key[/red]")
            raise typer.Exit(1)
    else:
        console.print(f"[red]Error: Unknown provider '{provider}'. Use 'anthropic' or 'openai'[/red]")
        raise typer.Exit(1)


@keys_app.command("get")
def keys_get(
    provider: str = typer.Argument(..., help="Provider (anthropic or openai)"),
):
    """Retrieve an API key from the system keyring"""
    key_manager = get_key_manager()
    
    if not key_manager.is_available():
        console.print("[red]Error: keyring library not installed[/red]")
        raise typer.Exit(1)
    
    provider = provider.lower()
    
    if provider == "anthropic":
        key = key_manager.get_anthropic_key()
    elif provider == "openai":
        key = key_manager.get_openai_key()
    else:
        console.print(f"[red]Error: Unknown provider '{provider}'. Use 'anthropic' or 'openai'[/red]")
        raise typer.Exit(1)
    
    if key:
        # Show masked key
        masked = key[:4] + "*" * (len(key) - 4)
        console.print(f"[bold cyan]{provider.capitalize()} API key:[/bold cyan] {masked}")
        console.print(f"[dim]Full key: {key}[/dim]")
    else:
        console.print(f"[yellow]No {provider} API key found in keyring or environment[/yellow]")


@keys_app.command("delete")
def keys_delete(
    provider: str = typer.Argument(..., help="Provider (anthropic or openai)"),
):
    """Delete an API key from the system keyring"""
    key_manager = get_key_manager()
    
    if not key_manager.is_available():
        console.print("[red]Error: keyring library not installed[/red]")
        raise typer.Exit(1)
    
    provider = provider.lower()
    
    if provider == "anthropic":
        success = key_manager.delete_anthropic_key()
        if success:
            console.print("[bold green]✓[/bold green] Anthropic API key deleted from keyring")
        else:
            console.print("[yellow]No Anthropic API key found in keyring[/yellow]")
    elif provider == "openai":
        success = key_manager.delete_openai_key()
        if success:
            console.print("[bold green]✓[/bold green] OpenAI API key deleted from keyring")
        else:
            console.print("[yellow]No OpenAI API key found in keyring[/yellow]")
    else:
        console.print(f"[red]Error: Unknown provider '{provider}'. Use 'anthropic' or 'openai'[/red]")
        raise typer.Exit(1)


@keys_app.command("list")
def keys_list():
    """List all stored API keys"""
    key_manager = get_key_manager()
    
    if not key_manager.is_available():
        console.print("[red]Error: keyring library not installed. Install with: pip install keyring[/red]")
        raise typer.Exit(1)
    
    keys = key_manager.list_keys()
    
    console.print("[bold cyan]Stored API Keys:[/bold cyan]\n")
    
    if not keys:
        console.print("[dim]No API keys stored in keyring[/dim]")
        console.print("[dim]Keys can also be set via environment variables (ANTHROPIC_API_KEY, OPENAI_API_KEY)[/dim]")
    else:
        for key_id in keys:
            if key_id == key_manager.ANTHROPIC_KEY:
                key = key_manager.get_anthropic_key()
                if key:
                    masked = key[:4] + "*" * (len(key) - 4)
                    console.print(f"  [bold]anthropic:[/bold] {masked}")
            elif key_id == key_manager.OPENAI_KEY:
                key = key_manager.get_openai_key()
                if key:
                    masked = key[:4] + "*" * (len(key) - 4)
                    console.print(f"  [bold]openai:[/bold] {masked}")
    
    # Check environment variables
    anthropic_env = key_manager.get_anthropic_key()
    openai_env = key_manager.get_openai_key()
    
    if anthropic_env and key_manager.ANTHROPIC_KEY not in keys:
        console.print(f"  [dim]anthropic (from env): {anthropic_env[:4]}{'*' * (len(anthropic_env) - 4)}[/dim]")
    if openai_env and key_manager.OPENAI_KEY not in keys:
        console.print(f"  [dim]openai (from env): {openai_env[:4]}{'*' * (len(openai_env) - 4)}[/dim]")


@keys_app.command("migrate")
def keys_migrate():
    """Migrate API keys from .env file to secure keyring"""
    key_manager = get_key_manager()
    
    if not key_manager.is_available():
        console.print("[red]Error: keyring library not installed. Install with: pip install keyring[/red]")
        raise typer.Exit(1)
    
    console.print("[bold cyan]Migrating API keys from environment to keyring...[/bold cyan]\n")
    
    migrated = key_manager.migrate_from_env()
    
    if migrated:
        for provider, success in migrated.items():
            if success:
                console.print(f"[bold green]✓[/bold green] {provider.capitalize()} key migrated to keyring")
            else:
                console.print(f"[yellow]Could not migrate {provider} key[/yellow]")
        
        console.print("\n[dim]Tip: You can now remove the API keys from your .env file for better security[/dim]")
    else:
        console.print("[yellow]No keys to migrate (keys already in keyring or not found in environment)[/yellow]")


# Add keys sub-app to main app
app.add_typer(keys_app, name="keys")


@app.command()
def stats(
    days: int = typer.Option(30, help="Number of days to include in statistics"),
    recent: int = typer.Option(10, help="Number of recent calls to show"),
):
    """Show usage statistics and metrics"""
    metrics_collector = get_metrics_collector()
    
    stats = metrics_collector.get_stats(days=days)
    recent_calls = metrics_collector.get_recent_calls(limit=recent)
    
    console.print(Panel(f"[bold cyan]Usage Statistics (Last {days} days)[/bold cyan]"))
    
    if stats.total_calls == 0:
        console.print("\n[dim]No API calls recorded yet.[/dim]")
        return
    
    # Summary
    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"  Total calls: {stats.total_calls}")
    console.print(f"  Successful: {stats.successful_calls}")
    console.print(f"  Failed: {stats.failed_calls}")
    console.print(f"  Total tokens: {stats.total_tokens:,}")
    console.print(f"  Avg latency: {stats.avg_latency_ms:.0f}ms")
    console.print(f"  Cache hits: {stats.cache_hits} ({stats.cache_hits/stats.total_calls*100:.1f}%)")
    
    # By provider
    console.print(f"\n[bold]By Provider:[/bold]")
    for provider, count in sorted(stats.by_provider.items(), key=lambda x: x[1], reverse=True):
        console.print(f"  {provider}: {count}")
    
    # By model
    console.print(f"\n[bold]By Model:[/bold]")
    for model, count in sorted(stats.by_model.items(), key=lambda x: x[1], reverse=True):
        console.print(f"  {model}: {count}")
    
    # By command
    console.print(f"\n[bold]By Command:[/bold]")
    for command, count in sorted(stats.by_command.items(), key=lambda x: x[1], reverse=True):
        console.print(f"  {command}: {count}")
    
    # Recent calls
    if recent_calls:
        console.print(f"\n[bold]Recent Calls (Last {len(recent_calls)}):[/bold]")
        for call in recent_calls:
            status = "[green]✓[/green]" if call.success else "[red]✗[/red]"
            cache = "[dim](cached)[/dim]" if call.cached else ""
            console.print(f"  {status} {call.timestamp[:19]} | {call.provider}/{call.model} | {call.command} | {call.tokens_used} tokens | {call.latency_ms:.0f}ms {cache}")


@app.command()
def clear_stats():
    """Clear all usage metrics"""
    metrics_collector = get_metrics_collector()
    
    console.print("[yellow]This will delete all stored usage metrics.[/yellow]")
    console.print("[dim]Metrics are stored locally and are not shared with any service.[/dim]")
    
    confirm = typer.confirm("Are you sure you want to clear all metrics?")
    if not confirm:
        console.print("[dim]Cancelled.[/dim]")
        return
    
    metrics_collector.clear_metrics()
    console.print("[bold green]✓[/bold green] Metrics cleared")


# Create a sub-app for RAG operations
rag_app = typer.Typer(help="RAG (Retrieval-Augmented Generation) operations")


@rag_app.command("index")
def rag_index(
    path: str = typer.Argument(..., help="File or directory to index"),
    pattern: str = typer.Option("*.md", help="File pattern to match (e.g., *.md, *.txt)"),
    output: str = typer.Option(None, help="Output file to save the index"),
    chunk_size: int = typer.Option(1000, help="Chunk size in characters"),
    chunk_overlap: int = typer.Option(200, help="Chunk overlap in characters"),
    provider: str = typer.Option("openai", help="Embedding provider (openai)"),
):
    """Index documents for RAG search"""
    from pathlib import Path
    from ai_multitool.rag.embeddings import OpenAIEmbeddings
    from ai_multitool.rag.chunkers import RecursiveCharacterChunker
    from ai_multitool.rag.indexer import DocumentIndexer
    
    settings = get_settings()
    
    # Get API key for embeddings
    if provider == "openai":
        api_key = settings.get_openai_key()
        if not api_key:
            console.print("[red]Error: OpenAI API key not found. Set OPENAI_API_KEY in .env or use 'ai-multitool keys set openai'[/red]")
            raise typer.Exit(1)
        
        embedding_model = OpenAIEmbeddings(api_key=api_key)
    else:
        console.print(f"[red]Error: Unknown provider '{provider}'. Use 'openai'[/red]")
        raise typer.Exit(1)
    
    # Initialize chunker
    chunker = RecursiveCharacterChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    
    # Initialize indexer
    indexer = DocumentIndexer(embedding_model=embedding_model, chunker=chunker)
    
    try:
        console.print(Panel(f"[bold cyan]Indexing: {path}[/bold cyan]"))
        console.print(f"[dim]Pattern: {pattern} | Chunk size: {chunk_size} | Overlap: {chunk_overlap}[/dim]\n")
        
        path_obj = Path(path)
        if path_obj.is_file():
            # Index single file
            content = read_file(path)
            from ai_multitool.rag.indexer import Document
            document = Document(
                text=content,
                doc_id=str(path_obj),
                metadata={"file_path": str(path_obj), "file_name": path_obj.name}
            )
            indexer.add_document(document)
            console.print(f"[bold green]✓[/bold green] Indexed 1 document")
        elif path_obj.is_dir():
            # Index directory
            count = indexer.index_directory(str(path_obj), pattern=pattern)
            console.print(f"[bold green]✓[/bold green] Indexed {count} documents")
        else:
            console.print(f"[red]Error: Not a file or directory: {path}[/red]")
            raise typer.Exit(1)
        
        # Show stats
        stats = indexer.get_stats()
        console.print(f"\n[dim]Total chunks: {stats['total_chunks']}[/dim]")
        console.print(f"[dim]Dimension: {stats['dimension']}[/dim]")
        
        # Save index if output specified
        if output:
            indexer.save(output)
            console.print(f"[bold green]✓[/bold green] Index saved to {output}")
        
        # Save default index location if not specified
        if not output:
            default_index = Path.home() / ".ai-multitool" / "index"
            default_index.parent.mkdir(parents=True, exist_ok=True)
            indexer.save(str(default_index))
            console.print(f"[dim]Index saved to {default_index}[/dim]")
        
    except Exception as e:
        handle_error(e)
        raise typer.Exit(1)


@rag_app.command("search")
def rag_search(
    query: str = typer.Argument(..., help="Search query"),
    top_k: int = typer.Option(5, help="Number of results to return"),
    index: str = typer.Option(None, help="Index file to load (default: ~/.ai-multitool/index)"),
    provider: str = typer.Option("openai", help="Embedding provider (openai)"),
):
    """Search indexed documents"""
    from pathlib import Path
    from ai_multitool.rag.embeddings import OpenAIEmbeddings
    from ai_multitool.rag.retriever import SimilarityRetriever
    from ai_multitool.rag.vector_store import InMemoryVectorStore
    
    settings = get_settings()
    
    # Determine index path
    if index is None:
        index = str(Path.home() / ".ai-multitool" / "index")
    
    # Check if index exists
    if not Path(index).with_suffix(".json").exists():
        console.print(f"[red]Error: Index not found at {index}[/red]")
        console.print("[dim]Run 'ai-multitool rag index <path>' to create an index first[/dim]")
        raise typer.Exit(1)
    
    # Get API key for embeddings
    if provider == "openai":
        api_key = settings.get_openai_key()
        if not api_key:
            console.print("[red]Error: OpenAI API key not found. Set OPENAI_API_KEY in .env or use 'ai-multitool keys set openai'[/red]")
            raise typer.Exit(1)
        
        embedding_model = OpenAIEmbeddings(api_key=api_key)
    else:
        console.print(f"[red]Error: Unknown provider '{provider}'. Use 'openai'[/red]")
        raise typer.Exit(1)
    
    try:
        console.print(Panel(f"[bold cyan]Searching: {query}[/bold cyan]"))
        console.print(f"[dim]Index: {index} | Top-K: {top_k}[/dim]\n")
        
        # Load vector store
        vector_store = InMemoryVectorStore(dimension=1536)
        vector_store.load(index)
        
        # Initialize retriever
        retriever = SimilarityRetriever(vector_store=vector_store, embedding_model=embedding_model)
        
        # Search
        result = retriever.retrieve(query, top_k=top_k)
        
        # Display results
        console.print(Panel(retriever.format_results(result), title="Search Results"))
        
    except Exception as e:
        handle_error(e)
        raise typer.Exit(1)


@rag_app.command("stats")
def rag_stats(
    index: str = typer.Option(None, help="Index file to load (default: ~/.ai-multitool/index)"),
):
    """Show statistics about an index"""
    from pathlib import Path
    from ai_multitool.rag.vector_store import InMemoryVectorStore
    
    # Determine index path
    if index is None:
        index = str(Path.home() / ".ai-multitool" / "index")
    
    # Check if index exists
    if not Path(index).with_suffix(".json").exists():
        console.print(f"[red]Error: Index not found at {index}[/red]")
        console.print("[dim]Run 'ai-multitool rag index <path>' to create an index first[/dim]")
        raise typer.Exit(1)
    
    try:
        # Load vector store
        vector_store = InMemoryVectorStore(dimension=1536)
        vector_store.load(index)
        
        console.print(Panel(f"[bold cyan]Index Statistics[/bold cyan]"))
        console.print(f"\n[bold]Total chunks:[/bold] {vector_store.count()}")
        console.print(f"[bold]Dimension:[/bold] {vector_store.dimension}")
        
    except Exception as e:
        handle_error(e)
        raise typer.Exit(1)


# Add RAG sub-app to main app
app.add_typer(rag_app, name="rag")


if __name__ == "__main__":
    app()
