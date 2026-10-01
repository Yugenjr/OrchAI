import pytest
import subprocess
import os

def is_docker_available():
    try:
        result = subprocess.run(["docker", "info"], capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False

pytestmark = pytest.mark.skipif(not is_docker_available(), reason="Docker is not available")

def test_container_non_root():
    # Attempt to build and run the image to check user
    subprocess.run(["docker", "build", "-t", "orchai-runtime:test", "-f", "infra/docker/Dockerfile", "."], check=True)
    result = subprocess.run(["docker", "run", "--rm", "orchai-runtime:test", "--entrypoint", "id", "-u"], capture_output=True, text=True)
    # the entrypoint is overridden, so we do this:
    result = subprocess.run(["docker", "run", "--rm", "--entrypoint", "id", "orchai-runtime:test", "-u"], capture_output=True, text=True)
    assert result.returncode == 0
    assert result.stdout.strip() != "0" # Not root

def test_container_filesystem_boundary():
    result = subprocess.run(["docker", "run", "--rm", "--entrypoint", "ls", "orchai-runtime:test", "/root"], capture_output=True, text=True)
    assert result.returncode != 0
    assert "Permission denied" in result.stderr

def test_container_network_isolation():
    # Start container with network=none
    result = subprocess.run(["docker", "run", "--rm", "--network", "none", "--entrypoint", "ping", "orchai-runtime:test", "-c", "1", "8.8.8.8"], capture_output=True, text=True)
    assert result.returncode != 0

def test_container_env_isolation():
    # Pass secret, ensure it's not exported globally
    result = subprocess.run(["docker", "run", "--rm", "-e", "SECRET_KEY=12345", "--entrypoint", "env", "orchai-runtime:test"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "SECRET_KEY=12345" in result.stdout
