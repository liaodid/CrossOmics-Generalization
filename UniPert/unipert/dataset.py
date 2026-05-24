import os
import pandas as pd
from torch.utils.data import Dataset
from collections import defaultdict


class CTPairDataset(Dataset):
    """
    Dataset of Compounds-arget Iterations for Align Training
    """
    def __init__(self, pair_file):
        # pair_file = os.path.join(DATA_DIR, 'processed_pubchem_CPI_24Jan_cid8533_ua4250_i53963.csv')
        self.data = pd.read_csv(pair_file).loc[:, ['canonical_smiles', 'UniProt accession']].drop_duplicates().dropna()
        self.sm = list(self.data.iloc[:, 0])
        self.ua = list(self.data.iloc[:, 1])
        print(f"CTPairDataset: {len(self.data)} pairs, {len(set(self.sm))} compounds, {len(set(self.ua))} targets loaded.")
    def __len__(self):
        return len(self.data)
    def __getitem__(self, idx):
        cp_sm = str(self.sm[idx])     # smiles
        tgt_ua = str(self.ua[idx])    # uniprot accession
        return (cp_sm, tgt_ua)
