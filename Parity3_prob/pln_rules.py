from truth_value import TruthValue

def clamp(v, lo, hi):
    return min(hi, max(v, lo))
def truth_c2w(c):
    """Confidence -> weight of evidence. w = c / (1-c)."""
    return c / (1 - c) if c < 1.0 else float("inf")
def truth_w2c(w):
    """Weight of evidence -> confidence. c = w / (w+1)."""
    if w == float("inf"):
        return 1.0
    return w / (w + 1)

def _smallest_intersection_probability(As, Bs):
    return clamp((As + Bs - 1) / As, 0, 1) if As > 0 else 0.0

def _largest_intersection_probability(As, Bs):
    return clamp(Bs / As, 0, 1) if As > 0 else 0.0

def _conditional_probability_consistency(As, Bs, ABs):
    if As <= 0:
        return False
    return _smallest_intersection_probability(As, Bs) <= ABs <= _largest_intersection_probability(As, Bs)


def deduction(P: TruthValue, Q: TruthValue, R: TruthValue, PQ: TruthValue, QR: TruthValue) -> TruthValue:

    Ps, Qs, Rs = P.strength, Q.strength, R.strength
    PQs, PQc = PQ.strength, PQ.confidence
    QRs, QRc = QR.strength, QR.confidence

    if not (_conditional_probability_consistency(Ps, Qs, PQs) and
            _conditional_probability_consistency(Qs, Rs, QRs)):
        return TruthValue(1.0, 0.0)

    if Qs > 0.9999:
        strength = Rs
    else:
        strength = PQs * QRs + ((1 - PQs) * (Rs - Qs * QRs)) / (1 - Qs)

    confidence = min(P.confidence, Q.confidence, R.confidence, PQc, QRc)
    return TruthValue(clamp(strength, 0, 1), confidence)


def induction(A: TruthValue, B: TruthValue, C: TruthValue, BA: TruthValue, BC: TruthValue) -> TruthValue:
    sA, sB, sC = A.strength, B.strength, C.strength
    sBA, sBC = BA.strength, BC.strength

    term1 = (sBA * sBC * sB) / sA if sA > 0 else 0.0
    term2 = (1 - (sBA * sB) / sA if sA > 0 else 1) * ((sC - sB * sBC) / (1 - sB) if sB < 1 else 0.0)
    strength = term1 + term2
    confidence = truth_w2c(min(BA.confidence, BC.confidence))
    return TruthValue(clamp(strength, 0, 1), confidence)


def abduction(A: TruthValue, B: TruthValue, C: TruthValue, AB: TruthValue, CB: TruthValue) -> TruthValue:
  
    sB, sC = B.strength, C.strength
    sAB, sCB = AB.strength, CB.strength

    term1 = (sAB * sCB * sC) / sB if sB > 0 else 0.0
    term2 = (sC * (1 - sAB) * (1 - sCB)) / (1 - sB) if sB < 1 else 0.0
    strength = term1 + term2
    confidence = truth_w2c(min(AB.confidence, CB.confidence))
    return TruthValue(clamp(strength, 0, 1), confidence)


def revision(tv1: TruthValue, tv2: TruthValue) -> TruthValue:

    c1, c2 = tv1.confidence, tv2.confidence
    w1, w2 = truth_c2w(c1), truth_c2w(c2)
    w = w1 + w2
    if w == 0:
        strength = (tv1.strength + tv2.strength) / 2
    else:
        strength = (w1 * tv1.strength + w2 * tv2.strength) / w
    confidence = min(1.0, max(truth_w2c(w), c1, c2))
    return TruthValue(min(1.0, strength), confidence)
