@echo off
REM Soil Health DSS - Vercel Deployment Script (Windows)

echo ======================================
echo Soil Health DSS - Vercel Deployment
echo ======================================
echo.

REM Check if Vercel CLI is installed
where vercel >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Vercel CLI is not installed.
    echo Install it with: npm install -g vercel
    exit /b 1
)

REM Check if Git is initialized
if not exist ".git" (
    echo Initializing Git repository...
    git init
    git add .
    git commit -m "Initial commit: Soil Health DSS"
    echo.
)

REM Get API URL from user
echo Enter your backend API URL (e.g., https://api.example.com):
set /p API_URL="URL: "

if "%API_URL%"=="" (
    echo Error: API URL is required
    exit /b 1
)

REM Update environment file
echo.
echo Updating frontend environment variables...
(
    echo REACT_APP_API_BASE_URL=%API_URL%
) > frontend\.env.production.local

REM Build frontend
echo.
echo Building frontend...
cd frontend
call npm run build
cd ..

if %ERRORLEVEL% NEQ 0 (
    echo Build failed!
    exit /b 1
)

REM Deploy to Vercel
echo.
echo Deploying to Vercel...
call vercel --prod --env REACT_APP_API_BASE_URL=%API_URL%

echo.
echo ======================================
echo Deployment Complete!
echo ======================================
echo.
echo Your application is now live!
echo Check your Vercel dashboard for more details.
pause
