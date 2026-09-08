import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def draw_factor_graph(
    variables,
    factors,
    title,
    output_path,
    variable_color="#2f6fb0",
    anchor_color="#1a3d63",
    factor_color="#e08a2e",
    figsize=(11, 9),
    layout="circular",
    hub_id=None,
    factor_styles=None,
):
    G = nx.Graph()
    for v in variables:
        G.add_node(v["id"], kind="variable", label=v["label"], anchor=v.get("anchor", False))

    var_graph = nx.Graph()
    var_graph.add_nodes_from(v["id"] for v in variables)
    for f in factors:
        if f.get("var_b") is not None:
            var_graph.add_edge(f["var_a"], f["var_b"])

    if hub_id is not None:
        ring_nodes = [v["id"] for v in variables if v["id"] != hub_id]
        ring_graph = var_graph.subgraph(ring_nodes)
        ring_pos = nx.circular_layout(ring_graph) if ring_nodes else {}
        pos = {n: p * 1.0 for n, p in ring_pos.items()}
        pos[hub_id] = (0.0, 0.0)
    elif layout == "circular":
        pos = nx.circular_layout(var_graph)
    else:
        pos = nx.spring_layout(var_graph, seed=7, k=1.6)

    factor_positions = {}
    for i, f in enumerate(factors):
        pa = pos[f["var_a"]]
        if f.get("var_b") is None:
            norm = (pa[0] ** 2 + pa[1] ** 2) ** 0.5
            if norm < 1e-6:
                dx, dy = 0.22, 0.0  # variable sits at center (e.g. a hub) -> pick a fixed direction
            else:
                dx, dy = (pa[0] / norm) * 0.22, (pa[1] / norm) * 0.22
            factor_positions[i] = (pa[0] + dx, pa[1] + dy)
        else:
            pb = pos[f["var_b"]]
            factor_positions[i] = ((pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2)

    def style_for(f):
        default = {"color": factor_color, "linestyle": "-"}
        if factor_styles and f.get("type") in factor_styles:
            merged = dict(default)
            merged.update(factor_styles[f["type"]])
            return merged
        return default

    fig, ax = plt.subplots(figsize=figsize)
    ax.set_aspect("equal")
    ax.axis("off")
    for i, f in enumerate(factors):
        fx, fy = factor_positions[i]
        vax, vay = pos[f["var_a"]]
        style = style_for(f)
        ax.plot([vax, fx], [vay, fy], color=style["color"], linewidth=1.4,
                 linestyle=style["linestyle"], zorder=1, alpha=0.8)
        if f.get("var_b") is not None:
            vbx, vby = pos[f["var_b"]]
            ax.plot([fx, vbx], [fy, vby], color=style["color"], linewidth=1.4,
                     linestyle=style["linestyle"], zorder=1, alpha=0.8)

    # Draw factor nodes
    for i, f in enumerate(factors):
        fx, fy = factor_positions[i]
        style = style_for(f)
        size = 0.045
        ax.add_patch(mpatches.FancyBboxPatch(
            (fx - size, fy - size), size * 2, size * 2,
            boxstyle="round,pad=0.002,rounding_size=0.004",
            facecolor="white", edgecolor=style["color"], linewidth=2, zorder=2,
        ))

    # Draw variable nodes
    for v in variables:
        x, y = pos[v["id"]]
        r = 0.09
        edge_w = 3.2 if v.get("anchor") else 2.0
        edge_c = anchor_color if v.get("anchor") else variable_color
        circ = mpatches.Circle((x, y), r, facecolor="white", edgecolor=edge_c,
                                linewidth=edge_w, zorder=3)
        ax.add_patch(circ)
        ax.text(x, y, v["label"], ha="center", va="center", fontsize=11,
                fontweight="bold", color=edge_c, zorder=4)

    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-1.3, 1.3)
    ax.set_title(title, fontsize=14, pad=16)

    legend_handles = [
        mpatches.Patch(facecolor="white", edgecolor=variable_color, linewidth=2, label="Variable node"),
        mpatches.Patch(facecolor="white", edgecolor=anchor_color, linewidth=3.2, label="Anchor variable"),
    ]
    if factor_styles:
        for type_name, style in factor_styles.items():
            legend_handles.append(mpatches.Patch(
                facecolor="white", edgecolor=style.get("color", factor_color),
                linewidth=2, label=f"Factor: {type_name}",
            ))
    else:
        legend_handles.append(mpatches.Patch(facecolor="white", edgecolor=factor_color, linewidth=2, label="Factor node"))
    ax.legend(handles=legend_handles, loc="lower center", bbox_to_anchor=(0.5, -0.08),
              ncol=min(len(legend_handles), 3), frameon=False, fontsize=9)

    plt.tight_layout()
    plt.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {output_path}")
