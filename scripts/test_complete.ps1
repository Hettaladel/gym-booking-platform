# Complete test: Create and Cancel
$loginBody = '{"username":"postman","password":"TestPass123!"}'
$loginResponse = Invoke-RestMethod -Uri "http://localhost:8001/api/auth/login/" -Method Post -ContentType "application/json" -Body $loginBody
$token = $loginResponse.access

$headers = @{
    Authorization = "Bearer $token"
}

Write-Host "1. Creating new reservation..." -ForegroundColor Yellow
$createBody = '{"session_id":2}'
try {
    $newRes = Invoke-RestMethod -Uri "http://localhost:8003/api/reservations/" -Method Post -Headers $headers -ContentType "application/json" -Body $createBody
    Write-Host "OK Created ID: $($newRes.id)" -ForegroundColor Green
    $resId = $newRes.id
}
catch {
    Write-Host "FAIL" -ForegroundColor Red
    Write-Host $_.ErrorDetails.Message
    exit
}

Write-Host "`n2. Cancelling reservation $resId..." -ForegroundColor Yellow
try {
    $cancelled = Invoke-RestMethod -Uri "http://localhost:8003/api/reservations/$resId/" -Method Delete -Headers $headers
    Write-Host "SUCCESS Cancelled!" -ForegroundColor Green
    Write-Host "  Status: $($cancelled.status)" -ForegroundColor Cyan
}
catch {
    Write-Host "FAIL" -ForegroundColor Red
    Write-Host $_.ErrorDetails.Message
}

Write-Host "`n3. Listing reservations..." -ForegroundColor Yellow
$list = Invoke-RestMethod -Uri "http://localhost:8003/api/reservations/my/" -Method Get -Headers $headers
$list | ForEach-Object {
    $color = if ($_.status -eq "CANCELLED") { "Red" } else { "Green" }
    Write-Host "  - ID: $($_.id), Status: $($_.status)" -ForegroundColor $color
}
