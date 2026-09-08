from itertools import combinations

from parity_data import CANDIDATES, evaluate_candidate, true_outputs
from truth_value import beta_from_counts

def agreement_counts(outputs_a, outputs_b):
    """successes = positions where a and b agree, failures = where they differ."""
    successes = sum(1 for x, y in zip(outputs_a, outputs_b) if x == y)
    failures = len(outputs_a) - successes
    return successes, failures

def build_candidate_outputs():
    return {idx: evaluate_candidate(expr) for idx, expr in CANDIDATES.items()}

def build_direct_evidence_beliefs():
    truth = true_outputs()
    outputs = build_candidate_outputs()
    beliefs = {}
    for idx, out in outputs.items():
        s, f = agreement_counts(out, truth)
        belief = beta_from_counts(s, f)
        beliefs[idx] = belief
    return beliefs, outputs

def build_correlation_factors(outputs):
    factors = {}
    for i, j in combinations(outputs.keys(), 2):
        s, f = agreement_counts(outputs[i], outputs[j])
        factors[(i, j)] = beta_from_counts(s, f)
    return factors

# TIER 1: Lowers complexity from O(n²) to O(k*n) with zero accuracy cost by only pairing candidates with pre-selected anchors.
# This requires selecting anchors first via direct evidence before building correlation factors (see propagate_sparse.py).

def build_correlation_factors_sparse(outputs, anchors):
    anchor_set = set(anchors)
    factors = {}
    all_ids = list(outputs.keys())
    for a in anchors:
        for j in all_ids:
            if j == a:
                continue
            i, k = (a, j) if a < j else (j, a)  # keep pair ordering consistent
            if (i, k) in factors:
                continue  # already computed  
            s, f = agreement_counts(outputs[i], outputs[k])
            factors[(i, k)] = beta_from_counts(s, f)
    return factors

# TIER 2: Approximates the O(k*n) anchor pairs by filtering factors via top-k correlation or a minimum strength threshold.
# This drops weak edges to boost speed, altering final Revision beliefs and requiring an accuracy-runtime trade-off evaluation.

def build_correlation_factors_topk(outputs, anchors, k_neighbors):
    full = build_correlation_factors_sparse(outputs, anchors)
    kept = {}
    for a in anchors:
        # Every candidate correlated with this anchor, ranked by strength.
        neighbors = []
        for j in outputs:
            if j == a:
                continue
            pair = (a, j) if a < j else (j, a)
            if pair in full:
                neighbors.append((pair, full[pair].mean))
        neighbors.sort(key=lambda x: x[1], reverse=True)
        for pair, _ in neighbors[:k_neighbors]:
            kept[pair] = full[pair]
    return kept

def build_correlation_factors_threshold(outputs, anchors, threshold):
    full = build_correlation_factors_sparse(outputs, anchors)
    return {pair: belief for pair, belief in full.items() if belief.mean >= threshold}

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
