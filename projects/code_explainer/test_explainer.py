"""
Tests for code explainer.
"""

import pytest
from explainer import CodeParser, CodeFormatter, CodeSummary


def test_code_parser_parse():
    """Test code parsing."""
    code = """
def hello():
    return "world"

class MyClass:
    pass
"""
    parser = CodeParser(code)
    assert parser.parse()


def test_code_parser_parse_error():
    """Test parse error handling."""
    code = "def broken syntax here"
    parser = CodeParser(code)
    assert not parser.parse()
    assert len(parser.parse_errors) > 0


def test_code_parser_get_functions():
    """Test extracting functions."""
    code = """
def func1():
    pass

def func2():
    pass
"""
    parser = CodeParser(code)
    parser.parse()
    functions = parser.get_functions()
    assert len(functions) == 2
    assert "func1" in functions
    assert "func2" in functions


def test_code_parser_get_classes():
    """Test extracting classes."""
    code = """
class MyClass:
    pass

class AnotherClass:
    pass
"""
    parser = CodeParser(code)
    parser.parse()
    classes = parser.get_classes()
    assert len(classes) == 2


def test_code_parser_get_imports():
    """Test extracting imports."""
    code = """
import os
import sys
from pathlib import Path
"""
    parser = CodeParser(code)
    parser.parse()
    imports = parser.get_imports()
    assert len(imports) >= 2


def test_code_parser_complexity():
    """Test complexity metrics."""
    code = """
import os

def func1():
    pass

class MyClass:
    def method(self):
        pass
"""
    parser = CodeParser(code)
    parser.parse()
    metrics = parser.get_complexity_metrics()
    assert metrics["functions"] > 0
    assert metrics["classes"] > 0


def test_code_formatter_line_numbers():
    """Test adding line numbers."""
    code = "line1\nline2\nline3"
    numbered = CodeFormatter.add_line_numbers(code)
    assert "1 |" in numbered
    assert "2 |" in numbered
    assert "3 |" in numbered


def test_code_formatter_markdown():
    """Test markdown formatting."""
    code = "def hello():\n    pass"
    markdown = CodeFormatter.to_markdown(code)
    assert "```python" in markdown
    assert code in markdown


def test_code_summary():
    """Test code summary generation."""
    code = """
def greet(name):
    '''Greet someone.'''
    return f"Hello {name}"

class Greeter:
    '''A greeter class.'''
    pass
"""
    summary = CodeSummary.create_summary(code)
    assert summary["success"]
    assert "greet" in summary["functions"]
    assert "Greeter" in summary["classes"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
