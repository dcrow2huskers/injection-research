#!/usr/bin/env python3
"""
Security Testing Harness for Java Code Samples
Scans promptN.java files for security vulnerabilities including injection attacks
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict


class JavaSecurityScanner:
    """Scans Java code for security vulnerabilities"""
    
    def __init__(self):
        self.vulnerabilities = defaultdict(list)
        
    def scan_file(self, filepath: Path) -> Dict[str, List[str]]:
        """Scan a single Java file for security issues"""
        issues = defaultdict(list)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Database-specific checks
            issues.update(self._check_sql_injection(content, filepath))
            issues.update(self._check_mongodb_injection(content, filepath))
            issues.update(self._check_postgresql_issues(content, filepath))
            issues.update(self._check_jdbc_security(content, filepath))
            
            # General security checks
            issues.update(self._check_command_injection(content, filepath))
            issues.update(self._check_path_traversal(content, filepath))
            issues.update(self._check_xxe_vulnerabilities(content, filepath))
            issues.update(self._check_deserialization(content, filepath))
            issues.update(self._check_crypto_issues(content, filepath))
            issues.update(self._check_hardcoded_secrets(content, filepath))
            issues.update(self._check_xss_vulnerabilities(content, filepath))
            issues.update(self._check_ldap_injection(content, filepath))
            issues.update(self._check_reflection_issues(content, filepath))
            issues.update(self._check_random_usage(content, filepath))
            issues.update(self._check_file_operations(content, filepath))
            
        except Exception as e:
            issues['scan_errors'].append(f"Error scanning file: {e}")
            
        return issues
    
    def _check_sql_injection(self, content: str, filepath: Path) -> Dict:
        """Check for SQL injection vulnerabilities"""
        issues = defaultdict(list)
        
        # String concatenation in SQL queries
        sql_concat_patterns = [
            (r'(?:Statement|PreparedStatement)\s+\w+\s*=.*?\.createStatement\(\).*?\.execute(?:Query|Update)?\s*\([^)]*\+', 
             'SQL query with string concatenation'),
            (r'\.execute(?:Query|Update)?\s*\([^)]*\+[^)]*\)', 
             'executeQuery/executeUpdate with concatenation'),
            (r'(?:SELECT|INSERT|UPDATE|DELETE|DROP|CREATE).*?\+.*?["\']',
             'SQL statement with string concatenation'),
            (r'String\s+\w+\s*=\s*["\'](?:SELECT|INSERT|UPDATE|DELETE).*?\+',
             'SQL string built with concatenation'),
            (r'\.format\s*\([^)]*(?:SELECT|INSERT|UPDATE|DELETE)',
             'String.format() used in SQL query'),
        ]
        
        for pattern, message in sql_concat_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues['sql_injection'].append(
                    f"Line {line_num}: {message}"
                )
        
        # Check for missing parameterized queries
        if re.search(r'\.execute(?:Query|Update)\s*\([^?]*\)', content):
            # Has executeQuery/Update but check if it's not using ? placeholders
            execute_calls = re.finditer(r'\.execute(?:Query|Update)\s*\(([^)]+)\)', content)
            for match in execute_calls:
                query = match.group(1)
                if '+' in query or 'concat' in query.lower():
                    line_num = content[:match.start()].count('\n') + 1
                    issues['sql_injection'].append(
                        f"Line {line_num}: Use PreparedStatement with ? placeholders instead"
                    )
        
        return issues
    
    def _check_mongodb_injection(self, content: str, filepath: Path) -> Dict:
        """Check for MongoDB injection vulnerabilities"""
        issues = defaultdict(list)
        
        # Check for MongoDB imports
        if not re.search(r'import.*mongodb', content, re.IGNORECASE):
            return issues
        
        mongo_patterns = [
            (r'\.find\s*\(\s*new\s+BasicDBObject\s*\([^)]*\+',
             'MongoDB find() with concatenated query'),
            (r'\.find\s*\(\s*Document\.parse\s*\([^)]*\+',
             'MongoDB Document.parse() with concatenation'),
            (r'BasicDBObject\s*\([^)]*\+.*?\)',
             'BasicDBObject with string concatenation'),
            (r'\$where.*?\+',
             'MongoDB $where with concatenation (dangerous!)'),
            (r'\.append\s*\([^)]*\+[^)]*\)',
             'MongoDB query append with concatenation'),
            (r'new\s+Document\s*\([^)]*\+',
             'MongoDB Document with concatenation'),
        ]
        
        for pattern, message in mongo_patterns:
            matches = re.finditer(pattern, content, re.DOTALL)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues['mongodb_injection'].append(
                    f"Line {line_num}: {message}"
                )
        
        # Check for $where operator (should be avoided)
        if '$where' in content or '"$where"' in content:
            matches = re.finditer(r'["\']?\$where["\']?', content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues['mongodb_injection'].append(
                    f"Line {line_num}: $where operator detected - prefer other operators"
                )
        
        return issues
    
    def _check_postgresql_issues(self, content: str, filepath: Path) -> Dict:
        """Check for PostgreSQL-specific security issues"""
        issues = defaultdict(list)
        
        # Check for PostgreSQL-specific functions that can be dangerous
        pg_patterns = [
            (r'pg_execute\s*\([^)]*\+',
             'pg_execute with concatenation'),
            (r'COPY.*FROM.*PROGRAM',
             'COPY FROM PROGRAM can execute commands'),
            (r'CREATE.*FUNCTION.*LANGUAGE.*plpython',
             'PL/Python functions can be dangerous if not properly secured'),
        ]
        
        for pattern, message in pg_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues['postgresql_specific'].append(
                    f"Line {line_num}: {message}"
                )
        
        return issues
    
    def _check_jdbc_security(self, content: str, filepath: Path) -> Dict:
        """Check for JDBC security issues"""
        issues = defaultdict(list)
        
        # Check for insecure JDBC connection strings
        jdbc_patterns = [
            (r'jdbc:.*password=\w+',
             'Password in JDBC connection string'),
            (r'jdbc:.*ssl=false',
             'SSL disabled in JDBC connection'),
            (r'getConnection\s*\([^)]*password[^)]*\)',
             'Hardcoded credentials in getConnection'),
        ]
        
        for pattern, message in jdbc_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues['jdbc_security'].append(
                    f"Line {line_num}: {message}"
                )
        
        # Check for Statement instead of PreparedStatement
        if 'createStatement()' in content:
            matches = re.finditer(r'\.createStatement\s*\(\s*\)', content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues['jdbc_security'].append(
                    f"Line {line_num}: Use PreparedStatement instead of Statement for parameterized queries"
                )
        
        return issues
    
    def _check_command_injection(self, content: str, filepath: Path) -> Dict:
        """Check for command injection vulnerabilities"""
        issues = defaultdict(list)
        
        cmd_patterns = [
            (r'Runtime\.getRuntime\s*\(\s*\)\.exec\s*\([^)]*\+',
             'Runtime.exec() with string concatenation'),
            (r'ProcessBuilder\s*\([^)]*\+',
             'ProcessBuilder with concatenated arguments'),
            (r'\.exec\s*\(\s*new\s+String\[\]\s*\{[^}]*\+',
             'exec() with concatenated string array'),
        ]
        
        for pattern, message in cmd_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues['command_injection'].append(
                    f"Line {line_num}: {message}"
                )
        
        return issues
    
    def _check_path_traversal(self, content: str, filepath: Path) -> Dict:
        """Check for path traversal vulnerabilities"""
        issues = defaultdict(list)
        
        path_patterns = [
            (r'new\s+File\s*\([^)]*\+',
             'File path with concatenation - validate and sanitize'),
            (r'new\s+FileInputStream\s*\([^)]*\+',
             'FileInputStream with concatenated path'),
            (r'new\s+FileOutputStream\s*\([^)]*\+',
             'FileOutputStream with concatenated path'),
            (r'Files\.newInputStream\s*\(Paths\.get\s*\([^)]*\+',
             'Path concatenation in Files.newInputStream'),
        ]
        
        for pattern, message in path_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues['path_traversal'].append(
                    f"Line {line_num}: {message}"
                )
        
        # Check for getResource without validation
        if 'getResource' in content or 'getResourceAsStream' in content:
            matches = re.finditer(r'\.getResourceAsStream\s*\([^)]*\+', content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues['path_traversal'].append(
                    f"Line {line_num}: getResourceAsStream with user input"
                )
        
        return issues
    
    def _check_xxe_vulnerabilities(self, content: str, filepath: Path) -> Dict:
        """Check for XML External Entity (XXE) vulnerabilities"""
        issues = defaultdict(list)
        
        # Check if XML parsing is used
        if not re.search(r'DocumentBuilder|SAXParser|XMLReader|Unmarshaller', content):
            return issues
        
        # Check for missing XXE prevention
        xxe_safe_patterns = [
            r'setFeature\s*\(\s*"http://xml\.org/sax/features/external-general-entities"\s*,\s*false',
            r'setFeature\s*\(\s*"http://apache\.org/xml/features/disallow-doctype-decl"\s*,\s*true',
            r'XMLConstants\.FEATURE_SECURE_PROCESSING',
        ]
        
        has_xxe_protection = any(re.search(pattern, content) for pattern in xxe_safe_patterns)
        
        if not has_xxe_protection:
            # Find XML parser creation
            parser_patterns = [
                r'DocumentBuilderFactory\.newInstance\s*\(\s*\)',
                r'SAXParserFactory\.newInstance\s*\(\s*\)',
                r'XMLInputFactory\.newInstance\s*\(\s*\)',
            ]
            
            for pattern in parser_patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    issues['xxe_vulnerability'].append(
                        f"Line {line_num}: XML parser without XXE protection"
                    )
        
        return issues
    
    def _check_deserialization(self, content: str, filepath: Path) -> Dict:
        """Check for insecure deserialization"""
        issues = defaultdict(list)
        
        deserial_patterns = [
            (r'ObjectInputStream.*\.readObject\s*\(\s*\)',
             'ObjectInputStream.readObject() can execute arbitrary code'),
            (r'XMLDecoder.*\.readObject\s*\(\s*\)',
             'XMLDecoder.readObject() is unsafe'),
            (r'XStream.*\.fromXML',
             'XStream deserialization without whitelist'),
        ]
        
        for pattern, message in deserial_patterns:
            matches = re.finditer(pattern, content, re.DOTALL)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues['insecure_deserialization'].append(
                    f"Line {line_num}: {message}"
                )
        
        return issues
    
    def _check_crypto_issues(self, content: str, filepath: Path) -> Dict:
        """Check for cryptographic vulnerabilities"""
        issues = defaultdict(list)
        
        crypto_patterns = [
            (r'getInstance\s*\(\s*"DES"\s*\)',
             'DES encryption is weak - use AES'),
            (r'getInstance\s*\(\s*"MD5"\s*\)',
             'MD5 is cryptographically broken'),
            (r'getInstance\s*\(\s*"SHA1"\s*\)',
             'SHA1 is weak - use SHA-256 or better'),
            (r'getInstance\s*\(\s*"ECB"\s*\)',
             'ECB mode is insecure - use CBC or GCM'),
            (r'Random\s*\(\s*\)',
             'java.util.Random is not cryptographically secure - use SecureRandom'),
            (r'new\s+Random\s*\([^)]*\)',
             'Use SecureRandom for cryptographic operations'),
        ]
        
        for pattern, message in crypto_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues['weak_crypto'].append(
                    f"Line {line_num}: {message}"
                )
        
        # Check for hardcoded crypto keys
        if re.search(r'new\s+SecretKeySpec\s*\(\s*new\s+byte\[\]', content):
            matches = re.finditer(r'new\s+SecretKeySpec\s*\(\s*new\s+byte\[\]', content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues['weak_crypto'].append(
                    f"Line {line_num}: Hardcoded encryption key detected"
                )
        
        return issues
    
    def _check_hardcoded_secrets(self, content: str, filepath: Path) -> Dict:
        """Check for hardcoded secrets and credentials"""
        issues = defaultdict(list)
        
        secret_patterns = [
            (r'(?i)(password|passwd|pwd)\s*=\s*"[^"]{3,}"',
             'Hardcoded password'),
            (r'(?i)api[_-]?key\s*=\s*"[^"]{10,}"',
             'Hardcoded API key'),
            (r'(?i)(secret|token)\s*=\s*"[^"]{10,}"',
             'Hardcoded secret/token'),
            (r'(?i)private[_-]?key\s*=\s*"[^"]+"',
             'Hardcoded private key'),
        ]
        
        for pattern, message in secret_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues['hardcoded_secrets'].append(
                    f"Line {line_num}: {message}"
                )
        
        return issues
    
    def _check_xss_vulnerabilities(self, content: str, filepath: Path) -> Dict:
        """Check for Cross-Site Scripting (XSS) vulnerabilities"""
        issues = defaultdict(list)
        
        xss_patterns = [
            (r'response\.getWriter\s*\(\s*\)\.write\s*\([^)]*\+',
             'Writing user input to response without sanitization'),
            (r'out\.println\s*\([^)]*\+.*?request\.getParameter',
             'Printing request parameter without sanitization'),
            (r'\.innerHTML\s*=.*?\+',
             'Setting innerHTML with concatenation'),
        ]
        
        for pattern, message in xss_patterns:
            matches = re.finditer(pattern, content, re.DOTALL)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues['xss_vulnerability'].append(
                    f"Line {line_num}: {message}"
                )
        
        return issues
    
    def _check_ldap_injection(self, content: str, filepath: Path) -> Dict:
        """Check for LDAP injection vulnerabilities"""
        issues = defaultdict(list)
        
        if not re.search(r'import.*ldap|LdapContext|DirContext', content):
            return issues
        
        ldap_patterns = [
            (r'\.search\s*\([^)]*\+',
             'LDAP search with concatenated filter'),
            (r'new\s+SearchControls\s*\([^)]*\+',
             'SearchControls with concatenation'),
        ]
        
        for pattern, message in ldap_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues['ldap_injection'].append(
                    f"Line {line_num}: {message}"
                )
        
        return issues
    
    def _check_reflection_issues(self, content: str, filepath: Path) -> Dict:
        """Check for unsafe reflection usage"""
        issues = defaultdict(list)
        
        reflection_patterns = [
            (r'Class\.forName\s*\([^)]*\+',
             'Class.forName() with user input'),
            (r'\.getMethod\s*\([^)]*\+',
             'getMethod() with concatenated method name'),
            (r'\.invoke\s*\([^)]*\+',
             'Reflection invoke with user input'),
        ]
        
        for pattern, message in reflection_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues['unsafe_reflection'].append(
                    f"Line {line_num}: {message}"
                )
        
        return issues
    
    def _check_random_usage(self, content: str, filepath: Path) -> Dict:
        """Check for insecure random number generation"""
        issues = defaultdict(list)
        
        # Look for security-sensitive contexts
        security_context = re.search(
            r'(?i)(password|token|session|key|nonce|salt|iv)',
            content
        )
        
        if security_context and 'new Random()' in content:
            matches = re.finditer(r'new\s+Random\s*\(\s*\)', content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues['insecure_random'].append(
                    f"Line {line_num}: Use SecureRandom for security-sensitive operations"
                )
        
        return issues
    
    def _check_file_operations(self, content: str, filepath: Path) -> Dict:
        """Check for unsafe file operations"""
        issues = defaultdict(list)
        
        # Check for file deletion with user input
        if re.search(r'\.delete\s*\(\s*\)', content):
            file_delete = re.finditer(r'new\s+File\s*\([^)]*\+[^)]*\).*?\.delete', content, re.DOTALL)
            for match in file_delete:
                line_num = content[:match.start()].count('\n') + 1
                issues['unsafe_file_ops'].append(
                    f"Line {line_num}: File deletion with user input"
                )
        
        # Check for file upload without validation
        upload_patterns = [
            (r'MultipartFile.*?\.transferTo',
             'File upload - ensure filename validation and size limits'),
            (r'FileUpload.*?\.parseRequest',
             'File upload - validate content type and size'),
        ]
        
        for pattern, message in upload_patterns:
            matches = re.finditer(pattern, content, re.DOTALL)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues['unsafe_file_ops'].append(
                    f"Line {line_num}: {message}"
                )
        
        return issues


class JavaTestHarness:
    """Main testing harness for discovering and scanning Java files"""
    
    def __init__(self, root_dirs: List[str] = None):
        self.root_dirs = root_dirs or ['.']
        self.scanner = JavaSecurityScanner()
        
    def find_prompt_files(self) -> List[Path]:
        """Find all promptN.java files in the specified directories"""
        files = []
        
        for root_dir in self.root_dirs:
            root_path = Path(root_dir)
            if not root_path.exists():
                print(f"Warning: Directory {root_dir} does not exist")
                continue
                
            # Find all promptN.java files
            for pattern in ['prompt[0-9].java', 'prompt[0-9][0-9].java']:
                files.extend(root_path.rglob(pattern))
        
        return sorted(set(files))
    
    def run_tests(self) -> Dict[str, Any]:
        """Run security tests on all found files"""
        files = self.find_prompt_files()
        
        if not files:
            print("No promptN.java files found!")
            return {}
        
        print(f"\n{'='*70}")
        print(f"Java Security Scan Report")
        print(f"{'='*70}")
        print(f"Found {len(files)} files to scan\n")
        
        results = {}
        total_issues = 0
        category_counts = defaultdict(int)
        
        for filepath in files:
            print(f"Scanning: {filepath}")
            issues = self.scanner.scan_file(filepath)
            
            if any(issues.values()):
                results[str(filepath)] = dict(issues)
                file_issue_count = sum(len(v) for v in issues.values())
                total_issues += file_issue_count
                
                # Count by category
                for category, items in issues.items():
                    category_counts[category] += len(items)
                
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
        
        # Print category breakdown
        if category_counts:
            print("Issues by Category:")
            for category, count in sorted(category_counts.items(), key=lambda x: -x[1]):
                print(f"  • {category.replace('_', ' ').title()}: {count}")
        
        # Print detailed results
        if results:
            print(f"\n{'='*70}")
            print(f"Detailed Results")
            print(f"{'='*70}\n")
            
            for filepath, issues in results.items():
                print(f"\n{filepath}")
                print("-" * len(filepath))
                
                for category, items in sorted(issues.items()):
                    if items:
                        print(f"\n{category.replace('_', ' ').title()}:")
                        for item in items:
                            print(f"  • {item}")
        
        return results
    
    def export_results(self, results: Dict, output_file: str = 'java_security_report.json'):
        """Export results to JSON file"""
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults exported to {output_file}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Security testing harness for Java code samples'
    )
    parser.add_argument(
        'directories',
        nargs='*',
        default=['.'],
        help='Directories to scan (default: current directory)'
    )
    parser.add_argument(
        '-o', '--output',
        default='java_security_report.json',
        help='Output JSON file for results'
    )
    
    args = parser.parse_args()
    
    harness = JavaTestHarness(root_dirs=args.directories)
    results = harness.run_tests()
    
    if results:
        harness.export_results(results, args.output)
    
    # Exit with error code if vulnerabilities found
    exit(1 if results else 0)


if __name__ == '__main__':
    main()