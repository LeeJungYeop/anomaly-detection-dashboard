# ai-model/train.py - GoogleNet Fine-tuning
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import models, datasets, transforms
import os
from pathlib import Path

# 하이퍼파라미터
BATCH_SIZE = 32
EPOCHS = 10
LR = 0.001
DATA_PATH = "/dais05/2026HDRB_data/data_split_final/train"  # 호스트 데이터셋 마운트

# 디바이스
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Training on {device}")

# 데이터 전처리 (GoogleNet 표준)
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# 데이터셋 로드 (0=정상, 1=비정상)
dataset = datasets.ImageFolder(DATA_PATH, transform=transform)
dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=4)

print(f"Dataset: {len(dataset)} images, Classes: {dataset.classes}")

# 모델 (GoogleNet fine-tuning)
model = models.googlenet(pretrained=True)
model.fc = nn.Linear(model.fc.in_features, 2)  # Binary
model.to(device)

# 옵티마이저, 손실함수
optimizer = optim.Adam(model.parameters(), lr=LR, weight_decay=1e-4)
criterion = nn.CrossEntropyLoss()

# 학습 루프
model.train()
for epoch in range(EPOCHS):
    running_loss = 0.0
    for inputs, labels in dataloader:
        inputs, labels = inputs.to(device), labels.to(device)
        
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        
        running_loss += loss.item()
    
    print(f"Epoch {epoch+1}/{EPOCHS}, Loss: {running_loss/len(dataloader):.4f}")

# 모델 저장
torch.save(model.state_dict(), "model.pth")
print("✅ model.pth 저장 완료! docker-compose up 실행하세요.")
