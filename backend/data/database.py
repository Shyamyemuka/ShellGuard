"""
SQLite Setup and Queries
"""
import aiosqlite
import json
import os
from typing import Optional, List
from datetime import datetime

from config import settings
from .models import CommandLogEntry, RiskLevel, CommandAction

# Ensure data directory exists
os.makedirs(os.path.dirname(settings.database_path) or ".", exist_ok=True)

async def init_database() -> None:
    """Initialize database schema"""
    async with aiosqlite.connect(settings.database_path) as db:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                ended_at TIMESTAMP,
                total_commands INTEGER DEFAULT 0,
                total_interceptions INTEGER DEFAULT 0,
                total_safe_swaps INTEGER DEFAULT 0
            );
            
            CREATE TABLE IF NOT EXISTS command_log (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                command TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                risk_level TEXT NOT NULL DEFAULT 'safe',
                action TEXT NOT NULL DEFAULT 'executed',
                risk_score INTEGER,
                risk_title TEXT,
                explanation TEXT,
                consequences TEXT,
                safer_alternative TEXT,
                alternative_used TEXT,
                data_loss_risk INTEGER,
                service_impact_risk INTEGER,
                reversibility INTEGER,
                working_directory TEXT,
                analysis_source TEXT,
                model_used TEXT,
                tokens_used INTEGER DEFAULT 0,
                analysis_latency_ms INTEGER DEFAULT 0,
                full_analysis TEXT
            );
            
            CREATE INDEX IF NOT EXISTS idx_command_log_session ON command_log(session_id);
            CREATE INDEX IF NOT EXISTS idx_command_log_timestamp ON command_log(timestamp DESC);
            CREATE INDEX IF NOT EXISTS idx_command_log_risk ON command_log(risk_level);
            CREATE INDEX IF NOT EXISTS idx_command_log_action ON command_log(action);
            
            CREATE TABLE IF NOT EXISTS daily_stats (
                date TEXT PRIMARY KEY,
                total_commands INTEGER DEFAULT 0,
                safe_commands INTEGER DEFAULT 0,
                interceptions INTEGER DEFAULT 0,
                safe_swaps INTEGER DEFAULT 0,
                approved INTEGER DEFAULT 0,
                cancelled INTEGER DEFAULT 0,
                blocked INTEGER DEFAULT 0,
                total_tokens INTEGER DEFAULT 0
            );
        """)
        await db.commit()
        print("📦 Database initialized")


class Database:
    """Database operations"""
    
    async def create_session(self, session_id: str) -> None:
        """Create a new session"""
        async with aiosqlite.connect(settings.database_path) as db:
            await db.execute(
                "INSERT INTO sessions (id, started_at) VALUES (?, ?)",
                (session_id, datetime.utcnow().isoformat())
            )
            await db.commit()
    
    async def end_session(self, session_id: str) -> None:
        """End a session"""
        async with aiosqlite.connect(settings.database_path) as db:
            await db.execute(
                "UPDATE sessions SET ended_at = ? WHERE id = ?",
                (datetime.utcnow().isoformat(), session_id)
            )
            await db.commit()
    
    async def log_command(self, entry: CommandLogEntry) -> None:
        """Log a command to the database"""
        async with aiosqlite.connect(settings.database_path) as db:
            analysis_json = None
            consequences = None
            
            if entry.analysis:
                analysis_json = json.dumps({
                    "risk_level": entry.analysis.risk_level.value,
                    "risk_score": entry.analysis.risk_score,
                    "title": entry.analysis.title,
                    "explanation": entry.analysis.explanation,
                    "consequences": entry.analysis.consequences,
                    "safer_alternative": entry.analysis.safer_alternative,
                    "data_loss_risk": entry.analysis.data_loss_risk,
                    "service_impact_risk": entry.analysis.service_impact_risk,
                    "reversibility": entry.analysis.reversibility
                })
                consequences = json.dumps(entry.analysis.consequences)
            
            await db.execute("""
                INSERT INTO command_log (
                    id, session_id, command, timestamp, risk_level, action,
                    risk_score, risk_title, explanation, consequences,
                    safer_alternative, alternative_used, data_loss_risk,
                    service_impact_risk, reversibility, working_directory,
                    analysis_source, model_used, tokens_used, analysis_latency_ms,
                    full_analysis
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(entry.id),
                str(entry.session_id),
                entry.command,
                entry.timestamp.isoformat(),
                entry.risk_level.value,
                entry.action.value,
                entry.analysis.risk_score if entry.analysis else None,
                entry.analysis.title if entry.analysis else None,
                entry.analysis.explanation if entry.analysis else None,
                consequences,
                entry.analysis.safer_alternative if entry.analysis else None,
                entry.alternative_used,
                entry.analysis.data_loss_risk if entry.analysis else None,
                entry.analysis.service_impact_risk if entry.analysis else None,
                entry.analysis.reversibility if entry.analysis else None,
                entry.working_directory,
                entry.analysis.analysis_source if entry.analysis else None,
                entry.analysis.model_used if entry.analysis else None,
                entry.analysis.tokens_used if entry.analysis else 0,
                entry.analysis_latency_ms,
                analysis_json
            ))
            await db.commit()
    
    async def get_history(
        self,
        session_id: Optional[str] = None,
        risk_level: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[dict]:
        """Get command history"""
        async with aiosqlite.connect(settings.database_path) as db:
            db.row_factory = aiosqlite.Row
            
            query = "SELECT * FROM command_log WHERE 1=1"
            params = []
            
            if session_id:
                query += " AND session_id = ?"
                params.append(session_id)
            
            if risk_level:
                query += " AND risk_level = ?"
                params.append(risk_level)
            
            if action:
                query += " AND action = ?"
                params.append(action)
            
            query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    async def get_stats(self) -> dict:
        """Get overall statistics"""
        async with aiosqlite.connect(settings.database_path) as db:
            # Total commands
            async with db.execute("SELECT COUNT(*) FROM command_log") as cursor:
                total = (await cursor.fetchone())[0]
            
            # By risk level
            async with db.execute("""
                SELECT risk_level, COUNT(*) as count 
                FROM command_log 
                GROUP BY risk_level
            """) as cursor:
                risk_counts = {row[0]: row[1] for row in await cursor.fetchall()}
            
            # By action
            async with db.execute("""
                SELECT action, COUNT(*) as count 
                FROM command_log 
                GROUP BY action
            """) as cursor:
                action_counts = {row[0]: row[1] for row in await cursor.fetchall()}
            
            # Interceptions
            interceptions = (
                action_counts.get("approved", 0) +
                action_counts.get("safe_swap", 0) +
                action_counts.get("cancelled", 0) +
                action_counts.get("blocked", 0)
            )
            
            # Safe swap rate
            warnings = interceptions - action_counts.get("blocked", 0)
            safe_swap_rate = 0.0
            if warnings > 0:
                safe_swap_rate = action_counts.get("safe_swap", 0) / warnings * 100
            
            return {
                "total_commands": total,
                "total_interceptions": interceptions,
                "safe_swap_rate": round(safe_swap_rate, 1),
                "risk_distribution": risk_counts,
                "action_distribution": action_counts
            }
