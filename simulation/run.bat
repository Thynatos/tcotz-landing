@echo off
echo ========================================
echo   BobaCo Simulation Dashboard
echo ========================================
echo.

:: Check if streamlit is installed
pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo [!] Dependencies not found. Installing...
    pip install -r requirements.txt
    echo.
)

echo Starting app on http://localhost:8503
echo Press Ctrl+C to stop
echo.
start http://localhost:8503
streamlit run app.py --server.port 8503
pause
