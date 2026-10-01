import sys
import subprocess
from pathlib import Path

def run_cmd(cmd, check=True):
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, text=True, capture_output=True)
    if check and result.returncode != 0:
        print(f"FAILED: {result.stderr}")
        sys.exit(1)
    return result.stdout

def main():
    try:
        run_cmd(["docker", "info"])
    except Exception:
        print("Docker not available. Skipping smoke test.")
        sys.exit(0)

    root = Path(__file__).parent.parent
    print("1. Building container...")
    run_cmd(["docker", "build", "-t", "orchai-runtime:smoke", "-f", "infra/docker/Dockerfile", str(root)])

    print("2. Running orchai doctor in container...")
    out = run_cmd(["docker", "run", "--rm", "orchai-runtime:smoke", "doctor"])
    print(out)
    assert "OrchAI Version" in out

    print("3. Container Smoke Test Passed.")

if __name__ == "__main__":
    main()
