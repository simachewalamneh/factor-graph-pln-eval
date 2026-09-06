from frame_data import ALL_FRAMES, FRAMES_BY_ID
from frame_graph import run
from embeddings import similarity_search

def main():
    result = run()
    direct, final, anchors = result["direct"], result["final"], result["anchors"]
    pc_pairs = result["parent_child_pairs"]

    print("=" * 78)
    print("RELATIONAL FRAME-SPACE BETA-GRAPH / PLN BELIEF PROPAGATION (BONUS)")
    print("=" * 78)

    print(f"\n{len(ALL_FRAMES)} frames loaded (Context-Frames data sets I and II).")
    print(f"Anchors chosen for propagation (strongest direct evidence): {anchors}\n")

    print("-" * 78)
    print("EXPLICIT relations in the data -> inference links (parentID field)")
    print("-" * 78)
    for parent, child in pc_pairs:
        p, c = FRAMES_BY_ID[parent], FRAMES_BY_ID[child]
        print(f"  {parent} ({p.deliverable!r}) --parent-of--> {child} ({c.deliverable!r})")

    sims = similarity_search(ALL_FRAMES)
    top5 = sorted(sims.items(), key=lambda kv: kv[1], reverse=True)[:5]
    print("\n" + "-" * 78)
    print("IMPLICIT relations discovered by vector-embedding similarity search")
    print("-" * 78)
    for (i, j), sim in top5:
        print(f"  {i} <-> {j}: similarity={sim:.3f}  ({'also parent-child' if (i,j) in pc_pairs or (j,i) in pc_pairs else 'discovered independently'})")

    print("\n" + "-" * 78)
    print("STEP A: direct evidence only (status field -> 'is resolved' belief)")
    print("-" * 78)
    for frame_id in sorted(direct.keys(), key=lambda x: int(x[1:])):
        frame = FRAMES_BY_ID[frame_id]
        print(f"  {frame_id:<4} [{frame.status:<9}] {direct[frame_id]}  -- {frame.deliverable}")

    print("\n" + "-" * 78)
    print("STEP B: after belief propagation (Deduction+Induction+Abduction, merged by Revision)")
    print("-" * 78)
    for frame_id in sorted(final.keys(), key=lambda x: int(x[1:])):
        d, f = direct[frame_id], final[frame_id]
        delta = f.strength - d.strength
        print(f"  {frame_id:<4} direct s={d.strength:.3f} -> final s={f.strength:.3f}  (delta {delta:+.3f}), confidence {f.confidence:.3f}")

    print("\n" + "-" * 78)
    print("CAVEAT (same root cause as the main task, inherited from the shared engine)")
    print("-" * 78)
    print(
        "Confidence ends up near 1.0 for every frame, same as in the main task. "
        "The reason is the same too: Revision treats every deduced, induced, "
        "and abducted estimate as independent evidence, but they aren't -- many "
        "come from overlapping similarity scores and the same few anchors. "
        "Seeing the same problem here confirms the engine really is shared "
        "(src/propagation_engine.py), not rebuilt separately for each task."
    )


if __name__ == "__main__":
    main()
