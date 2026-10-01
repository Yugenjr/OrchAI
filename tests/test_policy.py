from orchai.policy.engine import PathPolicyEngine
from orchai.core.models import AgentAction, AgentActionType, PolicyDecisionType

def test_policy_allow():
    engine = PathPolicyEngine(
        allowed_paths=["src/**"],
        forbidden_paths=[".env"],
        approval_required_paths=["infra/**"]
    )
    action = AgentAction(action_type=AgentActionType.WRITE, target="src/main.py")
    decision = engine.evaluate_action(action)
    assert decision.decision == PolicyDecisionType.ALLOW

def test_policy_deny():
    engine = PathPolicyEngine(
        allowed_paths=["src/**"],
        forbidden_paths=[".env", "secrets/**"],
        approval_required_paths=["infra/**"]
    )
    action = AgentAction(action_type=AgentActionType.READ, target=".env")
    decision = engine.evaluate_action(action)
    assert decision.decision == PolicyDecisionType.DENY
    
    action2 = AgentAction(action_type=AgentActionType.WRITE, target="secrets/key.txt")
    decision2 = engine.evaluate_action(action2)
    assert decision2.decision == PolicyDecisionType.DENY

def test_policy_require_approval():
    engine = PathPolicyEngine(
        allowed_paths=["src/**"],
        forbidden_paths=[".env"],
        approval_required_paths=["infra/**", "database/**"]
    )
    action = AgentAction(action_type=AgentActionType.WRITE, target="database/schema.sql")
    decision = engine.evaluate_action(action)
    assert decision.decision == PolicyDecisionType.REQUIRE_APPROVAL

def test_path_matching():
    engine = PathPolicyEngine(
        allowed_paths=["tests/**"],
        forbidden_paths=[],
        approval_required_paths=[]
    )
    # Tests fnmatch logic explicitly
    action1 = AgentAction(action_type=AgentActionType.WRITE, target="tests/unit/test_main.py")
    assert engine.evaluate_action(action1).decision == PolicyDecisionType.ALLOW
    
    action2 = AgentAction(action_type=AgentActionType.WRITE, target="untracked/file.txt")
    assert engine.evaluate_action(action2).decision == PolicyDecisionType.DENY
