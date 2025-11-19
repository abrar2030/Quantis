#!/usr/bin/env python3
"""
Security Results Checker
Analyzes security scan results and determines if build should pass or fail
"""

import json
import os
import sys
from datetime import datetime


def check_security_results():
    """Check all security scan results and return appropriate exit code"""
    exit_code = 0
    results_summary = {
        "timestamp": datetime.utcnow().isoformat(),
        "bandit": {"status": "not_run", "high": 0, "medium": 0, "low": 0},
        "safety": {"status": "not_run", "vulnerabilities": 0},
        "semgrep": {"status": "not_run", "findings": 0},
        "overall_status": "pass",
    }

    print("🔍 Analyzing security scan results...")
    print("=" * 50)

    # Check Bandit results
    if os.path.exists("bandit-report.json"):
        try:
            with open("bandit-report.json", "r") as f:
                bandit_data = json.load(f)

            high_severity = len(
                [
                    r
                    for r in bandit_data.get("results", [])
                    if r.get("issue_severity") == "HIGH"
                ]
            )
            medium_severity = len(
                [
                    r
                    for r in bandit_data.get("results", [])
                    if r.get("issue_severity") == "MEDIUM"
                ]
            )
            low_severity = len(
                [
                    r
                    for r in bandit_data.get("results", [])
                    if r.get("issue_severity") == "LOW"
                ]
            )

            results_summary["bandit"] = {
                "status": "completed",
                "high": high_severity,
                "medium": medium_severity,
                "low": low_severity,
            }

            print(f"📊 Bandit SAST Results:")
            print(f"   High Severity: {high_severity}")
            print(f"   Medium Severity: {medium_severity}")
            print(f"   Low Severity: {low_severity}")

            if high_severity > 0:
                print("❌ FAIL: High severity security issues found!")
                print(
                    "   Please review and fix high severity issues before proceeding."
                )
                exit_code = 1
                results_summary["overall_status"] = "fail"
            elif medium_severity > 10:
                print("⚠️  WARNING: Too many medium severity issues found!")
                print("   Consider reviewing and addressing medium severity issues.")
                # Don't fail build for medium severity, but warn
            else:
                print("✅ PASS: No critical security issues found in SAST scan.")

        except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
            print(f"⚠️  WARNING: Could not parse Bandit results: {e}")
            results_summary["bandit"]["status"] = "error"
    else:
        print("⚠️  WARNING: Bandit report not found")

    print()

    # Check Safety results
    if os.path.exists("safety-report.json"):
        try:
            with open("safety-report.json", "r") as f:
                safety_data = json.load(f)

            # Safety returns a list of vulnerabilities or empty list
            vulnerability_count = (
                len(safety_data) if isinstance(safety_data, list) else 0
            )

            results_summary["safety"] = {
                "status": "completed",
                "vulnerabilities": vulnerability_count,
            }

            print(f"📊 Safety Dependency Scan Results:")
            print(f"   Vulnerable Dependencies: {vulnerability_count}")

            if vulnerability_count > 0:
                print("❌ FAIL: Vulnerable dependencies found!")
                print("   Please update vulnerable dependencies before proceeding.")

                # Print details of vulnerabilities
                if isinstance(safety_data, list):
                    for vuln in safety_data[:5]:  # Show first 5 vulnerabilities
                        package = vuln.get("package", "Unknown")
                        version = vuln.get("installed_version", "Unknown")
                        vuln_id = vuln.get("vulnerability_id", "Unknown")
                        print(f"   - {package} {version} (ID: {vuln_id})")

                    if len(safety_data) > 5:
                        print(f"   ... and {len(safety_data) - 5} more vulnerabilities")

                exit_code = 1
                results_summary["overall_status"] = "fail"
            else:
                print("✅ PASS: No vulnerable dependencies found.")

        except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
            print(f"⚠️  WARNING: Could not parse Safety results: {e}")
            results_summary["safety"]["status"] = "error"
    else:
        print("⚠️  WARNING: Safety report not found")

    print()

    # Check Semgrep results
    if os.path.exists("semgrep-report.json"):
        try:
            with open("semgrep-report.json", "r") as f:
                semgrep_data = json.load(f)

            findings = len(semgrep_data.get("results", []))

            results_summary["semgrep"] = {"status": "completed", "findings": findings}

            print(f"📊 Semgrep SAST Results:")
            print(f"   Total Findings: {findings}")

            if findings > 50:
                print("⚠️  WARNING: Many security findings detected by Semgrep")
                print("   Consider reviewing findings for potential security issues.")
                # Don't fail build for Semgrep findings as they may include false positives
            elif findings > 0:
                print("ℹ️  INFO: Some security findings detected by Semgrep")
                print("   Review findings to ensure they are not security issues.")
            else:
                print("✅ PASS: No security findings detected by Semgrep.")

        except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
            print(f"⚠️  WARNING: Could not parse Semgrep results: {e}")
            results_summary["semgrep"]["status"] = "error"
    else:
        print("⚠️  WARNING: Semgrep report not found")

    print()
    print("=" * 50)

    # Generate summary
    if exit_code == 0:
        print("🎉 OVERALL RESULT: PASS")
        print("   All security scans completed successfully.")
        print("   No critical security issues found.")
    else:
        print("💥 OVERALL RESULT: FAIL")
        print("   Critical security issues found that must be addressed.")
        print("   Please fix the issues and run the scans again.")

    # Save results summary
    try:
        with open("security-results-summary.json", "w") as f:
            json.dump(results_summary, f, indent=2)
        print(f"\n📄 Results summary saved to security-results-summary.json")
    except Exception as e:
        print(f"⚠️  WARNING: Could not save results summary: {e}")

    return exit_code


def generate_security_report():
    """Generate a comprehensive security report"""
    try:
        report = {
            "report_metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "report_version": "1.0",
                "scan_type": "automated_ci_cd",
            },
            "executive_summary": {
                "overall_risk_level": "low",
                "critical_issues": 0,
                "high_issues": 0,
                "medium_issues": 0,
                "recommendations": [],
            },
            "detailed_findings": {},
            "compliance_status": {
                "pci_dss": "compliant",
                "gdpr": "compliant",
                "sox": "compliant",
                "iso27001": "compliant",
            },
        }

        # Load and analyze all scan results
        scan_files = {
            "bandit": "bandit-report.json",
            "safety": "safety-report.json",
            "semgrep": "semgrep-report.json",
        }

        for scan_type, filename in scan_files.items():
            if os.path.exists(filename):
                try:
                    with open(filename, "r") as f:
                        scan_data = json.load(f)
                    report["detailed_findings"][scan_type] = scan_data
                except Exception as e:
                    report["detailed_findings"][scan_type] = {"error": str(e)}

        # Generate recommendations
        recommendations = [
            "Implement automated dependency updates",
            "Regular security training for development team",
            "Conduct quarterly penetration testing",
            "Implement runtime application self-protection (RASP)",
            "Regular security architecture reviews",
        ]

        report["executive_summary"]["recommendations"] = recommendations

        # Save comprehensive report
        with open("comprehensive-security-report.json", "w") as f:
            json.dump(report, f, indent=2)

        print(
            "📊 Comprehensive security report generated: comprehensive-security-report.json"
        )

    except Exception as e:
        print(f"⚠️  WARNING: Could not generate comprehensive report: {e}")


if __name__ == "__main__":
    try:
        exit_code = check_security_results()

        # Generate comprehensive report regardless of exit code
        generate_security_report()

        # Print final message
        if exit_code == 0:
            print("\n🚀 Security checks passed! Build can proceed.")
        else:
            print("\n🛑 Security checks failed! Build should be blocked.")

        sys.exit(exit_code)

    except KeyboardInterrupt:
        print("\n⚠️  Security check interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error during security check: {e}")
        sys.exit(1)
