#!/usr/bin/env pwsh
# CA Policy Manager - Security Fixes Validation Script
# Tests that all 7 critical security fixes are properly implemented

Write-Host ""
Write-Host "🔒 Security Fixes Validation" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green
Write-Host ""

$testsPass = 0
$testsFail = 0

# Test 1: Check for hardcoded credentials
Write-Host "Test 1️⃣  Hardcoded Credentials" -ForegroundColor Cyan
$hasHardcodedID = Select-String -Path "CA_Policy_Manager_Web/config.py" -Pattern "bcb41e64-e9a8-421c-9331-699dd9041d58" -ErrorAction SilentlyContinue
if ($null -eq $hasHardcodedID) {
    Write-Host "✅ PASS: No hardcoded Client ID found" -ForegroundColor Green
    $testsPass++
}
else {
    Write-Host "❌ FAIL: Hardcoded Client ID still present!" -ForegroundColor Red
    $testsFail++
}

Write-Host ""

# Test 2: Check for debug mode
Write-Host "Test 2️⃣  Debug Mode Removal" -ForegroundColor Cyan
$debugMode = Select-String -Path "CA_Policy_Manager_Web/app.py" -Pattern "app\.run.*debug=True" -ErrorAction SilentlyContinue
$envControl = Select-String -Path "CA_Policy_Manager_Web/app.py" -Pattern "debug_mode = os\.environ\.get.*FLASK_ENV" -ErrorAction SilentlyContinue

if ($null -eq $debugMode -and $null -ne $envControl) {
    Write-Host "✅ PASS: Debug mode controlled by environment variable" -ForegroundColor Green
    $testsPass++
}
else {
    Write-Host "❌ FAIL: Debug mode still hardcoded" -ForegroundColor Red
    $testsFail++
}

Write-Host ""

# Test 3: Check SSL verification
Write-Host "Test 3️⃣  SSL Verification Defaults" -ForegroundColor Cyan
$sslDefault = Select-String -Path "CA_Policy_Manager_Web/config.py" -Pattern "VERIFY_SSL = os\.environ\.get.*true.*true" -ErrorAction SilentlyContinue
if ($null -ne $sslDefault) {
    Write-Host "✅ PASS: SSL verification defaults to true" -ForegroundColor Green
    $testsPass++
}
else {
    Write-Host "⚠️  CHECK: SSL verification default needs verification" -ForegroundColor Yellow
    $testsFail++
}

Write-Host ""

# Test 4: Check session manager
Write-Host "Test 4️⃣  Session Manager Implementation" -ForegroundColor Cyan
if (Test-Path "CA_Policy_Manager_Web/session_manager.py") {
    Write-Host "✅ PASS: session_manager.py exists" -ForegroundColor Green
    $testsPass++
}
else {
    Write-Host "❌ FAIL: session_manager.py not found" -ForegroundColor Red
    $testsFail++
}

Write-Host ""

# Test 5: Check error handling
Write-Host "Test 5️⃣  Error Response Sanitization" -ForegroundColor Cyan
$errorHandler = Select-String -Path "CA_Policy_Manager_Web/app.py" -Pattern "@app\.errorhandler" -ErrorAction SilentlyContinue
$safeError = Select-String -Path "CA_Policy_Manager_Web/app.py" -Pattern "safe_error_response" -ErrorAction SilentlyContinue

if ($null -ne $errorHandler -and $null -ne $safeError) {
    Write-Host "✅ PASS: Centralized error handling with safe responses" -ForegroundColor Green
    $testsPass++
}
else {
    Write-Host "❌ FAIL: Error handling not properly implemented" -ForegroundColor Red
    $testsFail++
}

Write-Host ""

# Test 6: Check CSRF protection
Write-Host "Test 6️⃣  CSRF Protection" -ForegroundColor Cyan
$csrfProtect = Select-String -Path "CA_Policy_Manager_Web/app.py" -Pattern "CSRFProtect" -ErrorAction SilentlyContinue
$csrfDep = Select-String -Path "CA_Policy_Manager_Web/requirements.txt" -Pattern "flask-wtf" -ErrorAction SilentlyContinue

if ($null -ne $csrfProtect -and $null -ne $csrfDep) {
    Write-Host "✅ PASS: CSRF protection implemented" -ForegroundColor Green
    $testsPass++
}
else {
    Write-Host "❌ FAIL: CSRF protection not found" -ForegroundColor Red
    $testsFail++
}

Write-Host ""

# Test 7: Check security headers
Write-Host "Test 7️⃣  Security Headers" -ForegroundColor Cyan
$secHeaders = Select-String -Path "CA_Policy_Manager_Web/app.py" -Pattern "@app\.after_request" -ErrorAction SilentlyContinue
$hsts = Select-String -Path "CA_Policy_Manager_Web/app.py" -Pattern "Strict-Transport-Security" -ErrorAction SilentlyContinue

if ($null -ne $secHeaders -and $null -ne $hsts) {
    Write-Host "✅ PASS: Security headers middleware implemented" -ForegroundColor Green
    $testsPass++
}
else {
    Write-Host "❌ FAIL: Security headers not found" -ForegroundColor Red
    $testsFail++
}

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Green

# Summary
Write-Host ""
Write-Host "📊 Test Summary" -ForegroundColor Cyan
Write-Host "   Passed: $testsPass/7 ✅" -ForegroundColor Green
Write-Host "   Failed: $testsFail/7" -ForegroundColor $(if ($testsFail -eq 0) { "Green" } else { "Red" })

Write-Host ""

if ($testsFail -eq 0) {
    Write-Host "✅ All security fixes verified!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Run: .\setup-local.ps1" -ForegroundColor Yellow
    Write-Host "2. Edit: CA_Policy_Manager_Web\.env" -ForegroundColor Yellow
    Write-Host "3. Run: cd CA_Policy_Manager_Web; python app.py" -ForegroundColor Yellow
}
else {
    Write-Host "⚠️  Some checks failed. Review the output above." -ForegroundColor Yellow
}

Write-Host ""
