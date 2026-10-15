import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import pandas as pd



class CTCLoss(nn.Module):
    r"""Compound-Target Contrastive Loss"""
    def __init__(self):
        super().__init__()
        self.logit_scale = nn.Parameter(torch.ones([]) * np.log(1 / 0.07)).exp()

    def forward(self, cp_features, tgt_features, cp_ids, tgt_ids):
        device = cp_features.device
        cp_ids = torch.tensor(pd.Categorical(cp_ids).codes).to(device)
        tgt_ids = torch.tensor(pd.Categorical(tgt_ids).codes).to(device)

        # cosine similarity as logits
        # L2 normalized features
        cp_features = F.normalize(cp_features, dim=1)
        tgt_features = F.normalize(tgt_features, dim=1)
        # dot product
        logits_per_cp = self.logit_scale * cp_features @ tgt_features.t()
        logits_per_tgt = logits_per_cp.t()      # [batch_size, batch_size]

        # process repeat compound and target in the batch
        # ref: https://jianfengwang.me/How-To-Implement-Image-Text-Contrastive-loss-Correctly-in-Pytorch/ 
        label_cp = cp_ids.reshape((-1, 1)) == cp_ids.reshape((1, -1))
        label_tgt = tgt_ids.reshape((-1, 1)) == tgt_ids.reshape((1, -1))
        labels = torch.logical_or(label_cp, label_tgt).to(device)

        ctc_loss1 = -torch.sum(labels * F.log_softmax(logits_per_cp, dim=1)) / labels.sum()
        ctc_loss2 = -torch.sum(labels.t() * F.log_softmax(logits_per_tgt, dim=1)) / labels.sum()
        ctc_loss = (ctc_loss1 + ctc_loss2) / 2

        return ctc_loss