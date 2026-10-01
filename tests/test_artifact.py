import pytest
from orchai.core.artifact import ArtifactMetadata

def test_artifact_metadata_generation():
    meta = ArtifactMetadata.generate()
    assert meta.version != ""
    assert meta.python_version != ""
    assert meta.platform != ""
    # Ensure native antigravity status remains explicitly UNVERIFIED
    assert meta.capabilities.native_antigravity == "UNSUPPORTED/UNVERIFIED"

def test_secret_redaction_in_artifact():
    meta = ArtifactMetadata.generate()
    d = meta.to_safe_dict()
    # Check for absence of secrets
    assert "token" not in str(d).lower()
    assert "secret" not in str(d).lower()

def test_deterministic_test_metrics():
    meta = ArtifactMetadata.generate()
    assert meta.test_metrics.total >= 168
    assert meta.test_metrics.blocked_skipped == 7
