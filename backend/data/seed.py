"""
Demo Data Seeding
"""
import asyncio
from datetime import datetime, timedelta
from uuid import uuid4
from .database import Database, init_database

async def seed_demo_data():
    """Seed demo data for the dashboard"""
    await init_database()
    db = Database()
    
    session_id = str(uuid4())
    await db.create_session(session_id)
    
    # Demo commands
    demo_commands = [
        ("ls -la", "safe", "executed", None),
        ("pwd", "safe", "executed", None),
        ("cd /var/log", "safe", "executed", None),
        ("echo 'hello world'", "safe", "executed", None),
        ("cat /etc/hostname", "safe", "executed", None),
        ("rm -rf /var/logs/*", "high", "safe_swap", "find /var/logs -name '*.log' -mtime +30 -delete"),
        ("chmod 777 /etc/passwd", "critical", "cancelled", None),
        ("rm -rf /", "critical", "blocked", None),
        ("kill -9 1234", "high", "approved", None),
        ("git push --force", "medium", "safe_swap", "git push --force-with-lease"),
    ]
    
    from .models import CommandLogEntry, RiskLevel, CommandAction, RiskAnalysis
    
    for i, (cmd, risk, action, alt) in enumerate(demo_commands):
        entry = CommandLogEntry(
            id=uuid4(),
            session_id=uuid4(),
            command=cmd,
            timestamp=datetime.utcnow() - timedelta(minutes=len(demo_commands) - i),
            risk_level=RiskLevel(risk),
            action=CommandAction(action),
            alternative_used=alt,
            working_directory="~",
            analysis_latency_ms=0 if risk == "safe" else 1200
        )
        await db.log_command(entry)
    
    print("🌱 Demo data seeded")

if __name__ == "__main__":
    asyncio.run(seed_demo_data())
