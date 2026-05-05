"""Advanced features usage example."""

import asyncio
from ai_multitool import AnthropicClient, AdvancedCodeRefactoring, AdvancedBugDetection, AdvancedCommitGenerator


async def main():
    """Example of using advanced features."""
    
    # Create LLM client
    client = AnthropicClient(
        api_key="your-api-key",
        model="claude-3-sonnet-20240229"
    )
    
    # Example 1: Code refactoring
    print("=== Code Refactoring ===")
    refactoring_tool = AdvancedCodeRefactoring(client)
    
    refactor_result = await refactoring_tool.execute(
        file_path="main.py",
        aggressive=False,
        focus_areas=["readability"]
    )
    
    if refactor_result.success:
        print(f"Refactoring suggestions: {refactor_result.suggestions}")
        print(f"Confidence: {refactor_result.confidence}")
    
    # Example 2: Bug detection
    print("\n=== Bug Detection ===")
    bug_tool = AdvancedBugDetection(client)
    
    bug_result = await bug_tool.execute(
        file_path="main.py",
        severity="all",
        include_fixes=True
    )
    
    if bug_result.success:
        print(f"Bugs found: {bug_result.data['total_bugs']}")
        print(f"Critical bugs: {bug_result.metrics['critical_bugs']}")
    
    # Example 3: Commit generation
    print("\n=== Commit Generation ===")
    commit_tool = AdvancedCommitGenerator(client)
    
    commit_result = await commit_tool.execute(
        repo_path=".",
        style="conventional"
    )
    
    if commit_result.success:
        print(f"Commit message: {commit_result.data['commit_message']}")
    
    # Example 4: Using tool pipeline
    print("\n=== Tool Pipeline ===")
    from ai_multitool import ToolPipeline
    
    pipeline = ToolPipeline([
        AdvancedBugDetection(client),
        AdvancedCodeRefactoring(client)
    ])
    
    pipeline_results = await pipeline.execute_sequential(file_path="main.py")
    print(f"Pipeline executed {len(pipeline_results)} tools")


if __name__ == "__main__":
    asyncio.run(main())
