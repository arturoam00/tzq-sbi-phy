from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from madminer_dag.node import Node
from madminer_dag.schemas import NodeType
from madminer_dag.typing import PathLike
from madminer_dag.utils import validate_var


class DAG:

    def __init__(self, filename: PathLike, name: Optional[str] = None) -> None:
        self.filename = Path(filename).with_suffix(".dag")
        self.name = name if name else self.filename.stem
        self._contents = []
        self._nodes: List[Node] = []
        self._subdags: List[DAG] = []
        self._dag = ""
        self._is_compiled = False
        self._is_splice = False

    @property
    def dirname(self) -> Path:
        return self.filename.parent

    @property
    def is_splice(self) -> bool:
        return self._is_splice

    @property
    def dag(self) -> str:
        if not self._is_compiled:
            self.compile()
        return self._dag

    def add(self, string: str) -> None:
        self._contents.append(string + "\n")

    def add_subdag(
        self, dag: DAG, is_splice: bool = False, from_parent: Optional[Node] = None
    ) -> None:
        dag._is_splice = is_splice
        if is_splice:
            self._contents.append(f"SPLICE {dag.name} {dag.filename}\n")

        if from_parent is not None:
            assert from_parent in self._nodes
            from_parent.add_child(Node(name=dag.name, script="", type=NodeType.SPLICE))

        self._subdags.append(dag)

    def add_global_vars(self, vars: Dict[str, Any]) -> None:
        variables = [
            f'VARS ALL_NODES {k.upper()}="{validate_var(v)}"' for k, v in vars.items()
        ]
        self._contents.append("\n".join(variables) + "\n")

    def add_node(self, node: Node, from_parent: Optional[Node] = None) -> None:
        self._nodes.append(node)
        self._contents.append(node)
        if from_parent is not None:
            assert from_parent in self._nodes
            from_parent.add_child(node)

    def compile(self) -> None:
        self._dag = "\n".join(str(c) for c in self._contents)
        for node in self._nodes:
            if node.children:
                self._dag += f"\nPARENT {node.name} CHILD {' '.join(child.name for child in node.children)}"

        for subdag in self._subdags:
            subdag.compile()

        self._is_compiled = True

    def write(self) -> None:
        self.dirname.mkdir(parents=True, exist_ok=True)

        with open(self.filename, "w") as f:
            f.write(self.dag)

        for subdag in self._subdags:
            subdag.write()
