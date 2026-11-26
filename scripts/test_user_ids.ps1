# Test to see user_data from auth service
$loginBody = '{"username":"postman","password":"TestPass123!"}'
$loginResponse = Invoke-RestMethod -Uri "http://localhost:8001/api/auth/login/" -Method Post -ContentType "application/json" -Body $loginBody
$token = $loginResponse.access

Write-Host "Token: $($token.Substring(0,20))..."

$headers = @{
    Authorization = "Bearer $token"
}

# Get user profile from auth service
$userProfile = Invoke-RestMethod -Uri "http://localhost:8001/api/users/me/" -Method Get -Headers $headers
Write-Host "`nUser Profile from Auth Service:"
Write-Host "  ID: $($userProfile.id) (type: $($userProfile.id.GetType().Name))"
Write-Host "  Username: $($userProfile.username)"
Write-Host "  Email: $($userProfile.email)"

# Get reservations
$reservations = Invoke-RestMethod -Uri "http://localhost:8003/api/reservations/my/" -Method Get -Headers $headers
Write-Host "`nReservations:"
$reservations | ForEach-Object {
    Write-Host "  Reservation ID: $($_.id), user_id: $($_.user_id) (type: $($_.user_id.GetType().Name))"
}
