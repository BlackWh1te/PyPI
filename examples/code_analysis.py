"""Code analysis usage example."""

from ai_multitool import CodeParser, SmartContextBuilder, GitHelper


def main():
    """Code analysis example."""
    # Parse a code file
    print("Parsing code file...")
    parser = CodeParser()

    try:
        structure = parser.parse_file("example.py")
        print(f"\nFile: {structure.file_path}")
        print(f"Language: {structure.language}")
        print(f"Functions: {len(structure.functions)}")
        print(f"Classes: {len(structure.classes)}")
        print(f"Imports: {len(structure.imports)}")
        print(f"Complexity Score: {structure.complexity_score}")

        print("\nFunctions:")
        for func in structure.functions:
            print(f"  - {func.get('name', 'unknown')}")

        print("\nClasses:")
        for cls in structure.classes:
            print(f"  - {cls.get('name', 'unknown')}")

    except Exception as e:
        print(f"Parse error: {e}")
        print("Note: This example requires a valid Python file named 'example.py'")
        return

    # Build smart context
    print("\nBuilding smart context...")
    context_builder = SmartContextBuilder()
    git_helper = GitHelper()

    try:
        context = context_builder.build_context(
            file_path="example.py",
            structure=structure,
            include_git=True
        )

        print(f"\nContext built successfully")
        print(f"File stats: {context.file_stats}")
        print(f"Git branch: {context.git_info.get('branch', 'N/A')}")
        print(f"Recent commits: {len(context.git_info.get('commits', []))}")

    except Exception as e:
        print(f"Context building error: {e}")


if __name__ == "__main__":
    main()
