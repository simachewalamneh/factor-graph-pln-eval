
import os
import random
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from beta_graph import (  # noqa: E402
    build_direct_evidence_beliefs,
    build_correlation_factors,
    build_correlation_factors_sparse,
    build_correlation_factors_topk,
    build_correlation_factors_threshold,
    agreement_counts,
)
from truth_value import beta_from_counts  # noqa: E402
from propagation_engine import propagate_generic, select_anchors  # noqa: E402
from propagate import propagate as propagate_dense  # noqa: E402
from propagate_sparse import propagate_sparse  # noqa: E402
from propagate_tier2 import propagate_topk, propagate_threshold  # noqa: E402

# Experiment 1: accuracy/quality on the REAL Parity-3 data

def spearman_rank_correlation(values_a, values_b):
    def ranks(values):
        order = sorted(range(len(values)), key=lambda i: values[i])
        r = [0] * len(values)
        for rank, idx in enumerate(order):
            r[idx] = rank
        return r

    ra, rb = ranks(values_a), ranks(values_b)
    n = len(ra)
    mean_a, mean_b = sum(ra) / n, sum(rb) / n
    cov = sum((ra[i] - mean_a) * (rb[i] - mean_b) for i in range(n))
    var_a = sum((x - mean_a) ** 2 for x in ra)
    var_b = sum((x - mean_b) ** 2 for x in rb)
    if var_a == 0 or var_b == 0:
        return float("nan")
    return cov / (var_a * var_b) ** 0.5


def mean_abs_strength_deviation(reference_final, variant_final):
    ids = sorted(reference_final.keys())
    diffs = [abs(reference_final[i].strength - variant_final[i].strength) for i in ids]
    return sum(diffs) / len(diffs)


def time_it(fn, repeats=200):
    start = time.perf_counter()
    for _ in range(repeats):
        fn()
    elapsed = time.perf_counter() - start
    return elapsed / repeats


def run_accuracy_experiment():
    print("=" * 78)
    print("EXPERIMENT 1: accuracy/quality on the REAL 20-candidate Parity-3 data")
    print("=" * 78)

    reference = propagate_sparse()  # Tier 1: proven identical to the dense baseline
    ref_ids = sorted(reference["final"].keys())
    ref_strengths = [reference["final"][i].strength for i in ref_ids]

    variants = {
        "Tier 0/1 (dense/exact-sparse, identical)": propagate_sparse,
        "Tier 2 top-8":     lambda: propagate_topk(k_neighbors=8),
        "Tier 2 top-4":     lambda: propagate_topk(k_neighbors=4),
        "Tier 2 thresh=0.60": lambda: propagate_threshold(threshold=0.60),
        "Tier 2 thresh=0.75": lambda: propagate_threshold(threshold=0.75),
    }

    rows = []
    for name, fn in variants.items():
        result = fn()
        strengths = [result["final"][i].strength for i in ref_ids]
        rank_corr = spearman_rank_correlation(ref_strengths, strengths)
        mae = mean_abs_strength_deviation(reference["final"], result["final"])
        runtime_ms = time_it(fn, repeats=50) * 1000
        rows.append((name, rank_corr, mae, runtime_ms))

    print(f"\n{'Variant':<32} {'Spearman vs Tier1':>18} {'MAE strength':>14} {'Runtime (ms)':>14}")
    for name, rank_corr, mae, runtime_ms in rows:
        rc_str = f"{rank_corr:.4f}" if rank_corr == rank_corr else "n/a"  # NaN check
        print(f"{name:<32} {rc_str:>18} {mae:>14.4f} {runtime_ms:>14.4f}")

    return rows

def synthetic_outputs(n_candidates, n_rows=8, seed=0):
    rng = random.Random(seed)
    return {i: [rng.randint(0, 1) for _ in range(n_rows)] for i in range(n_candidates)}


def time_dense_construction(outputs):
    start = time.perf_counter()
    build_correlation_factors(outputs)
    return time.perf_counter() - start


def time_sparse_construction(outputs, top_k_anchors=5):
    anchors = list(outputs.keys())[:top_k_anchors]
    start = time.perf_counter()
    build_correlation_factors_sparse(outputs, anchors)
    return time.perf_counter() - start


def run_scaling_experiment(sizes=(20, 50, 100, 200, 400, 800, 1600)):
    print("\n" + "=" * 78)
    print("EXPERIMENT 2: runtime scaling on SYNTHETIC data (construction cost only)")
    print("=" * 78)
    print("(labelled synthetic throughout -- NOT the real Parity-3 accuracy result)\n")

    results = []
    for n in sizes:
        outputs = synthetic_outputs(n)
        dense_t = time_dense_construction(outputs)
        sparse_t = time_sparse_construction(outputs)
        results.append((n, dense_t, sparse_t))
        print(f"  n={n:<5} dense (O(n^2)): {dense_t*1000:8.3f} ms   sparse (O(k*n)): {sparse_t*1000:7.3f} ms   speedup: {dense_t/sparse_t:6.1f}x")

    return results


def plot_scaling(results, output_path):
    import matplotlib.pyplot as plt

    ns = [r[0] for r in results]
    dense_ms = [r[1] * 1000 for r in results]
    sparse_ms = [r[2] * 1000 for r in results]

    fig, ax = plt.subplots(figsize=(8, 5.5))
    ax.plot(ns, dense_ms, marker="o", label="Dense construction O(n\u00b2)", color="#c0392b")
    ax.plot(ns, sparse_ms, marker="o", label="Sparse construction O(k\u00b7n)", color="#2f6fb0")
    ax.set_xlabel("n (number of candidates, SYNTHETIC data)")
    ax.set_ylabel("Construction time (ms)")
    ax.set_title("Correlation-factor construction: dense vs.\nsparse (Tier 1), synthetic scaling")
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"\nSaved scaling plot: {output_path}")


if __name__ == "__main__":
    accuracy_rows = run_accuracy_experiment()
    scaling_rows = run_scaling_experiment()
    plot_path = os.path.join(os.path.dirname(__file__), "scaling_plot.png")
    plot_scaling(scaling_rows, plot_path)
