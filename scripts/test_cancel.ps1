# Simple cancel test
$loginBody = '{"username":"postman","password":"TestPass123!"}'
$loginResponse = Invoke-RestMethod -Uri "http://localhost:8001/api/auth/login/" -Method Post -ContentType "application/json" -Body $loginBody
$token = $loginResponse.access

Write-Host "Token: $($token.Substring(0,20))..."

$headers = @{
    Authorization = "Bearer $token"
}

try {
    $result = Invoke-RestMethod -Uri "http://localhost:8003/api/reservations/8/" -Method Delete -Headers $headers
    Write-Host "SUCCESS: Cancelled" -ForegroundColor Green
    Write-Host $result | ConvertTo-Json
}
catch {
    Write-Host "FAILED" -ForegroundColor Red
    Write-Host $_.ErrorDetails.Message
}
