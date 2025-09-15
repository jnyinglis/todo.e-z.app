import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from app.schemas.response import BuildInfoResponse

router = APIRouter()


@router.get("/build-info")
async def get_build_info() -> BuildInfoResponse:
    """Get build information"""
    build_info_path = Path(__file__).parent.parent.parent / "build-info.json"

    try:
        with open(build_info_path, "r") as f:
            build_info_data = json.load(f)
        return BuildInfoResponse(**build_info_data)
    except FileNotFoundError:
        # Generate basic build info if file doesn't exist
        return BuildInfoResponse(
            version="dev",
            buildNumber="local",
            gitCommit="unknown",
            gitBranch="unknown",
            environment="development",
            buildTime="unknown",
            service="backend"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading build info: {str(e)}")