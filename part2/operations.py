import json
from typing import Any, Dict, List, Tuple, Callable, Optional
from evalutation import make_eval_func
from types import SimpleNamespace

DEBUG = False

def debug(*args, **kwargs):
    if DEBUG:
        print("[DEBUG]", *args, **kwargs)

def print_table(rows: List[Dict[str, Any]]):
    if not rows:
        print("(empty result)")
        return
    
    cols = []
    for r in rows:
        for k in r.keys():
            if k not in cols:
                cols.append(k)

    widths = {c: max(len(str(c)), max(len(str(r.get(c, ""))) for r in rows)) for c in cols}
    header = " | ".join(c.ljust(widths[c]) for c in cols)
    sep = "-+-".join("-" * widths[c] for c in cols)
    print(header)
    print(sep)
    for r in rows:
        print(" | ".join(str(r.get(c, "")).ljust(widths[c]) for c in cols))


def select(table: List[Dict[str, Any]], condition_expr: str):
    if not condition_expr or not condition_expr.strip():
        return [t.copy() for t in table]
    eval_fn = make_eval_func(condition_expr)
    out = []
    for tup in table:
        try:
            if eval_fn(tup):
                out.append(tup.copy())
        except Exception as e:
            debug("SELECT evaluation error:", e, "| tuple:", tup, "| cond:", condition_expr)
            continue
    return out

def _resolve_field_from_row(row: Dict[str, Any], field: str):
    if field in row:
        return row[field]
    last = field.split('.')[-1]
    if last in row:
        return row[last]
    L = row.get('L')
    R = row.get('R')
    if isinstance(L, dict) and last in L:
        return L.get(last)
    if isinstance(R, dict) and last in R:
        return R.get(last)
    return None

def project(table: List[Dict[str, Any]], fields: List[str]):
    out = []
    for t in table:
        row = {}
        for f in fields:
            alias = None
            ff = f
            if isinstance(f, str):
                if ':' in f:
                    ff, alias = [p.strip() for p in f.split(':', 1)]
                else:
                    parts = f.split()
                    if len(parts) >= 3 and parts[-2].upper() == 'AS':
                        alias = parts[-1]
                        ff = " ".join(parts[:-2])
            
            val = _resolve_field_from_row(t, ff)
            row[alias or ff] = val
        out.append(row)
    return out

def join(left: List[Dict[str, Any]], right: List[Dict[str, Any]], condition_expr: str = ""):
    eval_fn = make_eval_func(condition_expr) if condition_expr.strip() else None
    out = []
    for l in left:
        for r in right:
            Lobj = SimpleNamespace(**l)
            Robj = SimpleNamespace(**r)
            env = {**{f"L.{k}": v for k, v in l.items()},
                   **{f"R.{k}": v for k, v in r.items()},
                   **l, **r, "L": Lobj, "R": Robj}
            try:
                ok = True if eval_fn is None else bool(eval_fn(env))
            except Exception:
                ok = False
            if ok:
                merged = {**l}
                for k, v in r.items():
                    if k in merged:
                        merged[f"R.{k}"] = v
                    else:
                        merged[k] = v

                merged["L"] = Lobj
                merged["R"] = Robj
                out.append(merged)
    return out

def _key(t):
    items = []
    for k, v in sorted(t.items()):
        try:
            sval = json.dumps(v, sort_keys=True)
        except Exception:
            sval = repr(v)
        items.append((k, sval))
    return tuple(items)

def union(a, b):
    seen, out = {}, []
    for t in a + b:
        k = _key(t)
        if k not in seen:
            seen[k] = True
            out.append(t.copy())
    return out

def intersect(a, b):
    setb = {_key(t) for t in b}
    return [t.copy() for t in a if _key(t) in setb]

def difference(a, b):
    setb = {_key(t) for t in b}
    return [t.copy() for t in a if _key(t) not in setb]

def compute_agg(values: List[Any], func: str):
    func = func.upper()
    if func == "COUNT":
        return len(values)
    if func in ("SUM", "AVG"):
        nums = []
        for v in values:
            if v is None:
                continue
            if isinstance(v, (int, float)):
                nums.append(v)
                continue
            try:
                num = float(v)
                nums.append(num)
            except Exception:
                debug("compute_agg: skipping non-numeric value for SUM/AVG:", v)
                continue
        if func == "SUM":
            return sum(nums)
        return (sum(nums) / len(nums)) if nums else None
    if func == "MIN":
        vals = [v for v in values if v is not None]
        return min(vals) if vals else None
    if func == "MAX":
        vals = [v for v in values if v is not None]
        return max(vals) if vals else None
    raise ValueError(f"Unknown aggregate function: {func}")

def aggregate(table: List[Dict[str, Any]], group_by: List[str], agg_spec: Tuple[str, str]):
    func, field = agg_spec
    groups: Dict[Tuple[Any, ...], List[Dict[str, Any]]] = {}
    if group_by:
        for t in table:
            key = tuple(_resolve_field_from_row(t, g) for g in group_by)
            groups.setdefault(key, []).append(t)
    else:
        groups[("__ALL__",)] = list(table)

    out = []
    for key, rows in groups.items():
        if field == "*" or not field:
            vals = rows
        else:
            vals = [_resolve_field_from_row(r, field) for r in rows]
        agg_value = compute_agg(vals, func)
        row = {}
        if group_by:
            for i, g in enumerate(group_by):
                row[g] = key[i]
        row[f"{func}({field})"] = agg_value
        out.append(row)
    return out
