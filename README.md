# UniPert-G2CP_reproduce

This repository present code and analysis pipelines for reproducing the experiments, figures, and computational analyses presented in the UniPert–G2CP study. For a user-friendly inference-oriented UniPert framework, please refer to [the official UniPert repository](https://github.com/lynn-1998/UniPert)。

## Repository Structure

```text
UniPert-G2CP_reproduce/
├── README.md
├── .gitignore
│
├── UniPert/
│   ├── unipert/                  # Core UniPert framework
│   ├── perturbation_tasks/       # Benchmark tasks and adapted baselines
│   ├── run_scripts/              # Training and evaluation scripts
│   ├── data/                     # UniPert datasets (available via Zenodo) 
│   ├── saved_models/             # UniPert checkpoints (available via Zenodo)  
│   ├── current_model/            # Released UniPert inference model (available via Zenodo)  
│   └── results/                  # UniPert outputs and evaluations (available via Zenodo)  
│
├── G2CP/
│   ├── backbone_model/           # Adapted GEARS backbone
│   ├── run_scripts/              # G2CP training and inference scripts
│   ├── data/                     # G2CP datasets (available via Zenodo)  
│   ├── saved_models/             # G2CP checkpoints (available via Zenodo)  
│   └── results/                  # G2CP outputs and evaluations (available via Zenodo) 
│
└── analysis_assets/
    ├── fig1*.ipynb               # Figure 1 analyses
    ├── fig2*.ipynb               # Figure 2 analyses
    └── figS1*.ipynb              # Figure S1 analyses
```

## Data and Checkpoints

Datasets, pretrained models, and intermediate results are distributed separately via [Zenodo](https://doi.org/10.5281/zenodo.20355906).