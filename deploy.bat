@echo off
echo ========================================================
echo       Omaya Dashboard - GitHub Deployment Helper
echo ========================================================
echo.
echo I will help you push your code to GitHub.
echo.
echo 1. Go to https://github.com/new
echo 2. Create a new repository (name it 'omaya-dashboard' or similar)
echo 3. Copy the HTTPS URL (e.g., https://github.com/username/repo.git)
echo.
set /p repo_url="[STEP 1] Paste your GitHub Repository URL here: "

if "%repo_url%"=="" (
    echo.
    echo Error: URL cannot be empty.
    pause
    exit /b
)

echo.
echo [STEP 2] Configuring Remote...
git remote remove origin 2>nul
git remote add origin %repo_url%

echo.
echo [STEP 3] Pushing Code...
git branch -M main
git push -u origin main --force

echo.
echo ========================================================
echo If you see "Branch 'main' set up to track remote branch...", 
echo then the Push was SUCCESSFUL!
echo.
echo Now you can go to Vercel/Render and import this repository.
echo ========================================================
pause
