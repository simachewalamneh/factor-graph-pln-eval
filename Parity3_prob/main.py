 
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
        "\nNote: the confidence values end up almost 1.0 for every candidate. "
        "This is because Revision treats each new estimate as independent "
        "evidence, but they aren't , they all come from the same 8-row "
        "truth table. So confidence grows too fast and becomes misleading. "
        "A better version would use fewer, truly independent estimates "
        "per candidate instead of combining every one we generated."
    ) 

if __name__ == "__main__":
    main()
