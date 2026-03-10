import torch

def get_major_labels(labels):
    """
    Map sub-class labels (0-264) to major-class labels (0-3).
    [0, 52)   -> 0 (Kitchen)
    [52, 201)  -> 1 (Recyclable)
    [201, 251) -> 2 (Other)
    [251, 265) -> 3 (Hazardous)
    """
    major = torch.zeros_like(labels)
    major[(labels >= 52) & (labels < 201)] = 1
    major[(labels >= 201) & (labels < 251)] = 2
    major[(labels >= 251)] = 3
    return major
