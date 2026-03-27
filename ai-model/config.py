import os
import torch

MODEL_PATH = "/app/model.pth"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
