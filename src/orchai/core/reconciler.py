from typing import List, Dict, Any
from orchai.core.models import (
    AgentExecutionReport, 
    RepositorySnapshot,
    VerificationResult,
    ReconciledExecutionResult,
    ExecutionRecord
)

class ExecutionReconciler:
    def reconcile(
        self, 
        report: AgentExecutionReport, 
        git_diff_files: List[str], 
        verification: VerificationResult,
        execution_record: ExecutionRecord
    ) -> ReconciledExecutionResult:
        """
        Reconciles the agent's claim with Git evidence and verification result.
        """
        claimed_files = set(report.files_claimed_modified)
        observed_files = set(git_diff_files)
        
        agent_claim_matches = (claimed_files == observed_files)
        unexpected_changes = list(observed_files - claimed_files)
        
        return ReconciledExecutionResult(
            agent_claim_matches_repository=agent_claim_matches,
            unexpected_changes=unexpected_changes,
            execution_record=execution_record,
            report=report
        )
