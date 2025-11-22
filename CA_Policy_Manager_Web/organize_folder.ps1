# Folder Organization Script for CA Policy Manager Web
# This script organizes the project into a clean folder structure

Write-Host "🗂️  Organizing CA Policy Manager Web folder structure..." -ForegroundColor Cyan

# Create directory structure
$directories = @(
    "docs",
    "scripts",
    "utils",
    "data/backups",
    "data/uploads"
)

foreach ($dir in $directories) {
    $path = Join-Path $PWD $dir
    if (-not (Test-Path $path)) {
        New-Item -ItemType Directory -Path $path -Force | Out-Null
        Write-Host "✅ Created: $dir" -ForegroundColor Green
    }
}

# Move documentation files
$docsFiles = @(
    "README.md",
    "QUICK_SETUP.md",
    "QUICK_START.md",
    "SETUP_ENTRA_AUTH.md",
    "SHARE_WITH_FRIEND.md",
    "FIX_PERMISSIONS.md",
    "SUMMARY.md",
    "CA_POLICY_FRAMEWORK.md",
    "CA_POLICY_TEMPLATES_README.md"
)

foreach ($file in $docsFiles) {
    if (Test-Path $file) {
        Move-Item -Path $file -Destination "docs\" -Force
        Write-Host "📄 Moved $file to docs/" -ForegroundColor Yellow
    }
}

# Move script files
$scriptFiles = @(
    "Register-Entra App.ps1",
    "create_ca_groups.ps1",
    "start_web_app.bat",
    "startup.sh",
    "build_templates.py",
    "generate_policies.py",
    "test_templates.py"
)

foreach ($file in $scriptFiles) {
    if (Test-Path $file) {
        Move-Item -Path $file -Destination "scripts\" -Force
        Write-Host "🔧 Moved $file to scripts/" -ForegroundColor Yellow
    }
}

# Move backup/template files
$backupFiles = @(
    "ca_policy_examples_backup.py",
    "ca_policy_examples_new.py",
    "ca_policy_examples_TEMPLATE.txt"
)

foreach ($file in $backupFiles) {
    if (Test-Path $file) {
        Move-Item -Path $file -Destination "data\backups\" -Force
        Write-Host "💾 Moved $file to data/backups/" -ForegroundColor Yellow
    }
}

# Move uploads folder content
if (Test-Path "uploads") {
    Get-ChildItem "uploads" | Move-Item -Destination "data\uploads\" -Force
    Remove-Item "uploads" -Recurse -Force
    Write-Host "📁 Moved uploads content to data/uploads/" -ForegroundColor Yellow
}

# Move report_analyzer to utils (it's a utility module)
if (Test-Path "report_analyzer.py") {
    Move-Item -Path "report_analyzer.py" -Destination "utils\" -Force
    Write-Host "🔧 Moved report_analyzer.py to utils/" -ForegroundColor Yellow
}

Write-Host "`n✨ Folder organization complete!" -ForegroundColor Green
Write-Host "`n📊 New structure:" -ForegroundColor Cyan
Write-Host "  📁 Root (CA_Policy_Manager_Web/)" -ForegroundColor White
Write-Host "    ├── app.py (main Flask application)" -ForegroundColor Gray
Write-Host "    ├── ca_policy_manager.py (Graph API manager)" -ForegroundColor Gray
Write-Host "    ├── ca_policy_examples.py (policy templates)" -ForegroundColor Gray
Write-Host "    ├── requirements.txt" -ForegroundColor Gray
Write-Host "    ├── .gitignore" -ForegroundColor Gray
Write-Host "    ├── 📁 templates/ (HTML templates)" -ForegroundColor White
Write-Host "    ├── 📁 static/ (CSS, JS, images)" -ForegroundColor White
Write-Host "    ├── 📁 utils/ (utility modules)" -ForegroundColor White
Write-Host "    ├── 📁 docs/ (documentation)" -ForegroundColor White
Write-Host "    ├── 📁 scripts/ (setup & utility scripts)" -ForegroundColor White
Write-Host "    └── 📁 data/ (uploads & backups)" -ForegroundColor White

Write-Host "`n⚠️  Note: You'll need to update import paths in app.py:" -ForegroundColor Yellow
Write-Host "  - Change 'from report_analyzer import' to 'from utils.report_analyzer import'" -ForegroundColor Gray
