import asyncio
import os
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid
from orchai.runtime.models import AgentProcessStatus, AgentProcess

class AgentRuntime:
    def __init__(self, command: List[str], task_id: str, attempt_id: str, cwd: Optional[str] = None):
        self.process_id = str(uuid.uuid4())
        self.task_id = task_id
        self.attempt_id = attempt_id
        self.command = command
        self.cwd = cwd or os.getcwd()
        self.process: Optional[asyncio.subprocess.Process] = None
        self.status = AgentProcessStatus.CREATED
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.exit_code: Optional[int] = None
        self.error: Optional[str] = None

    async def start(self) -> AgentProcessStatus:
        self.status = AgentProcessStatus.STARTING
        env = {
            "PATH": os.environ.get("PATH", ""),
            "PYTHONUNBUFFERED": "1"
        }
        if "SystemRoot" in os.environ:
            env["SystemRoot"] = os.environ["SystemRoot"]
        if "SystemDrive" in os.environ:
            env["SystemDrive"] = os.environ["SystemDrive"]
        try:
            self.process = await asyncio.create_subprocess_exec(
                *self.command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.cwd,
                env=env,
                limit=1024*1024 # 1MB limit for streams
            )
            self.status = AgentProcessStatus.RUNNING
            self.started_at = datetime.now(timezone.utc)
            return self.status
        except Exception as e:
            self.status = AgentProcessStatus.FAILED
            self.error = str(e)
            return self.status

    async def send(self, data: bytes):
        if self.process and self.process.stdin:
            self.process.stdin.write(data)
            await self.process.stdin.drain()

    async def receive(self) -> Optional[bytes]:
        if self.process and self.process.stdout:
            try:
                line = await self.process.stdout.readline()
                if len(line) > 1024 * 1024:
                    self.cancel()
                    self.error = "Output size limit exceeded"
                    return None
                return line if line else None
            except Exception:
                return None
        return None

    def cancel(self):
        if self.process and self.status == AgentProcessStatus.RUNNING:
            try:
                self.process.kill() # Hard kill to prevent orphans
            except ProcessLookupError:
                pass
            self.status = AgentProcessStatus.CANCELLED
            self.completed_at = datetime.now(timezone.utc)

    async def wait(self, timeout: Optional[float] = None) -> int:
        if self.process:
            try:
                self.exit_code = await asyncio.wait_for(self.process.wait(), timeout)
                if self.status not in [AgentProcessStatus.CANCELLED, AgentProcessStatus.FAILED]:
                    self.status = AgentProcessStatus.COMPLETED
            except asyncio.TimeoutError:
                self.cancel()
                self.status = AgentProcessStatus.TIMEOUT
            finally:
                self.completed_at = datetime.now(timezone.utc)
        return self.exit_code if self.exit_code is not None else -1

    def get_status(self) -> AgentProcess:
        return AgentProcess(
            process_id=self.process_id,
            task_id=self.task_id,
            attempt_id=self.attempt_id,
            command=self.command,
            status=self.status,
            started_at=self.started_at,
            completed_at=self.completed_at,
            exit_code=self.exit_code,
            error=self.error
        )
