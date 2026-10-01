import os

models_path = 'src/orchai/core/models.py'
with open(models_path, 'r', encoding='utf-8') as f:
    content = f.read()

new_models = '''
class CapabilityStatus(str, Enum):
    IMPLEMENTED = "IMPLEMENTED"
    MOCK_VERIFIED = "MOCK_VERIFIED"
    RUNTIME_VERIFIED = "RUNTIME_VERIFIED"
    UNVERIFIED = "UNVERIFIED"
    UNSUPPORTED = "UNSUPPORTED"
    BLOCKED = "BLOCKED"

class RuntimeCapability(BaseModel):
    name: str
    status: CapabilityStatus
    source: str
    verified_at: Optional[datetime] = None
    evidence: Optional[str] = None
    limitations: Optional[str] = None

class AuthenticationConfig(BaseModel):
    provider: str
    runtime: str
    credential_source: str
    configured: bool
    validated: bool
    last_validated_at: Optional[datetime] = None
    
    # Never persist secrets. Only metadata.
    
class RuntimeTestResult(BaseModel):
    test_id: str
    test_name: str
    status: CapabilityStatus
    runtime: str
    adapter: str
    authentication_status: str
    before_sha: Optional[str] = None
    after_sha: Optional[str] = None
    expected_scope: List[str] = Field(default_factory=list)
    actual_scope: List[str] = Field(default_factory=list)
    agent_claim: Optional[str] = None
    events: List[AgentEvent] = Field(default_factory=list)
    verification: Optional[VerificationResult] = None
    reconciliation: Optional[ReconciledExecutionResult] = None
    evidence: Optional[str] = None
    limitations: Optional[str] = None
'''

if "CapabilityStatus" not in content:
    with open(models_path, 'a', encoding='utf-8') as f:
        f.write(new_models)
        
print("Models updated.")
