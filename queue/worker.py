"""Worker process for executing jobs."""

import os
import signal
import subprocess
import time
from datetime import datetime
from typing import Optional

from .job import Job
from .queue import JobQueue
from .config import Config


class Worker:
    """Worker process that executes jobs from the queue."""
    
    def __init__(self, queue: JobQueue, config: Config, worker_id: int = 1):
        """Initialize worker."""
        self.queue = queue
        self.config = config
        self.worker_id = worker_id
        self.running = False
        self.current_job: Optional[Job] = None
        self.pid = os.getpid()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        print(f"\n[Worker {self.worker_id}] Received shutdown signal, finishing current job...")
        self.running = False
    
    def start(self):
        """Start the worker loop."""
        self.running = True
        print(f"[Worker {self.worker_id}] Started (PID: {self.pid})")
        
        while self.running:
            try:
                # Try to claim a job
                job = self.queue.claim_job(self.pid)
                
                if job:
                    self.current_job = job
                    self._process_job(job)
                    self.current_job = None
                else:
                    # No jobs available, sleep briefly
                    time.sleep(1)
            
            except Exception as e:
                print(f"[Worker {self.worker_id}] Error in main loop: {e}")
                time.sleep(1)
        
        print(f"[Worker {self.worker_id}] Stopped")
    
    def _process_job(self, job: Job):
        """Process a single job."""
        print(f"[Worker {self.worker_id}] Processing job: {job.id}")
        
        try:
            # Execute the command
            timeout = self.config.get_int("job-timeout")
            
            result = subprocess.run(
                job.command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0:
                # Job succeeded
                print(f"[Worker {self.worker_id}] Job {job.id} completed successfully")
                job.mark_completed(result.returncode)
                self.queue.update_job(job)
            else:
                # Job failed
                error_msg = result.stderr.strip() if result.stderr else f"Exit code: {result.returncode}"
                print(f"[Worker {self.worker_id}] Job {job.id} failed: {error_msg}")
                self._handle_failed_job(job, error_msg, result.returncode)
        
        except subprocess.TimeoutExpired:
            error_msg = f"Job timed out after {timeout} seconds"
            print(f"[Worker {self.worker_id}] Job {job.id} timed out")
            self._handle_failed_job(job, error_msg, -1)
        
        except Exception as e:
            error_msg = str(e)
            print(f"[Worker {self.worker_id}] Job {job.id} error: {error_msg}")
            self._handle_failed_job(job, error_msg, -1)
    
    def _handle_failed_job(self, job: Job, error: str, exit_code: int):
        """Handle a failed job with retry logic."""
        job.mark_failed(error, exit_code)
        
        if job.state == "failed" and job.can_retry():
            # Schedule retry with exponential backoff
            backoff_base = self.config.get_int("backoff-base")
            delay = backoff_base ** job.attempts
            
            print(f"[Worker {self.worker_id}] Job {job.id} will retry in {delay}s (attempt {job.attempts}/{job.max_retries})")
            
            # Save the failed state
            self.queue.update_job(job)
            
            # Wait for backoff period
            time.sleep(delay)
            
            # Reset to pending for retry
            job.reset_for_retry()
            self.queue.update_job(job)
        
        elif job.state == "dead":
            # Job exhausted retries, move to DLQ
            print(f"[Worker {self.worker_id}] Job {job.id} moved to DLQ after {job.attempts} attempts")
            self.queue.update_job(job)
        
        else:
            # Save failed state
            self.queue.update_job(job)
    
    def stop(self):
        """Stop the worker gracefully."""
        self.running = False
