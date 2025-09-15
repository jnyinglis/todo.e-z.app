from __future__ import annotations

import json
import os
import re
import subprocess
import secrets
import string
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import dotenv_values, set_key


# Resolve important paths
HERE = Path(__file__).resolve().parent
BACKEND_DIR = HERE.parent
REPO_ROOT = BACKEND_DIR.parent

ENV_FILE = REPO_ROOT / ".env"
ENV_EXAMPLE_FILE = REPO_ROOT / ".env.example"
MAKEFILE = REPO_ROOT / "Makefile"
PACKAGE_JSON = REPO_ROOT / "package.json"
FRONTEND_PACKAGE_JSON = REPO_ROOT / "frontend" / "package.json"
MANIFEST_JSON = REPO_ROOT / "frontend" / "public" / "manifest.json"
SEO_HEAD_COMPONENT = REPO_ROOT / "frontend" / "src" / "components" / "SEOHead.tsx"


# Pydantic models for request/response
class AppConfiguration(BaseModel):
    app_name: str
    app_slug: str
    app_description: str = ""
    theme_color: str = "#646cff"
    background_color: str = "#ffffff"
    domain: str = ""
    github_repository: str = ""


class ConfigurationUpdate(BaseModel):
    updates: Dict[str, str]


REQUIRED_ENV_KEYS = [
    # Deployment and domain
    "DOMAIN",
    "ACME_EMAIL",
    # Backend secrets / config
    "SECRET_KEY",
    "POSTGRES_PASSWORD",
    # Google OAuth
    "GOOGLE_CLIENT_ID",
    "GOOGLE_CLIENT_SECRET",
    # Container registry / images
    "GITHUB_REPOSITORY",
    "IMAGE_TAG",
]


def load_envs() -> Dict[str, str]:
    current = {}
    if ENV_FILE.exists():
        current = dotenv_values(str(ENV_FILE)) or {}
    example = {}
    if ENV_EXAMPLE_FILE.exists():
        example = dotenv_values(str(ENV_EXAMPLE_FILE)) or {}
    # Merge, preferring current values
    merged = {**example, **current}
    return {k: v or "" for k, v in merged.items()}


def list_make_targets() -> List[str]:
    targets: List[str] = []
    if not MAKEFILE.exists():
        return targets
    pattern = re.compile(r"^(?P<name>[a-zA-Z0-9_.-]+):")
    for line in MAKEFILE.read_text().splitlines():
        if line.startswith("#") or line.strip() == "":
            continue
        m = pattern.match(line)
        if m:
            name = m.group("name")
            # Filter common special targets
            if name not in (".PHONY", "help", ".DEFAULT_GOAL"):
                targets.append(name)
    return sorted(set(targets))


def list_pnpm_scripts() -> List[str]:
    if not PACKAGE_JSON.exists():
        return []
    try:
        pkg = json.loads(PACKAGE_JSON.read_text())
        scripts = pkg.get("scripts", {})
        return sorted(scripts.keys())
    except Exception:
        return []


ALLOWED_RUNNERS = {"make", "pnpm"}


def run_command(runner: str, name: str, extra_args: Optional[List[str]] = None) -> Dict[str, str]:
    extra_args = extra_args or []
    if runner not in ALLOWED_RUNNERS:
        raise HTTPException(status_code=400, detail="Unsupported runner")

    if runner == "make":
        allowed = set(list_make_targets())
        if name not in allowed:
            raise HTTPException(status_code=400, detail=f"Unknown make target: {name}")
        cmd = ["make", name] + extra_args
    elif runner == "pnpm":
        allowed = set(list_pnpm_scripts())
        if name not in allowed:
            raise HTTPException(status_code=400, detail=f"Unknown pnpm script: {name}")
        cmd = ["pnpm", "run", name] + extra_args
    else:
        raise HTTPException(status_code=400, detail="Invalid runner")

    try:
        proc = subprocess.run(
            cmd,
            cwd=str(REPO_ROOT),
            check=False,
            capture_output=True,
            text=True,
        )
        return {
            "cmd": " ".join(cmd),
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "code": str(proc.returncode),
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=f"Command not found: {e}")


def write_env_updates(updates: Dict[str, str]) -> None:
    if not ENV_FILE.exists():
        ENV_FILE.write_text("")
    # Backup
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    backup = ENV_FILE.parent / f".env.backup.{timestamp}"
    try:
        backup.write_text(ENV_FILE.read_text())
    except Exception:
        # Best-effort backup; continue on failure
        pass
    # Apply updates
    for key, value in updates.items():
        set_key(str(ENV_FILE), key, value if value is not None else "")


def generate_secure_key(length: int = 64) -> str:
    """Generate a secure random key for secrets."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def slugify(text: str) -> str:
    """Convert text to a URL-friendly slug."""
    import re
    # Convert to lowercase and replace spaces with hyphens
    slug = re.sub(r'[^a-z0-9\s-]', '', text.lower())
    slug = re.sub(r'\s+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')


def update_json_file(file_path: Path, updates: Dict[str, Any]) -> None:
    """Update a JSON file with new values."""
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")

    try:
        with open(file_path, 'r') as f:
            data = json.load(f)

        # Apply updates
        for key, value in updates.items():
            data[key] = value

        # Write back
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update {file_path.name}: {str(e)}")


def update_svg_icon(svg_path: Path, app_name: str, theme_color: str) -> None:
    """Update SVG icon with app-specific branding."""
    if not svg_path.exists():
        return

    try:
        content = svg_path.read_text()

        # Update colors
        content = re.sub(r'stop-color:#646cff', f'stop-color:{theme_color}', content)
        content = re.sub(r'fill="#646cff"', f'fill="{theme_color}"', content)

        # Update text content if it exists
        if 'FS' in content:
            # Generate initials from app name
            words = app_name.split()
            if len(words) >= 2:
                initials = words[0][0].upper() + words[1][0].upper()
            else:
                initials = app_name[:2].upper()

            content = re.sub(r'>FS<', f'>{initials}<', content)

        svg_path.write_text(content)
    except Exception as e:
        print(f"Warning: Could not update {svg_path.name}: {str(e)}")


def update_seo_defaults(app_name: str, app_description: str, domain: str) -> None:
    """Update SEO component with app-specific defaults."""
    if not SEO_HEAD_COMPONENT.exists():
        return

    try:
        content = SEO_HEAD_COMPONENT.read_text()

        # Update default SEO values
        content = re.sub(
            r"title: 'Vite React FastAPI Template - Modern Full-Stack Development'",
            f"title: '{app_name} - Modern Full-Stack Application'",
            content
        )

        if app_description:
            content = re.sub(
                r"description: 'A modern full-stack template.*?'",
                f"description: '{app_description}'",
                content
            )

        if domain:
            # Update canonical URL
            content = re.sub(
                r"canonical: 'https://example\.com'",
                f"canonical: 'https://{domain}'",
                content
            )

        SEO_HEAD_COMPONENT.write_text(content)
    except Exception as e:
        print(f"Warning: Could not update SEO defaults: {str(e)}")


app = FastAPI(title="Setup Tool", description="Local configuration helper", version="0.1.0")

# Same-origin UI, but allow localhost access just in case
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5050", "http://localhost:5050"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/api/vars")
def get_vars() -> Dict[str, Any]:
    envs = load_envs()
    data = {k: envs.get(k, "") for k in REQUIRED_ENV_KEYS}
    return {"env": data, "file": str(ENV_FILE)}


@app.post("/api/vars")
def set_vars(payload: Dict[str, Dict[str, str]]) -> Dict[str, Any]:
    updates = payload.get("updates", {})
    if not isinstance(updates, dict):
        raise HTTPException(status_code=400, detail="Invalid payload: updates required")
    # Only allow known keys or explicitly passed keys
    filtered = {k: v for k, v in updates.items() if isinstance(k, str)}
    write_env_updates(filtered)
    return {"ok": True, "written": filtered}


@app.get("/api/scripts")
def scripts() -> Dict[str, List[str]]:
    return {
        "make": list_make_targets(),
        "pnpm": list_pnpm_scripts(),
    }


@app.post("/api/run")
def run(payload: Dict[str, object]) -> Dict[str, str]:
    runner = payload.get("runner")
    name = payload.get("name")
    args = payload.get("args", [])
    if not isinstance(runner, str) or not isinstance(name, str):
        raise HTTPException(status_code=400, detail="runner and name are required")
    if not isinstance(args, list):
        raise HTTPException(status_code=400, detail="args must be a list")
    result = run_command(runner, name, [str(a) for a in args])
    return result


@app.post("/api/ghcr-login")
def ghcr_login(payload: Dict[str, str]) -> Dict[str, Any]:
    username = payload.get("username")
    token = payload.get("token")
    if not username or not token:
        raise HTTPException(status_code=400, detail="username and token are required")
    try:
        proc = subprocess.run(
            ["docker", "login", "ghcr.io", "-u", username, "--password-stdin"],
            input=token,
            text=True,
            cwd=str(REPO_ROOT),
            capture_output=True,
            check=False,
        )
        return {
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "code": proc.returncode,
        }
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="docker not found. Please install Docker.")


@app.post("/api/generate-secret")
def generate_secret(length: Optional[int] = 64) -> Dict[str, str]:
    """Generate a secure secret key."""
    if length is not None and (length < 16 or length > 128):
        raise HTTPException(status_code=400, detail="Length must be between 16 and 128")
    return {"secret": generate_secure_key(length or 64)}


@app.post("/api/apply-configuration")
def apply_configuration(config: AppConfiguration) -> Dict[str, Any]:
    """Apply comprehensive application configuration."""
    try:
        results: Dict[str, List[str]] = {"updated": [], "errors": []}

        # 1. Update environment variables
        try:
            env_updates = {
                "SECRET_KEY": generate_secure_key(64),
                "POSTGRES_PASSWORD": generate_secure_key(32),
            }

            if config.domain:
                env_updates["DOMAIN"] = config.domain
                env_updates["FRONTEND_URL"] = f"https://{config.domain}"

            if config.github_repository:
                env_updates["GITHUB_REPOSITORY"] = config.github_repository

            write_env_updates(env_updates)
            results["updated"].append(".env")
        except Exception as e:
            results["errors"].append(f".env: {str(e)}")

        # 2. Update frontend package.json
        try:
            if FRONTEND_PACKAGE_JSON.exists():
                package_updates = {
                    "name": config.app_slug,
                    "description": config.app_description or f"{config.app_name} - A modern full-stack application",
                }
                update_json_file(FRONTEND_PACKAGE_JSON, package_updates)
                results["updated"].append("frontend/package.json")
        except Exception as e:
            results["errors"].append(f"frontend/package.json: {str(e)}")

        # 3. Update PWA manifest
        try:
            if MANIFEST_JSON.exists():
                manifest_updates = {
                    "name": config.app_name,
                    "short_name": config.app_name[:12],  # Truncate for mobile
                    "description": config.app_description or f"{config.app_name} - A modern full-stack application",
                    "theme_color": config.theme_color,
                    "background_color": config.background_color,
                }
                update_json_file(MANIFEST_JSON, manifest_updates)
                results["updated"].append("frontend/public/manifest.json")
        except Exception as e:
            results["errors"].append(f"manifest.json: {str(e)}")

        # 4. Update app icons
        try:
            icon_paths = [
                REPO_ROOT / "frontend" / "public" / "icon-192.svg",
                REPO_ROOT / "frontend" / "public" / "icon-512.svg"
            ]

            for icon_path in icon_paths:
                update_svg_icon(icon_path, config.app_name, config.theme_color)
                if icon_path.exists():
                    results["updated"].append(str(icon_path.relative_to(REPO_ROOT)))
        except Exception as e:
            results["errors"].append(f"app icons: {str(e)}")

        # 5. Update SEO defaults
        try:
            update_seo_defaults(config.app_name, config.app_description, config.domain)
            if SEO_HEAD_COMPONENT.exists():
                results["updated"].append(str(SEO_HEAD_COMPONENT.relative_to(REPO_ROOT)))
        except Exception as e:
            results["errors"].append(f"SEO defaults: {str(e)}")

        return {
            "success": len(results["errors"]) == 0,
            "updated_files": results["updated"],
            "errors": results["errors"],
            "message": f"Updated {len(results['updated'])} files" +
                      (f" with {len(results['errors'])} errors" if results["errors"] else "")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Configuration failed: {str(e)}")


@app.get("/api/app-config")
def get_app_config() -> Dict[str, Dict[str, str]]:
    """Get current app configuration from various sources."""
    config = {}

    try:
        # Try to read from frontend package.json
        if FRONTEND_PACKAGE_JSON.exists():
            with open(FRONTEND_PACKAGE_JSON, 'r') as f:
                pkg = json.load(f)
                config["app_slug"] = pkg.get("name", "")
                config["app_description"] = pkg.get("description", "")

        # Try to read from manifest.json
        if MANIFEST_JSON.exists():
            with open(MANIFEST_JSON, 'r') as f:
                manifest = json.load(f)
                config["app_name"] = manifest.get("name", "")
                config["theme_color"] = manifest.get("theme_color", "#646cff")
                config["background_color"] = manifest.get("background_color", "#ffffff")

        # Read environment variables
        envs = load_envs()
        config["domain"] = envs.get("DOMAIN", "")
        config["github_repository"] = envs.get("GITHUB_REPOSITORY", "")

    except Exception as e:
        print(f"Warning: Could not load existing config: {str(e)}")

    return {"config": config}


# Serve the simple UI
UI_DIR = HERE / "ui"
app.mount("/", StaticFiles(directory=str(UI_DIR), html=True), name="ui")


if __name__ == "__main__":
    import uvicorn

    print("\nSetup Tool running at http://127.0.0.1:5050")
    print(f"Repo root: {REPO_ROOT}")
    print(f".env path: {ENV_FILE}")
    uvicorn.run(app, host="127.0.0.1", port=5050)
