"""Storage layer for persistent job queue using SQLite."""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from contextlib import contextmanager

from .job import Job


class Storage:
    """SQLite-based storage for jobs and configuration."""
    
    def __init__(self, db_path: str = "queuectl.db"):
        """Initialize storage with database path."""
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Create jobs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    command TEXT NOT NULL,
                    state TEXT NOT NULL,
                    attempts INTEGER DEFAULT 0,
                    max_retries INTEGER DEFAULT 3,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_error TEXT,
                    exit_code INTEGER,
                    locked_by INTEGER,
                    locked_at TIMESTAMP
                )
            """)
            
            # Create config table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS config (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)
            
            # Create index on state for faster queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_jobs_state 
                ON jobs(state)
            """)
            
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """Get database connection context manager."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def save_job(self, job: Job):
        """Save or update a job."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO jobs 
                (id, command, state, attempts, max_retries, created_at, updated_at, 
                 last_error, exit_code, locked_by, locked_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job.id,
                job.command,
                job.state,
                job.attempts,
                job.max_retries,
                job.created_at.isoformat() if job.created_at else None,
                job.updated_at.isoformat() if job.updated_at else None,
                job.last_error,
                job.exit_code,
                job.locked_by,
                job.locked_at.isoformat() if job.locked_at else None,
            ))
            conn.commit()
    
    def get_job(self, job_id: str) -> Optional[Job]:
        """Get a job by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_job(row)
            return None
    
    def get_jobs_by_state(self, state: str) -> List[Job]:
        """Get all jobs with a specific state."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM jobs WHERE state = ?", (state,))
            rows = cursor.fetchall()
            return [self._row_to_job(row) for row in rows]
    
    def get_all_jobs(self) -> List[Job]:
        """Get all jobs."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM jobs ORDER BY created_at DESC")
            rows = cursor.fetchall()
            return [self._row_to_job(row) for row in rows]
    
    def claim_job(self, worker_pid: int) -> Optional[Job]:
        """Atomically claim a pending job for processing."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Find a pending job
            cursor.execute("""
                SELECT * FROM jobs 
                WHERE state = 'pending' 
                ORDER BY created_at ASC 
                LIMIT 1
            """)
            row = cursor.fetchone()
            
            if not row:
                return None
            
            job_id = row["id"]
            
            # Try to claim it atomically
            cursor.execute("""
                UPDATE jobs 
                SET state = 'processing',
                    locked_by = ?,
                    locked_at = ?,
                    updated_at = ?
                WHERE id = ? 
                  AND state = 'pending'
                  AND locked_by IS NULL
            """, (
                worker_pid,
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                job_id
            ))
            
            if cursor.rowcount > 0:
                conn.commit()
                # Fetch the updated job
                cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
                row = cursor.fetchone()
                return self._row_to_job(row)
            
            return None
    
    def get_job_counts(self) -> dict:
        """Get count of jobs by state."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT state, COUNT(*) as count 
                FROM jobs 
                GROUP BY state
            """)
            rows = cursor.fetchall()
            return {row["state"]: row["count"] for row in rows}
    
    def delete_job(self, job_id: str):
        """Delete a job."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
            conn.commit()
    
    def set_config(self, key: str, value: str):
        """Set a configuration value."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO config (key, value)
                VALUES (?, ?)
            """, (key, value))
            conn.commit()
    
    def get_config(self, key: str) -> Optional[str]:
        """Get a configuration value."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM config WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row["value"] if row else None
    
    def get_all_config(self) -> dict:
        """Get all configuration values."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM config")
            rows = cursor.fetchall()
            return {row["key"]: row["value"] for row in rows}
    
    def _row_to_job(self, row: sqlite3.Row) -> Job:
        """Convert database row to Job object."""
        return Job(
            id=row["id"],
            command=row["command"],
            state=row["state"],
            attempts=row["attempts"],
            max_retries=row["max_retries"],
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
            updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else None,
            last_error=row["last_error"],
            exit_code=row["exit_code"],
            locked_by=row["locked_by"],
            locked_at=datetime.fromisoformat(row["locked_at"]) if row["locked_at"] else None,
        )
