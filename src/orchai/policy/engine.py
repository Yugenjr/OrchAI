from fnmatch import fnmatch
from typing import List
from orchai.core.models import AgentAction, PolicyDecision, PolicyDecisionType

class PathPolicyEngine:
    def __init__(self, allowed_paths: List[str], forbidden_paths: List[str], approval_required_paths: List[str]):
        self.allowed_paths = allowed_paths
        self.forbidden_paths = forbidden_paths
        self.approval_required_paths = approval_required_paths

    def _matches_any(self, path: str, patterns: List[str]) -> bool:
        for pattern in patterns:
            if fnmatch(path, pattern) or fnmatch(path, pattern + "/*"):
                return True
        return False

    def evaluate_action(self, action: AgentAction) -> PolicyDecision:
        target = action.target
        
        if self._matches_any(target, self.forbidden_paths):
            return PolicyDecision(
                decision=PolicyDecisionType.DENY,
                reason=f"Path {target} is explicitly forbidden.",
                policy_identifier="forbidden_paths"
            )
            
        if self._matches_any(target, self.approval_required_paths):
            return PolicyDecision(
                decision=PolicyDecisionType.REQUIRE_APPROVAL,
                reason=f"Path {target} requires explicit human approval.",
                policy_identifier="approval_required_paths"
            )
            
        if self._matches_any(target, self.allowed_paths):
            return PolicyDecision(
                decision=PolicyDecisionType.ALLOW,
                reason=f"Path {target} is allowed.",
                policy_identifier="allowed_paths"
            )
            
        return PolicyDecision(
            decision=PolicyDecisionType.DENY,
            reason=f"Path {target} did not match any allowed paths.",
            policy_identifier="default_deny"
        )
