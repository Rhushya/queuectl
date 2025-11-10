"""Tests for Worker."""

import pytest
import tempfile
import os
from queue.worker import Worker
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


def test_worker_creation(queue):
    """Test worker creation."""
    config = queue.storage.__dict__  # Access config through storage
    storage = queue.storage
    config_obj = Config(storage)
    
    worker = Worker(queue, config_obj, worker_id=1)
    
    assert worker.worker_id == 1
    assert worker.running is False


def test_worker_process_successful_job(queue):
    """Test processing a successful job."""
    storage = queue.storage
    config_obj = Config(storage)
    
    # Enqueue a simple job
    if os.name == 'nt':
        command = 'echo test'
    else:
        command = 'echo test'
    
    job = queue.enqueue({"id": "test1", "command": command})
    
    # Create worker and process
    worker = Worker(queue, config_obj, worker_id=1)
    claimed_job = queue.claim_job(worker.pid)
    
    if claimed_job:
        worker._process_job(claimed_job)
        
        # Verify job completed
        updated_job = queue.get_job("test1")
        assert updated_job.state == "completed"
        assert updated_job.exit_code == 0


def test_worker_process_failed_job(queue):
    """Test processing a failed job."""
    storage = queue.storage
    config_obj = Config(storage)
    
    # Enqueue a failing job
    if os.name == 'nt':
        command = 'exit 1'
    else:
        command = 'exit 1'
    
    job = queue.enqueue({"id": "test1", "command": command, "max_retries": 1})
    
    # Create worker and process
    worker = Worker(queue, config_obj, worker_id=1)
    claimed_job = queue.claim_job(worker.pid)
    
    if claimed_job:
        worker._process_job(claimed_job)
        
        # Verify job is in failed or dead state
        updated_job = queue.get_job("test1")
        assert updated_job.state in ["failed", "dead"]
        assert updated_job.attempts >= 1
