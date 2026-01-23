from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Literal, NamedTuple, Optional, Tuple, Union


class Parameter(NamedTuple):
    lha_block: str
    lha_id: int
    parameter_range: Tuple[float, float]
    parameter_name: Optional[str] = None
    param_card_transform: Optional[str] = None
    morphing_max_power: int = 2


class Benchmark(NamedTuple):
    parameter_values: Dict[str, float]
    benchmark_name: Optional[str] = None
    verbose: float = True


class MorphingSetup(NamedTuple):
    max_overall_power: int = 2
    n_bases: int = 1
    include_existing_benchmarks: bool = True
    n_trials: int = 100
    n_test_thetas: int = 100


@dataclass
class DelphesSample:
    hepmc_filename: Path
    lhe_filename: Path
    delphes_filename: Path


@dataclass
class AnalysisSample(DelphesSample):
    sampled_from_benchmark: str
    is_background: bool = False
    k_factor: float = 1.0
    weights: Literal["lhe", "delphes"] = "lhe"
    systematics: Optional[List[str]] = None


"""The dataclasses below are available in `madminer.models.readers`, but 
I want to deferr hevy imports to when they are actually needed"""


class Cut(NamedTuple):
    name: str
    val_expression: str
    is_required: bool = False


class Observable(NamedTuple):
    name: str
    val_expression: Union[str, Callable]
    val_default: Optional[float] = None
    is_required: bool = False
