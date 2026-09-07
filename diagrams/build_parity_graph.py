import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from propagate import propagate  # noqa: E402
from beta_graph import build_direct_evidence_beliefs, build_correlation_factors  # noqa: E402
from render_factor_graph import draw_factor_graph  # noqa: E402

def build_and_render():
    result = propagate()
    anchors = result["anchors"]  # real anchors, e.g. [1, 2, 3, 4, 5]

    direct_beliefs, outputs = build_direct_evidence_beliefs()
    corr_beliefs = build_correlation_factors(outputs)

    def corr_belief(i, j):
        return corr_beliefs.get((i, j)) or corr_beliefs.get((j, i))

    non_anchors = [c for c in direct_beliefs if c not in anchors]
    non_anchors_sorted = sorted(
        non_anchors,
        key=lambda c: max(corr_belief(a, c).mean for a in anchors),
        reverse=True,
    )
    extra = non_anchors_sorted[:2]

    included = anchors + extra
    variables = [{"id": "T", "label": "Truth", "anchor": False}]
    variables += [
        {"id": f"C{c}", "label": f"C{c}", "anchor": (c in anchors)}
        for c in included
    ]

    factors = []
    for c in included:
        factors.append({"var_a": "T", "var_b": f"C{c}", "label": "direct evidence"})

    for i in range(len(anchors)):
        a, b = anchors[i], anchors[(i + 1) % len(anchors)]
        factors.append({"var_a": f"C{a}", "var_b": f"C{b}", "label": "correlates"})

    for c in extra:
        best_anchor = max(anchors, key=lambda a: corr_belief(a, c).mean)
        factors.append({"var_a": f"C{best_anchor}", "var_b": f"C{c}", "label": "correlates"})

    out_path = os.path.join(os.path.dirname(__file__), "factor_graph_render.png")
    draw_factor_graph(
        variables,
        factors,
        title="Parity-3 Beta-Graph (core subgraph: Truth, real anchors, 2 non-anchor candidates)",
        output_path=out_path,
        hub_id="T",
    )
    print(f"Anchors used: {anchors}")
    print(f"Extra non-anchor candidates shown: {extra}")


if __name__ == "__main__":
    build_and_render()
