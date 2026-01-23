from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Dict, Optional

from madminer_dag.dag import DAG
from madminer_dag.node import Node
from madminer_dag.schemas import PhPhases
from madminer_dag.typing import PathLike

__all__ = ["PhMetaDAG"]


class PhDAG(DAG):
    def __init__(self, id: int, dirname: PathLike, **kwds):
        super().__init__(Path(dirname) / f"{id}.dag", **kwds)
        self.id = id
        self.phases = {
            PhPhases.PREPARE_GENERATION: self.add_prepare_generation,
            PhPhases.RUN_GENERATION: self.add_run_generation,
            PhPhases.RUN_DELPHES: self.add_run_delphes,
            PhPhases.RUN_ANALYSIS: self.add_run_analysis,
        }

    def add_prepare_generation(
        self, parent_node: Optional[Node] = None, **kwds
    ) -> Node:
        node = Node(
            name=f"PREPARE_GENERATION_{self.id}", script="submit/prepare_generation.sub"
        )
        job_vars = [
            "cards_dir",
            "proc_card",
            "run_card",
            "param_card",
            "pythia_card",
            "benchmark",
            "proc_dir",
        ]
        node.add_vars({k: v for k, v in kwds.items() if k in job_vars})
        node.add_post(
            script="scripts/POST_prepare_generation",
            args=[
                self.id,
                "$JOBID",
                kwds["proc_dir"],
                kwds["n_subprocesses"],
                kwds["benchmark"],
                kwds["reweight_card_insert"],
                kwds["tmp_dir"],
                self.filename.parent,
            ],
        )
        self.add_node(node, from_parent=parent_node)
        return node

    def add_run_generation(self, parent_node: Optional[Node] = None, **kwds) -> Node:
        node = Node(
            name=f"RUN_GENERATION_{self.id}", script="submit/run_generation.sub"
        )
        node.add_vars({"ngen": self.id})
        self.add_node(node, from_parent=parent_node)
        return node

    def add_run_delphes(self, parent_node: Optional[Node] = None, **kwds) -> Node:
        node = Node(name=f"RUN_DELPHES_{self.id}", script="submit/run_delphes.sub")
        node.add_vars({"ngen": self.id})
        self.add_node(node, from_parent=parent_node)
        return node

    def add_run_analysis(self, parent_node: Optional[Node] = None, **kwds) -> Node:
        node = Node(name=f"RUN_ANALYSIS_{self.id}", script="submit/run_analysis.sub")
        node.add_vars({"ngen": self.id})
        self.add_node(node, from_parent=parent_node)
        return node

    def add_from_phase(self, phase: PhPhases, **kwds) -> None:
        if phase not in self.phases:
            raise ValueError(
                f"Invalid phase: {phase}. Valid phases are: {self.phases.keys()}"
            )
        parent_node = self.phases[phase](parent_node=None, **kwds)
        for i in range(phase + 1, max(self.phases) + 1):
            node = self.phases[i](parent_node=parent_node, **kwds)  # type: ignore
            parent_node = node


class PhMetaDAG(DAG):
    def __init__(self, filename: PathLike, conf: Dict[str, Any], **kwds) -> None:
        super().__init__(filename, **kwds)
        self._conf = self.preprocess_conf(conf)
        self.gvars_filename = None
        self.gvars = {}

    @staticmethod
    def preprocess_conf(conf: Dict[str, Any]) -> Dict[str, Any]:
        conf["setup_file"] = str(Path(conf["setup_dir"]) / conf["setup_file"])
        return conf

    @staticmethod
    def get_proc_dir(base_dir: PathLike, cards_dir: PathLike, benchmark: str) -> Path:
        cdir = str(Path(cards_dir).name)
        return Path(base_dir) / (cdir + "_" + benchmark)

    def init_directory(self) -> None:
        if self.dirname.exists() and self.dirname.is_dir():
            shutil.rmtree(self.dirname)
        self.dirname.mkdir(parents=True, exist_ok=True)

    def run(
        self,
        gvars_filename: str = "global.vars.dag",
        dag_conf: Optional[PathLike] = None,
    ) -> None:
        self.init_directory()

        # 1. Add Config
        if dag_conf:
            self.add(f"CONFIG {dag_conf}")

        # 2. Add global variables (across all DAGs)
        # NOTE: DON'T include them in MetaDAG (naming collisions)
        self.gvars_filename = self.dirname / gvars_filename
        gvars_subdag = DAG(filename=self.gvars_filename)

        # gvars_keys = [
        #     "setup_file",
        #     "setup_conf",
        #     "mg_dir",
        #     "delphes_dir",
        #     "ld_library_path",
        #     "tmp_dir",
        #     "observables",
        #     "h5_dir",
        #     "delphes_card",
        #     "root_files_dir",
        # ]

        self.gvars = {k: v for k, v in self._conf.items() if isinstance(v, str)}
        gvars_subdag.add_global_vars(self.gvars)
        self.add_subdag(gvars_subdag)

        # 3. Add physics subdags
        self.add_ph_subdags()

        # 4. Add additional output files
        status_filename = self.dirname / (self.filename.name + ".status")
        self.add(f"NODE_STATUS_FILE {status_filename} 45")
        dot_filename = str(self.filename).replace(".dag", ".dot")
        self.add(f"DOT {dot_filename}")

        self.compile()
        self.write()

    def add_ph_subdags(self) -> None:
        # 1. Add setup step
        setup_node = Node(name="RUN_SETUP", script="submit/run_setup.sub")
        setup_vars = ["setup_file", "setup_conf", "log_dir"]
        setup_node.add_vars({k: v for k, v in self._conf.items() if k in setup_vars})
        pre_setup_vars = [
            "setup_dir",
            "tmp_dir",
            "h5_dir",
            "processes_dir",
            "log_dir",
        ]
        setup_node.add_pre(
            script="scripts/PRE_run_setup",
            args=[self._conf[v] for v in pre_setup_vars],
        )
        self.add_node(setup_node)

        # 2. Add subdags from config file
        c = 1
        ph_subdags_names = []
        for process in self._conf["processes"]:
            proc_dir = self.get_proc_dir(
                base_dir=self._conf["processes_dir"],
                cards_dir=process["cards_dir"],
                benchmark=process["benchmark"],
            )
            process.update({"proc_dir": proc_dir, "tmp_dir": self._conf["tmp_dir"]})
            for _ in range(int(process["runs"])):
                ph_subdag = PhDAG(id=c, dirname=self.dirname / str(c), name=f"PH_{c}")
                if self.gvars_filename is not None:
                    ph_subdag.add(f"INCLUDE {self.gvars_filename}")
                ph_subdag.add_global_vars({"log_dir": ph_subdag.dirname})

                # Start from first phase (prepare generation)
                ph_subdag.add_from_phase(PhPhases.PREPARE_GENERATION, **process)

                self.add_subdag(ph_subdag, is_splice=True, from_parent=setup_node)
                ph_subdags_names.append(ph_subdag.name)
                c += 1

        # 4. Run data augmentation
        h5_dir = self.gvars["h5_dir"]
        augment_node = Node(
            name="RUN_AUGMENTATION", script="submit/run_augmentation.sub"
        )
        augment_vars = self._conf["augmentation"]
        augment_vars.update(
            {
                "events_file": Path(h5_dir).parent / (Path(h5_dir).parent.name + ".h5"),
                "log_dir": self.gvars["log_dir"],
            }
        )
        augment_node.add_vars(augment_vars)
        augment_node.add_pre(
            script="scripts/PRE_run_augmentation", args=[h5_dir, self.gvars["log_dir"]]
        )
        self.add_node(augment_node)

        # TODO: This is ugly af but as of now subdags are not nodes and
        # therefore cannot have children. A quick fix would be to create
        # 'fake' parent nodes with `Node(name=ph_subdag.name, script="")` and
        # allow for multiple parents in `from_parent` constructor of Node,
        # then `augment_node = Node(..., from_parents=[phsb.name for phsb in ph_subdags])`
        # Note that this 'fake' nodes already exist, since act as childs of `setup_node`
        self.add(f"PARENT {' '.join(ph_subdags_names)} CHILD {augment_node.name}")
