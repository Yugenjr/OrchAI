import os
import subprocess
import sys
import shutil
from pathlib import Path

def run_cmd(cmd, check=True):
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, text=True, capture_output=True)
    if check and result.returncode != 0:
        print(f"FAILED: {result.stderr}")
        sys.exit(1)
    return result.stdout

def main():
    root = Path(__file__).parent.parent
    os.chdir(root)
    
    print("1. Installing dependencies...")
    run_cmd([sys.executable, "-m", "pip", "install", "build", "pytest"])
    
    print("2. Running complete test suite...")
    run_cmd([sys.executable, "-m", "pytest", "tests/"])
    
    print("3. Building wheel/sdist...")
    # Clean previous builds
    if (root / "dist").exists():
        shutil.rmtree(root / "dist")
    run_cmd([sys.executable, "-m", "build"])
    
    print("4. Clean installation smoke test...")
    venv_dir = root / "temp_release_venv"
    if venv_dir.exists():
        shutil.rmtree(venv_dir)
        
    run_cmd([sys.executable, "-m", "venv", str(venv_dir)])
    
    if sys.platform == "win32":
        pip_exe = venv_dir / "Scripts" / "pip.exe"
        orchai_exe = venv_dir / "Scripts" / "orchai.exe"
        python_exe = venv_dir / "Scripts" / "python.exe"
    else:
        pip_exe = venv_dir / "bin" / "pip"
        orchai_exe = venv_dir / "bin" / "orchai"
        python_exe = venv_dir / "bin" / "python"
        
    whl_files = list((root / "dist").glob("*.whl"))
    if not whl_files:
        print("No wheel file generated!")
        sys.exit(1)
        
    run_cmd([str(pip_exe), "install", str(whl_files[0])])
    
    print("5. CLI Smoke Test...")
    run_cmd([str(orchai_exe), "--help"])
    out = run_cmd([str(orchai_exe), "doctor"])
    print(out)
    
    print("6. Artifact Metadata Validation...")
    out = run_cmd([str(orchai_exe), "artifact", "inspect"])
    print(out)
    if "UNSUPPORTED/UNVERIFIED" not in out:
        print("ERROR: Capability status incorrect in artifact manifest!")
        sys.exit(1)
        
    print("Release validation PASSED.")
    
    # Cleanup
    shutil.rmtree(venv_dir)

if __name__ == "__main__":
    main()
