# Poppler for Windows Installer Script
# Downloads and installs poppler-windows

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Poppler for Windows Installer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$installDir = "$env:LOCALAPPDATA\poppler"
$binDir = Join-Path $installDir "Library\bin"

$repo = "oschwartz10612/poppler-windows"
$apiUrl = "https://api.github.com/repos/$repo/releases/latest"

Write-Host "Checking latest release..." -ForegroundColor Yellow
try {
    $release = Invoke-RestMethod -Uri $apiUrl -Method Get
    $downloadUrl = ($release.assets | Where-Object { $_.name -like "Release-*.zip" } | Select-Object -First 1).browser_download_url
    
    if (-not $downloadUrl) {
        throw "Release file not found"
    }
    
    Write-Host "Download URL: $downloadUrl" -ForegroundColor Green
} catch {
    Write-Host "Error: Failed to get release info: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Manual installation:" -ForegroundColor Yellow
    Write-Host "1. Visit https://github.com/$repo/releases" -ForegroundColor White
    Write-Host "2. Download latest Release-*.zip" -ForegroundColor White
    Write-Host "3. Extract to C:\poppler" -ForegroundColor White
    Write-Host "4. Add Library\bin to PATH" -ForegroundColor White
    exit 1
}

$zipPath = Join-Path $env:TEMP "poppler-windows.zip"

Write-Host ""
Write-Host "Downloading Poppler..." -ForegroundColor Yellow
try {
    Invoke-WebRequest -Uri $downloadUrl -OutFile $zipPath -UseBasicParsing
    Write-Host "Download complete: $zipPath" -ForegroundColor Green
} catch {
    Write-Host "Error: Download failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Extracting..." -ForegroundColor Yellow
try {
    if (Test-Path $installDir) {
        Remove-Item -Path $installDir -Recurse -Force
    }
    
    $tempExtractDir = Join-Path $env:TEMP "poppler-extract"
    if (Test-Path $tempExtractDir) {
        Remove-Item -Path $tempExtractDir -Recurse -Force
    }
    New-Item -ItemType Directory -Path $tempExtractDir -Force | Out-Null
    
    Expand-Archive -Path $zipPath -DestinationPath $tempExtractDir -Force
    
    # Find the extracted directory (could be Release-* or just the root)
    $extractedDir = Get-ChildItem -Path $tempExtractDir -Directory | Select-Object -First 1
    if (-not $extractedDir) {
        # If no subdirectory, use the extract dir itself
        $extractedDir = Get-Item $tempExtractDir
    }
    
    if (-not $extractedDir) {
        throw "Extracted directory not found"
    }
    
    Move-Item -Path $extractedDir.FullName -Destination $installDir -Force
    Remove-Item -Path $tempExtractDir -ErrorAction SilentlyContinue
    Write-Host "Extraction complete: $installDir" -ForegroundColor Green
} catch {
    Write-Host "Error: Extraction failed: $_" -ForegroundColor Red
    exit 1
} finally {
    if (Test-Path $zipPath) {
        Remove-Item -Path $zipPath -Force
    }
}

Write-Host ""
Write-Host "Adding to PATH..." -ForegroundColor Yellow

$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($currentPath -notlike "*$binDir*") {
    $newPath = $currentPath + ";$binDir"
    [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
    Write-Host "Added to PATH: $binDir" -ForegroundColor Green
    Write-Host ""
    Write-Host "WARNING: Please restart PowerShell to apply PATH changes" -ForegroundColor Yellow
} else {
    Write-Host "Already in PATH" -ForegroundColor Green
}

Write-Host ""
Write-Host "Verifying installation..." -ForegroundColor Yellow
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$machinePath = [Environment]::GetEnvironmentVariable("Path", "Machine")
$env:Path = "$userPath;$machinePath"

try {
    $pdfinfoPath = Join-Path $binDir "pdfinfo.exe"
    if (Test-Path $pdfinfoPath) {
        $version = & $pdfinfoPath -v 2>&1
        Write-Host "Poppler installed successfully" -ForegroundColor Green
        Write-Host "Version: $version" -ForegroundColor White
    } else {
        Write-Host "Warning: pdfinfo.exe not found" -ForegroundColor Yellow
    }
} catch {
    Write-Host "Warning: Verification failed (may need PATH reload)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installation Complete" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Restart PowerShell" -ForegroundColor White
Write-Host "2. Verify: pdfinfo -v" -ForegroundColor White
Write-Host "3. Run pdftexter command again" -ForegroundColor White
