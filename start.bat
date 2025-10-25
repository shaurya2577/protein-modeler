@echo off
REM Quick start script for Windows users

echo ======================================
echo Protein-Disease-Therapy Map Starter
echo ======================================
echo.

REM Check if .env files exist
if not exist "backend\.env" (
    echo WARNING: Backend .env not found!
    echo Please copy backend\.env.example to backend\.env and add your API key
    pause
    exit /b 1
)

if not exist "protein-modeler-app\.env" (
    echo WARNING: Frontend .env not found!
    echo Please copy protein-modeler-app\.env.example to protein-modeler-app\.env
    pause
    exit /b 1
)

REM Check if data exists
if not exist "backend\protein_disease.db" (
    echo WARNING: Database not found!
    echo Please run: cd backend ^&^& python scripts\generate_data.py
    pause
    exit /b 1
)

echo Starting Backend API...
start "Backend API" cmd /k "cd backend && python main.py"

echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo.
echo Starting Frontend...
start "Frontend Dev" cmd /k "cd protein-modeler-app && npm run dev"

echo.
echo ======================================
echo Services Started!
echo ======================================
echo Backend API:  http://localhost:8000
echo API Docs:     http://localhost:8000/docs
echo Frontend:     http://localhost:5173
echo.
echo Close the terminal windows to stop services
echo.
pause

