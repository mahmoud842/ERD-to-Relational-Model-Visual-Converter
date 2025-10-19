from typing import Any, Dict

def make_eval_func(expr: str):
    code = compile(expr, filename="<condition>", mode="eval")

    def eval_fn(env: Dict[str, Any]):
        return eval(code, {}, env)
    
    return eval_fn
