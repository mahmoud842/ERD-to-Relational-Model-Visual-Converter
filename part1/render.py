from typing import Dict, List, Any, Optional
from graphviz import Digraph

def esc(s: str) -> str:
        return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
    
def port_name(s: str) -> str:
    return str(s).replace('"', '').replace(" ", "_").replace("-", "_").replace(".", "_")

def tables_to_graph(tables: Dict[str, List[Dict[str, Any]]], filename: str) -> str:

    g = Digraph(name="ER", format="png")
    g.attr(rankdir="LR")
    g.attr("node", shape="plaintext")

    # build nodes
    for tbl_name, cols in tables.items():
        parts = ['<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0">']
        parts.append(f'<TR><TD BGCOLOR="#b3cde0" COLSPAN="1"><B>{esc(tbl_name)}</B></TD></TR>')
        for col in cols:
            col_label = esc(col["name"])
            if col.get("primary"):
                col_label = f'<U><B>{col_label}</B></U>'
            if col.get("foreign"):
                col_label = f'<I>{col_label}</I>'
            port = port_name(col["name"])
            parts.append(f'<TR><TD ALIGN="LEFT" PORT="{port}">{col_label}</TD></TR>')
        parts.append('</TABLE>>')
        label = "".join(parts)
        g.node(tbl_name, label=label)

    # add edges for foreign keys
    for tbl_name, cols in tables.items():
        for col in cols:
            ref = col.get("references")
            if isinstance(ref, dict):
                to_table = ref["table"]
                to_attr = ref["attribute"]
                from_port = port_name(col["name"])
                to_port = port_name(to_attr)
                g.edge(f"{tbl_name}:{from_port}", f"{to_table}:{to_port}", arrowhead="normal")

    g.render(filename=filename, format="png", cleanup=True)
