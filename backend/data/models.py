"""
Data Models
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List
from uuid import UUID, uuid4

class RiskLevel(str, Enum):
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class CommandAction(str, Enum):
    EXECUTED = "executed"
    APPROVED = "approved"
    SAFE_SWAP = "safe_swap"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"

@dataclass
class CommandBreakdown:
    part: str
    meaning: str
    risk_contribution: str

@dataclass
class RiskAnalysis:
    risk_level: RiskLevel
    risk_score: int
    allow: bool
    title: str
    explanation: str
    consequences: List[str]
    safer_alternative: Optional[str]
    alternative_explanation: Optional[str]
    data_loss_risk: int
    service_impact_risk: int
    reversibility: int
    requires_sudo: bool
    affected_scope: str
    command_breakdown: List[CommandBreakdown]
    analysis_source: str
    model_used: Optional[str]
    tokens_used: int = 0
    analysis_latency_ms: int = 0
    
    def to_dict(self) -> dict:
        return {
            "risk_level": self.risk_level.value,
            "risk_score": self.risk_score,
            "allow": self.allow,
            "title": self.title,
            "explanation": self.explanation,
            "consequences": self.consequences,
            "safer_alternative": self.safer_alternative,
            "alternative_explanation": self.alternative_explanation,
            "data_loss_risk": self.data_loss_risk,
            "service_impact_risk": self.service_impact_risk,
            "reversibility": self.reversibility,
            "requires_sudo": self.requires_sudo,
            "affected_scope": self.affected_scope,
            "command_breakdown": [
                {"part": b.part, "meaning": b.meaning, "risk_contribution": b.risk_contribution}
                for b in self.command_breakdown
            ],
            "analysis_source": self.analysis_source,
            "model_used": self.model_used,
            "tokens_used": self.tokens_used,
            "analysis_latency_ms": self.analysis_latency_ms
        }

@dataclass
class CommandLogEntry:
    id: UUID = field(default_factory=uuid4)
    session_id: UUID = field(default_factory=uuid4)
    command: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    risk_level: RiskLevel = RiskLevel.SAFE
    action: CommandAction = CommandAction.EXECUTED
    analysis: Optional[RiskAnalysis] = None
    alternative_used: Optional[str] = None
    working_directory: str = "~"
    analysis_latency_ms: int = 0

@dataclass
class SessionStats:
    session_id: UUID = field(default_factory=uuid4)
    total_commands: int = 0
    safe_commands: int = 0
    warnings_issued: int = 0
    approved_risky: int = 0
    safe_swaps: int = 0
    cancelled: int = 0
    blocked: int = 0
    total_tokens_used: int = 0
    session_start: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def interception_rate(self) -> float:
        if self.total_commands == 0:
            return 0.0
        return (self.warnings_issued + self.blocked) / self.total_commands * 100
    
    @property
    def safe_swap_rate(self) -> float:
        if self.warnings_issued == 0:
            return 0.0
        return self.safe_swaps / self.warnings_issued * 100
    
    def to_dict(self) -> dict:
        return {
            "total_commands": self.total_commands,
            "safe_commands": self.safe_commands,
            "warnings_issued": self.warnings_issued,
            "approved_risky": self.approved_risky,
            "safe_swaps": self.safe_swaps,
            "cancelled": self.cancelled,
            "blocked": self.blocked,
            "interception_rate": round(self.interception_rate, 1),
            "safe_swap_rate": round(self.safe_swap_rate, 1)
        }

@dataclass
class DangerPattern:
    pattern: str
    is_regex: bool = False
    risk_level: RiskLevel = RiskLevel.HIGH
    category: str = ""
    description: str = ""
    hard_block: bool = False
    block_message: str = ""
