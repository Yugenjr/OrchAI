import subprocess
from pydantic import BaseModel, Field

class ContainerRuntimeConfig(BaseModel):
    image: str = "orchai-runtime:latest"
    memory_limit: str = "512m"
    cpu_limit: str = "0.5"
    network_mode: str = "none"

class ContainerRuntimeAdapter:
    def __init__(self, config: ContainerRuntimeConfig):
        self.config = config

    def is_available(self) -> bool:
        try:
            result = subprocess.run(["docker", "info"], capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False

    def execute(self, command: list[str]) -> bool:
        if not self.is_available():
            raise RuntimeError("Docker is unavailable")
            
        args = [
            "docker", "run", "--rm",
            "--memory", self.config.memory_limit,
            "--cpus", self.config.cpu_limit,
            "--network", self.config.network_mode,
            "--user", "orchai",
            self.config.image
        ] + command
        
        result = subprocess.run(args, capture_output=True, text=True)
        return result.returncode == 0
