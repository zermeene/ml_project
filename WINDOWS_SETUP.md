# Windows Setup Guide - FIXED VERSION 🪟

## Issues Fixed ✅
1. ✅ Unicode encoding error in report generation
2. ✅ Module import path issues on Windows
3. ✅ Added Windows-compatible scripts

---

## Quick Fix - Option 1 (Easiest) 🚀

### Step 1: Use the Windows-Compatible Files

```powershell
# Navigate to project directory
cd air-quality-mlops

# Use the Windows-compatible pipeline
python src/prefect_pipeline_windows.py

# Use the Windows-compatible API runner
python run_api.py
```

That's it! Everything should work now.

---

## Quick Fix - Option 2 (Alternative) 🔧

### For Prefect Pipeline:
Replace line 199 in `src/prefect_pipeline.py`:

**Change from:**
```python
with open('pipeline_report.txt', 'w', encoding='utf-8') as f:
```

**To:** (if not already UTF-8)
```python
with open('pipeline_report.txt', 'w', encoding='utf-8') as f:
```

### For API:
**Instead of:**
```powershell
uvicorn src.api:app --reload
```

**Use:**
```powershell
python run_api.py
```

---

## Complete Setup from Scratch 💻

### 1. Extract Project
```powershell
# Extract the ZIP file
# Navigate to extracted folder
cd air-quality-mlops
```

### 2. Create Virtual Environment
```powershell
# Create venv
python -m venv .venv

# Activate (PowerShell)
.\.venv\Scripts\Activate.ps1

# OR Activate (CMD)
.\.venv\Scripts\activate.bat
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Generate Data
```powershell
cd data
python generate_data.py
cd ..
```

### 5. Train Models (Windows-Compatible)
```powershell
# Use the Windows version
python src/prefect_pipeline_windows.py
```

### 6. Start API (Windows-Compatible)
```powershell
# Use the helper script
python run_api.py
```

### 7. Test the API
Open browser: http://localhost:8000/docs

---

## Troubleshooting Windows Issues 🔍

### Issue 1: PowerShell Execution Policy

**Error:**
```
cannot be loaded because running scripts is disabled
```

**Fix:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue 2: Unicode/Encoding Errors

**Error:**
```
UnicodeEncodeError: 'charmap' codec can't encode
```

**Fix:** Use the Windows-compatible version:
```powershell
python src/prefect_pipeline_windows.py
```

### Issue 3: Module Not Found

**Error:**
```
ModuleNotFoundError: No module named 'config'
```

**Fix:** Use the run script:
```powershell
python run_api.py
```

### Issue 4: Port Already in Use

**Error:**
```
Address already in use
```

**Fix:**
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process
taskkill /PID <process_id> /F

# Or use a different port
python run_api.py --port 8001
```

### Issue 5: Path Issues

**If you see path-related errors:**

Create `run_pipeline.py` in project root:
```python
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Now run pipeline
from prefect_pipeline_windows import air_quality_ml_pipeline
result = air_quality_ml_pipeline()
```

Then run:
```powershell
python run_pipeline.py
```

---

## Testing Everything 🧪

### Test 1: Pipeline
```powershell
python src/prefect_pipeline_windows.py
```

**Expected output:**
- ✅ All tasks complete
- ✅ Models trained
- ✅ Report generated
- ✅ No Unicode errors

### Test 2: API
```powershell
# Terminal 1: Start API
python run_api.py

# Terminal 2: Test endpoint
curl http://localhost:8000/health
```

**Expected output:**
```json
{
  "status": "healthy",
  "models_loaded": {
    "classifier": true,
    "regressor": true,
    "clustering": true,
    "scaler": true
  }
}
```

### Test 3: Run Tests
```powershell
pytest tests/ -v
```

---

## Docker on Windows 🐳

### Prerequisites
- Docker Desktop for Windows installed
- WSL2 enabled (recommended)

### Build and Run
```powershell
# Build image
docker build -t air-quality-api .

# Run container
docker run -p 8000:8000 air-quality-api

# Or use docker-compose
docker-compose up --build
```

---

## Command Reference 📝

### Essential Commands
```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Train models (Windows-compatible)
python src/prefect_pipeline_windows.py

# Start API (Windows-compatible)
python run_api.py

# Run tests
pytest tests/ -v

# Run specific test
pytest tests/test_api.py -v

# Docker
docker-compose up --build

# Deactivate virtual environment
deactivate
```

### Checking What's Installed
```powershell
# Check Python version
python --version

# Check pip version
pip --version

# List installed packages
pip list

# Check if models exist
dir models\
```

---

## File Locations 📁

```
air-quality-mlops/
├── run_api.py                          # ← NEW: Windows-compatible API runner
├── src/
│   ├── prefect_pipeline.py            # Original (may have Unicode issues)
│   ├── prefect_pipeline_windows.py    # ← NEW: Windows-compatible
│   ├── api.py
│   ├── models.py
│   ├── preprocessing.py
│   └── config.py
├── data/
│   ├── generate_data.py
│   └── air_quality_data.csv
├── models/                             # Generated after training
│   ├── aqi_classifier.pkl
│   ├── pm25_regressor.pkl
│   └── ...
└── tests/
```

---

## Step-by-Step Demo Recording 🎥

### For Your Video (5-10 minutes)

**Part 1: Setup (1 min)**
```powershell
# Show project structure
tree /F

# Show virtual environment active
python --version
pip list
```

**Part 2: Training (2 min)**
```powershell
# Run pipeline
python src/prefect_pipeline_windows.py

# Show generated models
dir models\

# Show visualizations
# Open models/confusion_matrix.png
# Open models/regression_predictions.png
```

**Part 3: API Demo (3 min)**
```powershell
# Start API
python run_api.py

# In browser, show:
# - http://localhost:8000/
# - http://localhost:8000/docs
# - Make a prediction in Swagger UI
```

**Part 4: Testing (2 min)**
```powershell
# Run tests
pytest tests/ -v

# Show test coverage
pytest tests/ --cov=src
```

**Part 5: Docker (2 min)**
```powershell
# Build and run
docker-compose up --build

# Test container
curl http://localhost:8000/health
```

---

## Common Windows-Specific Notes ⚠️

1. **Backslashes in Paths**: Windows uses `\` instead of `/`
   - Python handles this automatically with `Path`
   - Use `Path` objects from `pathlib` for cross-platform compatibility

2. **Line Endings**: Windows uses CRLF (`\r\n`) vs Unix LF (`\n`)
   - Git handles this automatically
   - Files should work fine

3. **Case Sensitivity**: Windows is case-insensitive
   - Be consistent with file names anyway
   - Helps with cross-platform compatibility

4. **Virtual Environment Activation**:
   - PowerShell: `.\.venv\Scripts\Activate.ps1`
   - CMD: `.\.venv\Scripts\activate.bat`
   - Git Bash: `source .venv/Scripts/activate`

---

## Success Checklist ✅

Before submitting, verify:

- [ ] Virtual environment created and activated
- [ ] All dependencies installed (`pip list` shows required packages)
- [ ] Data generated (`data/air_quality_data.csv` exists)
- [ ] Models trained (`models/*.pkl` files exist)
- [ ] Pipeline runs without errors (`python src/prefect_pipeline_windows.py`)
- [ ] API starts successfully (`python run_api.py`)
- [ ] API docs accessible (http://localhost:8000/docs)
- [ ] Predictions work (test in Swagger UI)
- [ ] Tests pass (`pytest tests/ -v`)
- [ ] Docker builds (`docker build -t air-quality-api .`)

---

## Getting Help 💬

### If You're Still Stuck:

1. **Check Error Messages**: Read the full error, it usually tells you what's wrong
2. **Check File Locations**: Make sure you're in the right directory
3. **Check Python Version**: Should be 3.10 or higher
4. **Check Virtual Environment**: Should be activated (see prompt)
5. **Try Docker**: If local setup fails, use Docker

### Common Error Patterns:

- "Module not found" → Virtual environment not activated OR wrong directory
- "File not found" → Wrong directory OR data not generated
- "Port in use" → Kill the process using that port
- "Encoding error" → Use Windows-compatible version
- "Permission denied" → Run as administrator OR check file permissions

---

## Quick Reference Card 🎴

```powershell
# ONE-TIME SETUP
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python data/generate_data.py

# EVERY TIME YOU WORK
.\.venv\Scripts\Activate.ps1

# TRAIN MODELS
python src/prefect_pipeline_windows.py

# START API
python run_api.py

# RUN TESTS
pytest tests/ -v

# DOCKER
docker-compose up --build
```

---

**You're all set! The Windows-compatible version should work perfectly now.** 🎉

If you still encounter issues, the error messages will tell you exactly what needs to be fixed. Just read them carefully!
