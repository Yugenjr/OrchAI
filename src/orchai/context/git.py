import subprocess
from typing import List, Optional
from orchai.core.models import RepositorySnapshot

class GitService:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path

    def _run_git(self, args: List[str]) -> str:
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except FileNotFoundError:
            raise RuntimeError("Git executable not found.")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Git command failed: {e.stderr.strip()}")

    def is_repository(self) -> bool:
        try:
            self._run_git(["rev-parse", "--is-inside-work-tree"])
            return True
        except RuntimeError:
            return False

    def current_branch(self) -> str:
        return self._run_git(["rev-parse", "--abbrev-ref", "HEAD"])

    def head_sha(self) -> str:
        try:
            return self._run_git(["rev-parse", "HEAD"])
        except RuntimeError:
            return ""

    def tracked_files(self) -> List[str]:
        output = self._run_git(["ls-files"])
        return [f for f in output.split("\n") if f]

    def staged_files(self) -> List[str]:
        output = self._run_git(["diff", "--name-only", "--cached"])
        return [f for f in output.split("\n") if f]

    def unstaged_files(self) -> List[str]:
        output = self._run_git(["diff", "--name-only"])
        return [f for f in output.split("\n") if f]

    def untracked_files(self) -> List[str]:
        output = self._run_git(["ls-files", "--others", "--exclude-standard"])
        return [f for f in output.split("\n") if f]

    def working_tree_clean(self) -> bool:
        return len(self.staged_files()) == 0 and len(self.unstaged_files()) == 0 and len(self.untracked_files()) == 0

    def changed_files(self) -> List[str]:
        staged = self.staged_files()
        unstaged = self.unstaged_files()
        untracked = self.untracked_files()
        return list(set(staged + unstaged + untracked))

    def snapshot(self) -> RepositorySnapshot:
        if not self.is_repository():
            raise RuntimeError("Not a git repository.")
            
        return RepositorySnapshot(
            head_sha=self.head_sha(),
            branch=self.current_branch(),
            tracked_files=self.tracked_files(),
            staged_files=self.staged_files(),
            unstaged_files=self.unstaged_files(),
            untracked_files=self.untracked_files(),
            working_tree_clean=self.working_tree_clean()
        )
