#!/bin/bash
cd frontend && python3 -m http.server 8080 > frontend.log 2>&1 &
cd ../backend && pip install -r requirements.txt && uvicorn main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
cd ../ai-model && pip install -r requirements.txt torch torchvision && uvicorn main:app --host 0.0.0.0 --port 5000 > ai.log 2>&1 &
echo "✅ http://localhost:8080 접속! 로그: tail -f *.log"
