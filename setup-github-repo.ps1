# Soil Health DSS - GitHub Repository Setup Script

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  Soil Health DSS - GitHub Repository Setup  " -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This script will link your local project to GitHub and push the code."
Write-Host ""

# Step 1: Check GitHub authentication status
$authStatus = & "C:\Program Files\GitHub CLI\gh.exe" auth status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Step 1: Authenticating with GitHub..." -ForegroundColor Yellow
    Write-Host "A browser window will open, or a code will be provided. Follow the instructions to sign in."
    Write-Host ""
    & "C:\Program Files\GitHub CLI\gh.exe" auth login
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to authenticate with GitHub. Please run this script again." -ForegroundColor Red
        Exit
    }
} else {
    Write-Host "Step 1: Already authenticated with GitHub!" -ForegroundColor Green
}

# Step 2: Create a new repository on GitHub and push the code
Write-Host ""
Write-Host "Step 2: Creating a new repository 'soil-health-dss' on your GitHub account..." -ForegroundColor Yellow

# Try to create repository and push
& "C:\Program Files\GitHub CLI\gh.exe" repo create "soil-health-dss" --public --source=. --remote=origin --push

if ($LASTEXITCODE -eq 0) {
    Write-Host "Success! Your repository has been created and the code has been pushed!" -ForegroundColor Green
    & "C:\Program Files\GitHub CLI\gh.exe" repo view --web
} else {
    Write-Host "Repository creation failed or repository already exists." -ForegroundColor Red
    Write-Host "Let's check if we can add the remote and push manually..."
    
    # Check if remote already exists, if not, add it
    $remoteCheck = & "C:\Program Files\Git\cmd\git.exe" remote
    if ($remoteCheck -notcontains "origin") {
        Write-Host "Enter your GitHub username to link the repository: " -NoNewline
        $username = Read-Host
        if ($username -ne "") {
            & "C:\Program Files\Git\cmd\git.exe" remote add origin "https://github.com/$username/soil-health-dss.git"
            Write-Host "Staging and pushing branch to GitHub..." -ForegroundColor Yellow
            & "C:\Program Files\Git\cmd\git.exe" branch -M main
            & "C:\Program Files\Git\cmd\git.exe" push -u origin main
        }
    } else {
        Write-Host "Staging and pushing branch to existing origin..." -ForegroundColor Yellow
        & "C:\Program Files\Git\cmd\git.exe" branch -M main
        & "C:\Program Files\Git\cmd\git.exe" push -u origin main
    }
}

Write-Host ""
Write-Host "Done! You can now link this repository in Render (https://render.com) for backend hosting." -ForegroundColor Green
Write-Host "And drag & drop the 'SoilDSS-build-new.zip' file into Netlify Drop (https://netlify.com/drop) for frontend hosting." -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Cyan
