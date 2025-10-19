import json
import sys
import csv
from typing import Any, Dict, List
from operations import *

def split_top_level_commas(s: str) -> List[str]:
    parts, cur, depth, in_str, quote_char = [], [], 0, False, ''
    for ch in s:
        if in_str:
            cur.append(ch)
            if ch == quote_char:
                in_str = False
            continue
        if ch in ('"', "'"):
            in_str = True
            quote_char = ch
            cur.append(ch)
            continue
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        elif ch == "," and depth == 0:
            parts.append("".join(cur).strip())
            cur = []
            continue
        cur.append(ch)
    if cur:
        parts.append("".join(cur).strip())
    return parts

def parse_arg(arg: str):
    arg = arg.strip()
    if not arg:
        return ""
    if arg.startswith("[") and arg.endswith("]"):
        inner = arg[1:-1].strip()
        return [] if not inner else [a.strip().strip("'\"") for a in split_top_level_commas(inner)]
    if (arg.startswith('"') and arg.endswith('"')) or (arg.startswith("'") and arg.endswith("'")):
        return arg[1:-1]
    return arg

def parse_formula(formula: str):
    formula = formula.strip()
    if "(" not in formula or not formula.endswith(")"):
        return formula, []

    idx = formula.find("(")
    op = formula[:idx].strip().upper()
    inner = formula[idx + 1:-1].strip()

    if not inner:
        raise ValueError(f"Missing arguments for {op}()")

    args = split_top_level_commas(inner)
    return op, args


def eval_formula(formula: str, tables: Dict[str, List[Dict[str, Any]]]):
    formula = formula.strip()

    # Base case
    if "(" not in formula or not formula.endswith(")"):
        if formula in tables:
            return tables[formula]
        raise ValueError(f"Unknown relation or malformed formula: {formula}")

    op, args = parse_formula(formula)

    def resolve(a: str):
        a = a.strip()
        if '(' in a and a.endswith(')'):
            head = a[:a.find('(')].strip().upper()
            known_ops = {"SELECT", "PROJECT", "JOIN", "UNION", "INTERSECT", "DIFFERENCE", "AGGREGATE"}
            if head in known_ops:
                return eval_formula(a, tables)
            return a
        if a in tables:
            return tables[a]
        return parse_arg(a)


    parsed = [resolve(a) for a in args]

    if op == "SELECT":
        rel = parsed[0]
        cond = args[1] if len(args) > 1 else ""
        return select(rel, cond)

    elif op == "PROJECT":
        rel, fields = parsed[0], parsed[1]
        return project(rel, fields)

    elif op == "JOIN":
        left, right = parsed[0], parsed[1]
        cond = args[2] if len(args) > 2 else ""
        return join(left, right, cond)

    elif op == "UNION":
        return union(parsed[0], parsed[1])

    elif op == "INTERSECT":
        return intersect(parsed[0], parsed[1])

    elif op == "DIFFERENCE":
        return difference(parsed[0], parsed[1])

    elif op == "AGGREGATE":
        rel = parsed[0]
        group = parsed[1]
        agg_part = args[2].strip()
        while agg_part.endswith(')') and agg_part.count('(') < agg_part.count(')'):
            agg_part = agg_part[:-1].strip()

        open_paren = agg_part.find('(')
        close_paren = agg_part.rfind(')')
        if open_paren == -1 or close_paren == -1:
            raise ValueError(f"Malformed aggregate expression: {agg_part}")

        fn = agg_part[:open_paren].strip().upper()
        fld = agg_part[open_paren + 1:close_paren].strip()
        return aggregate(rel, group, (fn, fld))
    
    else:
        raise ValueError(f"Unknown operation: {op}")

def write_csv(rows, path):
    if not rows:
        open(path, "w", encoding="utf-8").close(); return
    cols = []
    for r in rows:
        for k in r:
            if k not in cols: cols.append(k)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for r in rows:
            w.writerow([("" if r.get(c) is None else r.get(c)) for c in cols])

def main():
    if len(sys.argv) != 3:
        print("Usage: python main.py <data.json> <formula>")
        sys.exit(1)

    with open(sys.argv[1], "r") as f:
        tables = json.load(f)

    formula = sys.argv[2]

    result = eval_formula(formula, tables)
    print_table(result if isinstance(result, list) else [result])
    write_csv(result if isinstance(result, list) else [result], "output.csv")

if __name__ == "__main__":
    main()