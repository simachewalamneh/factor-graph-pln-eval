import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "relational_frame_task"))

from frame_data import DATA_SET_I, parent_child_pairs  # noqa: E402
from embeddings import similarity_search  # noqa: E402

sys.path.insert(0, os.path.dirname(__file__))
from render_factor_graph import draw_factor_graph  # noqa: E402

def build_and_render():
    frames = DATA_SET_I
    frame_ids = {f.frame_id for f in frames}

    pc_pairs = [(p, c) for p, c in parent_child_pairs() if p in frame_ids and c in frame_ids]
    pc_set = set(pc_pairs) | {(b, a) for a, b in pc_pairs}

    sims = similarity_search(frames)
    implicit_candidates = sorted(
        ((pair, s) for pair, s in sims.items() if pair not in pc_set),
        key=lambda kv: kv[1], reverse=True,
    )
    implicit_pairs = [pair for pair, _ in implicit_candidates[:3]]

    variables = [{"id": f.frame_id, "label": f.frame_id, "anchor": False} for f in frames]

    factors = []
    for f in frames:
        factors.append({"var_a": f.frame_id, "var_b": None, "label": f"status: {f.status}", "type": "status"})

    for parent, child in pc_pairs:
        factors.append({"var_a": parent, "var_b": child, "label": "parent-of", "type": "explicit"})

    for i, j in implicit_pairs:
        factors.append({"var_a": i, "var_b": j, "label": "similar", "type": "implicit"})

    out_path = os.path.join(os.path.dirname(__file__), "..", "relational_frame_task", "diagrams", "frame_graph_render.png")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    draw_factor_graph(
        variables,
        factors,
        title="Relational Frame-Space Beta-Graph (Data set I: F1-F10)",
        output_path=out_path,
        layout="circular",
        factor_styles={
            "status":   {"color": "#8a8a8a", "linestyle": "-"},
            "explicit": {"color": "#1a7a4c", "linestyle": "-"},
            "implicit": {"color": "#e08a2e", "linestyle": "--"},
        },
    )
    print(f"Explicit (parent-child) pairs drawn: {pc_pairs}")
    print(f"Implicit (similarity-discovered) pairs drawn: {implicit_pairs}")

if __name__ == "__main__":
    build_and_render()
