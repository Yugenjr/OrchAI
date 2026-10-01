import os

# 1. Update models.py
models_path = 'src/orchai/core/models.py'
with open(models_path, 'r', encoding='utf-8') as f:
    models_content = f.read()

new_models = '''
class AgentSessionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"

class AgentSession(BaseModel):
    id: str
    task_id: str
    adapter: str
    runtime: str
    external_session_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    status: AgentSessionStatus = AgentSessionStatus.ACTIVE
    attempt_ids: List[str] = Field(default_factory=list)

class DeveloperFeedback(BaseModel):
    id: str
    task_id: str
    attempt_id: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
'''

# We need to replace TaskAttempt if it already exists, or redefine it.
# Let's replace the TaskAttempt class completely.

import re

task_attempt_pattern = re.compile(r'class TaskAttempt\(BaseModel\):.*?review_result: Optional\[str\] = None\n', re.DOTALL)
new_task_attempt = '''class TaskAttempt(BaseModel):
    attempt_id: str
    task_id: str
    attempt_number: int
    session_id: str
    execution_id: str
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    objective: str
    developer_feedback: Optional[str] = None
    agent_result: Optional[AgentExecutionReport] = None
    verification_result: Optional[VerificationResult] = None
    reconciliation_result: Optional[ReconciledExecutionResult] = None
    review_result: Optional[str] = None
'''

if "AgentSession" not in models_content:
    if task_attempt_pattern.search(models_content):
        models_content = task_attempt_pattern.sub(new_task_attempt, models_content)
        models_content += "\n" + new_models
    else:
        models_content += "\n" + new_task_attempt + "\n" + new_models

    with open(models_path, 'w', encoding='utf-8') as f:
        f.write(models_content)

# 2. Update base adapter interface
adapter_path = 'src/orchai/adapters/base.py'
with open(adapter_path, 'r', encoding='utf-8') as f:
    adapter_content = f.read()

if "supports_session_resume" not in adapter_content:
    new_adapter_methods = '''
    def supports_session_resume(self) -> bool:
        return False
        
    def resume_session(self, session_id: str, context: str) -> AgentExecutionReport:
        raise NotImplementedError
'''
    adapter_content += new_adapter_methods
    with open(adapter_path, 'w', encoding='utf-8') as f:
        f.write(adapter_content)

# 3. Update antigravity adapter
antigravity_path = 'src/orchai/adapters/antigravity.py'
if os.path.exists(antigravity_path):
    with open(antigravity_path, 'r', encoding='utf-8') as f:
        anti_content = f.read()
    
    if "supports_session_resume" not in anti_content:
        anti_patch = '''
    def supports_session_resume(self) -> bool:
        return ANTIGRAVITY_SDK_AVAILABLE
        
    def resume_session(self, session_id: str, context: str) -> AgentExecutionReport:
        # Placeholder for actual session resumption, if unsupported:
        if not ANTIGRAVITY_SDK_AVAILABLE:
            raise Exception("SESSION_RESUME_UNAVAILABLE")
        # For MVP mockup:
        return AgentExecutionReport(
            task_id="mock",
            summary="Resumed",
            status="completed",
            final_message="Resumed"
        )
'''
        # Inject it into AntigravitySDKAdapter
        sdk_adapter_idx = anti_content.find('class AntigravitySDKAdapter')
        if sdk_adapter_idx != -1:
            exec_idx = anti_content.find('def execute', sdk_adapter_idx)
            if exec_idx != -1:
                # Find end of execute method
                next_def_idx = anti_content.find('def ', exec_idx + 1)
                if next_def_idx != -1:
                    anti_content = anti_content[:next_def_idx] + anti_patch + anti_content[next_def_idx:]
                else:
                    anti_content += anti_patch
            with open(antigravity_path, 'w', encoding='utf-8') as f:
                f.write(anti_content)

print("Phase 7 models and adapters scaffolded.")
