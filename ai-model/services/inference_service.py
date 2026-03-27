import io
import base64

import numpy as np
import torch
from PIL import Image
from torchvision import transforms

from config import DEVICE
from data.model_repo import get_model
from models import PredictResponse

transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

feature_maps = {}
gradients = {}


def _forward_hook(module, input, output):
    feature_maps['value'] = output


def _backward_hook(module, grad_input, grad_output):
    gradients['value'] = grad_output[0]


def _register_hooks(model):
    model.inception5b.register_forward_hook(_forward_hook)
    model.inception5b.register_full_backward_hook(_backward_hook)


def _apply_jet_colormap(grayscale: np.ndarray) -> np.ndarray:
    v = (np.clip(grayscale, 0, 1) * 255).astype(np.int32)
    step = 64
    r = np.zeros_like(v, dtype=np.uint8)
    g = np.zeros_like(v, dtype=np.uint8)
    b = np.zeros_like(v, dtype=np.uint8)

    mask = v < step
    g[mask] = (v[mask] * 4).astype(np.uint8)
    b[mask] = 255

    mask = (v >= step) & (v < step * 2)
    g[mask] = 255
    b[mask] = (255 - (v[mask] - step) * 4).astype(np.uint8)

    mask = (v >= step * 2) & (v < step * 3)
    r[mask] = ((v[mask] - step * 2) * 4).astype(np.uint8)
    g[mask] = 255

    mask = v >= step * 3
    r[mask] = 255
    g[mask] = (255 - (v[mask] - step * 3) * 4).astype(np.uint8)

    return np.stack([r, g, b], axis=-1)


def _generate_heatmap(image: Image.Image, input_tensor: torch.Tensor) -> str:
    model = get_model()
    input_tensor.requires_grad_(True)
    output = model(input_tensor)

    pred_class = output.argmax(dim=1).item()
    model.zero_grad()
    output[0, pred_class].backward()

    grads = gradients['value']
    fmaps = feature_maps['value']
    weights = grads.mean(dim=[2, 3], keepdim=True)
    cam = torch.relu((weights * fmaps).sum(dim=1, keepdim=True))
    cam = cam.squeeze().detach().cpu().numpy()

    if cam.max() > 0:
        cam = (cam - cam.min()) / (cam.max() - cam.min())

    cam_pil = Image.fromarray((cam * 255).astype(np.uint8))
    cam_resized = np.array(cam_pil.resize((224, 224), Image.BILINEAR), dtype=np.float32) / 255.0
    heatmap_colored = _apply_jet_colormap(cam_resized)

    rgb_img = np.array(image.resize((224, 224)), dtype=np.float32)
    overlay = np.clip(rgb_img * 0.6 + heatmap_colored.astype(np.float32) * 0.4, 0, 255).astype(np.uint8)

    buffer = io.BytesIO()
    Image.fromarray(overlay).save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def predict(image_bytes: bytes) -> PredictResponse:
    model = get_model()
    _register_hooks(model)

    image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    input_tensor = transform(image).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        outputs = model(input_tensor)
        probs = torch.nn.functional.softmax(outputs[0], dim=0)
        prob_normal = probs[0].item()
        prob_defect = probs[1].item()

    heatmap = _generate_heatmap(image, transform(image).unsqueeze(0).to(DEVICE))

    return PredictResponse(
        is_defect=prob_defect > 0.5,
        anomaly_score=round(prob_defect * 100, 1),
        prob_normal=round(prob_normal * 100, 1),
        prob_defect=round(prob_defect * 100, 1),
        heatmap_data=heatmap,
    )
