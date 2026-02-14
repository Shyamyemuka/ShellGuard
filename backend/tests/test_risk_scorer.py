"""
Tests for Risk Scorer
"""
from analysis.risk_scorer import RiskScorer
from data.models import RiskLevel

scorer = RiskScorer()

def test_low_risk():
    score = scorer.compute_score(10, 10, 90)
    assert score < 30

def test_high_risk():
    score = scorer.compute_score(80, 70, 10)
    assert score > 60

def test_critical_risk():
    score = scorer.compute_score(100, 100, 0)
    assert score > 80

def test_sudo_amplification():
    base = scorer.compute_score(50, 50, 50)
    sudo = scorer.compute_score(50, 50, 50, requires_sudo=True)
    assert sudo > base

def test_score_to_level():
    assert scorer.score_to_level(5) == RiskLevel.SAFE
    assert scorer.score_to_level(15) == RiskLevel.LOW
    assert scorer.score_to_level(45) == RiskLevel.MEDIUM
    assert scorer.score_to_level(70) == RiskLevel.HIGH
    assert scorer.score_to_level(90) == RiskLevel.CRITICAL
