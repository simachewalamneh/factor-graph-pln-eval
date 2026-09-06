
from truth_value import TruthValue
DEDUCTION_DISCOUNT = 0.9
INDUCTION_DISCOUNT = 0.8
ABDUCTION_DISCOUNT = 0.8
DEFAULT_S_B = 0.5

def _chain_confidence(c1, c2, discount):
    return discount * min(c1, c2)

def deduction(tv_AB: TruthValue, tv_BC: TruthValue, s_B: float = DEFAULT_S_B) -> TruthValue:
    sAB, sBC = tv_AB.strength, tv_BC.strength
    sC = sBC  
    denom = 1 - s_B
    if denom <= 1e-9:
        strength = sAB * sBC
    else:
        strength = sAB * sBC + (1 - sAB) * (sC - s_B * sBC) / denom
    strength = min(max(strength, 0.0), 1.0)
    confidence = _chain_confidence(tv_AB.confidence, tv_BC.confidence, DEDUCTION_DISCOUNT)
    return TruthValue(strength, confidence)

def induction(tv_BA: TruthValue, tv_BC: TruthValue) -> TruthValue:
    sBA, sBC = tv_BA.strength, tv_BC.strength
    strength = sBA * sBC + (1 - sBA) * (1 - sBC)
    confidence = _chain_confidence(tv_BA.confidence, tv_BC.confidence, INDUCTION_DISCOUNT)
    return TruthValue(strength, confidence)

def abduction(tv_AB: TruthValue, tv_CB: TruthValue) -> TruthValue:
    sAB, sCB = tv_AB.strength, tv_CB.strength
    strength = sAB * sCB + (1 - sAB) * (1 - sCB)
    confidence = _chain_confidence(tv_AB.confidence, tv_CB.confidence, ABDUCTION_DISCOUNT)
    return TruthValue(strength, confidence)

def revision(tv1: TruthValue, tv2: TruthValue) -> TruthValue:
    c1, c2 = tv1.confidence, tv2.confidence
    total_c = c1 + c2
    if total_c <= 1e-9:
        strength = (tv1.strength + tv2.strength) / 2
    else:
        strength = (tv1.strength * c1 + tv2.strength * c2) / total_c
    confidence = 1 - (1 - c1) * (1 - c2)
    return TruthValue(strength, confidence)
