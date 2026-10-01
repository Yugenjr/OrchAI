from fnmatch import fnmatch
from typing import List
from orchai.core.models import ScopeComparisonResult

class ScopeComparator:
    @staticmethod
    def _matches_any(path: str, patterns: List[str]) -> bool:
        # Normalize to forward slashes for matching
        path = path.replace("\\", "/")
        for pattern in patterns:
            # Match directly or as a directory prefix
            if fnmatch(path, pattern) or fnmatch(path, pattern + "/*"):
                return True
        return False

    @staticmethod
    def compare(expected_paths: List[str], actual_paths: List[str]) -> ScopeComparisonResult:
        unexpected = []
        for path in actual_paths:
            if not ScopeComparator._matches_any(path, expected_paths):
                unexpected.append(path)
                
        # To strictly enforce missing changes, we'd need to know if an expected glob 
        # MUST match something. For MVP, we'll leave missing empty unless implemented explicitly.
        missing = []
        
        return ScopeComparisonResult(
            expected_files=expected_paths,
            actual_files=actual_paths,
            unexpected_changes=unexpected,
            missing_expected_changes=missing,
            compliant=len(unexpected) == 0
        )
