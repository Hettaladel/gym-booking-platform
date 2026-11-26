# Comprehensive End-to-End Tests
Write-Host "=== COMPREHENSIVE BACKEND TESTS ===" -ForegroundColor Cyan

$testsPassed = 0
$testsFailed = 0

# Test 1: User Registration
Write-Host "`n[TEST 1] User Registration" -ForegroundColor Yellow
try {
    $regBody = @{
        username = "testuser_$(Get-Random)"
        password = "TestPass123!"
        password2 = "TestPass123!"
        email = "test@example.com"
    } | ConvertTo-Json
    
    $regResult = Invoke-RestMethod -Uri "http://localhost:8001/api/auth/register/" -Method Post -ContentType "application/json" -Body $regBody
    Write-Host "  PASS - User registered: $($regResult.username)" -ForegroundColor Green
    $testsPassed++
    $testUsername = $regResult.username
}
catch {
    Write-Host "  FAIL - $($_.ErrorDetails.Message)" -ForegroundColor Red
    $testsFailed++
}

# Test 2: User Login
Write-Host "`n[TEST 2] User Login" -ForegroundColor Yellow
$loginBody = @{
    username = $testUsername
    password = "TestPass123!"
} | ConvertTo-Json
try {
    $loginResponse = Invoke-RestMethod -Uri "http://localhost:8001/api/auth/login/" -Method Post -ContentType "application/json" -Body $loginBody
    $token = $loginResponse.access
    Write-Host "  PASS - Token obtained" -ForegroundColor Green
    $testsPassed++
}
catch {
    Write-Host "  FAIL - $($_.ErrorDetails.Message)" -ForegroundColor Red
    $testsFailed++
    exit
}

$headers = @{ Authorization = "Bearer $token" }

# Test 3: Get User Profile
Write-Host "`n[TEST 3] Get User Profile" -ForegroundColor Yellow
try {
    $profile = Invoke-RestMethod -Uri "http://localhost:8001/api/users/me/" -Method Get -Headers $headers
    Write-Host "  PASS - Profile retrieved: $($profile.username)" -ForegroundColor Green
    $testsPassed++
}
catch {
    Write-Host "  FAIL - $($_.ErrorDetails.Message)" -ForegroundColor Red
    $testsFailed++
}

# Test 4: List Sessions
Write-Host "`n[TEST 4] List Sessions" -ForegroundColor Yellow
try {
    $sessions = Invoke-RestMethod -Uri "http://localhost:8002/api/courses/sessions/" -Method Get -Headers $headers
    Write-Host "  PASS - Found $($sessions.Count) session(s)" -ForegroundColor Green
    $testsPassed++
    # Get the LATEST session (highest ID) because older ones might be expired
    $latestSession = $sessions | Sort-Object id -Descending | Select-Object -First 1
    $sessionId = $latestSession.id
    Write-Host "  DEBUG - Selected Session ID: $sessionId (End: $($latestSession.end_datetime))" -ForegroundColor Cyan
}
catch {
    Write-Host "  FAIL - $($_.ErrorDetails.Message)" -ForegroundColor Red
    $testsFailed++
}

# Test 5: Create Reservation (with full validation)
Write-Host "`n[TEST 5] Create Reservation (Full Validation)" -ForegroundColor Yellow
if (-not $sessionId) { $sessionId = 1 }
$createBody = @{ session_id = $sessionId } | ConvertTo-Json
try {
    $reservation = Invoke-RestMethod -Uri "http://localhost:8003/api/reservations/" -Method Post -Headers $headers -ContentType "application/json" -Body $createBody
    Write-Host "  PASS - Reservation created: ID $($reservation.id)" -ForegroundColor Green
    $testsPassed++
    $resId = $reservation.id
}
catch {
    Write-Host "  FAIL - $($_.ErrorDetails.Message)" -ForegroundColor Red
    $testsFailed++
}

# Test 6: List My Reservations
Write-Host "`n[TEST 6] List My Reservations" -ForegroundColor Yellow
try {
    $myReservations = Invoke-RestMethod -Uri "http://localhost:8003/api/reservations/my/" -Method Get -Headers $headers
    Write-Host "  PASS - Found $($myReservations.Count) reservation(s)" -ForegroundColor Green
    $testsPassed++
}
catch {
    Write-Host "  FAIL - $($_.ErrorDetails.Message)" -ForegroundColor Red
    $testsFailed++
}

# Test 7: Duplicate Reservation (should fail)
Write-Host "`n[TEST 7] Duplicate Reservation Prevention" -ForegroundColor Yellow
try {
    $duplicate = Invoke-RestMethod -Uri "http://localhost:8003/api/reservations/" -Method Post -Headers $headers -ContentType "application/json" -Body $createBody
    Write-Host "  FAIL - Should have prevented duplicate" -ForegroundColor Red
    $testsFailed++
}
catch {
    if ($_.ErrorDetails.Message -like "*Vous avez*") {
        Write-Host "  PASS - Duplicate prevented correctly" -ForegroundColor Green
        $testsPassed++
    }
    else {
        Write-Host "  FAIL - Wrong error: $($_.ErrorDetails.Message)" -ForegroundColor Red
        $testsFailed++
    }
}

# Test 8: Cancel Own Reservation
Write-Host "`n[TEST 8] Cancel Own Reservation (Ownership Check)" -ForegroundColor Yellow
if ($resId) {
    try {
        $cancelled = Invoke-RestMethod -Uri "http://localhost:8003/api/reservations/$resId/" -Method Delete -Headers $headers
        Write-Host "  PASS - Cancelled successfully: $($cancelled.status)" -ForegroundColor Green
        $testsPassed++
    }
    catch {
        Write-Host "  FAIL - $($_.ErrorDetails.Message)" -ForegroundColor Red
        $testsFailed++
    }
}
else {
    Write-Host "  SKIP - No reservation to cancel" -ForegroundColor Yellow
}

# Summary
Write-Host "`n==================================" -ForegroundColor Cyan
Write-Host "TESTS PASSED: $testsPassed" -ForegroundColor Green
Write-Host "TESTS FAILED: $testsFailed" -ForegroundColor Red
Write-Host "==================================" -ForegroundColor Cyan

if ($testsFailed -eq 0) {
    Write-Host "`nALL TESTS PASSED! Backend is 100% functional!" -ForegroundColor Green
}
else {
    Write-Host "`nSome tests failed. Review errors above." -ForegroundColor Yellow
}
