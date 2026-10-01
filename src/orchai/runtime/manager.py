from typing import Dict, Optional
from orchai.runtime.process import AgentRuntime

class RuntimeManager:
    def __init__(self):
        self._processes: Dict[str, AgentRuntime] = {}

    def register(self, runtime: AgentRuntime):
        self._processes[runtime.process_id] = runtime

    def get(self, process_id: str) -> Optional[AgentRuntime]:
        return self._processes.get(process_id)

    def remove(self, process_id: str):
        if process_id in self._processes:
            del self._processes[process_id]
            
    def list_all(self) -> Dict[str, AgentRuntime]:
        return self._processes.copy()
