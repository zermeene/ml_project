# ⚡ QUICK COMMAND REFERENCE

## 🔥 COPY-PASTE COMMANDS

### First Time Setup (Copy All):
```powershell
cd D:\python\3\ml_p\air-quality-mlops\air-quality-mlops
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
cd data
python generate_data.py
cd ..
python src\prefect_pipeline.py
```

### Every Day - Backend Only:
```powershell
cd D:\python\3\ml_p\air-quality-mlops\air-quality-mlops
.\.venv\Scripts\activate
uvicorn src.api:app --reload
```

### Every Day - With Frontend:
**Terminal 1 (Backend):**
```powershell
cd D:\python\3\ml_p\air-quality-mlops\air-quality-mlops
.\.venv\Scripts\activate
uvicorn src.api:app --reload
```

**Terminal 2 (Frontend):**
```powershell
cd D:\python\3\ml_p\air-quality-mlops\air-quality-mlops
.\.venv\Scripts\activate
streamlit run app.py
```

### Docker (All-in-One):
```powershell
cd D:\python\3\ml_p\air-quality-mlops\air-quality-mlops
docker-compose up --build
```

---

## 📋 WHAT TO DO WHEN

### ✅ ONE TIME (Never Repeat):
| Command | When | Why |
|---------|------|-----|
| `python -m venv .venv` | First time | Create virtual environment |
| `pip install -r requirements.txt` | First time | Install packages |
| `python data\generate_data.py` | First time | Create dataset |
| `python src\prefect_pipeline.py` | First time | Train models |

### 🔄 EVERY TIME (Each Session):
| Command | When | Why |
|---------|------|-----|
| `.\.venv\Scripts\activate` | Always | Activate environment |
| `uvicorn src.api:app --reload` | Always | Start backend |
| `streamlit run app.py` | Optional | Start frontend UI |

### 🧪 TESTING:
| Command | When | Why |
|---------|------|-----|
| `pytest tests\ -v` | When testing | Run all tests |
| `python demo.py` | Demo | Test predictions |

---

## 🎯 TYPICAL WORKFLOW

### Morning (Start Work):
```powershell
# 1. Open PowerShell
# 2. Navigate to project
cd D:\python\3\ml_p\air-quality-mlops\air-quality-mlops

# 3. Activate environment
.\.venv\Scripts\activate

# 4. Start backend
uvicorn src.api:app --reload

# 5. (New terminal) Start frontend
streamlit run app.py
```

### Testing Your Work:
```powershell
# Browser 1: Backend API
http://127.0.0.1:8000/docs

# Browser 2: Frontend UI
http://localhost:8501
```

### Evening (Stop Work):
```powershell
# Press Ctrl+C in both terminals
# Close terminals
```

---

## 🌐 URLS TO REMEMBER

| Service | URL | Description |
|---------|-----|-------------|
| FastAPI Docs | http://127.0.0.1:8000/docs | Interactive API testing |
| FastAPI Health | http://127.0.0.1:8000/health | Check if API is running |
| Streamlit UI | http://localhost:8501 | Frontend interface |
| Prefect (Docker) | http://localhost:4200 | Workflow dashboard |

---

## 🚨 EMERGENCY FIXES

### Port Already in Use:
```powershell
# Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <NUMBER> /F

# Or use different port
uvicorn src.api:app --reload --port 8001
streamlit run app.py --server.port 8502
```

### Models Not Found:
```powershell
python src\prefect_pipeline.py
```

### Import Errors:
```powershell
pip install -r requirements.txt
```

### Environment Issues:
```powershell
deactivate
Remove-Item -Recurse -Force .venv
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

---

## 📝 DEMO VIDEO COMMANDS

```powershell
# Show these in order:

# 1. Activate environment
.\.venv\Scripts\activate

# 2. Show models exist
dir models\

# 3. Start backend
uvicorn src.api:app --reload

# 4. (New terminal) Start frontend
streamlit run app.py

# 5. Show API in browser
# http://127.0.0.1:8000/docs

# 6. Show UI in browser
# http://localhost:8501

# 7. Make prediction in UI

# 8. (Optional) Run tests
pytest tests\ -v
```

---

## 🎬 SCREEN RECORDING SETUP

### Terminal 1 (Left):
```powershell
cd D:\python\3\ml_p\air-quality-mlops\air-quality-mlops
.\.venv\Scripts\activate
uvicorn src.api:app --reload
```

### Terminal 2 (Right):
```powershell
cd D:\python\3\ml_p\air-quality-mlops\air-quality-mlops
.\.venv\Scripts\activate
streamlit run app.py
```

### Browser 1: API Docs
`http://127.0.0.1:8000/docs`

### Browser 2: Streamlit UI
`http://localhost:8501`

---

## ⭐ MOST IMPORTANT COMMANDS

```powershell
# Start everything (daily use):
.\.venv\Scripts\activate
uvicorn src.api:app --reload

# (New terminal)
streamlit run app.py

# That's it! Just these 3 commands for daily work!
```

---

## 🐳 DOCKER SHORTCUT

```powershell
# One command to rule them all:
docker-compose up --build

# Stop:
# Press Ctrl+C, then:
docker-compose down
```

---

**PRINT THIS PAGE AND KEEP IT NEXT TO YOUR LAPTOP!** 📄✨
