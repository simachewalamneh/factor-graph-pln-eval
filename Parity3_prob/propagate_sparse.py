from beta_graph import build_direct_evidence_beliefs, build_correlation_factors_sparse
from propagation_engine import propagate_generic, select_anchors

def propagate_sparse(top_k_anchors=5):
    direct_beliefs, outputs = build_direct_evidence_beliefs()
    direct_tv = {i: b.to_truth_value() for i, b in direct_beliefs.items()}

    # Anchors chosen BEFORE any correlation factor is built -- this
    # ordering is what makes the O(k*n) construction below possible.
    anchors = select_anchors(direct_tv, top_k_anchors)

    corr_beliefs = build_correlation_factors_sparse(outputs, anchors)
    corr_tv = {pair: b.to_truth_value() for pair, b in corr_beliefs.items()}

    return propagate_generic(direct_tv, corr_tv, anchors=anchors)

if __name__ == "__main__":
    from propagate import propagate as propagate_dense

    dense_result = propagate_dense()
    sparse_result = propagate_sparse()

    print(f"Dense anchors:  {dense_result['anchors']}")
    print(f"Sparse anchors: {sparse_result['anchors']}")
    assert dense_result["anchors"] == sparse_result["anchors"], "Anchor selection differs!"

    mismatches = 0
    print(f"\n{'#':>3}  {'dense final':<22} {'sparse final':<22} {'match?'}")
    for j in sorted(dense_result["final"].keys()):
        d = dense_result["final"][j]
        s = sparse_result["final"][j]
        match = (abs(d.strength - s.strength) < 1e-12) and (abs(d.confidence - s.confidence) < 1e-12)
        if not match:
            mismatches += 1
        print(f"{j:>3}  {str(d):<22} {str(s):<22} {'YES' if match else 'NO -- MISMATCH'}")

    print(f"\n{mismatches} mismatches out of {len(dense_result['final'])} candidates.")
    assert mismatches == 0, "Tier 1 is supposed to be EXACT -- any mismatch is a bug."
    print("PROVEN: Tier 1 sparse construction produces identical final beliefs to the dense baseline.")
