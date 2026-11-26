# Test Ownership Verification
Write-Host "=== Testing Ownership Verification ===" -ForegroundColor Cyan

# Step 1: Login as postman
Write-Host "`n1. Login as postman..." -ForegroundColor Yellow
$loginBody = '{"username":"postman","password":"TestPass123!"}'
$loginResponse = Invoke-RestMethod -Uri "http://localhost:8001/api/auth/login/" -Method Post -ContentType "application/json" -Body $loginBody
$token = $loginResponse.access
Write-Host "OK Token obtained" -ForegroundColor Green

$headers = @{
    Authorization = "Bearer $token"
}

# Step 2: Create a reservation
Write-Host "`n2. Creating reservation..." -ForegroundColor Yellow
$createBody = '{"session_id":2}'
try {
    $reservation = Invoke-RestMethod -Uri "http://localhost:8003/api/reservations/" -Method Post -Headers $headers -ContentType "application/json" -Body $createBody
    Write-Host "OK Created reservation ID: $($reservation.id)" -ForegroundColor Green
    $resId = $reservation.id
}
catch {
    Write-Host "WARN Could not create (may already exist)" -ForegroundColor Yellow
    # Get existing reservation
    $myRes = Invoke-RestMethod -Uri "http://localhost:8003/api/reservations/my/" -Method Get -Headers $headers
    $resId = ($myRes | Where-Object { $_.status -eq "CONFIRMED" } | Select-Object -First 1).id
    Write-Host "Using existing reservation ID: $resId" -ForegroundColor Yellow
}

# Step 3: Cancel own reservation (should work)
Write-Host "`n3. Cancelling own reservation..." -ForegroundColor Yellow
try {
    $cancelled = Invoke-RestMethod -Uri "http://localhost:8003/api/reservations/$resId/" -Method Delete -Headers $headers
    Write-Host "SUCCESS! Cancelled own reservation" -ForegroundColor Green
    Write-Host "  Status: $($cancelled.status)" -ForegroundColor Cyan
}
catch {
    Write-Host "FAILED" -ForegroundColor Red
    Write-Host $_.ErrorDetails.Message
}

Write-Host "`n=== Ownership Verification Test Complete ===" -ForegroundColor Cyan
