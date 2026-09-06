"""
Parity-3-specific belief propagation.

This file now just BUILDS the parity-specific direct/correlation
TruthValues (via beta_graph.py) and hands them to the shared, reusable
engine in propagation_engine.py. All the actual PLN chaining logic lives
there, so the bonus (relational frame-space) task can reuse it too.
"""

from beta_graph import build_direct_evidence_beliefs, build_correlation_factors
from propagation_engine import propagate_generic


def propagate(top_k_anchors=5):
    direct_beliefs, outputs = build_direct_evidence_beliefs()
    direct_tv = {i: b.to_truth_value() for i, b in direct_beliefs.items()}
    corr_beliefs = build_correlation_factors(outputs)
    corr_tv = {pair: b.to_truth_value() for pair, b in corr_beliefs.items()}

    return propagate_generic(direct_tv, corr_tv, top_k_anchors=top_k_anchors)


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
