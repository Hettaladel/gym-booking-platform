# ============================================
# SCRIPT DE TEST COMPLET - PROJET GYM MANAGER
# ============================================

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "TEST COMPLET DE L'INFRASTRUCTURE" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# Test 1: RabbitMQ
Write-Host "`n[1/4] Test RabbitMQ..." -ForegroundColor Yellow
python test_rabbitmq.py

# Test 2: Consul
Write-Host "`n[2/4] Test Consul..." -ForegroundColor Yellow
python check_consul.py

# Test 3: Traefik
Write-Host "`n[3/4] Test Traefik..." -ForegroundColor Yellow
python test_traefik_full.py

# Test 4: Tests fonctionnels complets
Write-Host "`n[4/4] Tests fonctionnels E2E..." -ForegroundColor Yellow
.\test_complete.ps1

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "FIN DES TESTS" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
