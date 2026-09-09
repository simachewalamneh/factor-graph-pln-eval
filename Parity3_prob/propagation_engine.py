
from itertools import combinations

from truth_value import TruthValue
from pln_rules import deduction, induction, abduction, revision

_NEUTRAL_MEDIATOR = TruthValue(0.5, 0.5)
_NEUTRAL_STAMP = frozenset()

def select_anchors(direct_tv, top_k_anchors=5):
    """
    Pick the nodes whose direct evidence is most informative (furthest
    from an uninformative 0.5), to use as anchors for propagation.
    """
    return sorted(
        direct_tv.keys(),
        key=lambda i: abs(direct_tv[i].strength - 0.5),
        reverse=True,
    )[:top_k_anchors]


def _stamp_disjoint(s1, s2):
    return len(s1 & s2) == 0


def _merge_estimates(tv_stamp_list):
    items = list(tv_stamp_list)
    merged_something = True
    while merged_something:
        merged_something = False
        for a, b in combinations(range(len(items)), 2):
            tv_a, stamp_a = items[a]
            tv_b, stamp_b = items[b]
            if _stamp_disjoint(stamp_a, stamp_b):
                new_tv = revision(tv_a, tv_b)
                new_stamp = stamp_a | stamp_b
                items = [items[i] for i in range(len(items)) if i not in (a, b)]
                items.append((new_tv, new_stamp))
                merged_something = True
                break
    return max(items, key=lambda pair: pair[0].confidence)[0]


def propagate_generic(direct_tv, corr_tv, top_k_anchors=5, anchors=None):

    def corr(i, j):
        return corr_tv.get((i, j)) or corr_tv.get((j, i))

    if anchors is None:
        anchors = select_anchors(direct_tv, top_k_anchors)

    all_nodes = list(direct_tv.keys())
    estimates = {j: [(direct_tv[j], frozenset({j}))] for j in all_nodes}

    for i in anchors:
        for j in all_nodes:
            if i == j:
                continue
            tv_ij = corr(i, j)
            if tv_ij is None:
                continue
            result = deduction(
                P=direct_tv[i], Q=_NEUTRAL_MEDIATOR, R=direct_tv[j],
                PQ=direct_tv[i], QR=tv_ij,
            )
            stamp = frozenset({i}) | _NEUTRAL_STAMP | frozenset({i, j})
            estimates[j].append((result, stamp))

    # --- Induction & Abduction: t.
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
                ind = induction(A=direct_tv[a1], B=direct_tv[a2], C=direct_tv[j], BA=tv_a1_a2, BC=tv_a2_j)
                estimates[j].append((ind, frozenset({a1, a2, j})))
            abd = abduction(A=direct_tv[a1], B=direct_tv[j], C=direct_tv[a2], AB=tv_a1_j, CB=tv_a2_j)
            estimates[j].append((abd, frozenset({a1, a2, j})))

 
    final = {j: _merge_estimates(tv_stamp_list) for j, tv_stamp_list in estimates.items()}

    return {"anchors": anchors, "direct": direct_tv, "final": final}
