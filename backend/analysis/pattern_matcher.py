"""
Fast Pattern-Based Risk Detection
"""
import re
from typing import Optional
from dataclasses import dataclass

from data.models import RiskLevel
from data.patterns import DANGER_PATTERNS

@dataclass
class PatternMatchResult:
    """Result of pattern matching"""
    risk_level: RiskLevel
    category: Optional[str]
    description: Optional[str]
    hard_block: bool
    block_message: Optional[str]

class PatternMatcher:
    """Fast pattern-based risk detection"""
    
    def __init__(self):
        self.patterns = DANGER_PATTERNS
        self._compile_patterns()
    
    def _compile_patterns(self) -> None:
        """Pre-compile regex patterns"""
        self._compiled = {}
        for level, patterns in self.patterns.items():
            self._compiled[level] = []
            for p in patterns:
                if p.get("is_regex", False):
                    try:
                        compiled = re.compile(p["pattern"], re.IGNORECASE)
                        self._compiled[level].append((compiled, p))
                    except re.error:
                        pass
                else:
                    self._compiled[level].append((None, p))
    
    def check(self, command: str) -> PatternMatchResult:
        """Check a command against all patterns"""
        command_lower = command.lower().strip()
        
        # Check critical patterns first (hard blocks)
        for compiled, pattern in self._compiled.get("critical", []):
            if self._matches(command, command_lower, compiled, pattern):
                return PatternMatchResult(
                    risk_level=RiskLevel.CRITICAL,
                    category=pattern.get("category"),
                    description=pattern.get("description"),
                    hard_block=pattern.get("hard_block", False),
                    block_message=pattern.get("block_message")
                )
        
        # Check high risk patterns
        for compiled, pattern in self._compiled.get("high", []):
            if self._matches(command, command_lower, compiled, pattern):
                return PatternMatchResult(
                    risk_level=RiskLevel.HIGH,
                    category=pattern.get("category"),
                    description=pattern.get("description"),
                    hard_block=False,
                    block_message=None
                )
        
        # Check medium risk patterns
        for compiled, pattern in self._compiled.get("medium", []):
            if self._matches(command, command_lower, compiled, pattern):
                return PatternMatchResult(
                    risk_level=RiskLevel.MEDIUM,
                    category=pattern.get("category"),
                    description=pattern.get("description"),
                    hard_block=False,
                    block_message=None
                )
        
        # Check low risk patterns
        for compiled, pattern in self._compiled.get("low", []):
            if self._matches(command, command_lower, compiled, pattern):
                return PatternMatchResult(
                    risk_level=RiskLevel.LOW,
                    category=pattern.get("category"),
                    description=pattern.get("description"),
                    hard_block=False,
                    block_message=None
                )
        
        # No pattern matched - safe
        return PatternMatchResult(
            risk_level=RiskLevel.SAFE,
            category=None,
            description=None,
            hard_block=False,
            block_message=None
        )
    
    def _matches(
        self,
        command: str,
        command_lower: str,
        compiled: Optional[re.Pattern],
        pattern: dict
    ) -> bool:
        """Check if command matches a pattern"""
        if compiled:
            return bool(compiled.search(command))
        else:
            pattern_str = pattern.get("pattern", "").lower()
            return pattern_str in command_lower
