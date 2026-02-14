"""
Pydantic Request/Response Schemas
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class HealthStatus(BaseModel):
    status: str
    timestamp: str
    active_sessions: int

class StatsResponse(BaseModel):
    total_commands: int
    total_interceptions: int
    safe_swap_rate: float
    risk_distribution: dict
    action_distribution: dict

class HistoryEntry(BaseModel):
    id: str
    session_id: str
    command: str
    timestamp: str
    risk_level: str
    action: str
    risk_score: Optional[int]
    risk_title: Optional[str]
    analysis_latency_ms: int

class PaginatedHistory(BaseModel):
    items: List[HistoryEntry]
    limit: int
    offset: int

class DashboardSummary(BaseModel):
    total_commands: int
    total_interceptions: int
    safe_swap_rate: float
    avg_analysis_latency_ms: int
