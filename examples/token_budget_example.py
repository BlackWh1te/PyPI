"""
Example: Using Token Budget Controls

This example demonstrates how to use token budget controls to prevent
accidental overspending on LLM API calls.
"""

import asyncio
from ai_multitool.advanced.base import AdvancedSettings, AdvancedToolConfig
from ai_multitool.advanced.performance.profiler import PerformanceProfiler

# Mock LLM client for demonstration
class MockLLMClient:
    async def chat(self, messages):
        # Simulate token usage
        return type('Response', (), {
            'content': '{"issues": [], "summary": "No issues found"}',
            'tokens_used': 1500
        })()

async def main():
    print("=" * 60)
    print("Token Budget Control Example")
    print("=" * 60)
    
    # 1. Set conservative budget for development
    print("\n1. Setting conservative token budget...")
    AdvancedSettings.set(
        max_tokens_per_session=10000,      # 10K tokens (~$0.03)
        max_tokens_per_tool=2000,          # 2K tokens per tool
        warn_at_percent=0.7,               # Warn at 70%
        budget_exceeded_action="stop"      # Stop when exceeded
    )
    
    # 2. Reset budget at start of session
    print("2. Resetting token budget...")
    AdvancedSettings.reset_token_budget()
    
    # 3. Create tool with budget checking
    print("3. Creating performance profiler...")
    profiler = PerformanceProfiler(llm_client=MockLLMClient())
    
    # 4. Execute with budget check
    print("\n4. Executing tool with budget check...")
    result = await profiler.execute_with_budget_check(
        estimated_tokens=1500,
        file_path="app.py",
        focus="cpu"
    )
    
    print(f"   Success: {result.success}")
    print(f"   Tokens used: {result.tokens_used}")
    print(f"   Warnings: {result.warnings}")
    
    # 5. Check current usage
    print("\n5. Checking token usage...")
    used = AdvancedSettings.get_tokens_used()
    max_budget = AdvancedSettings.get().max_tokens_per_session
    percent = (used / max_budget) * 100
    print(f"   Usage: {used}/{max_budget} tokens ({percent:.1f}%)")
    
    # 6. Try to exceed budget
    print("\n6. Attempting to exceed budget...")
    for i in range(10):
        result = await profiler.execute_with_budget_check(
            estimated_tokens=1500,
            file_path="app.py",
            focus="cpu"
        )
        
        if not result.success:
            print(f"   Execution {i+1}: BLOCKED - {result.errors}")
            break
        else:
            used = AdvancedSettings.get_tokens_used()
            print(f"   Execution {i+1}: OK (total: {used} tokens)")
    
    # 7. Final usage
    print("\n7. Final token usage:")
    print(f"   Total used: {AdvancedSettings.get_tokens_used()}")
    print(f"   Budget: {AdvancedSettings.get().max_tokens_per_session}")
    
    # 8. Reset for new session
    print("\n8. Resetting budget for new session...")
    AdvancedSettings.reset_token_budget()
    print(f"   New usage: {AdvancedSettings.get_tokens_used()}")
    
    print("\n" + "=" * 60)
    print("Example complete!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
