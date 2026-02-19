import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, WeightedRandomSampler
from torchvision import models, datasets, transforms
from tqdm import tqdm
import numpy as np
import os

# 하이퍼파라미터
BATCH_SIZE = 32
EPOCHS = 30
LR = 0.0005  # ← 낮춤 (과적합 방지)
DATA_PATH = "/dais05/2026HDRB_data/data_split_final/train"
NUM_WORKERS = 16

print("🚀 학습 시작 (정상:17k vs 비정상:1.2k)")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Training on {device}")

# 데이터 전처리 (데이터 증강 추가)
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomRotation(degrees=5),
    transforms.ColorJitter(brightness=0.2, contrast=0.2),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# 데이터셋 로드
dataset = datasets.ImageFolder(DATA_PATH, transform=transform)

# 클래스별 샘플 수 계산 및 가중치
class_counts = np.bincount(dataset.targets)
print(f"📊 클래스 분포: 정상({class_counts[0]}장) vs 비정상({class_counts[1]}장)")
class_weights = 1.0 / class_counts
sample_weights = [class_weights[label] for label in dataset.targets]

# Weighted Sampler (비정상 샘플 우선)
sampler = WeightedRandomSampler(weights=sample_weights, num_samples=len(sample_weights), replacement=True)

dataloader = DataLoader(
    dataset, batch_size=BATCH_SIZE, sampler=sampler,  # shuffle=False
    num_workers=NUM_WORKERS, pin_memory=True, persistent_workers=True
)

print(f"⚙️  Weighted Sampling 적용 | Batches: {len(dataloader)}")

# 모델
model = models.googlenet(pretrained=True)
model.fc = nn.Linear(model.fc.in_features, 2)
model.to(device)

# 클래스 가중치 손실 함수 (불균형 보정)
class_weights_tensor = torch.FloatTensor([1.0, 14.45]).to(device)  # 17666/1223 ≈ 14.45
criterion = nn.CrossEntropyLoss(weight=class_weights_tensor)

optimizer = optim.Adam(model.parameters(), lr=LR, weight_decay=1e-4)
scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOCHS)

model.train()
best_acc = 0.0
patience = 7
no_improve = 0

for epoch in range(EPOCHS):
    print(f"\n🔄 Epoch {epoch+1:2d}/{EPOCHS}")
    running_loss = 0.0
    correct = 0
    total = 0
    
    progress_bar = tqdm(dataloader, desc="Training", leave=False)
    for batch_idx, (inputs, labels) in enumerate(progress_bar):
        inputs, labels = inputs.to(device, non_blocking=True), labels.to(device)
        
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()
        
        running_loss += loss.item()
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += predicted.eq(labels).sum().item()
        
        progress_bar.set_postfix({
            'Loss': f"{loss.item():.3f}",
            'Acc': f"{100.*correct/total:.1f}%",
            'LR': f"{scheduler.get_last_lr()[0]:.2e}"
        })
    
    epoch_loss = running_loss / len(dataloader)
    epoch_acc = 100. * correct / total
    scheduler.step()
    
    print(f"📈 Loss: {epoch_loss:.4f} | Acc: {epoch_acc:.1f}%")
    
    # Early Stopping
    if epoch_acc > best_acc:
        best_acc = epoch_acc
        torch.save(model.state_dict(), "best_model.pth")
        no_improve = 0
    else:
        no_improve += 1
        if no_improve >= patience:
            print(f"Early stopping at epoch {epoch+1}")
            break

print("\n💾 최종 저장...")
torch.save(model.state_dict(), "model.pth")
model_size = os.path.getsize("model.pth") / (1024 * 1024)
print(f"✅ model.pth: {model_size:.1f} MB | Best Acc: {best_acc:.1f}%")
print("🚀 docker-compose up --build")