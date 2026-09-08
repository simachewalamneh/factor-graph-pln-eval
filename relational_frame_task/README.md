# Bonus: Relational Frame-Space Belief Propagation

Extends the main Parity-3 task to the relational frame space described in
the training's bonus objective, using the real Context-Frame data sets
from the deck (F1-F20).

## Reuse (this was the point of the exercise)

This directory does **not** reimplement any PLN math. It imports directly
from `../src/`:
- `truth_value.py` (`beta_from_counts`) — same Beta-Bernoulli bridge used
  by the main task.
- `propagation_engine.py` (`propagate_generic`) — the exact same
  Deduction/Induction/Abduction/Revision engine, unmodified.

Only two things are new here: the frame data itself, and how frame
relations get turned into `TruthValue`s that the shared engine can
consume.

## Mapping frame relations -> variables / propositions / inference links

| Frame concept | Maps to |
|---|---|
| A frame's `status` field | **Proposition**: "this frame is resolved." `completed` → strong evidence for; `pending` → strong evidence against; `active` → genuinely ambiguous (still in progress), so evidence is split 50/50. |
| `parentID` (explicit relation) | **Inference link**, structural: every (parent, child) pair gets a correlation factor with bonus evidence on top of their text similarity, since this relation is given directly in the data rather than inferred. |
| Any other frame pair (implicit relation) | **Inference link**, discovered: correlation factor comes purely from vector-embedding similarity search over the frame's text (`deliverable` + `results`). |

## Vector-embedding similarity search

`embeddings.py` builds a TF-IDF-weighted bag-of-words vector per frame
and compares them with cosine similarity. This is an explicit
simplification of a real embedding model (no network access to an
embedding API in this environment) — same underlying idea (text → vector
→ compare vectors), fully self-contained, pure Python standard library.

Sanity check: the top similarity scores line up almost exactly with the
explicit parent-child pairs (F1↔F2, F12↔F13, F3↔F4, F19↔F20), which is a
good sign the similarity measure is picking up genuine topical overlap
rather than noise.

## Diagram

See `diagrams/frame_graph_render.png` for the graph structure — direct-evidence factors, explicit (parentID) links, implicit (similarity) links, and the propagation step.

## Running it

```bash
cd relational_frame_task
python3 main.py
```

## Same caveat as the main task (on purpose, left visible)

Confidence saturates near 1.0 for every frame. This is the identical
issue documented in the main task's README — Revision treats
non-independent estimates as if they were independent. It shows up here
too specifically *because* the engine is genuinely shared, not
reimplemented — which was the point of building it this way.