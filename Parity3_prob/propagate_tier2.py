from beta_graph import (
    build_direct_evidence_beliefs,
    build_correlation_factors_topk,
    build_correlation_factors_threshold,
)
from propagation_engine import propagate_generic, select_anchors

def propagate_topk(top_k_anchors=5, k_neighbors=8):
    direct_beliefs, outputs = build_direct_evidence_beliefs()
    direct_tv = {i: b.to_truth_value() for i, b in direct_beliefs.items()}
    anchors = select_anchors(direct_tv, top_k_anchors)

    corr_beliefs = build_correlation_factors_topk(outputs, anchors, k_neighbors)
    corr_tv = {pair: b.to_truth_value() for pair, b in corr_beliefs.items()}

    return propagate_generic(direct_tv, corr_tv, anchors=anchors)


def propagate_threshold(top_k_anchors=5, threshold=0.75):
    direct_beliefs, outputs = build_direct_evidence_beliefs()
    direct_tv = {i: b.to_truth_value() for i, b in direct_beliefs.items()}
    anchors = select_anchors(direct_tv, top_k_anchors)

    corr_beliefs = build_correlation_factors_threshold(outputs, anchors, threshold)
    corr_tv = {pair: b.to_truth_value() for pair, b in corr_beliefs.items()}

    return propagate_generic(direct_tv, corr_tv, anchors=anchors)

if __name__ == "__main__":
    from propagate_sparse import propagate_sparse

    exact = propagate_sparse()
    topk = propagate_topk(k_neighbors=8)
    thresh = propagate_threshold(threshold=0.75)

    print(f"{'#':>3}  {'Tier1 exact':<20} {'Tier2 top-8':<20} {'Tier2 thresh=.75':<20}")
    for j in sorted(exact["final"].keys()):
        e, t, h = exact["final"][j], topk["final"][j], thresh["final"][j]
        print(f"{j:>3}  {str(e):<20} {str(t):<20} {str(h):<20}")
