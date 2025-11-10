#!/usr/bin/env python
"""QueueCTL - CLI for background job queue system."""

import argparse
import json
import os
import sys
import signal
import subprocess
import time
from pathlib import Path

from queue import Job, JobQueue, Worker, Config
from queue.storage import Storage


class QueueCTL:
    """Main CLI application."""
    
    def __init__(self, db_path: str = "queuectl.db"):
        """Initialize QueueCTL."""
        self.storage = Storage(db_path)
        self.config = Config(self.storage)
        self.queue = JobQueue(self.storage, self.config)
        self.workers_file = Path("workers.pid")
    
    def init(self):
        """Initialize the queue system."""
        print("✓ QueueCTL initialized successfully")
        print(f"  Database: {self.storage.db_path}")
        return 0
    
    def enqueue(self, job_json: str):
        """Enqueue a new job."""
        try:
            job_data = json.loads(job_json)
            
            if "id" not in job_data:
                print("✗ Error: Job must have an 'id' field")
                return 1
            
            if "command" not in job_data:
                print("✗ Error: Job must have a 'command' field")
                return 1
            
            job = self.queue.enqueue(job_data)
            print(f"✓ Job {job.id} enqueued successfully")
            print(f"  State: {job.state}")
            print(f"  Command: {job.command}")
            return 0
        
        except json.JSONDecodeError as e:
            print(f"✗ Error: Invalid JSON: {e}")
            return 1
        except ValueError as e:
            print(f"✗ Error: {e}")
            return 1
        except Exception as e:
            print(f"✗ Error: {e}")
            return 1
    
    def get_job(self, job_id: str):
        """Get job details."""
        job = self.queue.get_job(job_id)
        if not job:
            print(f"✗ Job '{job_id}' not found")
            return 1
        
        print(f"Job Details: {job.id}")
        print("─" * 40)
        print(f"Command:      {job.command}")
        print(f"State:        {job.state}")
        print(f"Attempts:     {job.attempts}")
        print(f"Max Retries:  {job.max_retries}")
        print(f"Created:      {job.created_at}")
        print(f"Updated:      {job.updated_at}")
        if job.exit_code is not None:
            print(f"Exit Code:    {job.exit_code}")
        if job.last_error:
            print(f"Last Error:   {job.last_error}")
        
        return 0
    
    def list_jobs(self, state: str = None, verbose: bool = False):
        """List jobs."""
        jobs = self.queue.list_jobs(state)
        
        if not jobs:
            print("No jobs found")
            return 0
        
        # Print table header
        print("┌" + "─" * 10 + "┬" + "─" * 12 + "┬" + "─" * 10 + "┬" + "─" * 30 + "┐")
        print("│ ID       │ State      │ Attempts │ Command                      │")
        print("├" + "─" * 10 + "┼" + "─" * 12 + "┼" + "─" * 10 + "┼" + "─" * 30 + "┤")
        
        for job in jobs:
            job_id = job.id[:8]
            state = job.state[:10]
            attempts = f"{job.attempts}/{job.max_retries}"
            command = job.command[:28]
            
            print(f"│ {job_id:8s} │ {state:10s} │ {attempts:8s} │ {command:28s} │")
        
        print("└" + "─" * 10 + "┴" + "─" * 12 + "┴" + "─" * 10 + "┴" + "─" * 30 + "┘")
        
        return 0
    
    def status(self):
        """Show queue status."""
        counts = self.queue.get_status()
        
        print("Job Queue Status")
        print("┌" + "─" * 12 + "┬" + "─" * 7 + "┐")
        print("│ State      │ Count │")
        print("├" + "─" * 12 + "┼" + "─" * 7 + "┤")
        
        for state in ["pending", "processing", "completed", "failed", "dead"]:
            count = counts.get(state, 0)
            print(f"│ {state:10s} │ {count:5d} │")
        
        print("└" + "─" * 12 + "┴" + "─" * 7 + "┘")
        print()
        
        # Show active workers
        active_workers = self._get_active_workers()
        print(f"Active Workers: {len(active_workers)}")
        
        return 0
    
    def worker_start(self, count: int = 1):
        """Start worker processes."""
        started_pids = []
        
        for i in range(count):
            # Start worker in background
            if os.name == 'nt':  # Windows
                process = subprocess.Popen(
                    [sys.executable, __file__, "_worker", str(i + 1)],
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
            else:  # Unix-like
                process = subprocess.Popen(
                    [sys.executable, __file__, "_worker", str(i + 1)],
                    start_new_session=True
                )
            
            started_pids.append(process.pid)
        
        # Save worker PIDs
        self._save_worker_pids(started_pids)
        
        print(f"✓ Started {count} worker(s) (PIDs: {', '.join(map(str, started_pids))})")
        return 0
    
    def worker_stop(self):
        """Stop all workers gracefully."""
        pids = self._get_active_workers()
        
        if not pids:
            print("No active workers found")
            return 0
        
        print(f"✓ Gracefully stopping {len(pids)} worker(s)...")
        
        for pid in pids:
            try:
                if os.name == 'nt':  # Windows
                    os.kill(pid, signal.CTRL_BREAK_EVENT)
                else:  # Unix-like
                    os.kill(pid, signal.SIGTERM)
            except ProcessLookupError:
                pass  # Process already dead
            except Exception as e:
                print(f"  Warning: Could not stop worker {pid}: {e}")
        
        # Wait a bit for graceful shutdown
        time.sleep(2)
        
        # Clear worker PIDs
        if self.workers_file.exists():
            self.workers_file.unlink()
        
        print("✓ All workers stopped")
        return 0
    
    def worker_list(self):
        """List active workers."""
        pids = self._get_active_workers()
        
        if not pids:
            print("No active workers")
            return 0
        
        print(f"Active Workers: {len(pids)}")
        print("┌" + "─" * 8 + "┬" + "─" * 10 + "┐")
        print("│ PID    │ Status   │")
        print("├" + "─" * 8 + "┼" + "─" * 10 + "┤")
        
        for pid in pids:
            status = "Running" if self._is_process_running(pid) else "Dead"
            print(f"│ {pid:6d} │ {status:8s} │")
        
        print("└" + "─" * 8 + "┴" + "─" * 10 + "┘")
        
        return 0
    
    def dlq_list(self):
        """List DLQ jobs."""
        jobs = self.queue.get_dlq_jobs()
        
        if not jobs:
            print("Dead Letter Queue is empty")
            return 0
        
        print(f"Dead Letter Queue ({len(jobs)} jobs)")
        print("┌" + "─" * 10 + "┬" + "─" * 10 + "┬" + "─" * 40 + "┐")
        print("│ ID       │ Attempts │ Reason                                 │")
        print("├" + "─" * 10 + "┼" + "─" * 10 + "┼" + "─" * 40 + "┤")
        
        for job in jobs:
            job_id = job.id[:8]
            attempts = str(job.attempts)
            reason = (job.last_error or "Unknown error")[:38]
            
            print(f"│ {job_id:8s} │ {attempts:8s} │ {reason:38s} │")
        
        print("└" + "─" * 10 + "┴" + "─" * 10 + "┴" + "─" * 40 + "┘")
        
        return 0
    
    def dlq_retry(self, job_id: str = None, retry_all: bool = False):
        """Retry DLQ job(s)."""
        try:
            if retry_all:
                count = self.queue.retry_all_dlq()
                print(f"✓ Moved {count} job(s) from DLQ to pending queue")
            elif job_id:
                job = self.queue.retry_dlq_job(job_id)
                print(f"✓ Job {job.id} moved from DLQ to pending queue")
            else:
                print("✗ Error: Specify --job-id or --all")
                return 1
            
            return 0
        except ValueError as e:
            print(f"✗ Error: {e}")
            return 1
    
    def dlq_clear(self):
        """Clear DLQ."""
        count = self.queue.clear_dlq()
        print(f"✓ Cleared {count} job(s) from DLQ")
        return 0
    
    def config_show(self):
        """Show configuration."""
        print(self.config.show())
        return 0
    
    def config_set(self, key: str, value: str):
        """Set configuration value."""
        try:
            self.config.set(key, value)
            print(f"✓ Configuration '{key}' set to '{value}'")
            return 0
        except ValueError as e:
            print(f"✗ Error: {e}")
            return 1
    
    def _run_worker(self, worker_id: int):
        """Internal method to run a worker (called in subprocess)."""
        worker = Worker(self.queue, self.config, worker_id)
        worker.start()
        return 0
    
    def _save_worker_pids(self, pids: list):
        """Save worker PIDs to file."""
        existing_pids = self._get_active_workers()
        all_pids = existing_pids + pids
        self.workers_file.write_text("\n".join(map(str, all_pids)))
    
    def _get_active_workers(self) -> list:
        """Get list of active worker PIDs."""
        if not self.workers_file.exists():
            return []
        
        pids = []
        for line in self.workers_file.read_text().strip().split("\n"):
            if line:
                try:
                    pid = int(line)
                    if self._is_process_running(pid):
                        pids.append(pid)
                except ValueError:
                    pass
        
        return pids
    
    def _is_process_running(self, pid: int) -> bool:
        """Check if a process is running."""
        try:
            os.kill(pid, 0)
            return True
        except (OSError, ProcessLookupError):
            return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="QueueCTL - Background Job Queue System")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # init command
    subparsers.add_parser("init", help="Initialize the queue system")
    
    # enqueue command
    enqueue_parser = subparsers.add_parser("enqueue", help="Add a job to the queue")
    enqueue_parser.add_argument("job", help="Job JSON string")
    
    # get command
    get_parser = subparsers.add_parser("get", help="Get job details")
    get_parser.add_argument("job_id", help="Job ID")
    
    # list command
    list_parser = subparsers.add_parser("list", help="List jobs")
    list_parser.add_argument("--state", help="Filter by state")
    list_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    list_parser.add_argument("--all", action="store_true", help="List all jobs")
    
    # status command
    subparsers.add_parser("status", help="Show queue status")
    
    # worker commands
    worker_parser = subparsers.add_parser("worker", help="Worker management")
    worker_subparsers = worker_parser.add_subparsers(dest="worker_command")
    
    worker_start = worker_subparsers.add_parser("start", help="Start workers")
    worker_start.add_argument("--count", type=int, default=1, help="Number of workers")
    
    worker_subparsers.add_parser("stop", help="Stop all workers")
    worker_subparsers.add_parser("list", help="List active workers")
    
    # dlq commands
    dlq_parser = subparsers.add_parser("dlq", help="Dead Letter Queue management")
    dlq_subparsers = dlq_parser.add_subparsers(dest="dlq_command")
    
    dlq_subparsers.add_parser("list", help="List DLQ jobs")
    
    dlq_retry = dlq_subparsers.add_parser("retry", help="Retry DLQ job")
    dlq_retry.add_argument("--job-id", help="Job ID to retry")
    dlq_retry.add_argument("--all", action="store_true", help="Retry all DLQ jobs")
    
    dlq_subparsers.add_parser("clear", help="Clear DLQ")
    
    # config commands
    config_parser = subparsers.add_parser("config", help="Configuration management")
    config_subparsers = config_parser.add_subparsers(dest="config_command")
    
    config_subparsers.add_parser("show", help="Show configuration")
    
    config_set = config_subparsers.add_parser("set", help="Set configuration value")
    config_set.add_argument("key", help="Configuration key")
    config_set.add_argument("value", help="Configuration value")
    
    # Internal worker command (not shown in help)
    parser.add_argument("_worker", nargs="?", help=argparse.SUPPRESS)
    parser.add_argument("_worker_id", nargs="?", help=argparse.SUPPRESS)
    
    args = parser.parse_args()
    
    # Handle internal worker command
    if args._worker == "_worker" and args._worker_id:
        ctl = QueueCTL()
        return ctl._run_worker(int(args._worker_id))
    
    # Create QueueCTL instance
    ctl = QueueCTL()
    
    # Route to appropriate command
    if args.command == "init":
        return ctl.init()
    
    elif args.command == "enqueue":
        return ctl.enqueue(args.job)
    
    elif args.command == "get":
        return ctl.get_job(args.job_id)
    
    elif args.command == "list":
        return ctl.list_jobs(args.state, args.verbose)
    
    elif args.command == "status":
        return ctl.status()
    
    elif args.command == "worker":
        if args.worker_command == "start":
            return ctl.worker_start(args.count)
        elif args.worker_command == "stop":
            return ctl.worker_stop()
        elif args.worker_command == "list":
            return ctl.worker_list()
    
    elif args.command == "dlq":
        if args.dlq_command == "list":
            return ctl.dlq_list()
        elif args.dlq_command == "retry":
            return ctl.dlq_retry(args.job_id, args.all)
        elif args.dlq_command == "clear":
            return ctl.dlq_clear()
    
    elif args.command == "config":
        if args.config_command == "show":
            return ctl.config_show()
        elif args.config_command == "set":
            return ctl.config_set(args.key, args.value)
    
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
