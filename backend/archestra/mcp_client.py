"""
Archestra MCP Gateway Client
Provides integration with Archestra's Model Context Protocol Gateway
"""
import httpx
import json
from typing import Dict, Any, Optional
from config import settings
from data.models import RiskLevel, RiskAnalysis, CommandBreakdown


class ArchestraMCPClient:
    """Client for Archestra MCP Gateway"""
    
    def __init__(self):
        self.api_key = settings.archestra_api_key
        self.runtime_url = settings.archestra_runtime_url or "https://runtime.archestra.dev"
        self.project_id = settings.archestra_project_id
        self.enabled = bool(self.api_key and settings.archestra_observability_enabled)
        
        if self.enabled:
            print(f"🤖 Archestra MCP Gateway initialized")
            print(f"   Runtime: {self.runtime_url}")
            print(f"   Project: {self.project_id}")
        else:
            print("⚠️  Archestra MCP Gateway disabled (no API key)")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Archestra-Project-Id": self.project_id
        }
    
    async def call_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        timeout: int = 30
    ) -> Optional[Dict[str, Any]]:
        """
        Call an MCP tool through Archestra Gateway
        
        Args:
            tool_name: Name of the MCP tool to call
            parameters: Tool input parameters
            timeout: Request timeout in seconds
            
        Returns:
            Tool output as dictionary, or None if failed
        """
        if not self.enabled:
            return None
        
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    f"{self.runtime_url}/v1/tools/{tool_name}/invoke",
                    headers=self._get_headers(),
                    json={"parameters": parameters}
                )
                
                response.raise_for_status()
                result = response.json()
                
                # Archestra returns: {"status": "success", "output": {...}}
                if result.get("status") == "success":
                    return result.get("output", {})
                else:
                    print(f"❌ Archestra tool call failed: {result.get('error', 'Unknown error')}")
                    return None
                    
        except httpx.HTTPStatusError as e:
            print(f"❌ Archestra API error: {e.response.status_code} - {e.response.text}")
            return None
        except httpx.TimeoutException:
            print(f"⏱️  Archestra tool call timed out after {timeout}s")
            return None
        except Exception as e:
            print(f"❌ Archestra MCP error: {e}")
            return None
    
    async def analyze_command(
        self,
        command: str,
        working_directory: str = "~",
        user: str = "user",
        preliminary_risk: str = "medium"
    ) -> Optional[RiskAnalysis]:
        """
        Analyze a command using Archestra's analyze_command MCP tool
        
        Args:
            command: Shell command to analyze
            working_directory: Current directory context
            user: User executing the command
            preliminary_risk: Initial risk assessment from pattern matcher
            
        Returns:
            RiskAnalysis object or None if analysis failed
        """
        result = await self.call_tool(
            "analyze_command",
            {
                "command": command,
                "working_directory": working_directory,
                "user": user,
                "preliminary_risk": preliminary_risk
            }
        )
        
        if not result:
            return None
        
        try:
            # Parse Archestra response into RiskAnalysis
            breakdown = [
                CommandBreakdown(
                    part=b.get("part", ""),
                    meaning=b.get("meaning", ""),
                    risk_contribution=b.get("risk_contribution", "")
                )
                for b in result.get("command_breakdown", [])
            ]
            
            return RiskAnalysis(
                risk_level=RiskLevel(result.get("risk_level", "medium")),
                risk_score=result.get("risk_score", 50),
                allow=result.get("allow", False),
                title=result.get("title", "Risk Detected"),
                explanation=result.get("explanation", ""),
                consequences=result.get("consequences", []),
                safer_alternative=result.get("safer_alternative"),
                alternative_explanation=result.get("alternative_explanation"),
                data_loss_risk=result.get("data_loss_risk", 50),
                service_impact_risk=result.get("service_impact_risk", 50),
                reversibility=result.get("reversibility", 50),
                requires_sudo="sudo" in command.lower(),
                affected_scope=result.get("affected_scope", "Unknown"),
                command_breakdown=breakdown,
                analysis_source="archestra_mcp",
                model_used="archestra-gateway",
                tokens_used=result.get("tokens_used", 0)
            )
            
        except Exception as e:
            print(f"❌ Failed to parse Archestra response: {e}")
            return None
    
    async def suggest_alternative(
        self,
        command: str,
        risk_analysis: Optional[Dict[str, Any]] = None,
        intent: Optional[str] = None
    ) -> Optional[str]:
        """
        Suggest a safer alternative using Archestra MCP tool
        
        Args:
            command: Original dangerous command
            risk_analysis: Previous risk analysis result
            intent: User's intended goal
            
        Returns:
            Safer alternative command string, or None
        """
        result = await self.call_tool(
            "suggest_alternative",
            {
                "command": command,
                "risk_analysis": risk_analysis or {},
                "intent": intent or ""
            }
        )
        
        if result:
            return result.get("safer_alternative")
        return None
    
    async def explain_command(self, command: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed explanation of a command using Archestra MCP tool
        
        Args:
            command: Command to explain
            
        Returns:
            Explanation dict with plain_english, breakdown, etc., or None
        """
        return await self.call_tool(
            "explain_command",
            {"command": command}
        )
    
    async def send_trace(
        self,
        trace_id: str,
        command: str,
        risk_level: str,
        action: str,
        latency_ms: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send command trace to Archestra observability
        
        Args:
            trace_id: Unique trace identifier
            command: Command that was analyzed
            risk_level: Detected risk level
            action: Action taken (approved/blocked/cancelled)
            latency_ms: Analysis duration
            metadata: Additional trace metadata
            
        Returns:
            True if trace was sent successfully
        """
        if not self.enabled:
            return False
        
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                await client.post(
                    f"{self.runtime_url}/v1/traces",
                    headers=self._get_headers(),
                    json={
                        "trace_id": trace_id,
                        "project_id": self.project_id,
                        "command": command[:100],  # Truncate for privacy
                        "risk_level": risk_level,
                        "action": action,
                        "latency_ms": latency_ms,
                        "timestamp": metadata.get("timestamp") if metadata else None,
                        "metadata": metadata or {}
                    }
                )
                return True
        except Exception as e:
            # Don't fail the request if observability fails
            print(f"⚠️  Archestra trace failed: {e}")
            return False


# Global client instance
_client: Optional[ArchestraMCPClient] = None


def get_archestra_client() -> ArchestraMCPClient:
    """Get or create the global Archestra MCP client"""
    global _client
    if _client is None:
        _client = ArchestraMCPClient()
    return _client
