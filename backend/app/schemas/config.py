from pydantic import BaseModel
from typing import List, Union


class CorsConfig(BaseModel):
    """CORS configuration schema."""
    allow_origins: List[str]
    allow_credentials: bool
    allow_methods: List[str]
    allow_headers: List[str]
    expose_headers: List[str] = []
    max_age: int