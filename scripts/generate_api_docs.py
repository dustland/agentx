#!/usr/bin/env python3
"""
AgentX API Documentation Generator

Extracts docstrings from the AgentX codebase and generates comprehensive
API documentation in MDX format for the documentation site.

Usage:
    python scripts/generate_api_docs.py
"""

import ast
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class DocItem:
    """Represents a documented item (class, function, method, etc.)"""
    name: str
    type: str  # 'class', 'function', 'method', 'property', 'module'
    docstring: Optional[str] = None
    signature: Optional[str] = None
    parent: Optional[str] = None
    module_path: str = ""
    line_number: int = 0
    decorators: List[str] = field(default_factory=list)
    args: List[str] = field(default_factory=list)
    returns: Optional[str] = None
    raises: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)


class DocstringParser:
    """Parses docstrings and extracts structured information."""
    
    def parse(self, docstring: str) -> Dict[str, Any]:
        """Parse a docstring and extract structured information."""
        if not docstring:
            return {}
        
        # Clean up the docstring
        lines = [line.strip() for line in docstring.strip().split('\n')]
        
        # Extract summary (first line)
        summary = lines[0] if lines else ""
        
        # Extract description (everything before Args/Returns/Raises)
        description_lines = []
        i = 1
        while i < len(lines) and not self._is_section_header(lines[i]):
            if lines[i]:  # Skip empty lines
                description_lines.append(lines[i])
            i += 1
        
        description = ' '.join(description_lines) if description_lines else ""
        
        # Extract sections
        sections = self._extract_sections(lines)
        
        return {
            'summary': summary,
            'description': description,
            'args': sections.get('args', []),
            'returns': sections.get('returns', ''),
            'raises': sections.get('raises', []),
            'examples': sections.get('examples', []),
            'note': sections.get('note', ''),
            'warning': sections.get('warning', ''),
        }
    
    def _is_section_header(self, line: str) -> bool:
        """Check if a line is a section header."""
        headers = ['Args:', 'Arguments:', 'Parameters:', 'Returns:', 'Return:', 
                  'Yields:', 'Raises:', 'Examples:', 'Example:', 'Note:', 'Warning:']
        return any(line.startswith(header) for header in headers)
    
    def _extract_sections(self, lines: List[str]) -> Dict[str, Any]:
        """Extract sections from docstring lines."""
        sections = {}
        current_section = None
        current_content = []
        
        for line in lines:
            if self._is_section_header(line):
                # Save previous section
                if current_section:
                    sections[current_section] = self._process_section_content(current_section, current_content)
                
                # Start new section
                current_section = line.rstrip(':').lower()
                current_content = []
            elif current_section:
                current_content.append(line)
        
        # Save last section
        if current_section:
            sections[current_section] = self._process_section_content(current_section, current_content)
        
        return sections
    
    def _process_section_content(self, section: str, content: List[str]) -> Any:
        """Process content for a specific section."""
        if section in ['args', 'arguments', 'parameters']:
            return self._parse_args_section(content)
        elif section in ['raises']:
            return self._parse_raises_section(content)
        elif section in ['examples', 'example']:
            return self._parse_examples_section(content)
        else:
            return ' '.join(content).strip()
    
    def _parse_args_section(self, content: List[str]) -> List[Dict[str, str]]:
        """Parse arguments section."""
        args = []
        current_arg = None
        current_desc = []
        
        for line in content:
            if line and not line.startswith(' '):
                # New argument
                if current_arg:
                    args.append({
                        'name': current_arg,
                        'description': ' '.join(current_desc).strip()
                    })
                
                # Parse argument line (name: description or name (type): description)
                if ':' in line:
                    parts = line.split(':', 1)
                    current_arg = parts[0].strip()
                    current_desc = [parts[1].strip()] if len(parts) > 1 else []
                else:
                    current_arg = line.strip()
                    current_desc = []
            else:
                # Continuation of description
                if line.strip():
                    current_desc.append(line.strip())
        
        # Add last argument
        if current_arg:
            args.append({
                'name': current_arg,
                'description': ' '.join(current_desc).strip()
            })
        
        return args
    
    def _parse_raises_section(self, content: List[str]) -> List[Dict[str, str]]:
        """Parse raises section."""
        raises = []
        for line in content:
            if line and ':' in line:
                parts = line.split(':', 1)
                raises.append({
                    'exception': parts[0].strip(),
                    'description': parts[1].strip() if len(parts) > 1 else ''
                })
        return raises
    
    def _parse_examples_section(self, content: List[str]) -> List[str]:
        """Parse examples section."""
        return [line for line in content if line.strip()]


class CodeAnalyzer:
    """Analyzes Python code and extracts documentation."""
    
    def __init__(self):
        self.docstring_parser = DocstringParser()
    
    def analyze_file(self, file_path: Path) -> List[DocItem]:
        """Analyze a Python file and extract documentation."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            module_path = self._get_module_path(file_path)
            
            items = []
            
            # Module-level docstring
            if ast.get_docstring(tree):
                items.append(DocItem(
                    name=module_path,
                    type='module',
                    docstring=ast.get_docstring(tree),
                    module_path=module_path,
                    line_number=1
                ))
            
            # Analyze all nodes
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Only include public functions (not starting with _)
                    if not node.name.startswith('_'):
                        items.append(self._analyze_function(node, module_path))
                elif isinstance(node, ast.ClassDef):
                    # Only include public classes (not starting with _)
                    if not node.name.startswith('_'):
                        items.append(self._analyze_class(node, module_path))
                        # Analyze class methods
                        for method in node.body:
                            if isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef)):
                                # Include public methods and __init__ (but not other dunder methods)
                                if not method.name.startswith('_') or method.name == '__init__':
                                    items.append(self._analyze_method(method, node.name, module_path))
            
            return items
            
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return []
    
    def _get_module_path(self, file_path: Path) -> str:
        """Get the module path from file path."""
        # Convert file path to module path
        parts = file_path.parts
        if 'src' in parts:
            src_index = parts.index('src')
            module_parts = parts[src_index + 1:]
        else:
            module_parts = parts
        
        # Remove .py extension and convert to module path
        module_parts = list(module_parts)
        if module_parts[-1].endswith('.py'):
            module_parts[-1] = module_parts[-1][:-3]
        
        # Remove __init__ if present
        if module_parts[-1] == '__init__':
            module_parts = module_parts[:-1]
        
        return '.'.join(module_parts)
    
    def _analyze_function(self, node: ast.FunctionDef, module_path: str) -> DocItem:
        """Analyze a function node."""
        return DocItem(
            name=node.name,
            type='function',
            docstring=ast.get_docstring(node),
            signature=self._get_function_signature(node),
            module_path=module_path,
            line_number=node.lineno,
            decorators=[self._get_decorator_name(d) for d in node.decorator_list]
        )
    
    def _analyze_class(self, node: ast.ClassDef, module_path: str) -> DocItem:
        """Analyze a class node."""
        return DocItem(
            name=node.name,
            type='class',
            docstring=ast.get_docstring(node),
            signature=self._get_class_signature(node),
            module_path=module_path,
            line_number=node.lineno,
            decorators=[self._get_decorator_name(d) for d in node.decorator_list]
        )
    
    def _analyze_method(self, node: ast.FunctionDef, class_name: str, module_path: str) -> DocItem:
        """Analyze a method node."""
        return DocItem(
            name=node.name,
            type='method',
            docstring=ast.get_docstring(node),
            signature=self._get_function_signature(node),
            parent=class_name,
            module_path=module_path,
            line_number=node.lineno,
            decorators=[self._get_decorator_name(d) for d in node.decorator_list]
        )
    
    def _get_function_signature(self, node: ast.FunctionDef) -> str:
        """Get function signature as string."""
        args = []
        
        # Regular arguments
        for arg in node.args.args:
            args.append(arg.arg)
        
        # *args
        if node.args.vararg:
            args.append(f"*{node.args.vararg.arg}")
        
        # **kwargs
        if node.args.kwarg:
            args.append(f"**{node.args.kwarg.arg}")
        
        return f"{node.name}({', '.join(args)})"
    
    def _get_class_signature(self, node: ast.ClassDef) -> str:
        """Get class signature as string."""
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(f"{base.value.id}.{base.attr}")
        
        if bases:
            return f"{node.name}({', '.join(bases)})"
        else:
            return node.name
    
    def _get_decorator_name(self, decorator) -> str:
        """Get decorator name as string."""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return f"{decorator.value.id}.{decorator.attr}"
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                return decorator.func.id
            elif isinstance(decorator.func, ast.Attribute):
                return f"{decorator.func.value.id}.{decorator.func.attr}"
        return str(decorator)


class MDXGenerator:
    """Generates MDX documentation files."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.docstring_parser = DocstringParser()
    
    def generate_docs(self, items: List[DocItem]) -> None:
        """Generate MDX documentation files."""
        # Group items by module
        modules = defaultdict(list)
        for item in items:
            modules[item.module_path].append(item)
        
        # Generate documentation for each module
        for module_path, module_items in modules.items():
            self._generate_module_docs(module_path, module_items)
    
    def _generate_module_docs(self, module_path: str, items: List[DocItem]) -> None:
        """Generate documentation for a single module."""
        if not items:
            return
        
        # Create output directory structure - flatten by removing 'agentx' root
        module_parts = module_path.split('.')
        # Remove 'agentx' from the beginning if present
        if module_parts[0] == 'agentx':
            module_parts = module_parts[1:]
        
        if len(module_parts) == 0:
            # This is the root agentx module
            file_path = self.output_dir / "agentx.mdx"
        else:
            file_path = self.output_dir / '/'.join(module_parts[:-1]) / f"{module_parts[-1]}.mdx"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate content
        content = self._generate_module_content(module_path, items)
        
        # Write file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Generated documentation: {file_path}")
    
    def _generate_module_content(self, module_path: str, items: List[DocItem]) -> str:
        """Generate MDX content for a module."""
        lines = []
        
        # Header
        module_name = module_path.split('.')[-1]
        lines.append(f"# {module_name}")
        lines.append("")
        
        # Module docstring
        module_item = next((item for item in items if item.type == 'module'), None)
        if module_item and module_item.docstring:
            parsed = self.docstring_parser.parse(module_item.docstring)
            if parsed.get('summary'):
                lines.append(parsed['summary'])
                lines.append("")
            if parsed.get('description'):
                lines.append(parsed['description'])
                lines.append("")
        
        # Import path
        lines.append("```python")
        lines.append(f"from {module_path} import ...")
        lines.append("```")
        lines.append("")
        
        # Classes
        classes = [item for item in items if item.type == 'class']
        if classes:
            lines.append("## Classes")
            lines.append("")
            for cls in classes:
                lines.extend(self._generate_class_docs(cls, items))
                lines.append("")
        
        # Functions
        functions = [item for item in items if item.type == 'function']
        if functions:
            lines.append("## Functions")
            lines.append("")
            for func in functions:
                lines.extend(self._generate_function_docs(func))
                lines.append("")
        
        return '\n'.join(lines)
    
    def _generate_class_docs(self, cls: DocItem, all_items: List[DocItem]) -> List[str]:
        """Generate documentation for a class."""
        lines = []
        
        # Class header
        lines.append(f"### {cls.name}")
        lines.append("")
        
        # Class signature
        if cls.signature:
            lines.append("```python")
            lines.append(f"class {cls.signature}")
            lines.append("```")
            lines.append("")
        
        # Class docstring
        if cls.docstring:
            parsed = self.docstring_parser.parse(cls.docstring)
            if parsed.get('summary'):
                lines.append(parsed['summary'])
                lines.append("")
            if parsed.get('description'):
                lines.append(parsed['description'])
                lines.append("")
        
        # Methods
        methods = [item for item in all_items if item.type == 'method' and item.parent == cls.name]
        if methods:
            lines.append("#### Methods")
            lines.append("")
            for method in methods:
                lines.extend(self._generate_method_docs(method))
                lines.append("")
        
        return lines
    
    def _generate_function_docs(self, func: DocItem) -> List[str]:
        """Generate documentation for a function."""
        lines = []
        
        # Function header
        lines.append(f"### {func.name}")
        lines.append("")
        
        # Function signature
        if func.signature:
            lines.append("```python")
            if 'async' in func.decorators or func.signature.startswith('async '):
                lines.append(f"async def {func.signature}")
            else:
                lines.append(f"def {func.signature}")
            lines.append("```")
            lines.append("")
        
        # Function docstring
        if func.docstring:
            parsed = self.docstring_parser.parse(func.docstring)
            if parsed.get('summary'):
                lines.append(parsed['summary'])
                lines.append("")
            if parsed.get('description'):
                lines.append(parsed['description'])
                lines.append("")
            
            # Arguments
            if parsed.get('args'):
                lines.append("**Arguments:**")
                lines.append("")
                for arg in parsed['args']:
                    lines.append(f"- `{arg['name']}`: {arg['description']}")
                lines.append("")
            
            # Returns
            if parsed.get('returns'):
                lines.append("**Returns:**")
                lines.append("")
                lines.append(parsed['returns'])
                lines.append("")
            
            # Raises
            if parsed.get('raises'):
                lines.append("**Raises:**")
                lines.append("")
                for exc in parsed['raises']:
                    lines.append(f"- `{exc['exception']}`: {exc['description']}")
                lines.append("")
            
            # Examples
            if parsed.get('examples'):
                lines.append("**Examples:**")
                lines.append("")
                lines.append("```python")
                lines.extend(parsed['examples'])
                lines.append("```")
                lines.append("")
        
        return lines
    
    def _generate_method_docs(self, method: DocItem) -> List[str]:
        """Generate documentation for a method."""
        lines = []
        
        # Method header
        lines.append(f"##### {method.name}")
        lines.append("")
        
        # Method signature
        if method.signature:
            lines.append("```python")
            if 'async' in method.decorators:
                lines.append(f"async def {method.signature}")
            else:
                lines.append(f"def {method.signature}")
            lines.append("```")
            lines.append("")
        
        # Method docstring
        if method.docstring:
            parsed = self.docstring_parser.parse(method.docstring)
            if parsed.get('summary'):
                lines.append(parsed['summary'])
                lines.append("")
            if parsed.get('description'):
                lines.append(parsed['description'])
                lines.append("")
        
        return lines


def main():
    """Main function to generate API documentation."""
    # Setup paths
    project_root = Path(__file__).parent.parent
    src_dir = project_root / "src" / "agentx"
    output_dir = project_root / "docs" / "content" / "api"
    
    print(f"🔍 Analyzing AgentX source code in: {src_dir}")
    print(f"📝 Generating API docs in: {output_dir}")
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize analyzer and generator
    analyzer = CodeAnalyzer()
    generator = MDXGenerator(output_dir)
    
    # Find all Python files (exclude internal/test files)
    python_files = []
    exclude_patterns = ['test_', '__pycache__', '.pyc', 'conftest.py']
    
    for file_path in src_dir.rglob("*.py"):
        # Skip hidden files and excluded patterns
        if (not file_path.name.startswith('.') and 
            not any(pattern in file_path.name for pattern in exclude_patterns) and
            'test' not in file_path.parts):
            python_files.append(file_path)
    
    print(f"📁 Found {len(python_files)} Python files")
    
    # Analyze all files
    all_items = []
    for file_path in python_files:
        print(f"  Analyzing: {file_path.relative_to(project_root)}")
        items = analyzer.analyze_file(file_path)
        all_items.extend(items)
    
    print(f"📋 Extracted {len(all_items)} documented items")
    
    # Generate documentation
    generator.generate_docs(all_items)
    
    # Generate index file
    generate_index_file(output_dir, all_items)
    
    print("✅ API documentation generation complete!")


def generate_index_file(output_dir: Path, items: List[DocItem]) -> None:
    """Generate an index file for the API documentation."""
    index_path = output_dir / "index.mdx"
    
    # Group items by module
    modules = defaultdict(list)
    for item in items:
        modules[item.module_path].append(item)
    
    lines = []
    lines.append("# API Reference")
    lines.append("")
    lines.append("Complete API reference for the AgentX framework.")
    lines.append("")
    
    # Core modules
    core_modules = [mod for mod in modules.keys() if 'core' in mod]
    if core_modules:
        lines.append("## Core Modules")
        lines.append("")
        for module in sorted(core_modules):
            module_name = module.split('.')[-1]
            # Remove 'agentx.' prefix for flattened structure
            flattened_path = module.replace('agentx.', '')
            lines.append(f"- [{module_name}](./{flattened_path.replace('.', '/')}.mdx)")
        lines.append("")
    
    # Builtin tools
    tool_modules = [mod for mod in modules.keys() if 'builtin_tools' in mod]
    if tool_modules:
        lines.append("## Builtin Tools")
        lines.append("")
        for module in sorted(tool_modules):
            module_name = module.split('.')[-1]
            # Remove 'agentx.' prefix for flattened structure
            flattened_path = module.replace('agentx.', '')
            lines.append(f"- [{module_name}](./{flattened_path.replace('.', '/')}.mdx)")
        lines.append("")
    
    # Other modules
    other_modules = [mod for mod in modules.keys() if 'core' not in mod and 'builtin_tools' not in mod]
    if other_modules:
        lines.append("## Other Modules")
        lines.append("")
        for module in sorted(other_modules):
            module_name = module.split('.')[-1]
            # Remove 'agentx.' prefix for flattened structure
            flattened_path = module.replace('agentx.', '')
            lines.append(f"- [{module_name}](./{flattened_path.replace('.', '/')}.mdx)")
        lines.append("")
    
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"Generated index: {index_path}")


if __name__ == "__main__":
    main() 