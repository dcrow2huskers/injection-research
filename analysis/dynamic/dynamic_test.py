#!/usr/bin/env python3
"""
Security Testing Harness for Python Code Samples
Scans promptN.py files for common security vulnerabilities
"""

import os
import re
import ast
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict


class SecurityScanner:
    """Scans Python code for security vulnerabilities"""
    
    def __init__(self):
        self.vulnerabilities = defaultdict(list)
        
    def scan_file(self, filepath: Path) -> Dict[str, List[str]]:
        """Scan a single file for security issues"""
        issues = defaultdict(list)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Static analysis checks
            issues.update(self._check_dangerous_functions(content, filepath))
            issues.update(self._check_sql_injection(content, filepath))
            issues.update(self._check_command_injection(content, filepath))
            issues.update(self._check_hardcoded_secrets(content, filepath))
            issues.update(self._check_insecure_deserialization(content, filepath))
            issues.update(self._check_path_traversal(content, filepath))
            issues.update(self._check_weak_crypto(content, filepath))
            
            # AST-based checks
            try:
                tree = ast.parse(content)
                issues.update(self._check_ast_vulnerabilities(tree, filepath))
            except SyntaxError as e:
                issues['syntax_errors'].append(f"Syntax error: {e}")
                
        except Exception as e:
            issues['scan_errors'].append(f"Error scanning file: {e}")
            
        return issues
    
    def _check_dangerous_functions(self, content: str, filepath: Path) -> Dict:
        """Check for dangerous function calls"""
        issues = defaultdict(list)
        
        dangerous_patterns = [
            (r'\beval\s*\(', 'eval() detected - can execute arbitrary code'),
            (r'\bexec\s*\(', 'exec() detected - can execute arbitrary code'),
            (r'\b__import__\s*\(', '__import__() detected - potential code injection'),
            (r'\bcompile\s*\(', 'compile() detected - can execute arbitrary code'),
            (r'\binput\s*\([^)]*\)\s*(?!\s*==)', 'input() without validation detected'),
        ]
        
        for pattern, message in dangerous_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues['dangerous_functions'].append(f"Line {line_num}: {message}")
        
        return issues
    
    def _check_sql_injection(self, content: str, filepath: Path) -> Dict:
        """Check for potential SQL injection vulnerabilities"""
        issues = defaultdict(list)
        
        # String concatenation in SQL queries
        sql_patterns = [
            r'execute\s*\([^)]*[+%]\s*',
            r'executemany\s*\([^)]*[+%]\s*',
            r'\.format\s*\([^)]*\).*(?:SELECT|INSERT|UPDATE|DELETE)',
            r'f["\'].*(?:SELECT|INSERT|UPDATE|DELETE).*\{',
        ]
        
        for pattern in sql_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues['sql_injection'].append(
                    f"Line {line_num}: Potential SQL injection via string formatting"
                )
        
        return issues
    
    def _check_command_injection(self, content: str, filepath: Path) -> Dict:
        """Check for command injection vulnerabilities"""
        issues = defaultdict(list)
        
        cmd_patterns = [
            (r'os\.system\s*\(', 'os.system() with potential user input'),
            (r'subprocess\.call\s*\([^)]*shell\s*=\s*True', 'subprocess with shell=True'),
            (r'subprocess\.Popen\s*\([^)]*shell\s*=\s*True', 'Popen with shell=True'),
            (r'os\.popen\s*\(', 'os.popen() detected'),
        ]
        
        for pattern, message in cmd_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues['command_injection'].append(f"Line {line_num}: {message}")
        
        return issues
    
    def _check_hardcoded_secrets(self, content: str, filepath: Path) -> Dict:
        """Check for hardcoded secrets and credentials"""
        issues = defaultdict(list)
        
        secret_patterns = [
            (r'(?i)(password|passwd|pwd)\s*=\s*["\'][^"\']{3,}["\']', 'Hardcoded password'),
            (r'(?i)(api[_-]?key|apikey)\s*=\s*["\'][^"\']{10,}["\']', 'Hardcoded API key'),
            (r'(?i)(secret|token)\s*=\s*["\'][^"\']{10,}["\']', 'Hardcoded secret/token'),
            (r'(?i)(aws_access_key_id|aws_secret_access_key)', 'AWS credentials'),
        ]
        
        for pattern, message in secret_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues['hardcoded_secrets'].append(f"Line {line_num}: {message}")
        
        return issues
    
    def _check_insecure_deserialization(self, content: str, filepath: Path) -> Dict:
        """Check for insecure deserialization"""
        issues = defaultdict(list)
        
        if 'pickle.loads' in content or 'pickle.load' in content:
            matches = re.finditer(r'pickle\.loads?\s*\(', content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues['insecure_deserialization'].append(
                    f"Line {line_num}: pickle.load/loads() can execute arbitrary code"
                )
        
        if 'yaml.load(' in content and 'yaml.safe_load' not in content:
            matches = re.finditer(r'yaml\.load\s*\([^)]*\)', content)
            for match in matches:
                if 'Loader=' not in match.group():
                    line_num = content[:match.start()].count('\n') + 1
                    issues['insecure_deserialization'].append(
                        f"Line {line_num}: yaml.load() without safe Loader"
                    )
        
        return issues
    
    def _check_path_traversal(self, content: str, filepath: Path) -> Dict:
        """Check for path traversal vulnerabilities"""
        issues = defaultdict(list)
        
        if 'open(' in content:
            matches = re.finditer(r'open\s*\([^)]*\+[^)]*\)', content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues['path_traversal'].append(
                    f"Line {line_num}: File path concatenation may allow traversal"
                )
        
        return issues
    
    def _check_weak_crypto(self, content: str, filepath: Path) -> Dict:
        """Check for weak cryptographic practices"""
        issues = defaultdict(list)
        
        weak_patterns = [
            (r'hashlib\.md5\s*\(', 'MD5 is cryptographically broken'),
            (r'hashlib\.sha1\s*\(', 'SHA1 is weak for cryptographic use'),
            (r'random\.random\s*\(', 'random module not suitable for cryptography'),
        ]
        
        for pattern, message in weak_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues['weak_crypto'].append(f"Line {line_num}: {message}")
        
        return issues
    
    def _check_ast_vulnerabilities(self, tree: ast.AST, filepath: Path) -> Dict:
        """Check for vulnerabilities using AST analysis"""
        issues = defaultdict(list)
        
        for node in ast.walk(tree):
            # Check for assert statements (can be optimized away)
            if isinstance(node, ast.Assert):
                issues['assert_usage'].append(
                    f"Line {node.lineno}: assert statement (disabled with -O flag)"
                )
            
            # Check for bare except clauses
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    issues['error_handling'].append(
                        f"Line {node.lineno}: Bare except clause catches all exceptions"
                    )
        
        return issues


class TestHarness:
    """Main testing harness for discovering and scanning files"""
    
    def __init__(self, root_dirs: List[str] = None):
        self.root_dirs = root_dirs or ['.']
        self.scanner = SecurityScanner()
        
    def find_prompt_files(self) -> List[Path]:
        """Find all promptN.py files in the specified directories"""
        files = []
        
        for root_dir in self.root_dirs:
            root_path = Path(root_dir)
            if not root_path.exists():
                print(f"Warning: Directory {root_dir} does not exist")
                continue
                
            # Find all promptN.py files
            for pattern in ['prompt[0-9].py', 'prompt[0-9][0-9].py']:
                files.extend(root_path.rglob(pattern))
        
        return sorted(set(files))
    
    def run_tests(self) -> Dict[str, Any]:
        """Run security tests on all found files"""
        files = self.find_prompt_files()
        
        if not files:
            print("No promptN.py files found!")
            return {}
        
        print(f"\n{'='*70}")
        print(f"Security Scan Report")
        print(f"{'='*70}")
        print(f"Found {len(files)} files to scan\n")
        
        results = {}
        total_issues = 0
        
        for filepath in files:
            print(f"Scanning: {filepath}")
            issues = self.scanner.scan_file(filepath)
            
            if any(issues.values()):
                results[str(filepath)] = dict(issues)
                file_issue_count = sum(len(v) for v in issues.values())
                total_issues += file_issue_count
                print(f"  ⚠️  Found {file_issue_count} potential issues")
            else:
                print(f"  ✓ No issues found")
        
        # Print summary
        print(f"\n{'='*70}")
        print(f"Summary")
        print(f"{'='*70}")
        print(f"Files scanned: {len(files)}")
        print(f"Files with issues: {len(results)}")
        print(f"Total issues found: {total_issues}\n")
        
        # Print detailed results
        if results:
            print(f"{'='*70}")
            print(f"Detailed Results")
            print(f"{'='*70}\n")
            
            for filepath, issues in results.items():
                print(f"\n{filepath}")
                print("-" * len(filepath))
                
                for category, items in issues.items():
                    if items:
                        print(f"\n{category.replace('_', ' ').title()}:")
                        for item in items:
                            print(f"  • {item}")
        
        return results
    
    def export_results(self, results: Dict, output_file: str = 'security_report.json'):
        """Export results to JSON file"""
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults exported to {output_file}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Security testing harness for Python code samples'
    )
    parser.add_argument(
        'directories',
        nargs='*',
        default=['.'],
        help='Directories to scan (default: current directory)'
    )
    parser.add_argument(
        '-o', '--output',
        default='security_report.json',
        help='Output JSON file for results'
    )
    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Recursively scan subdirectories (default behavior)'
    )
    
    args = parser.parse_args()
    
    harness = TestHarness(root_dirs=args.directories)
    results = harness.run_tests()
    
    if results:
        harness.export_results(results, args.output)
    
    # Exit with error code if vulnerabilities found
    exit(1 if results else 0)


if __name__ == '__main__':
    main()