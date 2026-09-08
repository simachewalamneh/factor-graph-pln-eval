# Factor Graph + PLN Belief-Propagation Evaluation (Parity-3)

Independent evaluation task from the "Introduction to Factor Graphs" training.
Builds a Boolean-domain Beta-graph over the Parity-3 problem and its 20
candidate programs, then propagates beliefs using the 4 core PLN rules
(Deduction, Induction, Abduction, Revision).

## What this does

1. **`src/parity_data.py`** — the Parity-3 truth table (`A xor B xor C`) and
   the 20 candidate boolean programs from the slide, plus a tiny evaluator
   for the `(AND/OR/NOT ...)` expression trees.
2. **`src/truth_value.py`** — the bridge between the classical Beta-Bernoulli
   view (`alpha`, `beta` counts) and PLN's `(strength, confidence)` view.
   `strength` = Beta mean, `confidence` = evidence-count based on
   `n / (n + K)`.
3. **`src/beta_graph.py`** — builds the factor graph:
   - **Direct-evidence factors**: each candidate's agree/disagree count
     against the ground-truth table ("correlation and weighted count").
   - **Pairwise correlation factors**: how often each pair of candidates
     agrees with *each other*.
4. **`src/pln_rules.py`** — the 4 required PLN rules, implemented as
   simplified versions of the standard PLN formulas over `TruthValue`
   objects, reflecting the logic in the MeTTa reference
   (`trueagi-io/PeTTa/lib/lib_pln.metta`).
5. **`src/propagate.py`** — belief propagation: picks the most-informative
   candidates as "anchors," chains their direct evidence through
   correlation factors (Deduction), cross-checks candidates against pairs
   of anchors (Induction/Abduction), then merges every independent
   estimate for a candidate into one final belief (Revision).
6. **`src/main.py`** — runs everything and prints a before/after report.
7. **`diagrams/factor_graph.md`** — Mermaid diagram + written explanation
   of the graph structure, as required by the deliverable.

## Running everything

Full run-through, in a sensible order. Run each from inside the folder
shown — several of these scripts assume that working directory for their
relative imports.

### 1. Main task (dense baseline)
```bash
cd src
python3 main.py
```
No third-party dependencies — pure Python 3 standard library.

### 2. Tier 1 — exact sparse optimization, with its own proof
```bash
python3 propagate_sparse.py
```
Runs the dense and sparse versions and asserts they match exactly —
ends with `PROVEN: ...` if it passes.

### 3. Tier 2 — approximate top-k / threshold variants
```bash
python3 propagate_tier2.py
```
Shows Tier 1 (exact) vs. Tier 2 top-8 vs. Tier 2 threshold=0.75 side by side.

### 4. Bonus: relational frame-space task
```bash
cd ../relational_frame_task
python3 main.py
```

### 5. Diagrams (real rendered factor graphs)
```bash
cd ../diagrams
python3 build_parity_graph.py     # renders diagrams/factor_graph_render.png
python3 build_frame_graph.py      # renders relational_frame_task/diagrams/frame_graph_render.png
```
**Requires two extra packages, only for these two scripts** — nothing
else in the repo needs them:
```bash
pip install networkx matplotlib
```

### 6. Complexity experiment (full accuracy + scaling benchmark)
```bash
cd ../benchmarks
python3 complexity_experiment.py
```
Prints the real-data accuracy table and the synthetic scaling table, and
saves `scaling_plot.png`. Takes a few seconds longer than the others
since it's timing repeated runs.

### 7. (Optional) Rebuild the conceptual LaTeX note to PDF
Only needed if you edit `notes/conceptual_note.tex` — the PDF is already
committed, so this is optional:
```bash
cd ../notes
pdflatex conceptual_note.tex
pdflatex conceptual_note.tex   # run twice, for the table of contents
```
Requires a LaTeX toolchain (`pdflatex`) — e.g.
`sudo apt install texlive-latex-base texlive-latex-extra` if you don't
have one.

### All-in-one sanity check
Confirms nothing is broken after pulling changes, without producing full
output:
```bash
cd src && python3 main.py > /dev/null \
  && python3 propagate_sparse.py | tail -2 \
  && cd ../relational_frame_task && python3 main.py > /dev/null \
  && echo "All core scripts ran cleanly"
```

## Key results (summary)
- No candidate perfectly matches parity by direct evidence (expected —
  parity isn't representable by these low-arity AND/OR/NOT combinations,
  which is exactly why this is a genuinely *uncertain* reasoning problem
  rather than a lookup).
- Direct-evidence strengths range from 0.4 to 0.6 across the 20
  candidates (some agree with truth on 6/8 rows, some on only 3-4/8).
- After propagation, most beliefs regress toward 0.5 — the correlation
  factors between candidates are themselves noisy/uninformative for most
  pairs, so chaining through them adds little genuine signal.

## A note on confidence 
The propagated **confidence** values saturate close to `1.0` for every
candidate. This is a known consequence of a simplifying assumption made
explicit rather than hidden: Revision treats every
Deduction/Induction/Abduction estimate for a given candidate as
*independent* evidence. In reality, all of these estimates trace back to
the same 8-row truth table, so they are correlated, not independent —
Revision's confidence-combination rule (`1 - (1-c1)(1-c2)...`) therefore
overstates how much is actually known.

A more rigorous version could either (a) discount Revision's confidence
gain by the estimated evidence overlap between sources, or (b) feed
Revision only genuinely independent evidence per candidate (e.g. direct
evidence plus a single best deduced estimate, rather than every
anchor-pair's induction/abduction estimate). The simpler version was kept
in place and the caveat documented here, since the goal of this exercise
was to demonstrate correct *mechanics* of all 4 rules working together —
and recognizing this independence-assumption flaw is itself part of what
the deck asks interns to do ("identify where uncertainty enters").

## PLN rule semantics (short version)

| Rule | Inputs | Meaning here |
|---|---|---|
| Deduction | `A→B`, `B→C` | anchor's correctness + its correlation with candidate j ⇒ estimate of j's correctness |
| Induction | `B→A`, `B→C` | two anchors' mutual correlation + one anchor's correlation with j ⇒ estimate |
| Abduction | `A→B`, `C→B` | both anchors correlate with j ⇒ cross-validating estimate |
| Revision | two estimates of the same statement | confidence-weighted merge into final belief |

## Reusable engine

`src/propagation_engine.py` holds the domain-agnostic Deduction/
Induction/Abduction/Revision propagation logic (anchors, chaining,
merging) with no knowledge of parity or candidates. `src/propagate.py`
is now just a thin wrapper that builds parity-specific `TruthValue`s and
hands them to this shared engine. This is what makes the bonus task
possible without duplicating any PLN logic — see `relational_frame_task/`.

## Bonus: relational frame-space task (implemented)

See [`relational_frame_task/`](relational_frame_task/) — implements the
frame-space task using the real Context-Frame data sets from the deck, a
vector-embedding similarity search (TF-IDF + cosine similarity, pure
Python), and the exact same `propagation_engine.py` reused from this
directory. Full explanation of how frame relations map to
variables/propositions/inference links is in
`relational_frame_task/README.md`.

## Complexity reduction: sparsifying correlation-factor construction

See **[`benchmarks/COMPLEXITY_INVESTIGATION.md`](benchmarks/COMPLEXITY_INVESTIGATION.md)**
for the full narrative -- the starting assumption, the check that found
belief propagation was already O(n) (not O(n^2) as originally assumed),
what was implemented, and the honest experimental verdict on each tier.

`src/beta_graph.py`'s original `build_correlation_factors()` builds a
factor for every pair of candidates — O(n²). Tracing which of those pairs
`propagation_engine.py` actually looks up shows that every lookup
involves an anchor, so roughly half the O(n²) work (at n=20, 5 anchors)
is computed and never used.

- **`src/propagate_sparse.py`** (Tier 1): reorders the pipeline to pick
  anchors first, then builds correlation factors only for anchor-involving
  pairs — O(k·n). This is an **exact** optimization: running the file
  directly proves (via assertion) that its final beliefs are identical to
  the dense baseline's, to floating-point precision. Zero accuracy cost.
- **`src/propagate_tier2.py`** (Tier 2): further restricts which
  correlation factors are *kept* (top-k neighbors per anchor, or a
  strength threshold) — a genuine approximation that can change results.
- **`benchmarks/complexity_experiment.py`** + **`benchmarks/RESULTS.md`**:
  the full experimental comparison — real-data accuracy/quality table and
  a synthetic runtime-scaling benchmark, reported honestly. **Tier 2's
  measured accuracy on this dataset was poor** (Spearman rank correlation
  near zero or negative against the exact result) — see `RESULTS.md` for
  why, and why we recommend Tier 1 but not Tier 2 as currently built.