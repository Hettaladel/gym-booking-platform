# Test Reservations Endpoints
Write-Host "=== Testing Reservations Service ===" -ForegroundColor Cyan

# Step 1: Login to get token
Write-Host "`n1. Login..." -ForegroundColor Yellow
$loginBody = @{
    username = "postman"
    password = "TestPass123!"
} | ConvertTo-Json

$loginResponse = Invoke-RestMethod -Uri "http://localhost:8001/api/auth/login/" -Method Post -ContentType "application/json" -Body $loginBody
$token = $loginResponse.access
Write-Host "OK Token obtained" -ForegroundColor Green

$headers = @{
    Authorization = "Bearer $token"
}

# Step 2: List my reservations
Write-Host "`n2. List my reservations..." -ForegroundColor Yellow
try {
    $myReservations = Invoke-RestMethod -Uri "http://localhost:8003/api/reservations/my/" -Method Get -Headers $headers
    Write-Host "OK Found $($myReservations.Count) reservation(s)" -ForegroundColor Green
    $myReservations | ForEach-Object {
        Write-Host "  - Reservation ID: $($_.id), Session: $($_.session_id), Status: $($_.status)" -ForegroundColor Cyan
    }
    
    if ($myReservations.Count -gt 0) {
        $reservationId = $myReservations[0].id
    }
}
catch {
    Write-Host "FAIL to list reservations" -ForegroundColor Red
    Write-Host $_.Exception.Message
}

# Step 3: Create another reservation
Write-Host "`n3. Create a new reservation..." -ForegroundColor Yellow
$createBody = @{
    session_id = 2
} | ConvertTo-Json

try {
    $newReservation = Invoke-RestMethod -Uri "http://localhost:8003/api/reservations/" -Method Post -Headers $headers -ContentType "application/json" -Body $createBody
    Write-Host "OK Created reservation ID: $($newReservation.id)" -ForegroundColor Green
    $reservationToCancel = $newReservation.id
}
catch {
    Write-Host "WARN Could not create new reservation" -ForegroundColor Yellow
    $reservationToCancel = $reservationId
}

# Step 4: Cancel a reservation
if ($reservationToCancel) {
    Write-Host "`n4. Cancel reservation ID: $reservationToCancel..." -ForegroundColor Yellow
    try {
        $cancelResponse = Invoke-RestMethod -Uri "http://localhost:8003/api/reservations/$reservationToCancel/" -Method Delete -Headers $headers
        Write-Host "OK Reservation cancelled" -ForegroundColor Green
        Write-Host "  Status: $($cancelResponse.status)" -ForegroundColor Cyan
    }
    catch {
        Write-Host "FAIL to cancel reservation" -ForegroundColor Red
        Write-Host $_.ErrorDetails.Message
    }
}
else {
    Write-Host "`n4. Skipping cancellation test" -ForegroundColor Yellow
}

# Step 5: List reservations again
Write-Host "`n5. List reservations again..." -ForegroundColor Yellow
try {
    $finalReservations = Invoke-RestMethod -Uri "http://localhost:8003/api/reservations/my/" -Method Get -Headers $headers
    Write-Host "OK Current reservations:" -ForegroundColor Green
    $finalReservations | ForEach-Object {
        $color = if ($_.status -eq "CANCELLED") { "Red" } else { "Green" }
        Write-Host "  - ID: $($_.id), Session: $($_.session_id), Status: $($_.status)" -ForegroundColor $color
    }
}
catch {
    Write-Host "FAIL to list reservations" -ForegroundColor Red
}

Write-Host "`n=== Test Complete ===" -ForegroundColor Cyan
