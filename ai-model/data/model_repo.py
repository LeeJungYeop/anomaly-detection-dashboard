import os

import torch
import torch.nn as nn
from torchvision import models

from config import MODEL_PATH, DEVICE

_model = None


def get_model():
    global _model
    if _model is not None:
        return _model

    model = models.googlenet(pretrained=True)
    model.fc = nn.Linear(model.fc.in_features, 2)

    if os.path.exists(MODEL_PATH):
        model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
        print("Pretrained model loaded")
    else:
        print("No pretrained model found. Using random weights.")

    model.to(DEVICE)
    model.eval()
    _model = model
    return _model
