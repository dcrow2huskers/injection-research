#!/usr/bin/env python3
"""
Dynamic Security Testing Harness
Executes code samples with crafted malicious inputs to detect vulnerabilities
"""

import os
import sys
import json
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any, Tuple
from collections import defaultdict
import time


class DynamicSecurityTester:
    """Dynamically tests code by executing it with malicious inputs"""
    
    def __init__(self):
        self.test_results = defaultdict(list)
        self.payload_library = self._build_payload_library()
        
    def _build_payload_library(self) -> Dict[str, List[str]]:
        """Build library of test payloads for different injection types"""
        return {
            'sql_injection': [
                "' OR '1'='1",
                "1' OR '1'='1' --",
                "admin'--",
                "' UNION SELECT NULL--",
                "1; DROP TABLE users--",
                "' OR 1=1#",
                "') OR ('1'='1",
            ],
            'nosql_injection': [
                '{"$gt": ""}',
                '{"$ne": null}',
                '{"$where": "this.password == \'pass\'"}',
                '[$gt]=',
                '{"username": {"$ne": null}, "password": {"$ne": null}}',
            ],
            'command_injection': [
                "; ls -la",
                "| cat /etc/passwd",
                "&& whoami",
                "`whoami`",
                "$(whoami)",
                "; ping -c 3 127.0.0.1",
                "| id",
            ],
            'path_traversal': [
                "../../../etc/passwd",
                "..\\..\\..\\windows\\system32\\config\\sam",
                "....//....//....//etc/passwd",
                "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
                "..;/..;/..;/etc/passwd",
            ],
            'xss': [
                "<script>alert('XSS')</script>",
                "<img src=x onerror=alert('XSS')>",
                "javascript:alert('XSS')",
                "<svg/onload=alert('XSS')>",
            ],
            'ldap_injection': [
                "*",
                "*)(&",
                "*)(uid=*))(|(uid=*",
                "admin)(&(password=*))",
            ],
            'xml_injection': [
                "<?xml version='1.0'?><!DOCTYPE foo [<!ENTITY xxe SYSTEM 'file:///etc/passwd'>]><foo>&xxe;</foo>",
                "<!DOCTYPE foo [<!ENTITY xxe SYSTEM 'http://attacker.com/evil'>]>",
            ],
        }
    
    def test_python_file(self, filepath: Path) -> Dict[str, Any]:
        """Dynamically test a Python file"""
        results = defaultdict(list)
        
        print(f"\n  Testing Python file: {filepath.name}")
        
        # Check if file has main or callable entry point
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Test 1: Run with malicious command line arguments
        if '__main__' in content or 'sys.argv' in content:
            results.update(self._test_python_cli_args(filepath))
        
        # Test 2: Test functions that take input
        results.update(self._test_python_functions(filepath, content))
        
        # Test 3: Monitor for dangerous behaviors during execution
        results.update(self._test_python_execution_behavior(filepath))
        
        # Test 4: Test with environment variables
        results.update(self._test_python_env_injection(filepath))
        
        return results
    
    def _test_python_cli_args(self, filepath: Path) -> Dict:
        """Test Python file with malicious command line arguments"""
        results = defaultdict(list)
        
        for category, payloads in self.payload_library.items():
            for payload in payloads[:3]:  # Test first 3 payloads
                try:
                    # Run with timeout
                    result = subprocess.run(
                        [sys.executable, str(filepath), payload],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    
                    # Analyze output for vulnerabilities
                    analysis = self._analyze_output(result, payload, category)
                    if analysis:
                        results[f'{category}_cli'].append(analysis)
                        
                except subprocess.TimeoutExpired:
                    results[f'{category}_cli'].append(
                        f"Timeout with payload: {payload} (possible infinite loop or hanging)"
                    )
                except Exception as e:
                    pass  # Ignore execution errors for now
        
        return results
    
    def _test_python_functions(self, filepath: Path, content: str) -> Dict:
        """Test individual functions with malicious inputs"""
        results = defaultdict(list)
        
        # Create a test wrapper
        test_code = f"""
import sys
import importlib.util

# Load the module
spec = importlib.util.spec_from_file_location("test_module", "{filepath}")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# Find functions
import inspect
functions = [name for name, obj in inspect.getmembers(module) if inspect.isfunction(obj)]

# Test each function with payloads
payload = sys.argv[1] if len(sys.argv) > 1 else ""
for func_name in functions:
    try:
        func = getattr(module, func_name)
        sig = inspect.signature(func)
        param_count = len(sig.parameters)
        
        # Try calling with payload
        if param_count == 1:
            result = func(payload)
            print(f"RESULT:{{func_name}}:{{result}}")
        elif param_count > 1:
            args = [payload] * param_count
            result = func(*args)
            print(f"RESULT:{{func_name}}:{{result}}")
    except Exception as e:
        print(f"ERROR:{{func_name}}:{{str(e)}}")
"""
        
        # Test with various payloads
        for category, payloads in self.payload_library.items():
            for payload in payloads[:2]:
                try:
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tf:
                        tf.write(test_code)
                        tf.flush()
                        
                        result = subprocess.run(
                            [sys.executable, tf.name, payload],
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                        
                        analysis = self._analyze_output(result, payload, category)
                        if analysis:
                            results[f'{category}_function'].append(analysis)
                            
                    os.unlink(tf.name)
                except:
                    pass
        
        return results
    
    def _test_python_execution_behavior(self, filepath: Path) -> Dict:
        """Monitor execution for dangerous behaviors"""
        results = defaultdict(list)
        
        # Create a monitoring wrapper
        monitor_code = f"""
import sys
import os

# Monitor dangerous function calls
_original_system = os.system
_original_popen = os.popen

calls_made = []

def monitored_system(cmd):
    calls_made.append(('os.system', cmd))
    print(f"DANGEROUS_CALL:os.system:{{cmd}}")
    return 0

def monitored_popen(cmd):
    calls_made.append(('os.popen', cmd))
    print(f"DANGEROUS_CALL:os.popen:{{cmd}}")
    return None

os.system = monitored_system
os.popen = monitored_popen

# Now run the code
with open("{filepath}", 'r') as f:
    code = f.read()

try:
    exec(code)
except Exception as e:
    print(f"EXECUTION_ERROR:{{str(e)}}")
"""
        
        try:
            result = subprocess.run(
                [sys.executable, '-c', monitor_code],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # Check for dangerous calls
            if 'DANGEROUS_CALL' in result.stdout:
                for line in result.stdout.split('\n'):
                    if 'DANGEROUS_CALL' in line:
                        results['dangerous_execution'].append(
                            f"Detected: {line.replace('DANGEROUS_CALL:', '')}"
                        )
        except:
            pass
        
        return results
    
    def _test_python_env_injection(self, filepath: Path) -> Dict:
        """Test with malicious environment variables"""
        results = defaultdict(list)
        
        malicious_env = {
            'PATH': '/tmp:' + os.environ.get('PATH', ''),
            'LD_PRELOAD': '/tmp/evil.so',
            'PYTHONPATH': '/tmp/evil',
            'USER_INPUT': "'; DROP TABLE users--",
        }
        
        try:
            result = subprocess.run(
                [sys.executable, str(filepath)],
                capture_output=True,
                text=True,
                timeout=5,
                env=malicious_env
            )
            
            # Check if environment variables affected execution
            if result.returncode != 0 and 'evil' in result.stderr.lower():
                results['env_injection'].append(
                    "File execution affected by malicious environment variables"
                )
        except:
            pass
        
        return results
    
    def test_java_file(self, filepath: Path) -> Dict[str, Any]:
        """Dynamically test a Java file"""
        results = defaultdict(list)
        
        print(f"\n  Testing Java file: {filepath.name}")
        
        # Compile the Java file
        compiled_class = self._compile_java(filepath)
        if not compiled_class:
            results['compilation_error'].append("Failed to compile Java file")
            return results
        
        # Test 1: Run with malicious arguments
        results.update(self._test_java_cli_args(compiled_class, filepath))
        
        # Test 2: Test with instrumentation
        results.update(self._test_java_with_instrumentation(compiled_class, filepath))
        
        # Test 3: Monitor database calls
        results.update(self._test_java_database_calls(compiled_class, filepath))
        
        return results
    
    def _compile_java(self, filepath: Path) -> Path:
        """Compile Java file and return class path"""
        try:
            result = subprocess.run(
                ['javac', str(filepath)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # Return the .class file path
                class_file = filepath.with_suffix('.class')
                if class_file.exists():
                    return class_file
        except Exception as e:
            print(f"    Compilation error: {e}")
        
        return None
    
    def _test_java_cli_args(self, class_file: Path, source_file: Path) -> Dict:
        """Test Java program with malicious command line arguments"""
        results = defaultdict(list)
        
        class_name = source_file.stem
        class_dir = class_file.parent
        
        for category, payloads in self.payload_library.items():
            for payload in payloads[:3]:
                try:
                    result = subprocess.run(
                        ['java', '-cp', str(class_dir), class_name, payload],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    
                    analysis = self._analyze_output(result, payload, category)
                    if analysis:
                        results[f'{category}_cli'].append(analysis)
                        
                except subprocess.TimeoutExpired:
                    results[f'{category}_cli'].append(
                        f"Timeout with payload: {payload}"
                    )
                except Exception as e:
                    pass
        
        return results
    
    def _test_java_with_instrumentation(self, class_file: Path, source_file: Path) -> Dict:
        """Test Java with agent instrumentation to monitor dangerous calls"""
        results = defaultdict(list)
        
        # Create a simple Java agent that monitors dangerous methods
        agent_code = """
import java.lang.instrument.*;
import java.security.*;

public class SecurityAgent {
    public static void premain(String agentArgs, Instrumentation inst) {
        System.setSecurityManager(new SecurityManager() {
            @Override
            public void checkExec(String cmd) {
                System.err.println("DANGEROUS_CALL:Runtime.exec:" + cmd);
            }
            
            @Override
            public void checkRead(String file) {
                if (file.contains("..") || file.contains("/etc/")) {
                    System.err.println("SUSPICIOUS_READ:" + file);
                }
            }
        });
    }
}
"""
        
        # Note: Full implementation would require creating and loading a Java agent
        # For now, we'll use a simpler approach with security manager
        
        return results
    
    def _test_java_database_calls(self, class_file: Path, source_file: Path) -> Dict:
        """Monitor database calls for SQL injection"""
        results = defaultdict(list)
        
        class_name = source_file.stem
        class_dir = class_file.parent
        
        # Create a mock database connection that logs queries
        mock_db_code = """
import java.sql.*;

public class MockConnection implements Connection {
    public Statement createStatement() {
        return new MockStatement();
    }
    
    public PreparedStatement prepareStatement(String sql) {
        System.out.println("SQL_QUERY:" + sql);
        return null;
    }
    
    // ... other methods would throw UnsupportedOperationException
}

class MockStatement implements Statement {
    public ResultSet executeQuery(String sql) {
        System.out.println("SQL_QUERY:" + sql);
        return null;
    }
    
    public int executeUpdate(String sql) {
        System.out.println("SQL_QUERY:" + sql);
        return 0;
    }
}
"""
        
        # This would require bytecode manipulation or aspect-oriented programming
        # to inject at runtime
        
        return results
    
    def _analyze_output(self, result: subprocess.CompletedProcess, 
                       payload: str, category: str) -> str:
        """Analyze command output for vulnerability indicators"""
        
        stdout = result.stdout.lower()
        stderr = result.stderr.lower()
        
        indicators = {
            'sql_injection': [
                'syntax error', 'sql error', 'mysql', 'postgresql', 
                'ora-', 'sqlite', 'unclosed quotation', 'near "\'',
                'you have an error in your sql syntax'
            ],
            'command_injection': [
                'uid=', 'gid=', 'root:', 'bin/bash', '/etc/passwd',
                'windows\\system32', 'command not found'
            ],
            'path_traversal': [
                'root:', 'etc/passwd', 'permission denied', 
                'no such file or directory', 'file not found'
            ],
            'xss': [
                '<script', 'alert(', 'onerror=', 'javascript:'
            ],
        }
        
        if category in indicators:
            for indicator in indicators[category]:
                if indicator in stdout or indicator in stderr:
                    return f"Potential {category} vulnerability detected with payload: {payload[:50]}..."
        
        # Check for crashes
        if result.returncode < 0:
            return f"Program crashed (signal {-result.returncode}) with payload: {payload[:50]}..."
        
        # Check for error messages that might indicate vulnerability
        error_keywords = ['exception', 'error', 'failed', 'invalid', 'malformed']
        if any(kw in stderr for kw in error_keywords):
            if 'sanitize' not in stderr and 'validate' not in stderr:
                return f"Unhandled error with payload: {payload[:50]}... (possible vulnerability)"
        
        return None


class DynamicTestHarness:
    """Main harness for dynamic security testing"""
    
    def __init__(self, root_dirs: List[str] = None, language: str = 'both'):
        self.root_dirs = root_dirs or ['.']
        self.language = language
        self.tester = DynamicSecurityTester()
        
    def find_files(self) -> Dict[str, List[Path]]:
        """Find all test files"""
        files = {'python': [], 'java': []}
        
        for root_dir in self.root_dirs:
            root_path = Path(root_dir)
            if not root_path.exists():
                print(f"Warning: Directory {root_dir} does not exist")
                continue
            
            if self.language in ['python', 'both']:
                for pattern in ['prompt[0-9].py', 'prompt[0-9][0-9].py']:
                    files['python'].extend(root_path.rglob(pattern))
            
            if self.language in ['java', 'both']:
                for pattern in ['prompt[0-9].java', 'prompt[0-9][0-9].java']:
                    files['java'].extend(root_path.rglob(pattern))
        
        files['python'] = sorted(set(files['python']))
        files['java'] = sorted(set(files['java']))
        
        return files
    
    def run_tests(self) -> Dict[str, Any]:
        """Run dynamic security tests"""
        files = self.find_files()
        
        total_files = len(files['python']) + len(files['java'])
        if total_files == 0:
            print("No test files found!")
            return {}
        
        print(f"\n{'='*70}")
        print(f"Dynamic Security Testing Report")
        print(f"{'='*70}")
        print(f"Found {len(files['python'])} Python files and {len(files['java'])} Java files\n")
        print("⚠️  WARNING: This will execute potentially malicious code!")
        print("Ensure you're running this in a sandboxed environment.\n")
        
        response = input("Continue? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("Aborted.")
            return {}
        
        results = {}
        
        # Test Python files
        if files['python']:
            print(f"\n{'='*70}")
            print("Testing Python Files")
            print(f"{'='*70}")
            
            for filepath in files['python']:
                print(f"\nTesting: {filepath}")
                issues = self.tester.test_python_file(filepath)
                if issues:
                    results[str(filepath)] = dict(issues)
                    print(f"  ⚠️  Found {sum(len(v) for v in issues.values())} issues")
                else:
                    print(f"  ✓ No vulnerabilities detected")
        
        # Test Java files
        if files['java']:
            print(f"\n{'='*70}")
            print("Testing Java Files")
            print(f"{'='*70}")
            
            for filepath in files['java']:
                print(f"\nTesting: {filepath}")
                issues = self.tester.test_java_file(filepath)
                if issues:
                    results[str(filepath)] = dict(issues)
                    print(f"  ⚠️  Found {sum(len(v) for v in issues.values())} issues")
                else:
                    print(f"  ✓ No vulnerabilities detected")
        
        return results
    
    def export_results(self, results: Dict, output_file: str = 'dynamic_security_report.json'):
        """Export results to JSON"""
        output = {
            'test_type': 'dynamic_analysis',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_files_tested': len(results),
            'total_issues': sum(sum(len(issues) for issues in file_issues.values()) 
                               for file_issues in results.values()),
            'results': results
        }
        
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n{'='*70}")
        print(f"Results exported to {output_file}")
        print(f"{'='*70}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Dynamic security testing harness - RUNS CODE WITH MALICIOUS INPUTS'
    )
    parser.add_argument(
        'directories',
        nargs='*',
        default=['.'],
        help='Directories to scan'
    )
    parser.add_argument(
        '-l', '--language',
        choices=['python', 'java', 'both'],
        default='both',
        help='Language to test'
    )
    parser.add_argument(
        '-o', '--output',
        default='dynamic_security_report.json',
        help='Output JSON file'
    )
    
    args = parser.parse_args()
    
    harness = DynamicTestHarness(root_dirs=args.directories, language=args.language)
    results = harness.run_tests()
    
    if results:
        harness.export_results(results, args.output)
    
    exit(1 if results else 0)


if __name__ == '__main__':
    main()