import argparse
from dataclasses import fields
from pathlib import Path
from typing import Optional


def _ensure(p: Path) -> Optional[Path]:
    p = p.expanduser()
    return p if p.exists() else None


# TODO: Add support for "validation retry" in case paths are only
# available after wrapped function has been run
def validate_paths(*attr_names):
    def decorator(func):
        def wrapper(args: argparse.Namespace):
            # Preprocess
            retry = []
            for name in attr_names:
                if hasattr(args, name) and getattr(args, name) is not None:
                    p = _ensure(Path(getattr(args, name)))
                    if p is not None:
                        setattr(args, name, p)
                    else:
                        retry.append(name)

            # Wrapped function
            result = func(args)

            # postprocess: For paths created inside func
            for name in retry:
                if hasattr(args, name) and getattr(args, name) is not None:
                    path = Path(getattr(args, name))
                    p = _ensure(path)
                    if p is not None:
                        setattr(args, name, p)
                    else:
                        raise FileNotFoundError(path)

            return result

        return wrapper

    return decorator


def pack(arg_cls):
    def decorator(func):
        def wrapper(args: argparse.Namespace):
            result = func(args)
            required = [f.name for f in fields(arg_cls)]
            return arg_cls(**{k: v for k, v in vars(result).items() if k in required})

        return wrapper

    return decorator
