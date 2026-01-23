# Get started
Clone the repo 
```bash 
git clone https://github.com/arturoam00/tzq-sbi-phy
```
and install the dependencies
```bash 
cd tzq-sbi-phy
python3 -venv .venv && source ./.venv/bin/activate
python -m pip install -r requirements.txt
```

To create a [DAG](https://htcondor.readthedocs.io/en/latest/automated-workflows/index.html) for the one dimensional experiment, run
```bash
madminer-dag create -c conf/experiment_so_cht
```

## Redoing experiments
It might be the case that you need to redo event generation pipeline from an intermediate step. Try 
```bash
madminer-dag redo --help
```
to see the different options available. If you just want to redo augmentation on an already created `dag` experiment, do:
```bash
madminer-dag redo -e `dag/the_experiment_dir` -p augmentation
```
