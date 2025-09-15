#!/usr/bin/env python3
"""
Run type checking and linting for the backend
"""
import subprocess
import sys
from pathlib import Path


def run_command(command: str, description: str) -> bool:
    """Run a command and return success status"""
    print(f"\n🔍 {description}...")
    try:
        result = subprocess.run(
            command.split(),
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ {description} passed")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False


def main() -> None:
    """Run all checks"""
    checks = [
        ("python generate_types.py", "Generating TypeScript types from OpenAPI schema"),
        ("mypy app", "Type checking with mypy"),
        ("pytest --tb=short", "Running tests"),
    ]

    failed_checks = []

    for command, description in checks:
        if not run_command(command, description):
            failed_checks.append(description)

    if failed_checks:
        print(f"\n❌ {len(failed_checks)} check(s) failed:")
        for check in failed_checks:
            print(f"  - {check}")
        sys.exit(1)
    else:
        print("\n✅ All checks passed!")


if __name__ == "__main__":
    main()