"""Tests for code analysis functionality."""

import pytest
from pathlib import Path
from ai_multitool import CodeParser, CodeStructure, SmartContextBuilder, AnalysisContext


class TestCodeParser:
    """Test code parser functionality."""
    
    def test_parser_initialization(self):
        """Test parser initialization."""
        parser = CodeParser()
        assert parser is not None
    
    def test_parse_python_file(self, sample_python_file):
        """Test parsing a Python file."""
        parser = CodeParser()
        structure = parser.parse_file(sample_python_file)
        
        assert structure is not None
        assert structure.language == "python"
        assert len(structure.functions) > 0
        assert len(structure.classes) > 0
    
    def test_parse_nonexistent_file(self):
        """Test parsing a non-existent file."""
        parser = CodeParser()
        with pytest.raises(FileNotFoundError):
            parser.parse_file("nonexistent.py")
    
    def test_detect_language_by_extension(self):
        """Test language detection by file extension."""
        parser = CodeParser()
        
        assert parser._detect_language("test.py") == "python"
        assert parser._detect_language("test.js") == "javascript"
        assert parser._detect_language("test.ts") == "typescript"
        assert parser._detect_language("test.java") == "java"
        assert parser._detect_language("test.c") == "c"
        assert parser._detect_language("test.cpp") == "cpp"
    
    def test_detect_language_by_shebang(self, temp_dir):
        """Test language detection by shebang."""
        parser = CodeParser()
        
        # Create a file with Python shebang
        script_file = temp_dir / "script.sh"
        script_file.write_text("#!/usr/bin/env python\nprint('hello')")
        
        language = parser._detect_language(script_file)
        assert language == "python"


class TestCodeStructure:
    """Test CodeStructure model."""
    
    def test_structure_creation(self):
        """Test creating a code structure."""
        structure = CodeStructure(
            language="python",
            functions=[],
            classes=[],
            imports=[],
            metadata={}
        )
        assert structure.language == "python"
        assert len(structure.functions) == 0
    
    def test_structure_with_functions(self):
        """Test structure with functions."""
        from ai_multitool.parsers.code_parser import FunctionInfo
        
        functions = [
            FunctionInfo(name="func1", line_start=1, line_end=5, parameters=["x"]),
            FunctionInfo(name="func2", line_start=10, line_end=15, parameters=["y", "z"]),
        ]
        
        structure = CodeStructure(
            language="python",
            functions=functions,
            classes=[],
            imports=[],
            metadata={}
        )
        
        assert len(structure.functions) == 2
        assert structure.functions[0].name == "func1"
        assert structure.functions[1].parameters == ["y", "z"]
    
    def test_structure_with_classes(self):
        """Test structure with classes."""
        from ai_multitool.parsers.code_parser import ClassInfo
        
        classes = [
            ClassInfo(name="MyClass", line_start=1, line_end=20, methods=["method1", "method2"]),
        ]
        
        structure = CodeStructure(
            language="python",
            functions=[],
            classes=classes,
            imports=[],
            metadata={}
        )
        
        assert len(structure.classes) == 1
        assert structure.classes[0].name == "MyClass"
        assert len(structure.classes[0].methods) == 2


class TestSmartContextBuilder:
    """Test smart context builder."""
    
    def test_context_builder_initialization(self):
        """Test context builder initialization."""
        builder = SmartContextBuilder()
        assert builder is not None
    
    def test_build_context_without_git(self, sample_python_file):
        """Test building context without git integration."""
        builder = SmartContextBuilder()
        parser = CodeParser()
        structure = parser.parse_file(sample_python_file)
        
        context = builder.build_context(
            file_path=sample_python_file,
            structure=structure,
            include_git=False
        )
        
        assert context is not None
        assert context.file_path == sample_python_file
        assert context.structure is not None
        assert context.git_info is None
    
    def test_build_context_with_git(self, sample_python_file, sample_git_repo):
        """Test building context with git integration."""
        builder = SmartContextBuilder()
        parser = CodeParser()
        structure = parser.parse_file(sample_python_file)
        
        context = builder.build_context(
            file_path=sample_python_file,
            structure=structure,
            include_git=True
        )
        
        assert context is not None
        assert context.git_info is not None
    
    def test_build_context_with_related_files(self, temp_dir):
        """Test building context with related files detection."""
        builder = SmartContextBuilder()
        
        # Create multiple related files
        main_file = temp_dir / "main.py"
        main_file.write_text("import utils\ndef main(): pass")
        
        utils_file = temp_dir / "utils.py"
        utils_file.write_text("def helper(): pass")
        
        parser = CodeParser()
        structure = parser.parse_file(main_file)
        
        context = builder.build_context(
            file_path=main_file,
            structure=structure,
            include_git=False,
            include_related=True
        )
        
        assert context is not None
        assert context.related_files is not None


class TestAnalysisContext:
    """Test AnalysisContext model."""
    
    def test_context_creation(self):
        """Test creating an analysis context."""
        structure = CodeStructure(
            language="python",
            functions=[],
            classes=[],
            imports=[],
            metadata={}
        )
        
        context = AnalysisContext(
            file_path=Path("test.py"),
            structure=structure,
            file_stats={"lines": 100, "chars": 1000},
            git_info=None,
            related_files=[]
        )
        
        assert context.file_path == Path("test.py")
        assert context.structure.language == "python"
        assert context.file_stats["lines"] == 100
    
    def test_context_to_dict(self):
        """Test converting context to dictionary."""
        structure = CodeStructure(
            language="python",
            functions=[],
            classes=[],
            imports=[],
            metadata={}
        )
        
        context = AnalysisContext(
            file_path=Path("test.py"),
            structure=structure,
            file_stats={"lines": 100},
            git_info=None,
            related_files=[]
        )
        
        context_dict = context.to_dict()
        
        assert "file_path" in context_dict
        assert "structure" in context_dict
        assert "file_stats" in context_dict


class TestCodeLanguageDetection:
    """Test code language detection."""
    
    def test_supported_languages(self):
        """Test that supported languages are correctly identified."""
        parser = CodeParser()
        
        test_cases = [
            ("test.py", "python"),
            ("test.js", "javascript"),
            ("test.ts", "typescript"),
            ("test.jsx", "javascript"),
            ("test.tsx", "typescript"),
            ("test.java", "java"),
            ("test.c", "c"),
            ("test.cpp", "cpp"),
            ("test.h", "c"),
            ("test.hpp", "cpp"),
            ("test.go", "go"),
            ("test.rs", "rust"),
            ("test.rb", "ruby"),
            ("test.php", "php"),
            ("test.swift", "swift"),
            ("test.kt", "kotlin"),
            ("test.scala", "scala"),
        ]
        
        for filename, expected_lang in test_cases:
            detected = parser._detect_language(filename)
            assert detected == expected_lang, f"Failed for {filename}"
    
    def test_unsupported_language(self):
        """Test handling of unsupported language."""
        parser = CodeParser()
        detected = parser._detect_language("test.unknown")
        assert detected is None


class TestComplexityScoring:
    """Test complexity scoring."""
    
    def test_calculate_complexity_simple(self):
        """Test complexity calculation for simple code."""
        parser = CodeParser()
        
        simple_code = '''
def simple_function():
    return 42
'''
        
        complexity = parser._calculate_complexity(simple_code)
        assert complexity is not None
        assert complexity >= 0
    
    def test_calculate_complexity_complex(self):
        """Test complexity calculation for complex code."""
        parser = CodeParser()
        
        complex_code = '''
def complex_function(x):
    if x > 0:
        for i in range(10):
            if i % 2 == 0:
                for j in range(5):
                    if j > 2:
                        return i * j
    else:
        while x < 100:
            x += 1
            if x == 50:
                break
    return x
'''
        
        complexity = parser._calculate_complexity(complex_code)
        assert complexity is not None
        # Complex code should have higher complexity
        assert complexity > 0
