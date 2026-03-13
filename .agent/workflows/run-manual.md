---
description: How to run the HealthVault AI project manually
---

## Step 1: Navigate to Project Root
Open your terminal and ensure you are in the project folder. You should see `requirements.txt` when you list the files.

```powershell
cd c:\Users\tella\Desktop\healthvault
ls  # Verify requirements.txt is visible
```

## Step 2: Environment Setup
Ensure you have Python installed. It's recommended to use a virtual environment.

```powershell
# Create venv if not exists
python -m venv venv
# Activate venv
.\venv\Scripts\Activate.ps1
# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configuration
Ensure your `.env` file exists in the root directory. If you are using the local SQLite database (default), the `DATABASE_URL` can be left blank or pointed to `sqlite+aiosqlite:///./healthvault.db`.

## Step 3: Run the Server
Use `uvicorn` to start the FastAPI application.

```powershell
python -m uvicorn api.index:app --host 127.0.0.1 --port 8000 --reload
```

## Step 4: Access the Dashboard
Open your browser and navigate to:
`http://127.0.0.1:8000/`

---
// turbo-all
