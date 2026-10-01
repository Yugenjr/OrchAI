from typing import Dict, Any, Callable
from orchai.core.models import AgentCapabilityType, PolicyDecisionType

class PolicyBridge:
    def __init__(self, policies: Dict[AgentCapabilityType, PolicyDecisionType]):
        self.policies = policies

    def evaluate_tool(self, tool_name: str, args: Dict[str, Any]) -> PolicyDecisionType:
        """
        Evaluates a tool call against the OrchAI policies.
        Antigravity tools like run_command map to COMMAND_EXECUTION.
        """
        # Capability mapping
        capability = AgentCapabilityType.READ
        if tool_name == "run_command":
            capability = AgentCapabilityType.COMMAND_EXECUTION
        elif tool_name in ["edit_file", "replace_file_content", "multi_replace_file_content", "write_to_file"]:
            capability = AgentCapabilityType.WRITE
            
        return self.policies.get(capability, PolicyDecisionType.REQUIRE_APPROVAL)
