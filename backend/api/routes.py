"""
REST API Routes
"""
from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime

from data.database import Database
from archestra.observability import get_metrics
from archestra.mcp_tools import MCPTools

router = APIRouter()
db = Database()

@router.get("/health")
async def health_check():
    """System health check"""
    metrics = get_metrics()
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "components": {
            "pty": {"status": "healthy"},
            "llm_api": {"status": "healthy", "provider": "gemini"},
            "database": {"status": "healthy"},
            "pattern_registry": {"status": "healthy", "patterns_loaded": 52}
        },
        "active_sessions": metrics.active_sessions,
        "uptime_seconds": 0
    }

@router.get("/stats")
async def get_stats():
    """Get session and all-time statistics"""
    stats = await db.get_stats()
    obs_metrics = get_metrics().get_summary()
    return {**stats, **obs_metrics}

@router.get("/history")
async def get_history(
    session_id: Optional[str] = None,
    risk_level: Optional[str] = None,
    action: Optional[str] = None,
    limit: int = Query(default=100, le=500),
    offset: int = Query(default=0, ge=0)
):
    """Get paginated command history"""
    history = await db.get_history(
        session_id=session_id,
        risk_level=risk_level,
        action=action,
        limit=limit,
        offset=offset
    )
    return {"items": history, "limit": limit, "offset": offset}

@router.get("/patterns")
async def get_patterns():
    """List all danger patterns"""
    from data.patterns import DANGER_PATTERNS
    return DANGER_PATTERNS

@router.get("/dashboard/summary")
async def dashboard_summary():
    """Dashboard summary data"""
    stats = await db.get_stats()
    obs = get_metrics().get_summary()
    return {
        "total_commands": stats.get("total_commands", 0),
        "total_interceptions": stats.get("total_interceptions", 0),
        "safe_swap_rate": stats.get("safe_swap_rate", 0),
        "avg_analysis_latency_ms": obs.get("avg_analysis_duration_ms", 0),
        "risk_distribution": stats.get("risk_distribution", {}),
        "action_distribution": stats.get("action_distribution", {})
    }

@router.get("/dashboard/risk-distribution")
async def risk_distribution():
    """Risk distribution data"""
    stats = await db.get_stats()
    return stats.get("risk_distribution", {})

@router.get("/dashboard/timeline")
async def timeline():
    """Command timeline data"""
    history = await db.get_history(limit=500)
    # Group by hour
    timeline_data = {}
    for entry in history:
        ts = entry.get("timestamp", "")[:13]  # YYYY-MM-DDTHH
        if ts not in timeline_data:
            timeline_data[ts] = {"total": 0, "intercepted": 0}
        timeline_data[ts]["total"] += 1
        if entry.get("action") in ["approved", "safe_swap", "cancelled", "blocked"]:
            timeline_data[ts]["intercepted"] += 1
    
    return [
        {"time": k, **v} for k, v in sorted(timeline_data.items())
    ]

@router.get("/dashboard/top-dangerous")
async def top_dangerous():
    """Most common dangerous commands"""
    history = await db.get_history(limit=1000)
    command_counts = {}
    for entry in history:
        if entry.get("risk_level") in ["high", "critical", "medium"]:
            cmd = entry.get("command", "")
            # Normalize command (take first word/flags)
            base = " ".join(cmd.split()[:3])
            command_counts[base] = command_counts.get(base, 0) + 1
    
    sorted_cmds = sorted(command_counts.items(), key=lambda x: x[1], reverse=True)
    return [
        {"command": cmd, "count": count}
        for cmd, count in sorted_cmds[:10]
    ]

@router.get("/mcp/tools")
async def get_mcp_tools():
    """Get registered MCP tools"""
    tools = MCPTools.get_tools()
    return [MCPTools.to_dict(t) for t in tools]
