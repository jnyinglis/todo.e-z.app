#!/usr/bin/env python3
"""
Generate build info for the backend
"""
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def get_git_commit() -> str:
    """Get current git commit hash"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def get_git_branch() -> str:
    """Get current git branch"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def generate_build_info() -> dict:
    """Generate build information"""
    return {
        "version": os.getenv("BUILD_VERSION", "dev"),
        "buildNumber": os.getenv("BUILD_NUMBER", "local"),
        "gitCommit": os.getenv("GIT_COMMIT", get_git_commit()),
        "gitBranch": get_git_branch(),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "buildTime": datetime.now(timezone.utc).isoformat(),
        "service": "backend"
    }


def main() -> None:
    """Main function"""
    build_info = generate_build_info()

    # Write to build-info.json
    build_info_path = Path(__file__).parent / "build-info.json"
    with open(build_info_path, "w") as f:
        json.dump(build_info, f, indent=2)

    print(f"✅ Build info generated: {build_info_path}")
    print(json.dumps(build_info, indent=2))


if __name__ == "__main__":
    main()