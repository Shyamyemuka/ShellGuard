"""
LLM-Powered Deep Analysis
"""
import json
import time
from typing import Optional
import google.generativeai as genai

from config import settings
from data.models import RiskLevel, RiskAnalysis, CommandBreakdown

SYSTEM_PROMPT = """You are ShellGuard, an AI terminal safety assistant. Your job is to analyze
shell commands and assess their risk level before they are executed.

You must respond with a JSON object following this exact schema:
{
    "risk_level": "critical" | "high" | "medium" | "low",
    "risk_score": <integer 0-100>,
    "allow": <boolean - your recommendation>,
    "title": "<short risk title, max 50 chars>",
    "explanation": "<detailed explanation of what the command does and why it's risky, 2-3 sentences>",
    "consequences": ["<consequence 1>", "<consequence 2>", ...],
    "safer_alternative": "<a safer command that achieves a similar goal, or null if no safe alternative exists>",
    "alternative_explanation": "<why the alternative is safer, 1 sentence>",
    "data_loss_risk": <integer 0-100>,
    "service_impact_risk": <integer 0-100>,
    "reversibility": <integer 0-100, where 100 = fully reversible>,
    "requires_sudo": <boolean>,
    "affected_scope": "<what files/services/systems are affected>",
    "command_breakdown": [
        {
            "part": "<part of command>",
            "meaning": "<what it means>",
            "risk_contribution": "<how it contributes to risk>"
        }
    ]
}

Guidelines:
- Be accurate and specific about what the command does
- Consider the COMBINATION of flags (rm -rf is worse than rm -r)
- Consider the TARGET path (deleting /tmp is less risky than /etc)
- **CONTEXTUAL AWARENESS**: Consider the working directory - operations in system dirs like /etc, /usr, /var are riskier
- Operations in home directories (~) or /tmp are generally less critical
- Always suggest a safer alternative when possible
- The safer alternative should achieve a SIMILAR goal, not a completely different one
- If no safe alternative exists, set safer_alternative to null
- Be concise but thorough in explanations

Risk Score Guidelines:
- 0-20: Low risk, generally safe
- 21-50: Medium risk, could cause issues
- 51-80: High risk, likely to cause damage
- 81-100: Critical risk, catastrophic potential
- Increase risk scores by 20-30% when working directory is a system directory"""


class AIAnalyzer:
    """AI-powered command analysis using Gemini"""
    
    def __init__(self):
        if settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel(settings.llm_model)
        else:
            self.model = None
    
    async def analyze(
        self,
        command: str,
        working_directory: str = "~",
        user: str = "user",
        preliminary_risk: str = "medium"
    ) -> Optional[RiskAnalysis]:
        """Analyze a command using AI"""
        if not self.model:
            return self._fallback_analysis(command, preliminary_risk)
        
        try:
            prompt = f"""Analyze this shell command:

Command: {command}
Working Directory: {working_directory}
User: {user}
Preliminary Risk Assessment: {preliminary_risk}

Provide your analysis as a JSON object."""

            response = self.model.generate_content(
                [
                    {"role": "user", "parts": [SYSTEM_PROMPT]},
                    {"role": "model", "parts": ["I understand. I will analyze shell commands and respond with JSON."]},
                    {"role": "user", "parts": [prompt]}
                ],
                generation_config=genai.types.GenerationConfig(
                    temperature=settings.llm_temperature,
                    max_output_tokens=settings.llm_max_tokens,
                )
            )
            
            # Parse response
            text = response.text
            # Extract JSON from response
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            
            data = json.loads(text.strip())
            
            # Convert to RiskAnalysis
            breakdown = [
                CommandBreakdown(
                    part=b.get("part", ""),
                    meaning=b.get("meaning", ""),
                    risk_contribution=b.get("risk_contribution", "")
                )
                for b in data.get("command_breakdown", [])
            ]
            
            return RiskAnalysis(
                risk_level=RiskLevel(data.get("risk_level", "medium")),
                risk_score=data.get("risk_score", 50),
                allow=data.get("allow", False),
                title=data.get("title", "Risk Detected"),
                explanation=data.get("explanation", ""),
                consequences=data.get("consequences", []),
                safer_alternative=data.get("safer_alternative"),
                alternative_explanation=data.get("alternative_explanation"),
                data_loss_risk=data.get("data_loss_risk", 50),
                service_impact_risk=data.get("service_impact_risk", 50),
                reversibility=data.get("reversibility", 50),
                requires_sudo=data.get("requires_sudo", False),
                affected_scope=data.get("affected_scope", "Unknown"),
                command_breakdown=breakdown,
                analysis_source="ai",
                model_used=settings.llm_model,
                tokens_used=0  # TODO: Get from response
            )
            
        except Exception as e:
            print(f"AI analysis error: {e}")
            return self._fallback_analysis(command, preliminary_risk)
    
    def _fallback_analysis(self, command: str, preliminary_risk: str) -> RiskAnalysis:
        """Fallback analysis when AI is unavailable"""
        risk_level = RiskLevel(preliminary_risk)
        risk_scores = {
            "low": 25,
            "medium": 50,
            "high": 75,
            "critical": 95
        }
        
        return RiskAnalysis(
            risk_level=risk_level,
            risk_score=risk_scores.get(preliminary_risk, 50),
            allow=preliminary_risk == "low",
            title="Potentially Dangerous Command",
            explanation="This command has been flagged as potentially dangerous based on pattern matching. AI analysis is currently unavailable.",
            consequences=["Potential data loss", "Service disruption", "Security implications"],
            safer_alternative=None,
            alternative_explanation=None,
            data_loss_risk=50,
            service_impact_risk=50,
            reversibility=50,
            requires_sudo=False,
            affected_scope="Unknown",
            command_breakdown=[],
            analysis_source="pattern",
            model_used=None,
            tokens_used=0
        )
