"""
MCP Tool Definitions for Archestra
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class MCPTool:
    """MCP Tool definition"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]

class MCPTools:
    """Archestra MCP Tools for ShellGuard"""
    
    @staticmethod
    def get_tools() -> list[MCPTool]:
        """Get all MCP tool definitions"""
        return [
            MCPTools.analyze_command_tool(),
            MCPTools.suggest_alternative_tool(),
            MCPTools.explain_command_tool()
        ]
    
    @staticmethod
    def analyze_command_tool() -> MCPTool:
        """Command Risk Analyzer tool"""
        return MCPTool(
            name="analyze_command",
            description="Analyzes a shell command for safety risks. Evaluates the command's potential for data loss, service disruption, and system damage.",
            input_schema={
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "The shell command to analyze"},
                    "working_directory": {"type": "string", "default": "~"},
                    "user": {"type": "string", "default": "user"},
                    "preliminary_risk": {"type": "string", "enum": ["medium", "high", "critical"]}
                },
                "required": ["command"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "risk_level": {"type": "string"},
                    "risk_score": {"type": "integer"},
                    "allow": {"type": "boolean"},
                    "title": {"type": "string"},
                    "explanation": {"type": "string"},
                    "consequences": {"type": "array", "items": {"type": "string"}},
                    "safer_alternative": {"type": "string"},
                    "data_loss_risk": {"type": "integer"},
                    "service_impact_risk": {"type": "integer"},
                    "reversibility": {"type": "integer"}
                }
            }
        )
    
    @staticmethod
    def suggest_alternative_tool() -> MCPTool:
        """Safe Alternative Suggester tool"""
        return MCPTool(
            name="suggest_alternative",
            description="Given a dangerous shell command, suggests a safer alternative that achieves a similar goal.",
            input_schema={
                "type": "object",
                "properties": {
                    "command": {"type": "string"},
                    "risk_analysis": {"type": "object"},
                    "intent": {"type": "string"}
                },
                "required": ["command"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "safer_alternative": {"type": "string"},
                    "alternative_explanation": {"type": "string"},
                    "intent_preserved": {"type": "boolean"},
                    "risk_reduction": {"type": "string"}
                }
            }
        )
    
    @staticmethod
    def explain_command_tool() -> MCPTool:
        """Command Explainer tool"""
        return MCPTool(
            name="explain_command",
            description="Provides a detailed, beginner-friendly explanation of a shell command.",
            input_schema={
                "type": "object",
                "properties": {
                    "command": {"type": "string"}
                },
                "required": ["command"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "plain_english": {"type": "string"},
                    "breakdown": {"type": "array"},
                    "affected_resources": {"type": "array"},
                    "reversible": {"type": "boolean"},
                    "undo_command": {"type": "string"}
                }
            }
        )
    
    @staticmethod
    def to_dict(tool: MCPTool) -> Dict[str, Any]:
        """Convert tool to dictionary"""
        return asdict(tool)
