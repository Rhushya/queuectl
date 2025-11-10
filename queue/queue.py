"""Job queue management."""

import json
from typing import List, Optional
from .job import Job
from .storage import Storage
from .config import Config


class JobQueue:
    """Manages the job queue operations."""
    
    def __init__(self, storage: Storage, config: Config):
        """Initialize job queue."""
        self.storage = storage
        self.config = config
    
    def enqueue(self, job_data: dict) -> Job:
        """Add a job to the queue."""
        # Use configured max_retries if not specified
        if "max_retries" not in job_data:
            job_data["max_retries"] = self.config.get_int("max-retries")
        
        job = Job.from_dict(job_data)
        
        # Check if job already exists
        existing = self.storage.get_job(job.id)
        if existing:
            raise ValueError(f"Job with ID '{job.id}' already exists")
        
        self.storage.save_job(job)
        return job
    
    def get_job(self, job_id: str) -> Optional[Job]:
        """Get a specific job by ID."""
        return self.storage.get_job(job_id)
    
    def list_jobs(self, state: Optional[str] = None) -> List[Job]:
        """List jobs, optionally filtered by state."""
        if state:
            return self.storage.get_jobs_by_state(state)
        return self.storage.get_all_jobs()
    
    def get_status(self) -> dict:
        """Get queue status with job counts."""
        return self.storage.get_job_counts()
    
    def claim_job(self, worker_pid: int) -> Optional[Job]:
        """Claim a pending job for processing."""
        return self.storage.claim_job(worker_pid)
    
    def update_job(self, job: Job):
        """Update a job in the queue."""
        self.storage.save_job(job)
    
    def delete_job(self, job_id: str):
        """Delete a job from the queue."""
        self.storage.delete_job(job_id)
    
    def get_dlq_jobs(self) -> List[Job]:
        """Get all jobs in Dead Letter Queue (dead state)."""
        return self.storage.get_jobs_by_state("dead")
    
    def retry_dlq_job(self, job_id: str) -> Job:
        """Move a job from DLQ back to pending."""
        job = self.storage.get_job(job_id)
        if not job:
            raise ValueError(f"Job '{job_id}' not found")
        
        if job.state != "dead":
            raise ValueError(f"Job '{job_id}' is not in DLQ (state: {job.state})")
        
        job.reset_for_retry()
        job.attempts = 0  # Reset attempts for DLQ retry
        self.storage.save_job(job)
        return job
    
    def retry_all_dlq(self) -> int:
        """Retry all jobs in DLQ."""
        dlq_jobs = self.get_dlq_jobs()
        for job in dlq_jobs:
            job.reset_for_retry()
            job.attempts = 0
            self.storage.save_job(job)
        return len(dlq_jobs)
    
    def clear_dlq(self) -> int:
        """Clear all jobs from DLQ."""
        dlq_jobs = self.get_dlq_jobs()
        for job in dlq_jobs:
            self.storage.delete_job(job.id)
        return len(dlq_jobs)
