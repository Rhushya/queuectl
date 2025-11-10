@echo off
REM QueueCTL Demo Script for Windows

echo ========================================
echo QueueCTL Demo - Background Job Queue
echo ========================================
echo.

echo Step 1: Enqueueing jobs...
poetry run python queuectl.py enqueue "{\"id\":\"job1\",\"command\":\"echo Task 1\"}"
poetry run python queuectl.py enqueue "{\"id\":\"job2\",\"command\":\"echo Task 2\"}"
poetry run python queuectl.py enqueue "{\"id\":\"job3\",\"command\":\"echo Task 3\"}"
echo.

echo Step 2: Checking queue status...
poetry run python queuectl.py status
echo.

echo Step 3: Listing all jobs...
poetry run python queuectl.py list --all
echo.

echo Step 4: Starting a worker...
echo Note: Worker will process jobs in background
poetry run python queuectl.py worker start --count 1
echo.

echo Step 5: Waiting for jobs to complete...
timeout /t 3 /nobreak >nul
echo.

echo Step 6: Checking status again...
poetry run python queuectl.py status
echo.

echo Step 7: Getting details of job1...
poetry run python queuectl.py get job1
echo.

echo Step 8: Listing active workers...
poetry run python queuectl.py worker list
echo.

echo Step 9: Stopping workers...
poetry run python queuectl.py worker stop
echo.

echo ========================================
echo Demo Complete!
echo ========================================
