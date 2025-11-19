"""
Security Scanning Middleware and CI/CD Integration
Implements SAST, DAST, and dependency scanning integration
"""

import json
import logging
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class SecurityScanningService:
    """Service for integrating security scanning tools"""

    def __init__(self):
        self.scan_results_dir = "/tmp/security_scans"
        os.makedirs(self.scan_results_dir, exist_ok=True)

    def run_dependency_scan(self, requirements_file: str = "requirements.txt") -> Dict[str, Any]:
        """Run dependency vulnerability scanning"""
        try:
            # Using safety for Python dependency scanning
            result = subprocess.run([
                "safety", "check", "--json", "--file", requirements_file
            ], capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                scan_results = {
                    "status": "success",
                    "vulnerabilities": [],
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                try:
                    vulnerabilities = json.loads(result.stdout) if result.stdout else []
                except json.JSONDecodeError:
                    vulnerabilities = []

                scan_results = {
                    "status": "vulnerabilities_found",
                    "vulnerabilities": vulnerabilities,
                    "timestamp": datetime.utcnow().isoformat(),
                    "raw_output": result.stdout
                }

            # Save results
            results_file = os.path.join(self.scan_results_dir, f"dependency_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(results_file, 'w') as f:
                json.dump(scan_results, f, indent=2)

            return scan_results

        except subprocess.TimeoutExpired:
            logger.error("Dependency scan timed out")
            return {"status": "timeout", "timestamp": datetime.utcnow().isoformat()}
        except Exception as e:
            logger.error(f"Error running dependency scan: {e}")
            return {"status": "error", "error": str(e), "timestamp": datetime.utcnow().isoformat()}

    def run_bandit_sast_scan(self, source_dir: str = ".") -> Dict[str, Any]:
        """Run SAST scanning using Bandit"""
        try:
            result = subprocess.run([
                "bandit", "-r", source_dir, "-f", "json", "-o", "/tmp/bandit_results.json"
            ], capture_output=True, text=True, timeout=600)

            # Read results
            try:
                with open("/tmp/bandit_results.json", 'r') as f:
                    bandit_results = json.load(f)
            except FileNotFoundError:
                bandit_results = {"results": [], "metrics": {}}

            scan_results = {
                "status": "completed",
                "tool": "bandit",
                "results": bandit_results,
                "timestamp": datetime.utcnow().isoformat(),
                "high_severity_count": len([r for r in bandit_results.get("results", []) if r.get("issue_severity") == "HIGH"]),
                "medium_severity_count": len([r for r in bandit_results.get("results", []) if r.get("issue_severity") == "MEDIUM"]),
                "low_severity_count": len([r for r in bandit_results.get("results", []) if r.get("issue_severity") == "LOW"])
            }

            # Save results
            results_file = os.path.join(self.scan_results_dir, f"sast_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(results_file, 'w') as f:
                json.dump(scan_results, f, indent=2)

            return scan_results

        except subprocess.TimeoutExpired:
            logger.error("SAST scan timed out")
            return {"status": "timeout", "timestamp": datetime.utcnow().isoformat()}
        except Exception as e:
            logger.error(f"Error running SAST scan: {e}")
            return {"status": "error", "error": str(e), "timestamp": datetime.utcnow().isoformat()}

    def run_semgrep_sast_scan(self, source_dir: str = ".") -> Dict[str, Any]:
        """Run SAST scanning using Semgrep"""
        try:
            result = subprocess.run([
                "semgrep", "--config=auto", "--json", source_dir
            ], capture_output=True, text=True, timeout=600)

            try:
                semgrep_results = json.loads(result.stdout) if result.stdout else {"results": []}
            except json.JSONDecodeError:
                semgrep_results = {"results": []}

            scan_results = {
                "status": "completed",
                "tool": "semgrep",
                "results": semgrep_results,
                "timestamp": datetime.utcnow().isoformat(),
                "findings_count": len(semgrep_results.get("results", []))
            }

            # Save results
            results_file = os.path.join(self.scan_results_dir, f"semgrep_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(results_file, 'w') as f:
                json.dump(scan_results, f, indent=2)

            return scan_results

        except subprocess.TimeoutExpired:
            logger.error("Semgrep scan timed out")
            return {"status": "timeout", "timestamp": datetime.utcnow().isoformat()}
        except Exception as e:
            logger.error(f"Error running Semgrep scan: {e}")
            return {"status": "error", "error": str(e), "timestamp": datetime.utcnow().isoformat()}

    def generate_security_report(self) -> Dict[str, Any]:
        """Generate comprehensive security report"""
        try:
            # Run all scans
            dependency_results = self.run_dependency_scan()
            bandit_results = self.run_bandit_sast_scan()
            semgrep_results = self.run_semgrep_sast_scan()

            # Aggregate results
            report = {
                "report_timestamp": datetime.utcnow().isoformat(),
                "summary": {
                    "dependency_vulnerabilities": len(dependency_results.get("vulnerabilities", [])),
                    "sast_high_severity": bandit_results.get("high_severity_count", 0),
                    "sast_medium_severity": bandit_results.get("medium_severity_count", 0),
                    "sast_low_severity": bandit_results.get("low_severity_count", 0),
                    "semgrep_findings": semgrep_results.get("findings_count", 0)
                },
                "detailed_results": {
                    "dependency_scan": dependency_results,
                    "bandit_sast": bandit_results,
                    "semgrep_sast": semgrep_results
                },
                "recommendations": self._generate_recommendations(dependency_results, bandit_results, semgrep_results)
            }

            # Save comprehensive report
            report_file = os.path.join(self.scan_results_dir, f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)

            return report

        except Exception as e:
            logger.error(f"Error generating security report: {e}")
            return {"status": "error", "error": str(e), "timestamp": datetime.utcnow().isoformat()}

    def _generate_recommendations(self, dependency_results: Dict, bandit_results: Dict, semgrep_results: Dict) -> List[str]:
        """Generate security recommendations based on scan results"""
        recommendations = []

        # Dependency recommendations
        vuln_count = len(dependency_results.get("vulnerabilities", []))
        if vuln_count > 0:
            recommendations.append(f"Update {vuln_count} vulnerable dependencies to their latest secure versions")
            recommendations.append("Implement automated dependency scanning in CI/CD pipeline")

        # SAST recommendations
        high_severity = bandit_results.get("high_severity_count", 0)
        if high_severity > 0:
            recommendations.append(f"Address {high_severity} high-severity security issues identified by SAST scanning")

        medium_severity = bandit_results.get("medium_severity_count", 0)
        if medium_severity > 5:
            recommendations.append(f"Review and address {medium_severity} medium-severity security issues")

        # General recommendations
        recommendations.extend([
            "Implement regular security scanning in CI/CD pipeline",
            "Set up automated security alerts for new vulnerabilities",
            "Conduct regular penetration testing",
            "Implement security code review process",
            "Maintain security training for development team"
        ])

        return recommendations


class CICDSecurityIntegration:
    """CI/CD Security Integration utilities"""

    @staticmethod
    def generate_github_actions_workflow() -> str:
        """Generate GitHub Actions workflow for security scanning"""
        return """
name: Security Scanning

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 2 * * 1'  # Weekly scan on Mondays at 2 AM

jobs:
  security-scan:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install safety bandit semgrep
        pip install -r requirements.txt

    - name: Run dependency vulnerability scan
      run: |
        safety check --json --output safety-report.json || true

    - name: Run Bandit SAST scan
      run: |
        bandit -r . -f json -o bandit-report.json || true

    - name: Run Semgrep SAST scan
      run: |
        semgrep --config=auto --json --output=semgrep-report.json . || true

    - name: Upload security reports
      uses: actions/upload-artifact@v3
      with:
        name: security-reports
        path: |
          safety-report.json
          bandit-report.json
          semgrep-report.json

    - name: Check for high-severity issues
      run: |
        python scripts/check_security_results.py

    - name: Comment PR with security results
      if: github.event_name == 'pull_request'
      uses: actions/github-script@v6
      with:
        script: |
          const fs = require('fs');
          try {
            const banditReport = JSON.parse(fs.readFileSync('bandit-report.json', 'utf8'));
            const highSeverity = banditReport.results.filter(r => r.issue_severity === 'HIGH').length;
            const mediumSeverity = banditReport.results.filter(r => r.issue_severity === 'MEDIUM').length;

            const comment = `## Security Scan Results

            - High Severity Issues: ${highSeverity}
            - Medium Severity Issues: ${mediumSeverity}

            ${highSeverity > 0 ? '⚠️ High severity security issues found! Please review before merging.' : '✅ No high severity issues found.'}
            `;

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });
          } catch (error) {
            console.log('Could not parse security reports:', error);
          }

  dependency-review:
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'

    steps:
    - name: Dependency Review
      uses: actions/dependency-review-action@v3
      with:
        fail-on-severity: high
"""

    @staticmethod
    def generate_gitlab_ci_config() -> str:
        """Generate GitLab CI configuration for security scanning"""
        return """
stages:
  - security
  - test
  - deploy

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

cache:
  paths:
    - .cache/pip/

security_scan:
  stage: security
  image: python:3.11
  before_script:
    - pip install safety bandit semgrep
    - pip install -r requirements.txt
  script:
    - safety check --json --output safety-report.json || true
    - bandit -r . -f json -o bandit-report.json || true
    - semgrep --config=auto --json --output=semgrep-report.json . || true
    - python scripts/check_security_results.py
  artifacts:
    reports:
      sast: bandit-report.json
    paths:
      - safety-report.json
      - bandit-report.json
      - semgrep-report.json
    expire_in: 1 week
  only:
    - merge_requests
    - main
    - develop

dependency_scanning:
  stage: security
  image: python:3.11
  script:
    - pip install safety
    - safety check --json --output dependency-scan.json
  artifacts:
    reports:
      dependency_scanning: dependency-scan.json
  only:
    - merge_requests
    - main

secret_detection:
  stage: security
  image: registry.gitlab.com/gitlab-org/security-products/analyzers/secrets:latest
  script:
    - /analyzer run
  artifacts:
    reports:
      secret_detection: gl-secret-detection-report.json
  only:
    - merge_requests
    - main
"""

    @staticmethod
    def generate_security_check_script() -> str:
        """Generate Python script to check security results"""
        return """#!/usr/bin/env python3
import json
import sys
import os

def check_security_results():
    exit_code = 0

    # Check Bandit results
    if os.path.exists('bandit-report.json'):
        with open('bandit-report.json', 'r') as f:
            bandit_data = json.load(f)

        high_severity = len([r for r in bandit_data.get('results', []) if r.get('issue_severity') == 'HIGH'])
        medium_severity = len([r for r in bandit_data.get('results', []) if r.get('issue_severity') == 'MEDIUM'])

        print(f"Bandit SAST Results: {high_severity} high, {medium_severity} medium severity issues")

        if high_severity > 0:
            print("❌ High severity security issues found!")
            exit_code = 1
        elif medium_severity > 10:
            print("⚠️  Too many medium severity issues found!")
            exit_code = 1

    # Check Safety results
    if os.path.exists('safety-report.json'):
        with open('safety-report.json', 'r') as f:
            safety_data = json.load(f)

        if isinstance(safety_data, list) and len(safety_data) > 0:
            print(f"Safety Results: {len(safety_data)} vulnerable dependencies found")
            print("❌ Vulnerable dependencies found!")
            exit_code = 1
        else:
            print("✅ No vulnerable dependencies found")

    # Check Semgrep results
    if os.path.exists('semgrep-report.json'):
        with open('semgrep-report.json', 'r') as f:
            semgrep_data = json.load(f)

        findings = len(semgrep_data.get('results', []))
        print(f"Semgrep Results: {findings} findings")

        if findings > 20:
            print("⚠️  Many security findings detected")
            # Don't fail on Semgrep findings as they may include false positives

    return exit_code

if __name__ == "__main__":
    sys.exit(check_security_results())
"""


# Service instance
security_scanning_service = SecurityScanningService()
cicd_integration = CICDSecurityIntegration()
"""
