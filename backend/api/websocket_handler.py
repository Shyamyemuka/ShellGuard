"""
WebSocket Message Routing
"""
import json
import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from typing import Optional

from core.session import ShellGuardSession
from core.interceptor import InterceptionResult
from data.models import SessionStats
from archestra.observability import track_command


class WebSocketHandler:
    """Handles WebSocket connections for terminal sessions"""
    
    def __init__(self, websocket: WebSocket):
        self.ws = websocket
        self.session: Optional[ShellGuardSession] = None
    
    async def handle(self):
        """Main handler for the WebSocket connection"""
        await self.ws.accept()
        
        # Create session
        self.session = ShellGuardSession()
        self.session.on_output = self._send_output
        self.session.on_warning = self._send_warning
        self.session.on_blocked = self._send_blocked
        self.session.on_analyzing = self._send_analyzing
        self.session.on_stats_update = self._send_stats_update
        
        # Start PTY session
        started = await self.session.start()
        if not started:
            await self.ws.send_json({
                "type": "error",
                "message": "Failed to start terminal session"
            })
            await self.ws.close()
            return
        
        try:
            # Read initial PTY output
            await asyncio.sleep(0.5)
            
            # Message loop
            while True:
                try:
                    raw = await asyncio.wait_for(
                        self.ws.receive_text(),
                        timeout=1800  # 30 minute idle timeout
                    )
                    message = json.loads(raw)
                    await self._route_message(message)
                except asyncio.TimeoutError:
                    await self.ws.send_json({
                        "type": "error",
                        "message": "Session timed out due to inactivity"
                    })
                    break
                except json.JSONDecodeError:
                    continue
                    
        except WebSocketDisconnect:
            pass
        except Exception as e:
            print(f"WebSocket error: {e}")
        finally:
            if self.session:
                await self.session.stop()
    
    async def _route_message(self, message: dict):
        """Route incoming WebSocket messages"""
        msg_type = message.get("type")
        
        if msg_type == "input":
            data = message.get("data", "")
            if data and self.session:
                await self.session.handle_input(data)
        
        elif msg_type == "approve":
            if self.session:
                await self.session.approve()
        
        elif msg_type == "use_alternative":
            command = message.get("command", "")
            if command and self.session:
                await self.session.use_alternative(command)
        
        elif msg_type == "cancel":
            if self.session:
                await self.session.cancel()
        
        elif msg_type == "resize":
            rows = message.get("rows", 24)
            cols = message.get("cols", 80)
            if self.session:
                await self.session.resize(rows, cols)
        
        elif msg_type == "ping":
            await self.ws.send_json({"type": "pong"})
    
    async def _send_output(self, data: bytes):
        """Send PTY output to client"""
        try:
            await self.ws.send_json({
                "type": "output",
                "data": data.decode("utf-8", errors="replace")
            })
        except Exception:
            pass
    
    async def _send_warning(self, result: InterceptionResult):
        """Send warning to client"""
        try:
            msg = {
                "type": "warning",
                "command": self.session._pending_command if self.session else "",
                "analysis": result.analysis.to_dict() if result.analysis else {}
            }
            await self.ws.send_json(msg)
            
            # Track in observability
            if result.analysis:
                track_command(
                    command=self.session._pending_command if self.session else "",
                    risk_level=result.risk_level.value,
                    action="warning_shown",
                    latency_ms=result.analysis_latency_ms,
                    pattern_matched=result.pattern_matched,
                    ai_invoked=result.analysis.analysis_source == "ai",
                    tokens_used=result.analysis.tokens_used
                )
        except Exception as e:
            print(f"Error sending warning: {e}")
    
    async def _send_blocked(self, result: InterceptionResult):
        """Send block notification to client"""
        try:
            msg = {
                "type": "blocked",
                "command": self.session._pending_command if self.session else "",
                "message": result.analysis.explanation if result.analysis else "Command blocked",
                "explanation": result.analysis.explanation if result.analysis else "",
                "risk_level": result.risk_level.value
            }
            await self.ws.send_json(msg)
        except Exception as e:
            print(f"Error sending blocked: {e}")
    
    async def _send_analyzing(self, command: str):
        """Send analyzing indicator to client"""
        try:
            await self.ws.send_json({
                "type": "analyzing",
                "command": command
            })
        except Exception:
            pass
    
    async def _send_stats_update(self, stats: SessionStats):
        """Send stats update to client"""
        try:
            await self.ws.send_json({
                "type": "stats_update",
                "stats": stats.to_dict()
            })
        except Exception:
            pass
