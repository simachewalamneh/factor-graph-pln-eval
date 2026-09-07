from dataclasses import dataclass
K = 8
PRIOR_ALPHA = 1.0  
PRIOR_BETA = 1.0

@dataclass
class TruthValue:
    strength: float   
    confidence: float  

    def __repr__(self):
        return f"<s={self.strength:.3f}, c={self.confidence:.3f}>"

@dataclass
class BetaBelief:
    alpha: float
    beta: float

    @property
    def mean(self):
        return self.alpha / (self.alpha + self.beta)

    @property
    def evidence_count(self):
        return (self.alpha + self.beta) - (PRIOR_ALPHA + PRIOR_BETA)

    def to_truth_value(self):
        n = self.evidence_count
        confidence = n / (n + K) if (n + K) > 0 else 0.0
        return TruthValue(strength=self.mean, confidence=confidence)

    def update(self, successes, failures):
        """Beta-Bernoulli conjugate update: additive in successes/failures."""
        return BetaBelief(self.alpha + successes, self.beta + failures)

def beta_from_counts(successes, failures):
    return BetaBelief(PRIOR_ALPHA + successes, PRIOR_BETA + failures)
