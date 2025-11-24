#!/usr/bin/env python3
"""
Unused Functions Analysis Script

Identifies potentially unused functions and checks for external usage.
"""
import ast
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def extract_functions(file_path: Path) -> List[Dict]:
    """Extract all function definitions from a Python file."""
    functions = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            tree = ast.parse(content, filename=str(file_path))
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Get function signature
                args = [arg.arg for arg in node.args.args]
                decorators = [ast.unparse(d) if hasattr(ast, 'unparse') else str(d) for d in node.decorator_list]
                
                functions.append({
                    'name': node.name,
                    'line': node.lineno,
                    'args': args,
                    'decorators': decorators,
                    'is_method': any('self' in arg or 'cls' in arg for arg in args),
                    'docstring': ast.get_docstring(node) or '',
                    'file': str(file_path.relative_to(project_root)),
                })
    except Exception as e:
        print(f"Error parsing {file_path}: {e}", file=sys.stderr)
    
    return functions


def extract_function_calls(file_path: Path) -> Set[str]:
    """Extract all function calls from a Python file."""
    calls = set()
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            tree = ast.parse(content, filename=str(file_path))
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    calls.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    # For method calls like obj.method()
                    calls.add(node.func.attr)
    except Exception as e:
        print(f"Error parsing {file_path}: {e}", file=sys.stderr)
    
    return calls


def check_external_usage(function_name: str, module_name: str, external_dirs: List[Path]) -> List[str]:
    """Check if a function is used in external directories."""
    usages = []
    for ext_dir in external_dirs:
        if not ext_dir.exists():
            continue
        for py_file in ext_dir.rglob('*.py'):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Simple text search for function usage
                    # Look for patterns like: function_name(, .function_name(, function_name=
                    patterns = [
                        f'{function_name}(',
                        f'.{function_name}(',
                        f'{function_name}=',
                        f'from {module_name} import.*{function_name}',
                        f'import {module_name}.*{function_name}',
                    ]
                    for pattern in patterns:
                        if pattern in content:
                            usages.append(str(py_file.relative_to(project_root.parent)))
                            break
            except Exception as e:
                pass
    return usages


def analyze_unused_functions():
    """Analyze unused functions across the codebase."""
    amilib_dir = project_root / 'amilib'
    test_dir = project_root / 'test'
    external_dirs = [
        project_root.parent / 'amiclimate',
        project_root.parent / 'docanalysis',
        project_root.parent / 'diagrams',
        project_root.parent / 'encyclopedia',
        project_root.parent / 'ipcc',
        project_root.parent / 'pyamiimage',
        project_root.parent / 'pyamihtml',
        project_root.parent / 'pygetpapers',
        project_root.parent / 'semantic_corpus',
    ]
    
    print("Analyzing functions...")
    
    # Collect all functions
    all_functions = []
    function_locations = {}  # function_name -> list of locations
    
    for py_file in amilib_dir.rglob('*.py'):
        if py_file.name == '__init__.py':
            continue
        
        functions = extract_functions(py_file)
        all_functions.extend(functions)
        
        for func in functions:
            if func['name'] not in function_locations:
                function_locations[func['name']] = []
            function_locations[func['name']].append(func)
    
    print(f"Found {len(all_functions)} functions")
    
    # Collect all function calls in amilib and tests
    all_calls = set()
    for py_file in list(amilib_dir.rglob('*.py')) + list(test_dir.rglob('*.py')):
        if py_file.name == '__init__.py':
            continue
        calls = extract_function_calls(py_file)
        all_calls.update(calls)
    
    # Find potentially unused functions
    # Exclude: __init__, __str__, __repr__, etc. (dunder methods)
    # Exclude: methods that might be called via getattr or dynamically
    unused = []
    for func in all_functions:
        name = func['name']
        
        # Skip dunder methods and common patterns
        if name.startswith('__') and name.endswith('__'):
            continue
        if name.startswith('_') and not name.startswith('__'):
            # Private methods - might be intentionally unused
            continue
        
        # Check if function is called
        if name not in all_calls:
            # Check external usage
            module_name = func['file'].replace('/', '.').replace('.py', '').replace('amilib.', 'amilib.')
            external_usages = check_external_usage(name, 'amilib', external_dirs)
            
            unused.append({
                'function': func,
                'external_usages': external_usages,
            })
    
    # Group by file
    unused_by_file = defaultdict(list)
    for item in unused:
        file = item['function']['file']
        unused_by_file[file].append(item)
    
    print(f"\nFound {len(unused)} potentially unused functions")
    print(f"Functions with external usage: {sum(1 for item in unused if item['external_usages'])}")
    
    # Write detailed report
    output_dir = project_root / 'docs' / 'analysis'
    output_dir.mkdir(parents=True, exist_ok=True)
    report_file = output_dir / 'unused_functions_analysis.txt'
    
    with open(report_file, 'w') as f:
        f.write("Unused Functions Analysis Report\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Total functions analyzed: {len(all_functions)}\n")
        f.write(f"Potentially unused functions: {len(unused)}\n")
        f.write(f"Functions with external usage: {sum(1 for item in unused if item['external_usages'])}\n\n")
        
        f.write("UNUSED FUNCTIONS BY FILE\n")
        f.write("-" * 80 + "\n")
        for file, items in sorted(unused_by_file.items()):
            f.write(f"\n{file}: {len(items)} unused functions\n")
            f.write("=" * 80 + "\n")
            for item in items:
                func = item['function']
                f.write(f"\n  Function: {func['name']}\n")
                f.write(f"  Line: {func['line']}\n")
                f.write(f"  Args: {', '.join(func['args'])}\n")
                if func['decorators']:
                    f.write(f"  Decorators: {', '.join(func['decorators'])}\n")
                if func['docstring']:
                    f.write(f"  Docstring: {func['docstring'][:200]}...\n")
                if item['external_usages']:
                    f.write(f"  EXTERNAL USAGE FOUND in:\n")
                    for usage in item['external_usages']:
                        f.write(f"    - {usage}\n")
                else:
                    f.write(f"  No external usage found\n")
    
    # Print summary
    print("\nUnused functions by file:")
    for file, items in sorted(unused_by_file.items()):
        print(f"  {file}: {len(items)} functions")
        for item in items[:5]:  # Show first 5
            func = item['function']
            external = " [EXTERNAL USAGE]" if item['external_usages'] else ""
            print(f"    - {func['name']} (line {func['line']}){external}")
        if len(items) > 5:
            print(f"    ... and {len(items) - 5} more")
    
    print(f"\nDetailed report written to: {report_file}")
    
    # Create a summary list for review
    summary_file = output_dir / 'unused_functions_summary.txt'
    with open(summary_file, 'w') as f:
        f.write("Unused Functions Summary for Review\n")
        f.write("=" * 80 + "\n\n")
        f.write("Format: File | Function | Line | External Usage\n")
        f.write("-" * 80 + "\n")
        for file, items in sorted(unused_by_file.items()):
            for item in items:
                func = item['function']
                external = ", ".join(item['external_usages']) if item['external_usages'] else "None"
                f.write(f"{file} | {func['name']} | {func['line']} | {external}\n")
    
    print(f"Summary list written to: {summary_file}")


if __name__ == '__main__':
    analyze_unused_functions()
