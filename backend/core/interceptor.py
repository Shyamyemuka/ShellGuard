"""
Command Interception Logic
"""
import time
from typing import Optional, Tuple
from dataclasses import dataclass

from analysis.pattern_matcher import PatternMatcher
from analysis.ai_analyzer import AIAnalyzer
from analysis.risk_scorer import RiskScorer
from data.models import RiskLevel, RiskAnalysis
from archestra.guardrails import GuardrailsValidator

@dataclass
class InterceptionResult:
    """Result of command interception"""
    should_block: bool
    risk_level: RiskLevel
    analysis: Optional[RiskAnalysis]
    is_hard_block: bool
    pattern_matched: Optional[str]
    analysis_latency_ms: int

class CommandInterceptor:
    """Intercepts and analyzes commands before execution"""
    
    # Common safe commands that don't need AI analysis
    KNOWN_SAFE_COMMANDS = {
        'ls', 'dir', 'cd', 'pwd', 'echo', 'cat', 'less', 'more', 'head', 'tail',
        'grep', 'find', 'which', 'whereis', 'whoami', 'date', 'time', 'uptime',
        'ps', 'top', 'htop', 'free', 'df', 'du', 'history', 'exit', 'clear', 'cls',
        'man', 'help', 'type', 'alias', 'env', 'printenv', 'hostname', 'uname',
        'git status', 'git log', 'git diff', 'git branch', 'npm list', 'pip list',
        'python --version', 'node --version', 'java -version', 'gcc --version',
        'ping', 'traceroute', 'nslookup', 'dig', 'curl', 'wget',
    }
    
    def __init__(self):
        self.pattern_matcher = PatternMatcher()
        self.ai_analyzer = AIAnalyzer()
        self.risk_scorer = RiskScorer()
        self.guardrails = GuardrailsValidator()
    
    def _is_known_safe_command(self, command: str) -> bool:
        """Check if command is a known safe command"""
        cmd_lower = command.lower().strip()
        # Check exact matches
        if cmd_lower in self.KNOWN_SAFE_COMMANDS:
            return True
        # Check if starts with a known safe command
        cmd_parts = cmd_lower.split()
        if cmd_parts:
            base_cmd = cmd_parts[0]
            # Common read-only flags
            if base_cmd in {'ls', 'dir', 'cat', 'grep', 'find', 'git', 'npm', 'pip', 'python', 'node'}:
                # These are generally safe with most flags
                return True
        return False
    
    async def intercept(
        self,
        command: str,
        working_directory: str = "~",
        user: str = "user"
    ) -> InterceptionResult:
        """
        Intercept and analyze a command
        Returns whether to block and full analysis
        """
        start_time = time.time()
        
        # Skip empty commands
        if not command.strip():
            return InterceptionResult(
                should_block=False,
                risk_level=RiskLevel.SAFE,
                analysis=None,
                is_hard_block=False,
                pattern_matched=None,
                analysis_latency_ms=0
            )
        
        # Tier 1: Quick pattern matching
        pattern_result = self.pattern_matcher.check(command)
        
        # Handle safe commands - check if it's a known safe command first
        if pattern_result.risk_level == RiskLevel.SAFE:
            # If it's a known safe command, pass through immediately
            if self._is_known_safe_command(command):
                latency = int((time.time() - start_time) * 1000)
                return InterceptionResult(
                    should_block=False,
                    risk_level=RiskLevel.SAFE,
                    analysis=None,
                    is_hard_block=False,
                    pattern_matched=None,
                    analysis_latency_ms=latency
                )
            
            # Unknown command - use AI to check if it's valid/exists
            analysis = await self.ai_analyzer.analyze(
                command=command,
                working_directory=working_directory,
                user=user,
                preliminary_risk="safe"
            )
            
            latency = int((time.time() - start_time) * 1000)
            if analysis:
                analysis.analysis_latency_ms = latency
                
            return InterceptionResult(
                should_block=False,
                risk_level=RiskLevel.SAFE,
                analysis=analysis,
                is_hard_block=False,
                pattern_matched=None,
                analysis_latency_ms=latency
            )
        
        # Handle hard blocks - no AI needed
        if pattern_result.hard_block:
            latency = int((time.time() - start_time) * 1000)
            analysis = RiskAnalysis(
                risk_level=RiskLevel.CRITICAL,
                risk_score=100,
                allow=False,
                title="Command Blocked",
                explanation=pattern_result.block_message or "This command is blocked for safety.",
                consequences=["System destruction", "Data loss", "Irreversible damage"],
                safer_alternative=None,
                alternative_explanation=None,
                data_loss_risk=100,
                service_impact_risk=100,
                reversibility=0,
                requires_sudo=False,
                affected_scope="Entire system",
                command_breakdown=[],
                analysis_source="hard_block",
                model_used=None,
                tokens_used=0,
                analysis_latency_ms=latency
            )
            return InterceptionResult(
                should_block=True,
                risk_level=RiskLevel.CRITICAL,
                analysis=analysis,
                is_hard_block=True,
                pattern_matched=pattern_result.category,
                analysis_latency_ms=latency
            )
        
        # Tier 2: AI analysis for medium+ risk
        if pattern_result.risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]:
            analysis = await self.ai_analyzer.analyze(
                command=command,
                working_directory=working_directory,
                user=user,
                preliminary_risk=pattern_result.risk_level.value
            )
            
            # Validate alternative through guardrails
            if analysis and analysis.safer_alternative:
                alt_check = self.pattern_matcher.check(analysis.safer_alternative)
                if alt_check.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                    analysis.safer_alternative = None
                    analysis.alternative_explanation = "No safe alternative could be verified."
            
            latency = int((time.time() - start_time) * 1000)
            if analysis:
                analysis.analysis_latency_ms = latency
            
            return InterceptionResult(
                should_block=True,
                risk_level=analysis.risk_level if analysis else pattern_result.risk_level,
                analysis=analysis,
                is_hard_block=False,
                pattern_matched=pattern_result.category,
                analysis_latency_ms=latency
            )
        
        # Low risk - log but don't block
        latency = int((time.time() - start_time) * 1000)
        return InterceptionResult(
            should_block=False,
            risk_level=pattern_result.risk_level,
            analysis=None,
            is_hard_block=False,
            pattern_matched=pattern_result.category,
            analysis_latency_ms=latency
        )
