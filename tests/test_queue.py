"""Tests for JobQueue."""

import pytest
import tempfile
import os
from queue.job import Job
from queue.queue import JobQueue
from queue.storage import Storage
from queue.config import Config


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def queue(temp_db):
    """Create a JobQueue instance for testing."""
    storage = Storage(temp_db)
    config = Config(storage)
    return JobQueue(storage, config)


def test_enqueue_job(queue):
    """Test enqueueing a job."""
    job_data = {"id": "test1", "command": "echo hello"}
    job = queue.enqueue(job_data)
    
    assert job.id == "test1"
    assert job.state == "pending"


def test_enqueue_duplicate_job(queue):
    """Test enqueueing duplicate job raises error."""
    job_data = {"id": "test1", "command": "echo hello"}
    queue.enqueue(job_data)
    
    with pytest.raises(ValueError):
        queue.enqueue(job_data)


def test_get_job(queue):
    """Test getting a job by ID."""
    job_data = {"id": "test1", "command": "echo hello"}
    queue.enqueue(job_data)
    
    job = queue.get_job("test1")
    assert job is not None
    assert job.id == "test1"


def test_get_nonexistent_job(queue):
    """Test getting a non-existent job."""
    job = queue.get_job("nonexistent")
    assert job is None


def test_list_jobs(queue):
    """Test listing jobs."""
    queue.enqueue({"id": "test1", "command": "echo 1"})
    queue.enqueue({"id": "test2", "command": "echo 2"})
    
    jobs = queue.list_jobs()
    assert len(jobs) == 2


def test_list_jobs_by_state(queue):
    """Test listing jobs filtered by state."""
    queue.enqueue({"id": "test1", "command": "echo 1"})
    job = queue.enqueue({"id": "test2", "command": "echo 2"})
    
    job.state = "completed"
    queue.update_job(job)
    
    pending_jobs = queue.list_jobs(state="pending")
    assert len(pending_jobs) == 1
    
    completed_jobs = queue.list_jobs(state="completed")
    assert len(completed_jobs) == 1


def test_get_status(queue):
    """Test getting queue status."""
    queue.enqueue({"id": "test1", "command": "echo 1"})
    queue.enqueue({"id": "test2", "command": "echo 2"})
    
    status = queue.get_status()
    assert status.get("pending", 0) == 2


def test_claim_job(queue):
    """Test claiming a job."""
    queue.enqueue({"id": "test1", "command": "echo 1"})
    
    job = queue.claim_job(worker_pid=1234)
    assert job is not None
    assert job.state == "processing"
    assert job.locked_by == 1234


def test_claim_job_empty_queue(queue):
    """Test claiming from empty queue."""
    job = queue.claim_job(worker_pid=1234)
    assert job is None


def test_retry_dlq_job(queue):
    """Test retrying a DLQ job."""
    job_data = {"id": "test1", "command": "echo 1"}
    job = queue.enqueue(job_data)
    
    # Move to DLQ
    job.state = "dead"
    job.attempts = 3
    queue.update_job(job)
    
    # Retry
    retried_job = queue.retry_dlq_job("test1")
    assert retried_job.state == "pending"
    assert retried_job.attempts == 0


def test_retry_non_dlq_job(queue):
    """Test retrying a non-DLQ job raises error."""
    job_data = {"id": "test1", "command": "echo 1"}
    queue.enqueue(job_data)
    
    with pytest.raises(ValueError):
        queue.retry_dlq_job("test1")


def test_clear_dlq(queue):
    """Test clearing DLQ."""
    job1 = queue.enqueue({"id": "test1", "command": "echo 1"})
    job2 = queue.enqueue({"id": "test2", "command": "echo 2"})
    
    job1.state = "dead"
    job2.state = "dead"
    queue.update_job(job1)
    queue.update_job(job2)
    
    count = queue.clear_dlq()
    assert count == 2
    
    dlq_jobs = queue.get_dlq_jobs()
    assert len(dlq_jobs) == 0
