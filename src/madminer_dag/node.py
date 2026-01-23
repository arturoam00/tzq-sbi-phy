from __future__ import annotations

from typing import Any, Dict, List

from madminer_dag.schemas import NodeType, ScriptType
from madminer_dag.utils import validate_var


class Node:
    def __init__(self, name: str, script: str, type: NodeType = NodeType.JOB):
        self.name = name
        self.script = script
        self.children: List[Node] = []
        self._job = f"{type.value} {self.name} {self.script}\n"
        self._vars = ""
        self._post = ""
        self._pre = ""

    def _create_script(self, type: ScriptType, script: str, args: List[Any]) -> str:
        arguments = [str(a) for a in args]
        return f"SCRIPT {type.value} {self.name} {script} {' '.join(arguments)}\n"

    def add_vars(self, vars: Dict[str, Any]) -> None:
        variables = [f'{k.upper()}="{validate_var(v)}"' for k, v in vars.items()]
        self._vars = f"VARS {self.name} {' '.join(variables)}\n"

    def add_post(self, script: str, args: List[Any]) -> None:
        self._post = self._create_script(ScriptType.POST, script, args)

    def add_pre(self, script: str, args: List[Any]) -> None:
        self._pre = self._create_script(ScriptType.PRE, script, args)

    def add_child(self, node: Node) -> None:
        self.children.append(node)

    def __str__(self):
        return self._job + self._vars + self._pre + self._post
