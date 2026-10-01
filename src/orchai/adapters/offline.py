from typing import List, Dict, Any, Optional
from orchai.adapters.base import AgentAdapter

class OfflineAgentAdapter(AgentAdapter):
    """
    Deterministic offline adapter for orchestration testing without an external LLM.
    Exposes zero real capabilities and performs no repository modifications.
    """
    def __init__(self):
        pass
        
    def initialize(self) -> bool:
        return True
        
    def health_check(self) -> str:
        return "OFFLINE"
        
    def capabilities(self) -> List[str]:
        return []
        
    def prepare_task(self, task_id: str, scope: List[str]) -> bool:
        return True
        
    def execute(self, task_id: str, attempt_id: str) -> Dict[str, Any]:
        return {"status": "SUCCESS", "message": "Offline execution simulated.", "artifacts": []}
        
    def collect_result(self, task_id: str) -> Dict[str, Any]:
        return {"result": "Simulated"}
        
    def stream_events(self):
        yield from []
        
    def cancel(self) -> bool:
        return True
        
    def supports_session_resume(self) -> bool:
        return False
        
    def resume_session(self, session_id: str) -> bool:
        return False
