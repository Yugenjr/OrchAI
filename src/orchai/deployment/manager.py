from typing import Optional
from pydantic import BaseModel

class DeploymentTarget(BaseModel):
    id: str
    type: str = "local_docker"
    status: str = "UNKNOWN"

class DeploymentRequest(BaseModel):
    task_id: str
    target_id: str

class DeploymentResult(BaseModel):
    success: bool
    status: str
    message: Optional[str] = None

class DeploymentManager:
    def __init__(self):
        self.targets = {
            "local": DeploymentTarget(id="local", type="local_docker", status="READY")
        }

    def get_target(self, target_id: str) -> Optional[DeploymentTarget]:
        return self.targets.get(target_id)
        
    def deploy(self, request: DeploymentRequest) -> DeploymentResult:
        target = self.get_target(request.target_id)
        if not target:
            return DeploymentResult(success=False, status="FAILED", message="Target not found")
        if target.type != "local_docker":
            return DeploymentResult(success=False, status="UNSUPPORTED", message="Only local_docker is supported")
            
        return DeploymentResult(success=True, status="DEPLOYED", message="Successfully dispatched to container")
