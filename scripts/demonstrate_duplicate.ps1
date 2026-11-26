# Demonstrate Duplicate Reservation Prevention
Write-Host "=== TEST : PREVENTION DES DOUBLONS ===" -ForegroundColor Cyan

# 1. Login
try {
    $login = Invoke-RestMethod -Uri "http://localhost:8001/api/auth/login/" -Method Post -Body (@{username="superadmin"; password="admin123"} | ConvertTo-Json) -ContentType "application/json"
    $token = $login.access
    $headers = @{ Authorization = "Bearer $token" }
    Write-Host "1. Login Admin... OK" -ForegroundColor Green
} catch {
    Write-Host "ERREUR LOGIN. Arret." -ForegroundColor Red
    exit
}

# 2. Get Session
try {
    $sessions = Invoke-RestMethod -Uri "http://localhost:8002/api/courses/sessions/" -Method Get -Headers $headers
    $sessionId = $sessions | Sort-Object id -Descending | Select-Object -First 1 -ExpandProperty id
    Write-Host "2. Cible: Séance ID $sessionId" -ForegroundColor Green
} catch {
    Write-Host "ERREUR RECUPERATION SESSION. Arret." -ForegroundColor Red
    exit
}

# 3. First Reservation
try {
    $body = @{session_id=$sessionId} | ConvertTo-Json
    Invoke-RestMethod -Uri "http://localhost:8003/api/reservations/" -Method Post -Headers $headers -ContentType "application/json" -Body $body | Out-Null
    Write-Host "3. Première Réservation... REUSSIE (201 Created)" -ForegroundColor Green
} catch {
    Write-Host "3. Première Réservation... (Déjà existante, on continue)" -ForegroundColor Yellow
}

# 4. SECOND Reservation (MUST FAIL)
Write-Host "4. Tentative de DOUBLON (Même séance)..." -ForegroundColor Yellow
try {
    $body = @{session_id=$sessionId} | ConvertTo-Json
    Invoke-RestMethod -Uri "http://localhost:8003/api/reservations/" -Method Post -Headers $headers -ContentType "application/json" -Body $body | Out-Null
    Write-Host "⛔ ECHEC : Le doublon a été accepté ! (Ce n'est pas normal)" -ForegroundColor Red
} catch {
    Write-Host "✅ SUCCES : Le système a bloqué le doublon !" -ForegroundColor Green -BackgroundColor Black
    # Access exception correctly for PS 5.1
    $msg = $_.Exception.Message
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $msg = $reader.ReadToEnd()
    }
    Write-Host "   Message d'erreur reçu : $msg" -ForegroundColor Red
}
Write-Host "======================================" -ForegroundColor Cyan
