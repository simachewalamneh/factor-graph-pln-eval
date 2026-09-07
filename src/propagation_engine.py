from itertools import combinations
from pln_rules import deduction, induction, abduction, revision

def propagate_generic(direct_tv, corr_tv, top_k_anchors=5):
    def corr(i, j):
        return corr_tv.get((i, j)) or corr_tv.get((j, i))

    anchors = sorted(
        direct_tv.keys(),
        key=lambda i: abs(direct_tv[i].strength - 0.5),
        reverse=True,
    )[:top_k_anchors]

    all_nodes = list(direct_tv.keys())
    estimates = {j: [direct_tv[j]] for j in all_nodes}  # start with direct evidence

    # Deduction
    for i in anchors:
        for j in all_nodes:
            if i == j:
                continue
            tv_ij = corr(i, j)
            if tv_ij is None:
                continue
            estimates[j].append(deduction(direct_tv[i], tv_ij))

    # Induction & Abduction
    for a1, a2 in combinations(anchors, 2):
        for j in all_nodes:
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

    #  Revision 
    final = {}
    for j, tv_list in estimates.items():
        merged = tv_list[0]
        for tv in tv_list[1:]:
            merged = revision(merged, tv)
        final[j] = merged

    return {"anchors": anchors, "direct": direct_tv, "final": final}
