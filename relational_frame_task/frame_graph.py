import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from truth_value import beta_from_counts   
from propagation_engine import propagate_generic  
from embeddings import similarity_search  
from frame_data import ALL_FRAMES, FRAMES_BY_ID, parent_child_pairs  

SIMILARITY_PSEUDO_N = 10
PARENT_CHILD_BONUS = 4

def status_to_counts(status):
    if status == "completed":
        return 1.0, 0.0
    if status == "pending":
        return 0.0, 1.0
    if status == "active":
        return 0.5, 0.5  
    raise ValueError(f"Unknown status: {status}")

def build_direct_evidence():
    """Direct evidence per frame, from its own status field."""
    direct_tv = {}
    for frame in ALL_FRAMES:
        s, f = status_to_counts(frame.status)
        belief = beta_from_counts(s, f)
        direct_tv[frame.frame_id] = belief.to_truth_value()
    return direct_tv

def build_correlation_factors():
    sims = similarity_search(ALL_FRAMES)
    parent_child = set(parent_child_pairs()) | {(b, a) for a, b in parent_child_pairs()}
    corr_tv = {}
    for (i, j), sim in sims.items():
        successes = sim * SIMILARITY_PSEUDO_N
        if (i, j) in parent_child:
            successes += PARENT_CHILD_BONUS
        successes = min(successes, SIMILARITY_PSEUDO_N + PARENT_CHILD_BONUS)
        failures = (SIMILARITY_PSEUDO_N + PARENT_CHILD_BONUS) - successes
        belief = beta_from_counts(successes, failures)
        corr_tv[(i, j)] = belief.to_truth_value()
    return corr_tv

def run(top_k_anchors=5):
    direct_tv = build_direct_evidence()
    corr_tv = build_correlation_factors()
    result = propagate_generic(direct_tv, corr_tv, top_k_anchors=top_k_anchors)
    result["parent_child_pairs"] = parent_child_pairs()
    return result

if __name__ == "__main__":
    result = run()
    print(f"Anchors: {result['anchors']}\n")
    print(f"{'frame':<6} {'status':<10} {'direct TV':<20} {'final TV':<22}")
    for frame_id in sorted(result["direct"].keys(), key=lambda x: int(x[1:])):
        frame = FRAMES_BY_ID[frame_id]
        d = result["direct"][frame_id]
        f = result["final"][frame_id]
        print(f"{frame_id:<6} {frame.status:<10} {str(d):<20} {str(f):<22}")
