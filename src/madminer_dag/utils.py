def validate_var(v: str) -> str:
    v = str(v)
    # who knows why so many ...
    return v.replace(" ", "").replace('"', '\\\\\\"').replace("'", '\\\\\\"')
