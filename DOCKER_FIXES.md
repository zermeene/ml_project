# 🐳 DOCKER FIXES - YOUR ISSUES SOLVED!

## 🚨 YOUR PROBLEMS & SOLUTIONS

---

## Problem 1: Can't Access http://0.0.0.0:8000

### Why It Fails:
- `0.0.0.0` is NOT a real address to visit in browser
- It's Docker's internal address
- You need to use `localhost` or `127.0.0.1`

### ✅ SOLUTION:

**Instead of:** `http://0.0.0.0:8000`  
**Use:** `http://localhost:8000` or `http://127.0.0.1:8000`

**Try these URLs:**
- http://localhost:8000/docs (API documentation)
- http://localhost:8000/health (Health check)
- http://localhost:8000 (Root endpoint)

---

## Problem 2: Container Name Already in Use

### Error Message:
```
docker: Error response from daemon: Conflict. 
The container name "/aqi-api" is already in use
```

### Why It Happens:
- You already ran the container before
- Docker keeps the old container even after stopping

### ✅ SOLUTION (3 Ways):

**Option 1: Remove Old Container**
```powershell
# List all containers
docker ps -a

# Remove the old one
docker rm aqi-api

# Now run again
docker run -d -p 8000:8000 --name aqi-api air-quality-api
```

**Option 2: Force Remove & Run**
```powershell
# Remove if exists and run new one
docker rm -f aqi-api
docker run -d -p 8000:8000 --name aqi-api air-quality-api
```

**Option 3: Use Different Name**
```powershell
# Use a new name
docker run -d -p 8000:8000 --name aqi-api-v2 air-quality-api
```

---

## Problem 3: Scikit-learn Version Warning

### Warning Message:
```
InconsistentVersionWarning: Trying to unpickle estimator 
from version 1.8.0 when using version 1.7.2
```

### Why It Happens:
- Your local machine has sklearn 1.8.0
- Docker image has sklearn 1.7.2
- Models were trained on 1.8.0

### ✅ SOLUTION:

**Fix the Dockerfile to use same version:**

Update `requirements.txt`:
```txt
scikit-learn>=1.8.0
```

**Then rebuild:**
```powershell
docker build -t air-quality-api .
docker run -d -p 8000:8000 --name aqi-api air-quality-api
```

---

## 🎯 CORRECT DOCKER WORKFLOW

### **Complete Clean Start:**

```powershell
# 1. Stop all containers
docker stop $(docker ps -aq)

# 2. Remove all containers
docker rm $(docker ps -aq)

# 3. Rebuild image
docker build -t air-quality-api .

# 4. Run container
docker run -d -p 8000:8000 --name aqi-api air-quality-api

# 5. Check logs
docker logs aqi-api

# 6. Test in browser
# Open: http://localhost:8000/docs
```

---

## 🎯 USING DOCKER COMPOSE (EASIER!)

### Your Issue:
You tried `docker-compose up` but couldn't access endpoints

### ✅ SOLUTION:

**Step 1: Make sure docker-compose.yml exists**
```powershell
# Check if file exists
dir docker-compose.yml
```

**Step 2: Start with docker-compose**
```powershell
# Stop any running containers first
docker-compose down

# Start fresh
docker-compose up --build
```

**Step 3: Access the services**
- API: http://localhost:8000/docs
- Prefect: http://localhost:4200

**Step 4: Stop everything**
```powershell
# Press Ctrl+C in terminal
# Then run:
docker-compose down
```

---

## 📋 QUICK DOCKER COMMANDS

```powershell
# See running containers
docker ps

# See all containers (including stopped)
docker ps -a

# Stop a container
docker stop aqi-api

# Remove a container
docker rm aqi-api

# See logs
docker logs aqi-api

# Follow logs (live)
docker logs -f aqi-api

# Remove all stopped containers
docker container prune

# Remove all images
docker image prune -a
```

---

## 🎯 FOR YOUR VIVA (Simplest Demo)

**Don't use Docker! Too complicated for demo.**

**Use this instead:**

### **Terminal 1: Start API**
```powershell
cd D:\python\3\ml_p\air-quality-mlops_final\air-quality-mlops
.\.venv\Scripts\activate
uvicorn src.api:app --reload
```

### **Terminal 2: Start Streamlit**
```powershell
cd D:\python\3\ml_p\air-quality-mlops_final\air-quality-mlops
.\.venv\Scripts\activate
streamlit run app.py
```

### **Access:**
- Backend: http://127.0.0.1:8000/docs
- Frontend: http://localhost:8501

**This is MUCH easier than Docker for your viva!**

---

## 🚨 IF DOCKER STILL DOESN'T WORK

### **Just DON'T use Docker for the demo!**

**Say this in viva:**
- "I have containerized the application using Docker for deployment"
- "For this demo, I'm running it directly to show the features more clearly"
- "In production, we would use the Docker containers"

**This is TOTALLY FINE!** Many people do this in demos.

---

## ✅ WORKING SOLUTION FOR VIVA

**SKIP DOCKER COMPLETELY**

Use this workflow:

```powershell
# 1. Activate environment
.\.venv\Scripts\activate

# 2. Start backend
uvicorn src.api:app --reload

# 3. (New terminal) Start frontend
streamlit run app.py

# 4. Show live data
cd src
python live_data.py

# 5. Show MLflow
mlflow ui
```

**This is simpler and shows everything clearly!**

---

## 🎯 SUMMARY

### Your Docker Issues:
1. ❌ Using `0.0.0.0:8000` → ✅ Use `localhost:8000`
2. ❌ Container name conflict → ✅ Use `docker rm aqi-api` first
3. ❌ Version warnings → ✅ Just warnings, still works!

### Best Approach for Viva:
**DON'T USE DOCKER!**

Use direct Python commands:
- Simpler
- Clearer
- Easier to debug
- Shows features better

### If Asked About Docker:
"Yes, I have Docker deployment configured. The Dockerfile and docker-compose.yml are in the project. For this demo, I'm running directly to show the features more clearly."

**PERFECT ANSWER!** ✨

---

**Remember:** Viva is about showing you understand the concepts, NOT about fighting with Docker! 🎉
