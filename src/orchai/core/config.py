from datetime import datetime
from pydantic import BaseModel, Field
from typing import Dict, Any

class OrchAIConfig(BaseModel):
    project_name: str
    project_root: str
    version: str = "0.1.0"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    policy: Dict[str, Any] = Field(default_factory=dict)
