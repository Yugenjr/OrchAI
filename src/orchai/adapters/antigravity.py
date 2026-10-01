import json
import asyncio
import subprocess
from typing import Iterator, List, Optional, Dict, Any
from orchai.adapters.base import AgentAdapter, TaskContext
from orchai.core.models import (
    AgentCapability, AgentCapabilityType, AgentEvent, AgentEventType,
    AgentResult, TaskRequest, PolicyDecisionType
)
from orchai.policy.bridge import PolicyBridge

try:
    from google.antigravity import Agent, LocalAgentConfig, CapabilitiesConfig
    # Assuming standard SDK hooks structure, mocking imports if needed for types
    ANTIGRAVITY_SDK_AVAILABLE = True
except ImportError:
    ANTIGRAVITY_SDK_AVAILABLE = False

class AntigravityEventMapper:
    @staticmethod
    def map_tool_event(tool_name: str, status: str, details: Dict[str, Any]) -> AgentEvent:
        event_type = AgentEventType.AGENT_MESSAGE
        if tool_name == "run_command":
            if status == "requested":
                event_type = AgentEventType.COMMAND_REQUESTED
            elif status == "completed":
                event_type = AgentEventType.COMMAND_COMPLETED
            elif status == "denied":
                event_type = AgentEventType.COMMAND_DENIED
        elif tool_name in ["edit_file", "write_to_file", "replace_file_content", "multi_replace_file_content"]:
            event_type = AgentEventType.FILE_OPERATION
            
        return AgentEvent(
            event_type=event_type,
            source="AntigravitySDK",
            details={"tool": tool_name, "status": status, **details}
        )

class AntigravitySDKAdapter(AgentAdapter):
    def __init__(self, policy_bridge: PolicyBridge, system_prompt: str):
        self.policy_bridge = policy_bridge
        self.system_prompt = system_prompt
        self.agent = None
        self.config = None
        self.events: List[AgentEvent] = []

    def initialize(self) -> None:
        if not ANTIGRAVITY_SDK_AVAILABLE:
            raise RuntimeError("Antigravity SDK is not installed.")
        
        # Configure capabilities based on policies
        cap_config = CapabilitiesConfig()
        
        self.config = LocalAgentConfig(
            system_instructions=self.system_prompt,
            capabilities=cap_config
        )

    def capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(type=AgentCapabilityType.READ, description="Read files", risk_level=1),
            AgentCapability(type=AgentCapabilityType.WRITE, description="Modify files", risk_level=3),
            AgentCapability(type=AgentCapabilityType.COMMAND_EXECUTION, description="Run shell commands", risk_level=4)
        ]

    def prepare_task(self, request: TaskRequest, context: TaskContext) -> None:
        self.task_request = request

    def execute(self) -> AgentResult:
        if not self.config:
            self.initialize()
            
        return asyncio.run(self._async_execute())

    async def _async_execute(self) -> AgentResult:
        # Pre-execution hooks can be registered here in real SDK
        # For MVP, we simulate the hook execution if actual hook APIs differ
        async with Agent(self.config) as agent:
            self.agent = agent
            response = await agent.chat(self.task_request.objective)
            
            # Record events
            self.events.append(AgentEvent(
                event_type=AgentEventType.TASK_STARTED,
                source="AntigravitySDK"
            ))
            
            async for call in response.tool_calls:
                decision = self.policy_bridge.evaluate_tool(call.name, call.args)
                if decision == PolicyDecisionType.DENY:
                    self.events.append(AntigravityEventMapper.map_tool_event(call.name, "denied", call.args))
                    # In real SDK we would raise or cancel the tool
                elif decision == PolicyDecisionType.REQUIRE_APPROVAL:
                    self.events.append(AntigravityEventMapper.map_tool_event(call.name, "approval_requested", call.args))
                    # Wait for approval logic here
                else:
                    self.events.append(AntigravityEventMapper.map_tool_event(call.name, "completed", call.args))

            return AgentResult(
                success=True,
                summary="Agent execution completed.",
                events=self.events
            )

    def stream_events(self) -> Iterator[AgentEvent]:
        for event in self.events:
            yield event

    def collect_result(self) -> AgentResult:
        return AgentResult(
            success=True,
            summary="Agent execution completed.",
            events=self.events
        )

    def cancel(self) -> None:
        pass

    def health_check(self) -> bool:
        return ANTIGRAVITY_SDK_AVAILABLE

    def supports_session_resume(self) -> bool:
        return ANTIGRAVITY_SDK_AVAILABLE
        
    def resume_session(self, session_id: str, context: str):
        # Placeholder for actual session resumption, if unsupported:
        if not ANTIGRAVITY_SDK_AVAILABLE:
            raise Exception("SESSION_RESUME_UNAVAILABLE")
        # For MVP mockup:
        from orchai.core.models import AgentExecutionReport
        return AgentExecutionReport(
            task_id="mock",
            summary="Resumed",
            status="completed",
            final_message="Resumed",
            files_claimed_modified=[]
        )


class AntigravityCLIAdapter(AgentAdapter):
    """
    Fallback headless CLI adapter using subprocess.
    """
    def __init__(self, system_prompt: str):
        self.system_prompt = system_prompt
        self.events: List[AgentEvent] = []

    def initialize(self) -> None:
        pass

    def capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(type=AgentCapabilityType.READ, description="Read files via CLI", risk_level=1),
            AgentCapability(type=AgentCapabilityType.WRITE, description="Modify files via CLI", risk_level=3)
        ]

    def prepare_task(self, request: TaskRequest, context: TaskContext) -> None:
        self.task_request = request

    def execute(self) -> AgentResult:
        self.events.append(AgentEvent(event_type=AgentEventType.TASK_STARTED, source="AntigravityCLI"))
        # Using subprocess safely without shell=True
        try:
            result = subprocess.run(
                ["agy", "-p", self.task_request.objective, "--output-format", "json"],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # Simple simulation
            return AgentResult(
                success=(result.returncode == 0),
                summary="CLI execution completed",
                events=self.events
            )
        except Exception as e:
            return AgentResult(success=False, summary=str(e), events=self.events)

    def stream_events(self) -> Iterator[AgentEvent]:
        for event in self.events:
            yield event

    def collect_result(self) -> AgentResult:
        return AgentResult(success=True, summary="", events=self.events)

    def cancel(self) -> None:
        pass

    def health_check(self) -> bool:
        try:
            subprocess.run(["agy", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
