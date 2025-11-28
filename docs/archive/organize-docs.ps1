#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Organize documentation files into clean folder structure
.DESCRIPTION
    Moves scattered .md files into organized docs/ subfolder
#>

$ErrorActionPreference = "Stop"

Write-Host "📁 Organizing Documentation Files..." -ForegroundColor Cyan
Write-Host ""

# Create docs folder structure
$docsRoot = "docs"
New-Item -ItemType Directory -Path $docsRoot -Force | Out-Null
New-Item -ItemType Directory -Path "$docsRoot\setup" -Force | Out-Null
New-Item -ItemType Directory -Path "$docsRoot\security" -Force | Out-Null
New-Item -ItemType Directory -Path "$docsRoot\archive" -Force | Out-Null

# Files to KEEP in root (essential user-facing docs)
$keepInRoot = @(
    "README.md",
    "LICENSE",
    "CONTRIBUTING.md",
    "SECURITY.md"
)

# Setup/Getting Started docs
$setupDocs = @(
    "QUICK_START.md",
    "QUICK_START_LOCAL.md",
    "START_HERE.md",
    "LOCAL_TESTING_GUIDE.md",
    "FIRST_TIME_SETUP_CHECKLIST.md",
    "SETUP_FLOW_DIAGRAM.md",
    "SETUP_FOR_FORKS.md",
    "TESTING_LOCAL_SETUP.md"
)

# Security/Publishing docs
$securityDocs = @(
    "CRITICAL_SECURITY_FIXES_SUMMARY.md",
    "SECURITY_FIXES_COMPLETE.md",
    "SECURITY_REMEDIATION_DETAILED.md",
    "PRE_PUBLICATION_SECURITY_CHECKLIST.md",
    "PUBLICATION_GUIDE.md",
    "PUBLISHING_INSTALL_GUIDE.md",
    "GITHUB_PREP.md"
)

# Archive (outdated/redundant docs)
$archiveDocs = @(
    "AUTOMATION_PACKAGE_SUMMARY.md",
    "DOCUMENTATION_INDEX.md"
)

# Move setup docs
Write-Host "📦 Moving setup documentation..." -ForegroundColor Yellow
foreach ($file in $setupDocs) {
    if (Test-Path $file) {
        Move-Item -Path $file -Destination "$docsRoot\setup\" -Force
        Write-Host "  ✓ Moved $file → docs\setup\" -ForegroundColor Green
    }
}

# Move security/publishing docs
Write-Host ""
Write-Host "🔒 Moving security & publishing documentation..." -ForegroundColor Yellow
foreach ($file in $securityDocs) {
    if (Test-Path $file) {
        Move-Item -Path $file -Destination "$docsRoot\security\" -Force
        Write-Host "  ✓ Moved $file → docs\security\" -ForegroundColor Green
    }
}

# Move archive docs
Write-Host ""
Write-Host "📦 Archiving outdated documentation..." -ForegroundColor Yellow
foreach ($file in $archiveDocs) {
    if (Test-Path $file) {
        Move-Item -Path $file -Destination "$docsRoot\archive\" -Force
        Write-Host "  ✓ Moved $file → docs\archive\" -ForegroundColor Green
    }
}

# Create index in docs folder
Write-Host ""
Write-Host "📝 Creating documentation index..." -ForegroundColor Yellow

$indexContent = @"
# Documentation Index

This folder contains all documentation for the CA Policy Manager Tool.

## 📂 Organization

### Root Level (Essential Docs)
- **README.md** - Main project overview and quick start
- **LICENSE** - Project license
- **CONTRIBUTING.md** - Contribution guidelines
- **SECURITY.md** - Security policy and reporting

### 📦 setup/
Getting started, installation, and configuration guides:
- **QUICK_START.md** - Fast-track setup for experienced users
- **START_HERE.md** - Comprehensive beginner's guide
- **LOCAL_TESTING_GUIDE.md** - Local development setup
- **SETUP_FOR_FORKS.md** - Fork-specific setup instructions
- **FIRST_TIME_SETUP_CHECKLIST.md** - Step-by-step setup checklist
- **SETUP_FLOW_DIAGRAM.md** - Visual setup flow
- **TESTING_LOCAL_SETUP.md** - Testing your local installation

### 🔒 security/
Security, publishing, and production deployment:
- **PUBLICATION_GUIDE.md** - How to publish this project
- **PUBLISHING_INSTALL_GUIDE.md** - Installation guide for end users
- **GITHUB_PREP.md** - Preparing for GitHub publication
- **PRE_PUBLICATION_SECURITY_CHECKLIST.md** - Security review checklist
- **SECURITY_FIXES_COMPLETE.md** - Security improvements log
- **SECURITY_REMEDIATION_DETAILED.md** - Detailed security remediation
- **CRITICAL_SECURITY_FIXES_SUMMARY.md** - Critical fixes summary

### 📦 archive/
Outdated or superseded documentation:
- **AUTOMATION_PACKAGE_SUMMARY.md** - Old automation docs
- **DOCUMENTATION_INDEX.md** - Replaced by this index

## 🚀 Quick Links

**First Time User?** Start with [setup/START_HERE.md](setup/START_HERE.md)

**Quick Setup?** See [setup/QUICK_START.md](setup/QUICK_START.md)

**Publishing?** Read [security/PUBLICATION_GUIDE.md](security/PUBLICATION_GUIDE.md)

**Contributing?** Check [../CONTRIBUTING.md](../CONTRIBUTING.md)
"@

Set-Content -Path "$docsRoot\README.md" -Value $indexContent -Force
Write-Host "  ✓ Created docs\README.md index" -ForegroundColor Green

# Summary
Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "✅ Documentation organization complete!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""
Write-Host "📁 New structure:" -ForegroundColor White
Write-Host "  / (root)           - 4 essential files" -ForegroundColor Gray
Write-Host "  docs/setup/        - $(($setupDocs | Where-Object { Test-Path "$docsRoot\setup\$_" }).Count) setup guides" -ForegroundColor Gray
Write-Host "  docs/security/     - $(($securityDocs | Where-Object { Test-Path "$docsRoot\security\$_" }).Count) security/publishing docs" -ForegroundColor Gray
Write-Host "  docs/archive/      - $(($archiveDocs | Where-Object { Test-Path "$docsRoot\archive\$_" }).Count) archived files" -ForegroundColor Gray
Write-Host ""
Write-Host "📖 Start here: docs\README.md" -ForegroundColor Cyan
