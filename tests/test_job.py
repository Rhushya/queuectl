"""Tests for Job model."""

import pytest
from datetime import datetime
from queue.job import Job


def test_job_creation():
    """Test basic job creation."""
    job = Job(id="test1", command="echo hello")
    
    assert job.id == "test1"
    assert job.command == "echo hello"
    assert job.state == "pending"
    assert job.attempts == 0
    assert job.max_retries == 3


def test_job_to_dict():
    """Test job serialization to dict."""
    job = Job(id="test1", command="echo hello")
    data = job.to_dict()
    
    assert data["id"] == "test1"
    assert data["command"] == "echo hello"
    assert data["state"] == "pending"


def test_job_from_dict():
    """Test job deserialization from dict."""
    data = {
        "id": "test1",
        "command": "echo hello",
        "state": "pending",
        "attempts": 0,
        "max_retries": 3
    }
    job = Job.from_dict(data)
    
    assert job.id == "test1"
    assert job.command == "echo hello"


def test_job_can_retry():
    """Test retry logic."""
    job = Job(id="test1", command="echo hello", max_retries=3)
    
    assert job.can_retry() is True
    
    job.attempts = 3
    assert job.can_retry() is False


def test_job_mark_processing():
    """Test marking job as processing."""
    job = Job(id="test1", command="echo hello")
    job.mark_processing(worker_pid=1234)
    
    assert job.state == "processing"
    assert job.locked_by == 1234
    assert job.locked_at is not None


def test_job_mark_completed():
    """Test marking job as completed."""
    job = Job(id="test1", command="echo hello")
    job.mark_completed(exit_code=0)
    
    assert job.state == "completed"
    assert job.exit_code == 0
    assert job.locked_by is None


def test_job_mark_failed_with_retry():
    """Test marking job as failed with retry available."""
    job = Job(id="test1", command="echo hello", max_retries=3)
    job.mark_failed(error="Command failed", exit_code=1)
    
    assert job.state == "failed"
    assert job.attempts == 1
    assert job.last_error == "Command failed"
    assert job.exit_code == 1


def test_job_mark_failed_no_retry():
    """Test marking job as failed with no retries left."""
    job = Job(id="test1", command="echo hello", max_retries=1, attempts=1)
    job.mark_failed(error="Command failed", exit_code=1)
    
    assert job.state == "dead"
    assert job.attempts == 2


def test_job_reset_for_retry():
    """Test resetting job for retry."""
    job = Job(id="test1", command="echo hello", state="failed", attempts=1)
    job.reset_for_retry()
    
    assert job.state == "pending"
    assert job.locked_by is None
    assert job.locked_at is None
