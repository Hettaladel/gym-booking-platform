# Test 1: Login to get token
$loginBody = @{
    username = "postman"
    password = "TestPass123!"
} | ConvertTo-Json

Write-Host "=== Test 1: Login ===" -ForegroundColor Cyan
$loginResponse = Invoke-RestMethod -Uri "http://localhost:8001/api/auth/login/" -Method Post -ContentType "application/json" -Body $loginBody
$token = $loginResponse.access
Write-Host "Token obtained: $($token.Substring(0,20))..." -ForegroundColor Green

# Test 2: Access session with token
Write-Host "`n=== Test 2: Get Session 2 Details ===" -ForegroundColor Cyan
$headers = @{
    Authorization = "Bearer $token"
}

try {
    $sessionResponse = Invoke-RestMethod -Uri "http://localhost:8002/api/sessions/2/" -Method Get -Headers $headers
    Write-Host "SUCCESS! Session details:" -ForegroundColor Green
    $sessionResponse | ConvertTo-Json
} catch {
    Write-Host "FAILED! Error:" -ForegroundColor Red
    Write-Host $_.Exception.Message
    Write-Host $_.ErrorDetails.Message
}
