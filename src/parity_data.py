from itertools import product
TRUTH_TABLE = [
    ((0, 0, 0), 0),
    ((0, 0, 1), 1),
    ((0, 1, 0), 1),
    ((0, 1, 1), 0),
    ((1, 0, 0), 1),
    ((1, 0, 1), 0),
    ((1, 1, 0), 0),
    ((1, 1, 1), 1),
]

assert len(TRUTH_TABLE) == 8
for (a, b, c), o in TRUTH_TABLE:
    assert o == (a ^ b ^ c), "check table really is A xor B xor C"

def eval_expr(expr, values):
    if isinstance(expr, str):
        return values[expr]
    op = expr[0]
    if op == "NOT":
        return 1 - eval_expr(expr[1], values)
    if op == "AND":
        return eval_expr(expr[1], values) & eval_expr(expr[2], values)
    if op == "OR":
        return eval_expr(expr[1], values) | eval_expr(expr[2], values)
    raise ValueError(f"Unknown op: {op}")
# The hypothesis 
CANDIDATES = {
    1: ("AND", "A", ("OR", "B", "C")),
    2: ("OR", ("AND", "A", "B"), "C"),
    3: ("NOT", ("AND", "A", ("OR", "B", "C"))),
    4: ("OR", ("NOT", "A"), ("AND", "B", "C")),
    5: ("AND", ("OR", "A", "B"), ("NOT", "C")),
    6: ("OR", ("AND", "A", ("NOT", "B")), ("AND", "B", "C")),
    7: ("AND", ("NOT", "A"), ("OR", "B", ("NOT", "C"))),
    8: ("OR", ("NOT", ("AND", "A", "B")), "C"),
    9: ("AND", ("OR", "A", ("NOT", "B")), ("OR", "B", "C")),
    10: ("NOT", ("OR", ("AND", "A", "C"), "B")),
    11: ("OR", ("AND", "A", "B"), ("AND", ("NOT", "A"), "C")),
    12: ("AND", ("OR", "A", "C"), ("OR", ("NOT", "B"), "C")),
    13: ("OR", ("AND", ("NOT", "A"), "B"), ("AND", "A", "C")),
    14: ("NOT", ("AND", ("OR", "A", "B"), ("NOT", "C"))),
    15: ("AND", ("NOT", ("OR", "A", "C")), ("OR", "B", "C")),
    16: ("OR", ("AND", "A", ("NOT", "C")), ("AND", ("NOT", "B"), "C")),
    17: ("AND", ("OR", ("NOT", "A"), "B"), ("NOT", ("AND", "B", "C"))),
    18: ("OR", ("NOT", ("OR", "A", "B")), ("AND", "A", "C")),
    19: ("AND", ("OR", "A", ("AND", "B", "C")), ("OR", ("NOT", "B"), "C")),
    20: ("OR", ("AND", "A", ("NOT", "B")), ("AND", ("OR", "B", "C"), ("NOT", "A"))),
}

def evaluate_candidate(expr):
    outputs = []
    for (a, b, c), _ in TRUTH_TABLE:
        outputs.append(eval_expr(expr, {"A": a, "B": b, "C": c}))
    return outputs

def true_outputs():
    return [o for _, o in TRUTH_TABLE] # only returns truth value not A,B,C

if __name__ == "__main__":
    truth = true_outputs()
    print(f"{'#':>3}  {'outputs':<10} matches truth?")
    for idx, expr in CANDIDATES.items():
        out = evaluate_candidate(expr)
        agree = sum(1 for x, y in zip(out, truth) if x == y) # compare against truth
        print(f"{idx:>3}  {''.join(map(str, out))}   {agree}/8 agree")
