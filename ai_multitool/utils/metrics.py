"""Metrics collection and monitoring for usage analytics."""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict

from ai_multitool.core.exceptions import MetricsError, ValidationError
from ai_multitool.constants import DEFAULT_MAX_METRICS
from ai_multitool.utils.validation import is_empty_string


@dataclass
class APICallMetrics:
    """Metrics for a single API call."""
    timestamp: str
    provider: str
    model: str
    command: str  # chat, analyze, etc.
    tokens_used: int
    latency_ms: float
    cached: bool
    success: bool
    error_message: Optional[str] = None

    def __str__(self) -> str:
        """String representation."""
        status = "SUCCESS" if self.success else "FAILED"
        return f"APICallMetrics({self.provider}/{self.model}, {self.command}, {status}, {self.tokens_used} tokens, {self.latency_ms:.2f}ms)"

    def __repr__(self) -> str:
        """Detailed representation."""
        return (f"APICallMetrics(timestamp={self.timestamp}, provider={self.provider}, "
                f"model={self.model}, command={self.command}, tokens_used={self.tokens_used}, "
                f"latency_ms={self.latency_ms}, cached={self.cached}, success={self.success})")


@dataclass
class UsageStats:
    """Aggregated usage statistics."""
    total_calls: int
    successful_calls: int
    failed_calls: int
    total_tokens: int
    total_latency_ms: float
    avg_latency_ms: float
    cache_hits: int
    cache_misses: int
    by_provider: Dict[str, int]
    by_model: Dict[str, int]
    by_command: Dict[str, int]

    def __str__(self) -> str:
        """String representation."""
        success_rate = (self.successful_calls / self.total_calls * 100) if self.total_calls > 0 else 0
        return (f"UsageStats(calls={self.total_calls}, success_rate={success_rate:.1f}%, "
                f"tokens={self.total_tokens}, avg_latency={self.avg_latency_ms:.2f}ms)")

    def __repr__(self) -> str:
        """Detailed representation."""
        return (f"UsageStats(total_calls={self.total_calls}, successful_calls={self.successful_calls}, "
                f"failed_calls={self.failed_calls}, total_tokens={self.total_tokens}, "
                f"avg_latency_ms={self.avg_latency_ms:.2f}, cache_hits={self.cache_hits}, "
                f"cache_misses={self.cache_misses})")


class MetricsCollector:
    """Collect and track usage metrics."""
    
    def __init__(self, metrics_file: str = None, max_metrics: int = None):
        """Initialize the metrics collector.
        
        Args:
            metrics_file: Path to metrics file
            max_metrics: Maximum number of metrics to keep (default: from constants)
        """
        if max_metrics is None:
            max_metrics = DEFAULT_MAX_METRICS
        
        if metrics_file is None:
            # Default to ~/.ai-multitool/metrics.json
            home_dir = Path.home()
            metrics_dir = home_dir / ".ai-multitool"
            metrics_dir.mkdir(exist_ok=True)
            metrics_file = metrics_dir / "metrics.json"
        
        self.metrics_file = Path(metrics_file)
        self.max_metrics = max_metrics
        self.metrics: List[APICallMetrics] = []
        self._load_metrics()
    
    def _load_metrics(self):
        """Load metrics from file."""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r') as f:
                    data = json.load(f)
                    self.metrics = [APICallMetrics(**m) for m in data]
            except json.JSONDecodeError as e:
                raise MetricsError(
                    f"Metrics file is corrupted or invalid JSON",
                    file_path=str(self.metrics_file),
                    details={"error": str(e)},
                    suggestion="Delete the metrics file and it will be recreated"
                )
            except Exception as e:
                raise MetricsError(
                    f"Failed to load metrics file",
                    file_path=str(self.metrics_file),
                    details={"error_type": type(e).__name__, "error": str(e)}
                )
    
    def _save_metrics(self):
        """Save metrics to file."""
        try:
            # Ensure parent directory exists
            self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.metrics_file, 'w') as f:
                json.dump([asdict(m) for m in self.metrics], f, indent=2)
        except PermissionError as e:
            raise MetricsError(
                f"Permission denied when saving metrics",
                file_path=str(self.metrics_file),
                details={"error": str(e)},
                suggestion="Check write permissions for the metrics directory"
            )
        except Exception as e:
            raise MetricsError(
                f"Failed to save metrics file",
                file_path=str(self.metrics_file),
                details={"error_type": type(e).__name__, "error": str(e)}
            )
    
    def record_call(
        self,
        provider: str,
        model: str,
        command: str,
        tokens_used: int,
        latency_ms: float,
        cached: bool,
        success: bool = True,
        error_message: Optional[str] = None
    ):
        """Record an API call."""
        if is_empty_string(provider):
            raise ValidationError("Provider cannot be empty", field="provider")
        
        if is_empty_string(model):
            raise ValidationError("Model cannot be empty", field="model")
        
        if is_empty_string(command):
            raise ValidationError("Command cannot be empty", field="command")
        
        if tokens_used < 0:
            raise ValidationError("Tokens used must be non-negative", field="tokens_used")
        
        if latency_ms < 0:
            raise ValidationError("Latency must be non-negative", field="latency_ms")
        
        try:
            metric = APICallMetrics(
                timestamp=datetime.now().isoformat(),
                provider=provider,
                model=model,
                command=command,
                tokens_used=tokens_used,
                latency_ms=latency_ms,
                cached=cached,
                success=success,
                error_message=error_message
            )
            self.metrics.append(metric)
            
            # Enforce max limit to prevent unbounded memory growth
            if len(self.metrics) > self.max_metrics:
                self.metrics = self.metrics[-self.max_metrics:]
            
            self._save_metrics()
        except (MetricsError, ValidationError):
            raise
        except Exception as e:
            raise MetricsError(
                f"Failed to record API call",
                details={"error_type": type(e).__name__, "error": str(e)}
            )
    
    def get_stats(self, days: int = 30) -> UsageStats:
        """Get aggregated usage statistics."""
        if days < 1 or days > 365:
            raise ValidationError("Days must be between 1 and 365", field="days")
        
        try:
            # Filter metrics by date range
            cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
            recent_metrics = [
                m for m in self.metrics
                if datetime.fromisoformat(m.timestamp).timestamp() > cutoff
            ]
        except ValueError as e:
            raise MetricsError(
                f"Failed to parse timestamp in metrics",
                details={"error": str(e)},
                suggestion="Metrics file may be corrupted"
            )
        
        if not recent_metrics:
            return UsageStats(
                total_calls=0,
                successful_calls=0,
                failed_calls=0,
                total_tokens=0,
                total_latency_ms=0,
                avg_latency_ms=0,
                cache_hits=0,
                cache_misses=0,
                by_provider={},
                by_model={},
                by_command={}
            )
        
        total_calls = len(recent_metrics)
        successful_calls = sum(1 for m in recent_metrics if m.success)
        failed_calls = total_calls - successful_calls
        total_tokens = sum(m.tokens_used for m in recent_metrics)
        total_latency = sum(m.latency_ms for m in recent_metrics)
        avg_latency = total_latency / total_calls
        cache_hits = sum(1 for m in recent_metrics if m.cached)
        cache_misses = total_calls - cache_hits
        
        by_provider = defaultdict(int)
        by_model = defaultdict(int)
        by_command = defaultdict(int)
        
        for m in recent_metrics:
            by_provider[m.provider] += 1
            by_model[m.model] += 1
            by_command[m.command] += 1
        
        return UsageStats(
            total_calls=total_calls,
            successful_calls=successful_calls,
            failed_calls=failed_calls,
            total_tokens=total_tokens,
            total_latency_ms=total_latency,
            avg_latency_ms=avg_latency,
            cache_hits=cache_hits,
            cache_misses=cache_misses,
            by_provider=dict(by_provider),
            by_model=dict(by_model),
            by_command=dict(by_command)
        )
    
    def get_recent_calls(self, limit: int = 10) -> List[APICallMetrics]:
        """Get recent API calls."""
        return self.metrics[-limit:][::-1]  # Last N calls, reversed
    
    def clear_metrics(self):
        """Clear all metrics."""
        self.metrics = []
        self._save_metrics()
    
    def export_metrics(self, output_file: str):
        """Export metrics to a file."""
        if is_empty_string(output_file):
            raise ValidationError("Output file path cannot be empty", field="output_file")
        
        output_path = Path(output_file)
        
        try:
            # Ensure parent directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w') as f:
                json.dump([asdict(m) for m in self.metrics], f, indent=2)
            return True
        except PermissionError as e:
            raise MetricsError(
                f"Permission denied when exporting metrics",
                file_path=str(output_path),
                details={"error": str(e)},
                suggestion="Check write permissions for the output directory"
            )
        except Exception as e:
            raise MetricsError(
                f"Failed to export metrics",
                file_path=str(output_path),
                details={"error_type": type(e).__name__, "error": str(e)}
            )


class MetricsContext:
    """Context manager for timing and recording API calls."""
    
    def __init__(self, collector: MetricsCollector, provider: str, model: str, command: str):
        """Initialize the metrics context."""
        self.collector = collector
        self.provider = provider
        self.model = model
        self.command = command
        self.start_time = None
        self.success = True
        self.error_message = None
        self.tokens_used = 0
        self.cached = False
    
    def __enter__(self):
        """Start timing."""
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End timing and record metrics."""
        if exc_type is not None:
            self.success = False
            self.error_message = str(exc_val)
        
        latency_ms = (time.time() - self.start_time) * 1000 if self.start_time else 0
        
        self.collector.record_call(
            provider=self.provider,
            model=self.model,
            command=self.command,
            tokens_used=self.tokens_used,
            latency_ms=latency_ms,
            cached=self.cached,
            success=self.success,
            error_message=self.error_message
        )
        return False  # Don't suppress exceptions


# Singleton instance
_metrics_collector_instance: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Get the singleton metrics collector instance."""
    global _metrics_collector_instance
    if _metrics_collector_instance is None:
        _metrics_collector_instance = MetricsCollector()
    return _metrics_collector_instance
