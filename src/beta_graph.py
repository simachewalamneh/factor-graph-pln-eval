from itertools import combinations

from parity_data import CANDIDATES, evaluate_candidate, true_outputs
from truth_value import beta_from_counts

def agreement_counts(outputs_a, outputs_b):
    successes = sum(1 for x, y in zip(outputs_a, outputs_b) if x == y)
    failures = len(outputs_a) - successes
    return successes, failures

def build_candidate_outputs():
    return {idx: evaluate_candidate(expr) for idx, expr in CANDIDATES.items()}
#Each candidate therefore becomes an 8-dimensional Boolean vector.
def build_direct_evidence_beliefs():
    truth = true_outputs()
    outputs = build_candidate_outputs()
    beliefs = {}
    for idx, out in outputs.items():
        s, f = agreement_counts(out, truth)
        belief = beta_from_counts(s, f)
        beliefs[idx] = belief
    return beliefs, outputs
#totally 190 combination between candidate items where #candicate=20
def build_correlation_factors(outputs):
    factors = {}
    for i, j in combinations(outputs.keys(), 2):
        s, f = agreement_counts(outputs[i], outputs[j])
        factors[(i, j)] = beta_from_counts(s, f)
    return factors

if __name__ == "__main__":
    direct, outputs = build_direct_evidence_beliefs()
    print("Direct evidence (candidate vs. ground truth):")
    for idx, belief in sorted(direct.items()):
        tv = belief.to_truth_value()
        print(f"  #{idx:2d}: alpha={belief.alpha:.0f} beta={belief.beta:.0f}  -> {tv}")

    corr = build_correlation_factors(outputs)
    print("\nSample pairwise correlation factors:")
    for (i, j), belief in list(corr.items())[:5]:
        tv = belief.to_truth_value()
        print(f"  ({i:2d},{j:2d}): alpha={belief.alpha:.0f} beta={belief.beta:.0f} -> {tv}")
