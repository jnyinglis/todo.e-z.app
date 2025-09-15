from pydantic import BaseModel


class MessageResponse(BaseModel):
    message: str


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    service: str


class TextResponse(BaseModel):
    content: str


class BuildInfoResponse(BaseModel):
    """Build information response schema."""
    version: str
    buildNumber: str
    gitCommit: str
    gitBranch: str
    environment: str
    buildTime: str
    service: str