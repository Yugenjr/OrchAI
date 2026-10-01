import pytest
from orchai.auth.credentials import CredentialManager
from datetime import datetime, timedelta

def test_credential_generation_and_hashing(tmp_path):
    mgr = CredentialManager(str(tmp_path))
    cred, raw = mgr.generate("user_1", "tenant_a")
    
    assert cred.credential_id.startswith("cred_")
    assert cred.token_hash != raw
    assert raw.startswith("orchai_")

def test_credential_verification_success(tmp_path):
    mgr = CredentialManager(str(tmp_path))
    _, raw = mgr.generate("user_1", "tenant_a")
    
    verified = mgr.verify(raw)
    assert verified is not None
    assert verified.user_id == "user_1"

def test_credential_verification_invalid(tmp_path):
    mgr = CredentialManager(str(tmp_path))
    mgr.generate("user_1", "tenant_a")
    
    verified = mgr.verify("invalid_token")
    assert verified is None

def test_credential_revocation(tmp_path):
    mgr = CredentialManager(str(tmp_path))
    cred, raw = mgr.generate("user_1", "tenant_a")
    
    mgr.revoke(cred.credential_id)
    verified = mgr.verify(raw)
    assert verified is None

def test_credential_expiration(tmp_path):
    mgr = CredentialManager(str(tmp_path))
    # mock expired token
    cred, raw = mgr.generate("user_1", "tenant_a", expires_at=datetime.utcnow() - timedelta(days=1))
    
    verified = mgr.verify(raw)
    assert verified is None
