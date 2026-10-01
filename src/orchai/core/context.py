import json
from typing import List, Optional
from orchai.core.models import Task, RepositorySnapshot

from orchai.core.models import Task, RepositorySnapshot, MemoryEntry

class OrchAIContextCompiler:
    def compile_prompt(
        self,
        task: Task,
        snapshot: Optional[RepositorySnapshot],
        architectural_constraints: List[str],
        relevant_memories: Optional[List[MemoryEntry]] = None
    ) -> str:
        """
        Compiles the agent prompt with selective context and persistent memory.
        """
        prompt_parts = []
        
        prompt_parts.append("You are the execution agent managed by OrchAI.")
        prompt_parts.append(f"\nOBJECTIVE:\n{task.title}\n{task.description}")
        
        if relevant_memories:
            prompt_parts.append("\nENGINEERING DECISIONS & MEMORY:")
            for m in relevant_memories:
                prompt_parts.append(f"[{m.type.value}] {m.title}: {m.content}")
        
        if snapshot:
            prompt_parts.append("\nPROJECT CONTEXT:")
            prompt_parts.append(f"Branch: {snapshot.branch}")
            # Do not dump all tracked files, just give a summary or top-level.
            # In a real app we would use selective fetching.
            prompt_parts.append(f"Tracked files count: {len(snapshot.tracked_files)}")
            
        prompt_parts.append(f"\nEXPECTED CHANGE SCOPE:")
        if task.expected_scope:
            prompt_parts.append(json.dumps(task.expected_scope, indent=2))
        else:
            prompt_parts.append("No specific files expected to change.")
            
        if architectural_constraints:
            prompt_parts.append("\nARCHITECTURAL CONSTRAINTS:")
            for constraint in architectural_constraints:
                prompt_parts.append(f"- {constraint}")
                
        prompt_parts.append("\nFORBIDDEN PATHS:")
        prompt_parts.append("Do not modify anything outside the expected scope.")
        
        prompt_parts.append("\nVERIFICATION REQUIREMENTS:")
        prompt_parts.append("Your changes will be verified independently by OrchAI observing Git. Do not fake file writes.")
        
        prompt_parts.append("\nREPORT FORMAT:")
        prompt_parts.append("At completion produce a structured execution report in JSON matching the requested schema, or in plain text if structured output fails.")
        
        return "\n".join(prompt_parts)
