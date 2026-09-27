@echo off
echo ========================================================
echo   DisasterLens: AI/ML Disaster Decision-Support System
echo ========================================================
echo.

IF NOT EXIST ".venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found. Creating .venv...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    pip install -r requirements.txt
) ELSE (
    call .venv\Scripts\activate.bat
)

IF NOT EXIST "models\severity_model.json" (
    echo [INFO] Severity model not found. Training XGBoost model...
    python models\train_severity.py
)

echo.
echo [INFO] Launching DisasterLens Decision-Support Dashboard...
streamlit run app\main.py
pause
