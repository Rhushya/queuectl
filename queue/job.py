"""Job model for the queue system."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Job:
    """Represents a job in the queue system."""
    
    id: str
    command: str
    state: str = "pending"
    attempts: int = 0
    max_retries: int = 3
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_error: Optional[str] = None
    exit_code: Optional[int] = None
    locked_by: Optional[int] = None
    locked_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize timestamps if not provided."""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def to_dict(self) -> dict:
        """Convert job to dictionary."""
        return {
            "id": self.id,
            "command": self.command,
            "state": self.state,
            "attempts": self.attempts,
            "max_retries": self.max_retries,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_error": self.last_error,
            "exit_code": self.exit_code,
            "locked_by": self.locked_by,
            "locked_at": self.locked_at.isoformat() if self.locked_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Job":
        """Create job from dictionary."""
        # Parse datetime strings
        if isinstance(data.get("created_at"), str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if isinstance(data.get("updated_at"), str):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        if isinstance(data.get("locked_at"), str):
            data["locked_at"] = datetime.fromisoformat(data["locked_at"])
        
        return cls(**data)
    
    def can_retry(self) -> bool:
        """Check if job can be retried."""
        return self.attempts < self.max_retries
    
    def mark_processing(self, worker_pid: int):
        """Mark job as processing."""
        self.state = "processing"
        self.locked_by = worker_pid
        self.locked_at = datetime.now()
        self.updated_at = datetime.now()
    
    def mark_completed(self, exit_code: int):
        """Mark job as completed."""
        self.state = "completed"
        self.exit_code = exit_code
        self.updated_at = datetime.now()
        self.locked_by = None
        self.locked_at = None
    
    def mark_failed(self, error: str, exit_code: int):
        """Mark job as failed."""
        self.attempts += 1
        self.last_error = error
        self.exit_code = exit_code
        self.updated_at = datetime.now()
        self.locked_by = None
        self.locked_at = None
        
        if self.can_retry():
            self.state = "failed"
        else:
            self.state = "dead"
    
    def reset_for_retry(self):
        """Reset job state for retry."""
        self.state = "pending"
        self.locked_by = None
        self.locked_at = None
        self.updated_at = datetime.now()
