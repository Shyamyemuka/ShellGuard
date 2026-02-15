"""
Metrics and Tracing Setup
"""
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class CommandTrace:
    """Trace for a command analysis"""
    trace_id: str
    command: str
    timestamp: datetime
    risk_level: str
    action: str
    analysis_latency_ms: int
    pattern_matched: Optional[str]
    ai_invoked: bool
    tokens_used: int = 0
    attributes: Dict[str, Any] = field(default_factory=dict)

class Metrics:
    """In-memory metrics tracking"""
    
    def __init__(self):
        self.commands_total: Dict[str, int] = {}
        self.interceptions_total: Dict[str, int] = {}
        self.safe_swaps_total: int = 0
        self.analysis_durations: list[float] = []
        self.tokens_total: int = 0
        self.active_sessions: int = 0
        self.traces: list[CommandTrace] = []
    
    def increment_command(self, risk_level: str, action: str) -> None:
        """Increment command counter"""
        key = f"{risk_level}:{action}"
        self.commands_total[key] = self.commands_total.get(key, 0) + 1
    
    def increment_interception(self, risk_level: str, trigger: str) -> None:
        """Increment interception counter"""
        key = f"{risk_level}:{trigger}"
        self.interceptions_total[key] = self.interceptions_total.get(key, 0) + 1
    
    def record_analysis_duration(self, duration_seconds: float) -> None:
        """Record analysis duration"""
        self.analysis_durations.append(duration_seconds)
        # Keep only last 1000
        if len(self.analysis_durations) > 1000:
            self.analysis_durations = self.analysis_durations[-1000:]
    
    def add_trace(self, trace: CommandTrace) -> None:
        """Add a command trace"""
        self.traces.append(trace)
        # Keep only last 1000
        if len(self.traces) > 1000:
            self.traces = self.traces[-1000:]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""
        total_commands = sum(self.commands_total.values())
        total_interceptions = sum(self.interceptions_total.values())
        
        avg_duration = 0.0
        if self.analysis_durations:
            avg_duration = sum(self.analysis_durations) / len(self.analysis_durations)
        
        return {
            "total_commands": total_commands,
            "total_interceptions": total_interceptions,
            "safe_swaps": self.safe_swaps_total,
            "avg_analysis_duration_ms": int(avg_duration * 1000),
            "tokens_used": self.tokens_total,
            "active_sessions": self.active_sessions
        }

# Global metrics instance
_metrics = Metrics()

def setup_observability() -> None:
    """Initialize observability"""
    print("📊 Observability initialized")

def get_metrics() -> Metrics:
    """Get metrics instance"""
    return _metrics

def track_command(
    command: str,
    risk_level: str,
    action: str,
    latency_ms: int,
    pattern_matched: Optional[str] = None,
    ai_invoked: bool = False,
    tokens_used: int = 0
) -> None:
    """Track a command execution (locally and send to Archestra)"""
    import uuid
    import asyncio
    
    trace_id = str(uuid.uuid4())
    
    trace = CommandTrace(
        trace_id=trace_id,
        command=command[:100],  # Truncate for privacy
        timestamp=datetime.utcnow(),
        risk_level=risk_level,
        action=action,
        analysis_latency_ms=latency_ms,
        pattern_matched=pattern_matched,
        ai_invoked=ai_invoked,
        tokens_used=tokens_used
    )
    
    # Store locally
    _metrics.add_trace(trace)
    _metrics.increment_command(risk_level, action)
    
    if action in ["approved", "safe_swap", "cancelled", "blocked"]:
        _metrics.increment_interception(risk_level, "pattern" if not ai_invoked else "ai")
    
    if action == "safe_swap":
        _metrics.safe_swaps_total += 1
    
    _metrics.record_analysis_duration(latency_ms / 1000)
    _metrics.tokens_total += tokens_used
    
    # Send to Archestra observability (async, non-blocking)
    try:
        from .mcp_client import get_archestra_client
        client = get_archestra_client()
        if client.enabled:
            # Fire and forget - don't block on observability
            asyncio.create_task(
                client.send_trace(
                    trace_id=trace_id,
                    command=command,
                    risk_level=risk_level,
                    action=action,
                    latency_ms=latency_ms,
                    metadata={
                        "timestamp": trace.timestamp.isoformat(),
                        "pattern_matched": pattern_matched,
                        "ai_invoked": ai_invoked,
                        "tokens_used": tokens_used
                    }
                )
            )
    except Exception as e:
        # Don't fail if observability fails
        print(f"⚠️  Archestra observability error: {e}")
