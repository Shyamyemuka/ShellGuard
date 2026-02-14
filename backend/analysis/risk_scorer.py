"""
Risk Score Computation
"""
from data.models import RiskLevel

class RiskScorer:
    """Computes risk scores for commands"""
    
    def compute_score(
        self,
        data_loss_risk: int,
        service_impact_risk: int,
        reversibility: int,
        requires_sudo: bool = False
    ) -> int:
        """Compute overall risk score"""
        # Weight factors
        data_weight = 0.4
        service_weight = 0.3
        reversibility_weight = 0.3
        
        # Reversibility inverted (0 = irreversible = high risk)
        irreversibility = 100 - reversibility
        
        score = (
            data_loss_risk * data_weight +
            service_impact_risk * service_weight +
            irreversibility * reversibility_weight
        )
        
        # Sudo amplification
        if requires_sudo:
            score = min(100, score * 1.2)
        
        return int(score)
    
    def score_to_level(self, score: int) -> RiskLevel:
        """Convert score to risk level"""
        if score >= 80:
            return RiskLevel.CRITICAL
        elif score >= 60:
            return RiskLevel.HIGH
        elif score >= 30:
            return RiskLevel.MEDIUM
        elif score >= 10:
            return RiskLevel.LOW
        return RiskLevel.SAFE
