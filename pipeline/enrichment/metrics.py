"""Thread-safe per-run metrics collector."""
import time
from threading import Lock


class Metrics:
    __slots__ = (
        "ok", "skipped", "failed", "retried",
        "network_errors", "parse_errors", "structural_errors", "cache_hits",
        "_lock", "_start",
    )

    def __init__(self) -> None:
        for s in self.__slots__[:-2]:
            object.__setattr__(self, s, 0)
        object.__setattr__(self, "_lock", Lock())
        object.__setattr__(self, "_start", time.time())

    def inc(self, **kwargs: int) -> None:
        with self._lock:
            for k, v in kwargs.items():
                object.__setattr__(self, k, getattr(self, k) + v)

    @property
    def total(self) -> int:
        return self.ok + self.skipped + self.failed

    def elapsed_min(self) -> float:
        return (time.time() - self._start) / 60.0

    def throughput(self) -> float:
        el = time.time() - self._start
        return (self.total / el * 60) if el > 0 else 0.0

    def success_rate(self) -> float:
        return (self.ok / self.total * 100) if self.total > 0 else 0.0

    def summary(self) -> dict:
        return {
            "total":              self.total,
            "ok":                 self.ok,
            "skipped":            self.skipped,
            "failed":             self.failed,
            "retried":            self.retried,
            "network_errors":     self.network_errors,
            "parse_errors":       self.parse_errors,
            "structural_errors":  self.structural_errors,
            "cache_hits":         self.cache_hits,
            "elapsed_min":        round(self.elapsed_min(), 1),
            "success_rate_pct":   round(self.success_rate(), 1),
            "throughput_per_min": round(self.throughput(), 1),
        }
