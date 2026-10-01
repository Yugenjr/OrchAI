import hashlib
import secrets
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, List, Dict
from orchai.auth.models import ApiCredential

class CredentialManager:
    def __init__(self, storage_dir: str = ".orchai/auth"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.credentials_file = self.storage_dir / "credentials.json"
        if not self.credentials_file.exists():
            with open(self.credentials_file, "w") as f:
                json.dump([], f)

    def _hash_token(self, token: str) -> str:
        # Use simple SHA-256 for MVP. In prod use Argon2/bcrypt
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def _read_creds(self) -> List[ApiCredential]:
        with open(self.credentials_file, "r") as f:
            data = json.load(f)
        return [ApiCredential(**c) for c in data]

    def _write_creds(self, creds: List[ApiCredential]):
        with open(self.credentials_file, "w") as f:
            json.dump([c.model_dump(mode='json') for c in creds], f, indent=2)

    def generate(self, user_id: str, tenant_id: str, expires_at: Optional[datetime] = None) -> tuple[ApiCredential, str]:
        raw_token = f"orchai_{secrets.token_urlsafe(32)}"
        token_hash = self._hash_token(raw_token)
        
        cred = ApiCredential(
            user_id=user_id,
            tenant_id=tenant_id,
            token_hash=token_hash,
            expires_at=expires_at
        )
        
        creds = self._read_creds()
        creds.append(cred)
        self._write_creds(creds)
        
        return cred, raw_token

    def verify(self, raw_token: str) -> Optional[ApiCredential]:
        token_hash = self._hash_token(raw_token)
        creds = self._read_creds()
        
        for cred in creds:
            if cred.token_hash == token_hash:
                if cred.status != "ACTIVE":
                    return None
                if cred.expires_at and cred.expires_at < datetime.utcnow(): # simplified timezone handling for mock
                    return None
                
                # Update last used
                cred.last_used_at = datetime.utcnow()
                self._write_creds(creds)
                return cred
        return None

    def revoke(self, credential_id: str):
        creds = self._read_creds()
        for cred in creds:
            if cred.credential_id == credential_id:
                cred.status = "REVOKED"
                cred.revoked_at = datetime.utcnow()
                self._write_creds(creds)
                return True
        return False
        
    def list_user_credentials(self, user_id: str) -> List[ApiCredential]:
        return [c for c in self._read_creds() if c.user_id == user_id]
