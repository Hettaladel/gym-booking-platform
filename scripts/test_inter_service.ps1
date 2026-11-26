# Test Inter-Service Communication
Write-Host "=== Testing Inter-Service Communication ===" -ForegroundColor Cyan

# Step 1: Login
Write-Host "`n1. Login..." -ForegroundColor Yellow
$loginBody = '{"username":"postman","password":"TestPass123!"}'
$loginResponse = Invoke-RestMethod -Uri "http://localhost:8001/api/auth/login/" -Method Post -ContentType "application/json" -Body $loginBody
$token = $loginResponse.access
Write-Host "OK Token obtained" -ForegroundColor Green

$headers = @{
    Authorization = "Bearer $token"
}

# Step 2: Create reservation (should call auth + courses services)
Write-Host "`n2. Creating reservation (testing inter-service calls)..." -ForegroundColor Yellow
$createBody = '{"session_id":2}'

try {
    $reservation = Invoke-RestMethod -Uri "http://localhost:8003/api/reservations/" -Method Post -Headers $headers -ContentType "application/json" -Body $createBody
    Write-Host "SUCCESS! Reservation created with ID: $($reservation.id)" -ForegroundColor Green
    Write-Host "  User ID: $($reservation.user_id)" -ForegroundColor Cyan
    Write-Host "  Session ID: $($reservation.session_id)" -ForegroundColor Cyan
    Write-Host "  Status: $($reservation.status)" -ForegroundColor Cyan
    Write-Host "`nInter-service communication is WORKING!" -ForegroundColor Green
}
catch {
    Write-Host "FAILED" -ForegroundColor Red
    Write-Host $_.ErrorDetails.Message
    Write-Host "`nChecking logs for details..." -ForegroundColor Yellow
}
