from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class Role(str, Enum):
    ADMIN = "ADMIN"
    DEVELOPER = "DEVELOPER"
    OPERATOR = "OPERATOR"
    VIEWER = "VIEWER"
    SERVICE = "SERVICE"

class Permission(str, Enum):
    TASK_CREATE = "TASK_CREATE"
    TASK_READ = "TASK_READ"
    TASK_CANCEL = "TASK_CANCEL"
    TASK_REVIEW = "TASK_REVIEW"
    TASK_APPROVE = "TASK_APPROVE"
    TASK_RESUME = "TASK_RESUME"
    TASK_DELETE = "TASK_DELETE"

    TOOL_EXECUTE = "TOOL_EXECUTE"
    TOOL_APPROVE = "TOOL_APPROVE"

    AUDIT_READ = "AUDIT_READ"
    AUDIT_VERIFY = "AUDIT_VERIFY"

    METRICS_READ = "METRICS_READ"

    RUNTIME_READ = "RUNTIME_READ"
    RUNTIME_EXECUTE = "RUNTIME_EXECUTE"
    RUNTIME_CANCEL = "RUNTIME_CANCEL"

    TENANT_ADMIN = "TENANT_ADMIN"
    USER_ADMIN = "USER_ADMIN"
    
    TENANT_CROSS_READ = "TENANT_CROSS_READ"
    TENANT_CROSS_OPERATE = "TENANT_CROSS_OPERATE"

ROLE_PERMISSIONS = {
    Role.ADMIN: [p for p in Permission],
    Role.DEVELOPER: [
        Permission.TASK_CREATE, Permission.TASK_READ, Permission.TASK_CANCEL,
        Permission.TASK_REVIEW, Permission.TASK_APPROVE, Permission.TASK_RESUME,
        Permission.TOOL_EXECUTE, Permission.TOOL_APPROVE, Permission.AUDIT_READ,
        Permission.RUNTIME_READ, Permission.RUNTIME_EXECUTE, Permission.RUNTIME_CANCEL
    ],
    Role.OPERATOR: [
        Permission.TASK_READ, Permission.TASK_CANCEL, Permission.TASK_RESUME,
        Permission.AUDIT_READ, Permission.METRICS_READ, Permission.RUNTIME_READ,
        Permission.RUNTIME_CANCEL
    ],
    Role.VIEWER: [
        Permission.TASK_READ, Permission.AUDIT_READ, Permission.METRICS_READ,
        Permission.RUNTIME_READ
    ],
    Role.SERVICE: [
        Permission.TASK_CREATE, Permission.TASK_READ, Permission.TASK_CANCEL,
        Permission.TOOL_EXECUTE, Permission.AUDIT_READ, Permission.AUDIT_VERIFY,
        Permission.RUNTIME_READ, Permission.RUNTIME_EXECUTE, Permission.RUNTIME_CANCEL
    ]
}

class Tenant(BaseModel):
    tenant_id: str
    name: str
    status: str = "ACTIVE"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class User(BaseModel):
    user_id: str
    tenant_id: str
    username: str
    display_name: str
    status: str = "ACTIVE"
    roles: List[Role] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ApiCredential(BaseModel):
    credential_id: str = Field(default_factory=lambda: f"cred_{uuid.uuid4().hex}")
    user_id: str
    tenant_id: str
    token_hash: str
    status: str = "ACTIVE"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None

class AuthContext(BaseModel):
    user_id: str
    tenant_id: str
    roles: List[Role]
    permissions: List[Permission]
    credential_id: Optional[str] = None
    
    def has_permission(self, permission: Permission) -> bool:
        return permission in self.permissions
        
    def check_tenant(self, tenant_id: str) -> bool:
        if self.has_permission(Permission.TENANT_CROSS_READ) or self.has_permission(Permission.TENANT_CROSS_OPERATE):
            return True
        return self.tenant_id == tenant_id
