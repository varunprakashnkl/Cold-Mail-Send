#!/usr/bin/env python3
"""
Security Monitoring Script
This script performs security checks on the codebase and generates a report.
"""

import os
import sys
import re
import json
import subprocess
import datetime
from pathlib import Path

def check_for_hardcoded_credentials():
    """Check for hardcoded credentials in Python files"""
    print("Checking for hardcoded credentials...")
    
    patterns = [
        r'password\s*=\s*["\'][^"\']+["\']',
        r'api_key\s*=\s*["\'][^"\']+["\']',
        r'secret\s*=\s*["\'][^"\']+["\']',
        r'token\s*=\s*["\'][^"\']+["\']',
    ]
    
    findings = []
    
    for file_path in Path('.').rglob('*.py'):
        if 'venv' in str(file_path) or '.git' in str(file_path):
            continue
            
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            try:
                content = f.read()
                line_num = 1
                for line in content.split('\n'):
                    for pattern in patterns:
                        if re.search(pattern, line, re.IGNORECASE) and 'os.getenv' not in line and 'input(' not in line:
                            findings.append({
                                'file': str(file_path),
                                'line': line_num,
                                'content': line.strip(),
                                'type': 'Potential hardcoded credential'
                            })
                    line_num += 1
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    
    return findings

def check_for_security_vulnerabilities():
    """Run bandit to check for security vulnerabilities"""
    print("Checking for security vulnerabilities...")
    
    findings = []
    
    try:
        # Check if bandit is installed
        subprocess.run(['bandit', '--version'], capture_output=True, check=True)
        
        # Run bandit on all Python files
        result = subprocess.run(
            ['bandit', '-r', '.', '-f', 'json', '--skip', 'B101'],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0 and result.stdout:
            try:
                bandit_results = json.loads(result.stdout)
                for result in bandit_results.get('results', []):
                    findings.append({
                        'file': result.get('filename'),
                        'line': result.get('line_number'),
                        'content': result.get('code'),
                        'type': f"Security issue: {result.get('issue_text')}",
                        'severity': result.get('issue_severity')
                    })
            except json.JSONDecodeError:
                print("Failed to parse bandit output")
    except FileNotFoundError:
        print("Bandit is not installed. Install it with: pip install bandit")
    except Exception as e:
        print(f"Error running bandit: {e}")
    
    return findings

def check_for_input_validation():
    """Check for proper input validation in code"""
    print("Checking for input validation issues...")
    
    patterns = [
        r'eval\s*\(',
        r'exec\s*\(',
        r'os\.system\s*\(',
        r'subprocess\.call\s*\(',
        r'subprocess\.Popen\s*\(',
    ]
    
    findings = []
    
    for file_path in Path('.').rglob('*.py'):
        if 'venv' in str(file_path) or '.git' in str(file_path):
            continue
            
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            try:
                content = f.read()
                line_num = 1
                for line in content.split('\n'):
                    for pattern in patterns:
                        if re.search(pattern, line):
                            findings.append({
                                'file': str(file_path),
                                'line': line_num,
                                'content': line.strip(),
                                'type': 'Potential input validation issue'
                            })
                    line_num += 1
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    
    return findings

def check_for_outdated_dependencies():
    """Check for outdated dependencies"""
    print("Checking for outdated dependencies...")
    
    findings = []
    
    try:
        if os.path.exists('requirements.txt'):
            # Run pip list --outdated
            result = subprocess.run(
                ['pip', 'list', '--outdated', '--format=json'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0 and result.stdout:
                try:
                    outdated = json.loads(result.stdout)
                    for package in outdated:
                        findings.append({
                            'file': 'requirements.txt',
                            'line': 0,
                            'content': f"{package['name']} {package['version']} -> {package['latest_version']}",
                            'type': 'Outdated dependency'
                        })
                except json.JSONDecodeError:
                    print("Failed to parse pip output")
    except Exception as e:
        print(f"Error checking dependencies: {e}")
    
    return findings

def generate_report(findings):
    """Generate a security report"""
    print("\nGenerating security report...")
    
    report = {
        'timestamp': datetime.datetime.now().isoformat(),
        'findings': findings,
        'summary': {
            'total_issues': len(findings),
            'high_severity': len([f for f in findings if f.get('severity') == 'HIGH']),
            'medium_severity': len([f for f in findings if f.get('severity') == 'MEDIUM']),
            'low_severity': len([f for f in findings if f.get('severity') == 'LOW']),
            'other_issues': len([f for f in findings if f.get('severity') not in ['HIGH', 'MEDIUM', 'LOW']])
        }
    }
    
    # Save report to file
    with open('security_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print(f"\nSecurity Report Summary:")
    print(f"Total issues found: {report['summary']['total_issues']}")
    print(f"High severity issues: {report['summary']['high_severity']}")
    print(f"Medium severity issues: {report['summary']['medium_severity']}")
    print(f"Low severity issues: {report['summary']['low_severity']}")
    print(f"Other issues: {report['summary']['other_issues']}")
    print(f"\nDetailed report saved to security_report.json")
    
    # Also generate a text report
    with open('security_report.txt', 'w') as f:
        f.write(f"Security Report - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*80 + "\n\n")
        f.write(f"Total issues found: {report['summary']['total_issues']}\n")
        f.write(f"High severity issues: {report['summary']['high_severity']}\n")
        f.write(f"Medium severity issues: {report['summary']['medium_severity']}\n")
        f.write(f"Low severity issues: {report['summary']['low_severity']}\n")
        f.write(f"Other issues: {report['summary']['other_issues']}\n\n")
        
        if findings:
            f.write("Detailed Findings:\n")
            f.write("-"*80 + "\n\n")
            
            for i, finding in enumerate(findings, 1):
                f.write(f"Issue #{i}:\n")
                f.write(f"  File: {finding.get('file')}\n")
                f.write(f"  Line: {finding.get('line')}\n")
                f.write(f"  Type: {finding.get('type')}\n")
                if finding.get('severity'):
                    f.write(f"  Severity: {finding.get('severity')}\n")
                f.write(f"  Content: {finding.get('content')}\n\n")
    
    print(f"Text report saved to security_report.txt")
    
    # Return non-zero exit code if high severity issues found
    if report['summary']['high_severity'] > 0:
        return 1
    return 0

def main():
    """Main function"""
    print("Starting security monitoring...")
    
    all_findings = []
    
    # Check for hardcoded credentials
    all_findings.extend(check_for_hardcoded_credentials())
    
    # Check for security vulnerabilities
    all_findings.extend(check_for_security_vulnerabilities())
    
    # Check for input validation issues
    all_findings.extend(check_for_input_validation())
    
    # Check for outdated dependencies
    all_findings.extend(check_for_outdated_dependencies())
    
    # Generate report
    exit_code = generate_report(all_findings)
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())