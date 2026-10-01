from typing import Dict
from collections import defaultdict
import time
import threading

class MetricsStore:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(MetricsStore, cls).__new__(cls)
                cls._instance._init()
            return cls._instance
            
    def _init(self):
        self.counters: Dict[str, int] = defaultdict(int)
        self.histograms: Dict[str, list] = defaultdict(list)
        
    def increment(self, name: str, value: int = 1):
        with self._lock:
            self.counters[name] += value
            
    def observe(self, name: str, value: float):
        with self._lock:
            self.histograms[name].append(value)
            
    def get_metrics(self) -> Dict[str, any]:
        with self._lock:
            return {
                "counters": dict(self.counters),
                "histograms": {k: {"count": len(v), "sum": sum(v), "avg": sum(v)/len(v) if v else 0} for k, v in self.histograms.items()}
            }
            
    def format_prometheus(self) -> str:
        lines = []
        with self._lock:
            for k, v in self.counters.items():
                lines.append(f"# TYPE {k} counter")
                lines.append(f"{k} {v}")
                
            for k, v in self.histograms.items():
                lines.append(f"# TYPE {k} summary")
                lines.append(f"{k}_count {len(v)}")
                lines.append(f"{k}_sum {sum(v)}")
        return "\n".join(lines) + "\n"
