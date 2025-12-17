# 🚀 COMPLETE PROJECT WORKFLOW - Terminal Commands

## 📋 Table of Contents
1. [ONE-TIME SETUP](#one-time-setup) (Do this ONCE)
2. [DAILY WORKFLOW](#daily-workflow) (Do this EVERY TIME)
3. [Docker Deployment](#docker-deployment) (Alternative method)
4. [Troubleshooting](#troubleshooting)

---

# 🔧 ONE-TIME SETUP (Do This ONCE!)

## Step 1: Extract Project
```powershell
# Navigate to your project location
cd D:\python\3\ml_p

# Extract the zip (if not already done)
# Right-click air-quality-mlops.zip → Extract Here

# Enter the project folder
cd air-quality-mlops\air-quality-mlops
```

## Step 2: Create Virtual Environment
```powershell
# Create venv (if not already created)
python -m venv .venv

# Activate it
.\.venv\Scripts\activate

# You should see (.venv) in your prompt
```

## Step 3: Install Dependencies
```powershell
# Install all required packages (takes 2-3 minutes)
pip install -r requirements.txt

# Verify installation
pip list | findstr fastapi
pip list | findstr prefect
```

## Step 4: Generate Dataset (ONE TIME!)
```powershell
# Navigate to data folder
cd data

# Generate the dataset (creates air_quality_data.csv)
python generate_data.py

# Go back to project root
cd ..
```

## Step 5: Train Models (ONE TIME!)
```powershell
# This trains all 3 ML models (takes 2-3 minutes)
# Creates files in models/ folder
python src\prefect_pipeline.py

# You should see:
# ✅ Classification model trained
# ✅ Regression model trained  
# ✅ Clustering model trained
# ✅ Pipeline completed successfully

# Verify models are created
dir models\

# Should show:
# - aqi_classifier.pkl
# - pm25_regressor.pkl
# - city_clustering.pkl
# - scaler.pkl
```

✅ **ONE-TIME SETUP COMPLETE!** You never need to do Steps 1-5 again!

---

# 🔄 DAILY WORKFLOW (Do This EVERY TIME You Work)

## Quick Start (3 Commands!)
```powershell
# 1. Navigate to project
cd D:\python\3\ml_p\air-quality-mlops\air-quality-mlops

# 2. Activate virtual environment
.\.venv\Scripts\activate

# 3. Start FastAPI backend
uvicorn src.api:app --reload
```

That's it! Backend is running! 🎉

---

## Full Daily Workflow (With Frontend)

### Terminal 1: Backend (FastAPI)
```powershell
# Navigate and activate
cd D:\python\3\ml_p\air-quality-mlops\air-quality-mlops
.\.venv\Scripts\activate

# Start FastAPI server
uvicorn src.api:app --reload

# Output:
# INFO: Uvicorn running on http://127.0.0.1:8000
# ✅ Backend is ready!
```

**Keep this terminal running!** Don't close it.

**Test Backend:** Open browser → http://127.0.0.1:8000/docs

---

### Terminal 2: Frontend (Streamlit) - Optional
```powershell
# Open NEW terminal (don't close Terminal 1!)
# Navigate and activate
cd D:\python\3\ml_p\air-quality-mlops\air-quality-mlops
.\.venv\Scripts\activate

# Run Streamlit app
streamlit run app.py

# Output:
# Local URL: http://localhost:8501
# ✅ Frontend is ready!
```

**Keep both terminals running!**

---

## What Runs When?

### ✅ ONE TIME ONLY (Never run again unless you want to retrain):
```powershell
python data\generate_data.py          # Generate dataset
python src\prefect_pipeline.py        # Train models
```

### 🔄 EVERY TIME (Each session):
```powershell
.\.venv\Scripts\activate              # Activate environment
uvicorn src.api:app --reload          # Start backend
streamlit run app.py                  # Start frontend (optional)
```

### 🧪 When Testing:
```powershell
pytest tests\ -v                      # Run tests
python demo.py                        # Run demo script
```

---

# 🐳 DOCKER DEPLOYMENT (Alternative to Manual Setup)

## Option 1: Docker Compose (Easiest - Everything at Once)

### One-Time Setup:
```powershell
# Make sure Docker Desktop is running!
# Check Docker is working
docker --version
docker-compose --version
```

### Start Everything:
```powershell
cd D:\python\3\ml_p\air-quality-mlops\air-quality-mlops

# Build and start all services
docker-compose up --build

# Output:
# ✅ Building API container...
# ✅ Starting services...
# ✅ API running on http://localhost:8000
# ✅ Prefect UI on http://localhost:4200

# Keep terminal open!
```

### Stop Everything:
```powershell
# In the same terminal, press Ctrl+C
# Then run:
docker-compose down

# Or in new terminal:
docker-compose down -v  # Also removes volumes
```

---

## Option 2: Manual Docker (API Only)

### Build Image:
```powershell
# Build the Docker image (one time)
docker build -t air-quality-api .

# Takes 2-3 minutes
```

### Run Container:
```powershell
# Start the API container
docker run -p 8000:8000 air-quality-api

# Or run in background (-d flag)
docker run -d -p 8000:8000 --name aqi-api air-quality-api

# Test: http://localhost:8000/docs
```

### Stop Container:
```powershell
# Stop the running container
docker stop aqi-api

# Remove container
docker rm aqi-api
```

---

# 📊 COMPLETE WORKFLOW DIAGRAM

```
ONE-TIME SETUP (Do Once):
┌─────────────────────────────────────┐
│ 1. Extract ZIP                      │
│ 2. Create venv                      │
│ 3. Install requirements             │
│ 4. Generate dataset                 │
│ 5. Train models (prefect_pipeline)  │
└─────────────────────────────────────┘
         ↓
    ✅ DONE! Never repeat!


DAILY WORK (Every Session):
┌─────────────────────────────────────┐
│ Terminal 1:                         │
│  → cd project_folder                │
│  → .\.venv\Scripts\activate         │
│  → uvicorn src.api:app --reload     │
│                                     │
│ Terminal 2 (Optional):              │
│  → cd project_folder                │
│  → .\.venv\Scripts\activate         │
│  → streamlit run app.py             │
└─────────────────────────────────────┘
         ↓
    🎯 Work on project!


TESTING (When Needed):
┌─────────────────────────────────────┐
│  → pytest tests\ -v                 │
│  → python demo.py                   │
└─────────────────────────────────────┘


DOCKER (Alternative):
┌─────────────────────────────────────┐
│  → docker-compose up --build        │
│     (Everything runs automatically) │
│                                     │
│  → Press Ctrl+C to stop             │
│  → docker-compose down              │
└─────────────────────────────────────┘
```

---

# 🎬 TYPICAL DAILY SESSION

## Morning Routine:
```powershell
# 1. Open PowerShell
cd D:\python\3\ml_p\air-quality-mlops\air-quality-mlops

# 2. Activate environment
.\.venv\Scripts\activate

# 3. Start backend
uvicorn src.api:app --reload

# 4. Open browser: http://127.0.0.1:8000/docs

# ✅ Start working!
```

## When You're Done:
```powershell
# In the terminal running uvicorn:
# Press Ctrl+C

# Deactivate environment (optional)
deactivate

# Close terminal
```

---

# 🔍 QUICK REFERENCE

## Essential Commands:

```powershell
# Activate environment
.\.venv\Scripts\activate

# Start backend
uvicorn src.api:app --reload

# Start frontend
streamlit run app.py

# Run tests
pytest tests\ -v

# Train models (only if needed)
python src\prefect_pipeline.py

# Docker all-in-one
docker-compose up --build
```

## URLs to Remember:

- **API Docs:** http://127.0.0.1:8000/docs
- **API Health:** http://127.0.0.1:8000/health
- **Streamlit:** http://localhost:8501
- **Prefect UI (Docker):** http://localhost:4200

---

# 🛠️ TROUBLESHOOTING

## Issue 1: "Models not found"
```powershell
# Solution: Train models
python src\prefect_pipeline.py
```

## Issue 2: "Port 8000 already in use"
```powershell
# Solution: Use different port
uvicorn src.api:app --reload --port 8001

# Or kill the process using port 8000
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER> /F
```

## Issue 3: "Module not found"
```powershell
# Solution: Reinstall requirements
pip install -r requirements.txt
```

## Issue 4: Virtual environment not working
```powershell
# Solution: Recreate venv
deactivate
Remove-Item -Recurse -Force .venv
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## Issue 5: Docker not starting
```powershell
# Check Docker is running
docker --version

# Clean Docker
docker-compose down -v
docker system prune -a

# Rebuild
docker-compose up --build
```

---

# 📝 SUMMARY CHEAT SHEET

## ONE TIME (First Day):
```powershell
cd D:\python\3\ml_p\air-quality-mlops\air-quality-mlops
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
cd data && python generate_data.py && cd ..
python src\prefect_pipeline.py
```

## EVERY TIME (Daily):
```powershell
cd D:\python\3\ml_p\air-quality-mlops\air-quality-mlops
.\.venv\Scripts\activate
uvicorn src.api:app --reload
# Visit: http://127.0.0.1:8000/docs
```

## DOCKER (Alternative):
```powershell
cd D:\python\3\ml_p\air-quality-mlops\air-quality-mlops
docker-compose up --build
# Visit: http://localhost:8000/docs
```

---

# 🎯 WHAT TO DO FOR YOUR DEMO VIDEO

## Record This Flow:

1. **Show Terminal:**
   ```powershell
   cd air-quality-mlops\air-quality-mlops
   .\.venv\Scripts\activate
   uvicorn src.api:app --reload
   ```

2. **Show Browser:**
   - Open http://127.0.0.1:8000/docs
   - Test `/predict/aqi` endpoint
   - Show the response

3. **Show Models (Optional):**
   ```powershell
   dir models\
   # Show the .pkl files
   ```

4. **Show Tests (Optional):**
   ```powershell
   pytest tests\ -v
   ```

5. **Show Docker (Optional):**
   ```powershell
   docker-compose up
   # Show it running
   ```

---

# ✅ YOU'RE READY!

**Remember:**
- ✅ ONE-TIME: Setup, install, generate data, train models
- 🔄 EVERY TIME: Activate venv, start uvicorn
- 🐳 DOCKER: Alternative easy method

**SLAAYYY! You got this!** 🚀
