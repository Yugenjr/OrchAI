from abc import ABC, abstractmethod
from orchai.core.models import VerificationResult

class VerificationInterface(ABC):
    @abstractmethod
    def inspect_git_diff(self) -> None:
        pass

    @abstractmethod
    def execute_tests(self) -> None:
        pass

    @abstractmethod
    def generate_result(self) -> VerificationResult:
        pass
