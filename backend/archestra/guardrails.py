"""
Guardrail Configurations
"""
from typing import Optional
from analysis.pattern_matcher import PatternMatcher
from data.models import RiskLevel

class GuardrailsValidator:
    """Validates inputs and outputs against guardrails"""
    
    def __init__(self):
        self.pattern_matcher = PatternMatcher()
        self.max_command_length = 10000
    
    def validate_input(self, command: str) -> tuple[bool, Optional[str]]:
        """Validate input command"""
        # Length check
        if len(command) > self.max_command_length:
            return False, "Command exceeds maximum length"
        
        # Prompt injection patterns
        injection_patterns = [
            "ignore previous instructions",
            "you are now",
            "system prompt",
            "ASSISTANT:",
            "\\n\\nHuman:"
        ]
        
        command_lower = command.lower()
        for pattern in injection_patterns:
            if pattern.lower() in command_lower:
                return False, "Potential prompt injection detected"
        
        return True, None
    
    def validate_alternative(self, original: str, alternative: str) -> tuple[bool, Optional[str]]:
        """Validate that an alternative is actually safer"""
        if not alternative:
            return True, None
        
        original_result = self.pattern_matcher.check(original)
        alt_result = self.pattern_matcher.check(alternative)
        
        # Alternative should not be critical
        if alt_result.risk_level == RiskLevel.CRITICAL:
            return False, "Alternative contains critical risk patterns"
        
        # Alternative should not be riskier
        risk_order = [RiskLevel.SAFE, RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]
        if risk_order.index(alt_result.risk_level) > risk_order.index(original_result.risk_level):
            return False, "Alternative is riskier than original"
        
        return True, None
