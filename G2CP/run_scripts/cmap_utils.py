import numpy as np
import pandas as pd

def calculate_gsea_es(ranked_genes, rank_scores, gene_set, p=1):
    """
    Calculate the Enrichment Score (ES) for GSEA, considering both positive and negative deviations.
    
    Parameters:
        ranked_genes (list): Ordered list of gene names.
        rank_scores (list): Corresponding ranking scores for the genes.
        gene_set (set): Target gene set of interest.
        p (float): Weight parameter (default is 1).
        
    Returns:
        float: Enrichment Score (ES), considering both positive and negative deviations.
        list: Cumulative enrichment scores for visualization.
    """
    # Step 1: Initialize variables
    N = len(ranked_genes)  # Total number of genes
    S = set(list(gene_set))  # Convert gene_set to a set for fast lookup
    N_hit = len(S)  # Number of genes in gene_set
    N_miss = N - N_hit  # Number of genes not in gene_set

    # Step 2: Calculate normalization factors
    weighted_scores = np.array([abs(rank_scores[i])**p if ranked_genes[i] in S else 0 
                                 for i in range(N)])
    P_hit_norm = np.sum(weighted_scores)  # Normalization factor for P_hit
    P_miss_norm = N_miss  # Normalization factor for P_miss

    # Step 3: Compute cumulative enrichment scores
    cumulative_scores = []
    P_hit, P_miss = 0, 0  # Initialize running totals
    for i in range(N):
        if ranked_genes[i] in S:
            P_hit += abs(rank_scores[i])**p / P_hit_norm  # Update P_hit
        else:
            P_miss += 1 / P_miss_norm  # Update P_miss
        cumulative_scores.append(P_hit - P_miss)  # Calculate cumulative score

    # Step 4: Determine Enrichment Score (ES)
    es = max(cumulative_scores, key=abs)  # ES is the maximum absolute deviation point
    
    return es, cumulative_scores


def calculate_wtcs(query_scores, reference_scores, landmarks, n_genes=None): 
    """
    Calculate the Weighted Connectivity Score (WTCS) for a query against a reference.

    Parameters:
        query_scores (list or np.array): Query scores for each landmark gene.
        reference_scores (list or np.array): Reference scores for each landmark gene.
        landmarks (list): List of landmark gene names.
        n_genes (int): Number of top up-regulated and down-regulated genes to consider.

    Returns:
        tuple: WTCS, ESup, and ESdown.
    """

    import numpy as np

    if n_genes:
        # Sort query scores and get the corresponding gene indices
        sorted_indices = np.argsort(query_scores)[::-1]
        sorted_landmarks = [landmarks[i] for i in sorted_indices]

        # Identify up-regulated and down-regulated genes
        qup = sorted_landmarks[:n_genes] if n_genes is not None else sorted_landmarks
        qdown = sorted_landmarks[-n_genes:] if n_genes is not None else sorted_landmarks
    else:
        # Identify up-regulated and down-regulated genes
        qup = [landmarks[i] for i, score in enumerate(query_scores) if score > 0]
        qdown = [landmarks[i] for i, score in enumerate(query_scores) if score < 0]

    # Rank reference scores
    ranked_genes = np.argsort(reference_scores)[::-1]  # Sort indices by descending score
    ranked_gene_names = [landmarks[i] for i in ranked_genes]
    ranked_scores = np.sort(reference_scores)[::-1]  # Sorted reference scores

    # Compute ES for up-regulated and down-regulated genes
    ESup, CSup = calculate_gsea_es(ranked_gene_names, ranked_scores, qup)
    ESdown, CSdown = calculate_gsea_es(ranked_gene_names, ranked_scores, qdown)

    # Compute WTCS
    if np.sign(ESup) != np.sign(ESdown):
        WTCS = (ESup - ESdown) / 2
    else:
        WTCS = 0

    return WTCS, ESup, ESdown
