from itertools import combinations
from beta_graph import (
    build_candidate_outputs,
    build_direct_evidence_beliefs,
    build_correlation_factors,
)
from pln_rules import deduction, induction, abduction, revision
from truth_value import TruthValue

def propagate(top_k_anchors=5):
    direct_beliefs, outputs = build_direct_evidence_beliefs()
    direct_tv = {i: b.to_truth_value() for i, b in direct_beliefs.items()}
    corr_beliefs = build_correlation_factors(outputs)
    corr_tv = {pair: b.to_truth_value() for pair, b in corr_beliefs.items()}

    def corr(i, j):
        return corr_tv.get((i, j)) or corr_tv.get((j, i))

    anchors = sorted(
        direct_tv.keys(),
        key=lambda i: abs(direct_tv[i].strength - 0.5),
        reverse=True,
    )[:top_k_anchors]

    all_candidates = list(direct_tv.keys())
    estimates = {j: [direct_tv[j]] for j in all_candidates}  # start with direct evidence
    for i in anchors:
        for j in all_candidates:
            if i == j:
                continue
            tv_ij = corr(i, j)
            if tv_ij is None:
                continue
            estimates[j].append(deduction(direct_tv[i], tv_ij))

    for a1, a2 in combinations(anchors, 2):
        for j in all_candidates:
            if j in (a1, a2):
                continue
            tv_a1_j = corr(a1, j)
            tv_a2_j = corr(a2, j)
            if tv_a1_j is None or tv_a2_j is None:
                continue
            tv_a1_a2 = corr(a1, a2)
            if tv_a1_a2 is not None:
                estimates[j].append(induction(tv_a1_a2, tv_a1_j))
            estimates[j].append(abduction(tv_a1_j, tv_a2_j))

    final = {}
    for j, tv_list in estimates.items():
        merged = tv_list[0]
        for tv in tv_list[1:]:
            merged = revision(merged, tv)
        final[j] = merged

    return {
        "anchors": anchors,
        "direct": direct_tv,
        "final": final,
    }
if __name__ == "__main__":
    result = propagate()
    print(f"Anchors used for propagation: {result['anchors']}\n")
    print(f"{'#':>3}  {'direct TV':<20} {'final (post-propagation) TV':<28} change")
    for j in sorted(result["direct"].keys()):
        d = result["direct"][j]
        f = result["final"][j]
        change = f.strength - d.strength
        arrow = "up" if change > 1e-6 else ("down" if change < -1e-6 else "same")
        print(f"{j:>3}  {str(d):<20} {str(f):<28} {arrow} ({change:+.3f})")
