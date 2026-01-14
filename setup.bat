@echo off
echo ========================================
echo   Python Screenshot App Setup
echo ========================================
echo.

echo Checking Python...
python --version
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found in PATH
    exit /b 1
)

echo.
echo [1/3] Installing dependencies...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install dependencies
    exit /b 1
)

echo.
echo [2/3] Installing Playwright browsers...
python -m playwright install chromium
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Playwright browser install may have had issues
    echo You can run this manually: python -m playwright install chromium
)

echo.
echo [3/3] Setup Complete!
echo.
echo To run the application:
echo   python main.py
echo.
echo Or create a shortcut with target:
echo   python "P:\Open Code CLI\screenshot-go\main.py"
echo.

pause
