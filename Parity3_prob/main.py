from parity_data import CANDIDATES, evaluate_candidate, true_outputs
from propagate import propagate

def main():
    truth = true_outputs()
    result = propagate()
    direct, final, anchors = result["direct"], result["final"], result["anchors"]

    print("=" * 72)
    print("PARITY-3 BETA-GRAPH / PLN BELIEF PROPAGATION")
    print("=" * 72)
    print(f"\nGround truth (A B C -> O), 8 rows: {truth}")
    print(f"Anchors chosen for propagation (strongest direct evidence): {anchors}\n")

    ranked_direct = sorted(direct.items(), key=lambda kv: kv[1].strength, reverse=True)
    ranked_final = sorted(final.items(), key=lambda kv: kv[1].strength, reverse=True)

    print("-" * 72)
    print("STEP A: direct evidence only (correlation / weighted count vs truth)")
    print("-" * 72)
    for idx, tv in ranked_direct:
        print(f"  Candidate #{idx:2d}: {CANDIDATES[idx]}")
        print(f"      {tv}")

    print("\n" + "-" * 72)
    print("STEP B: after belief propagation (Deduction+Induction+Abduction, merged by Revision)")
    print("-" * 72)
    for idx, tv in ranked_final:
        d = direct[idx]
        delta = tv.strength - d.strength
        print(f"  Candidate #{idx:2d}: direct s={d.strength:.3f} -> final s={tv.strength:.3f}  (delta {delta:+.3f}), confidence {tv.confidence:.3f}")

    best_direct = ranked_direct[0]
    best_final = ranked_final[0]
    print("\n" + "-" * 72)
    print("SUMMARY")
    print("-" * 72)
    print(f"Best candidate by direct evidence alone : #{best_direct[0]} ({best_direct[1]})")
    print(f"Best candidate after propagation         : #{best_final[0]} ({best_final[1]})")
    print(
        "\nNote: propagation leaves every belief unchanged here (final == direct, "
        "confidence stays at 0.5, never inflating to 1.0). Using the exact MeTTa "
        "PLN formulas with evidence stamping, no deduced/induced/abducted "
        "estimate for a candidate is ever more confident than that candidate's "
        "own direct evidence -- and since every estimate's evidence stamp "
        "always includes the candidate's own evidence, Revision is never "
        "licensed to merge them. This replaces an earlier version where "
        "confidence artificially saturated near 1.0 by treating overlapping "
        "evidence as independent; the exact formulas correctly refuse to do that."
    )


if __name__ == "__main__":
    main()
