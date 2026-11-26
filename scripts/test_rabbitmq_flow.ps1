# ============================================
# TEST COMPLET - RABBITMQ avec Réservation
# ============================================

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "TEST RABBITMQ - Flux Complet" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# 1. Créer un utilisateur
Write-Host "`n[1/5] Création d'un utilisateur..." -ForegroundColor Yellow
$registerResponse = Invoke-RestMethod -Uri "http://localhost:8001/api/auth/register/" -Method Post -Body (@{
    username = "testrabbit"
    password = "test123"
    email = "testrabbit@test.com"
    role = "member"
} | ConvertTo-Json) -ContentType "application/json"

Write-Host "✓ Utilisateur créé: $($registerResponse.username)" -ForegroundColor Green

# 2. Se connecter
Write-Host "`n[2/5] Connexion..." -ForegroundColor Yellow
$loginResponse = Invoke-RestMethod -Uri "http://localhost:8001/api/auth/login/" -Method Post -Body (@{
    username = "testrabbit"
    password = "test123"
} | ConvertTo-Json) -ContentType "application/json"

$token = $loginResponse.access
Write-Host "✓ Token obtenu" -ForegroundColor Green

# 3. Créer une réservation (cela devrait envoyer un message à RabbitMQ)
Write-Host "`n[3/5] Création d'une réservation..." -ForegroundColor Yellow
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

try {
    $reservationResponse = Invoke-RestMethod -Uri "http://localhost:8003/api/reservations/" -Method Post -Headers $headers -Body (@{
        session_id = 1
    } | ConvertTo-Json)
    
    Write-Host "✓ Réservation créée: ID $($reservationResponse.id)" -ForegroundColor Green
} catch {
    Write-Host "⚠ Erreur lors de la création: $_" -ForegroundColor Yellow
}

# 4. Vérifier RabbitMQ
Write-Host "`n[4/5] Vérification de RabbitMQ..." -ForegroundColor Yellow
python test_rabbitmq_api.py

# 5. Vérifier les logs du consumer
Write-Host "`n[5/5] Logs du notification-service..." -ForegroundColor Yellow
docker logs notification-service --tail 10

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "FIN DU TEST" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
