# QueueCTL Demo Script for PowerShell

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "QueueCTL Demo - Background Job Queue" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Step 1: Enqueueing jobs..." -ForegroundColor Yellow
poetry run python queuectl.py enqueue '{"id":"job1","command":"echo Task 1"}'
poetry run python queuectl.py enqueue '{"id":"job2","command":"echo Task 2"}'
poetry run python queuectl.py enqueue '{"id":"job3","command":"echo Task 3"}'
Write-Host ""

Write-Host "Step 2: Checking queue status..." -ForegroundColor Yellow
poetry run python queuectl.py status
Write-Host ""

Write-Host "Step 3: Listing all jobs..." -ForegroundColor Yellow
poetry run python queuectl.py list --all
Write-Host ""

Write-Host "Step 4: Starting a worker..." -ForegroundColor Yellow
Write-Host "Note: Worker will process jobs in background" -ForegroundColor Gray
poetry run python queuectl.py worker start --count 1
Write-Host ""

Write-Host "Step 5: Waiting for jobs to complete..." -ForegroundColor Yellow
Start-Sleep -Seconds 3
Write-Host ""

Write-Host "Step 6: Checking status again..." -ForegroundColor Yellow
poetry run python queuectl.py status
Write-Host ""

Write-Host "Step 7: Getting details of job1..." -ForegroundColor Yellow
poetry run python queuectl.py get job1
Write-Host ""

Write-Host "Step 8: Listing active workers..." -ForegroundColor Yellow
poetry run python queuectl.py worker list
Write-Host ""

Write-Host "Step 9: Stopping workers..." -ForegroundColor Yellow
poetry run python queuectl.py worker stop
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Demo Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
