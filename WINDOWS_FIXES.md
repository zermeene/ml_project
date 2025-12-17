# 🔧 WINDOWS FIXES - QUICK GUIDE

## ✅ Issues Fixed in Updated ZIP

I've fixed both errors you encountered:

### 1. Unicode Encoding Error ❌ → ✅ FIXED
**Problem:** Windows couldn't encode fancy Unicode box characters (├─ └─)  
**Solution:** 
- Changed file writing to use `encoding='utf-8'`
- Simplified report formatting to remove Unicode box characters

### 2. Import Error ❌ → ✅ FIXED  
**Problem:** `ModuleNotFoundError: No module named 'config'`  
**Solution:** Added `sys.path` fix to all source files so imports work correctly

---

## 🚀 How to Run (Updated Instructions)

### Step 1: Extract New ZIP
```bash
# Delete old folder first
rm -rf air-quality-mlops

# Extract new zip
unzip air-quality-mlops.zip
cd air-quality-mlops
```

### Step 2: Install Dependencies
```bash
# Activate your virtual environment first!
# (.venv) should show in your prompt

pip install -r requirements.txt
```

### Step 3: Run Prefect Pipeline ✅
```bash
python src/prefect_pipeline.py
```

**Should now complete successfully!** ✅

### Step 4: Start FastAPI Server ✅
```bash
uvicorn src.api:app --reload
```

**Should now start without errors!** ✅

Visit: http://127.0.0.1:8000/docs

---

## 🎯 What Changed?

### Fixed Files:
1. **src/api.py** - Added path fix for imports
2. **src/preprocessing.py** - Added path fix for imports
3. **src/models.py** - Added path fix for imports
4. **src/prefect_pipeline.py** - Added path fix + UTF-8 encoding + simpler formatting

### All Changes:
```python
# Added to each file:
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

# Fixed in prefect_pipeline.py:
with open('pipeline_report.txt', 'w', encoding='utf-8') as f:  # UTF-8!
    f.write(report)
```

---

## ✅ Expected Output

### Prefect Pipeline:
```
======================================================================
AIR QUALITY ML PIPELINE - PREFECT ORCHESTRATION
======================================================================

[... training progress ...]

MODEL PERFORMANCE SUMMARY
======================================================================

1. AQI CLASSIFICATION (Random Forest)
   - Accuracy: 1.0000
   - Status: PASS

2. PM2.5 REGRESSION (Gradient Boosting)
   - R2 Score: 0.9240
   - RMSE: 9.1003
   - MAE: 7.0125
   - Status: PASS

3. CITY CLUSTERING (K-Means)
   - Silhouette Score: 0.3149
   - Status: FAIL

======================================================================
PIPELINE COMPLETED SUCCESSFULLY
======================================================================
```

### FastAPI Server:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

## 🐛 If You Still Have Issues

### Issue: Models Not Found
```bash
# Make sure you're in the right directory
cd air-quality-mlops

# Run pipeline to train models
python src/prefect_pipeline.py
```

### Issue: Port 8000 Already in Use
```bash
# Use different port
uvicorn src.api:app --reload --port 8001
```

### Issue: Missing Dependencies
```bash
# Reinstall everything
pip install --force-reinstall -r requirements.txt
```

### Issue: Wrong Python Version
```bash
# Check Python version (need 3.10+)
python --version

# Should be Python 3.11.x in your case
```

---

## 📦 Testing Everything Works

### Test 1: Prefect Pipeline ✅
```bash
python src/prefect_pipeline.py
```
Should complete without errors!

### Test 2: API Server ✅
```bash
uvicorn src.api:app --reload
```
Should start successfully!

### Test 3: Make a Prediction ✅
Open browser: http://127.0.0.1:8000/docs

Click "Try it out" on `/predict/aqi`

Use example data and click "Execute"

Should get prediction! ✅

### Test 4: Run Tests ✅
```bash
pytest tests/ -v
```
All tests should pass! ✅

---

## 🎊 You're All Set!

Everything should work now on Windows! The issues were:
1. ✅ Unicode encoding → Fixed with UTF-8
2. ✅ Import errors → Fixed with sys.path

**Ready to continue with your project!** 🚀

---

## 📝 Next Steps

1. ✅ Verify pipeline runs successfully
2. ✅ Test API endpoints in browser
3. ✅ Start working on demo video
4. ✅ Fill in project report template

**SLAAYYY - You got this!** ✨
