# QueueCTL - CLI-based Background Job Queue System

A production-grade job queue system with worker processes, automatic retries with exponential backoff, and Dead Letter Queue (DLQ) support.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
  - [Enqueue Jobs](#enqueue-jobs)
  - [Worker Management](#worker-management)
  - [Job Status & Listing](#job-status--listing)
  - [Dead Letter Queue](#dead-letter-queue)
  - [Configuration](#configuration)
- [Job Specification](#job-specification)
- [Job Lifecycle](#job-lifecycle)
- [Testing](#testing)
- [Architecture Details](#architecture-details)
- [Design Decisions & Trade-offs](#design-decisions--trade-offs)
- [Demo](#demo)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

**QueueCTL** is a lightweight, persistent job queue system designed for managing background tasks with reliability and fault tolerance. It supports multiple concurrent workers, automatic retry mechanisms, and maintains failed jobs in a Dead Letter Queue for manual intervention.

### Key Capabilities

- ✅ **Persistent Storage** - Jobs survive system restarts
- ✅ **Concurrent Workers** - Multiple workers process jobs in parallel
- ✅ **Retry Logic** - Exponential backoff for failed jobs
- ✅ **Dead Letter Queue** - Isolate permanently failed jobs
- ✅ **CLI Interface** - Complete command-line control
- ✅ **Job Locking** - Prevent duplicate processing
- ✅ **Graceful Shutdown** - Workers complete current jobs before exit

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Job Queueing** | Add jobs with custom commands and retry policies |
| **Worker Pool** | Start/stop multiple workers dynamically |
| **Auto-Retry** | Exponential backoff with configurable max retries |
| **DLQ Management** | View and retry permanently failed jobs |
| **State Tracking** | Monitor jobs across their lifecycle |
| **Persistence** | SQLite-based storage (or JSON/file-based) |
| **Configuration** | Customize retry count, backoff base, timeouts |
| **Concurrency Safe** | File/row-level locking prevents race conditions |

---

## 🏗️ Architecture

### High-Level Overview

```
┌─────────────┐
│   CLI       │
│  Interface  │
└──────┬──────┘
       │
       ├──────> Enqueue Jobs
       ├──────> Start/Stop Workers
       ├──────> Query Status
       └──────> Manage Config
              │
              ▼
       ┌──────────────┐
       │  Job Queue   │
       │  (Persistent)│
       └──────┬───────┘
              │
    ┌─────────┴─────────┐
    │                   │
    ▼                   ▼
┌────────┐         ┌────────┐
│Worker 1│         │Worker N│
└───┬────┘         └───┬────┘
    │                  │
    ├─> Process Job    │
    ├─> Update State   │
    └─> Retry/DLQ  <───┘
```

### Job State Machine

```
pending -> processing -> completed
              │
              ├─> failed (retry) -> processing
              │
              └─> dead (max retries) -> DLQ
```

---

## 📦 Prerequisites

- **Python 3.8+** / **Go 1.19+** / **Node.js 16+** / **Java 17+** (depending on implementation)
- SQLite3 (bundled with most systems)
- OS: Linux, macOS, Windows

---

## 🚀 Installation

### Option 1: From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/queuectl.git
cd queuectl

# Install dependencies with Poetry
poetry install

# Make CLI executable
chmod +x queuectl.py
# OR create an alias
alias queuectl='poetry run python queuectl.py'
```

### Option 2: Binary Installation (if provided)

```bash
# Download the binary for your platform
curl -L https://github.com/yourusername/queuectl/releases/latest/download/queuectl-linux-amd64 -o queuectl

# Make it executable
chmod +x queuectl

# Move to PATH
sudo mv queuectl /usr/local/bin/
```

---

## 🏁 Quick Start

```bash
# 1. Initialize the system (creates database)
queuectl init

# 2. Add a simple job
queuectl enqueue '{"id":"job1","command":"echo Hello World"}'

# 3. Start 2 workers
queuectl worker start --count 2

# 4. Check status
queuectl status

# 5. Stop workers (gracefully)
queuectl worker stop
```

---

## 📖 Usage

### Enqueue Jobs

**Basic job:**
```bash
queuectl enqueue '{"id":"job1","command":"sleep 2"}'
```

**Job with custom retries:**
```bash
queuectl enqueue '{
  "id":"job2",
  "command":"python process.py",
  "max_retries":5
}'
```

**Output:**
```
✓ Job job1 enqueued successfully
  State: pending
  Command: sleep 2
```

### Worker Management

**Start workers:**
```bash
# Start 3 workers
queuectl worker start --count 3

# Output:
# ✓ Started 3 workers (PIDs: 1234, 1235, 1236)
```

**Stop workers:**
```bash
queuectl worker stop

# Output:
# ✓ Gracefully stopping 3 workers...
# ✓ All workers stopped
```

**Check active workers:**
```bash
queuectl worker list

# Output:
# Active Workers: 3
# ┌──────┬─────────┬────────────────────┐
# │ PID  │ Status  │ Current Job        │
# ├──────┼─────────┼────────────────────┤
# │ 1234 │ Running │ job5               │
# │ 1235 │ Idle    │ -                  │
# │ 1236 │ Running │ job7               │
# └──────┴─────────┴────────────────────┘
```

### Job Status & Listing

**Overall status:**
```bash
queuectl status

# Output:
# Job Queue Status
# ┌────────────┬───────┐
# │ State      │ Count │
# ├────────────┼───────┤
# │ pending    │ 5     │
# │ processing │ 2     │
# │ completed  │ 120   │
# │ failed     │ 3     │
# │ dead       │ 1     │
# └────────────┴───────┘
# 
# Active Workers: 3
```

**List jobs by state:**
```bash
# List pending jobs
queuectl list --state pending

# List all jobs
queuectl list --all

# List with details
queuectl list --state failed --verbose

# Output:
# ┌───────┬─────────┬──────────┬─────────────────────┐
# │ ID    │ State   │ Attempts │ Command             │
# ├───────┼─────────┼──────────┼─────────────────────┤
# │ job1  │ pending │ 0        │ echo Hello          │
# │ job3  │ pending │ 0        │ python script.py    │
# └───────┴─────────┴──────────┴─────────────────────┘
```

**Get specific job details:**
```bash
queuectl get job1

# Output:
# Job Details: job1
# ─────────────────────────
# Command:      echo Hello World
# State:        completed
# Attempts:     1
# Max Retries:  3
# Created:      2025-11-10 10:30:00
# Updated:      2025-11-10 10:30:05
# Exit Code:    0
```

### Dead Letter Queue

**List DLQ jobs:**
```bash
queuectl dlq list

# Output:
# Dead Letter Queue (1 jobs)
# ┌───────┬──────────┬─────────────────────────────┐
# │ ID    │ Attempts │ Reason                      │
# ├───────┼──────────┼─────────────────────────────┤
# │ job99 │ 3        │ Command not found: badcmd   │
# └───────┴──────────┴─────────────────────────────┘
```

**Retry DLQ job:**
```bash
queuectl dlq retry job99

# Output:
# ✓ Job job99 moved from DLQ to pending queue
```

**Retry all DLQ jobs:**
```bash
queuectl dlq retry --all
```

**Clear DLQ:**
```bash
queuectl dlq clear
```

### Configuration

**View current config:**
```bash
queuectl config show

# Output:
# Configuration
# ─────────────────────────
# max-retries:      3
# backoff-base:     2
# worker-count:     1
# job-timeout:      300
```

**Set configuration:**
```bash
# Set max retries
queuectl config set max-retries 5

# Set backoff base
queuectl config set backoff-base 2

# Set default worker count
queuectl config set worker-count 3

# Set job timeout (seconds)
queuectl config set job-timeout 600
```

---

## 📄 Job Specification

Each job is represented as a JSON object:

```json
{
  "id": "unique-job-id",
  "command": "echo 'Hello World'",
  "state": "pending",
  "attempts": 0,
  "max_retries": 3,
  "created_at": "2025-11-10T10:30:00Z",
  "updated_at": "2025-11-10T10:30:00Z",
  "last_error": null,
  "exit_code": null
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier for the job |
| `command` | string | Shell command to execute |
| `state` | string | Current state (pending/processing/completed/failed/dead) |
| `attempts` | integer | Number of execution attempts |
| `max_retries` | integer | Maximum retry attempts before moving to DLQ |
| `created_at` | timestamp | When the job was created |
| `updated_at` | timestamp | Last modification time |
| `last_error` | string | Error message from last failed attempt |
| `exit_code` | integer | Exit code from command execution |

---

## 🔄 Job Lifecycle

### State Transitions

| State | Description | Next States |
|-------|-------------|-------------|
| **pending** | Waiting to be picked up by a worker | processing |
| **processing** | Currently being executed by a worker | completed, failed |
| **completed** | Successfully executed (exit code 0) | *(terminal)* |
| **failed** | Failed but retryable (attempts < max_retries) | processing, dead |
| **dead** | Permanently failed (moved to DLQ) | *(terminal, can be manually retried)* |

### Retry Mechanism

- **Exponential Backoff Formula:** `delay = backoff_base ^ attempts` seconds
- **Example** (base=2):
  - 1st retry: 2¹ = 2 seconds
  - 2nd retry: 2² = 4 seconds
  - 3rd retry: 2³ = 8 seconds

### Worker Behavior

1. **Poll** - Worker queries for pending jobs
2. **Lock** - Atomically claim a job (state: pending → processing)
3. **Execute** - Run the command in a subprocess
4. **Update** - Mark as completed or failed based on exit code
5. **Retry/DLQ** - Schedule retry with backoff or move to DLQ
6. **Repeat** - Continue polling for next job

---

## 🧪 Testing

### Automated Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
pytest --cov=queuectl tests/

# Run specific test
pytest tests/test_worker.py -v
```

### Manual Test Scenarios

#### 1. Basic Job Completion
```bash
queuectl enqueue '{"id":"test1","command":"echo success"}'
queuectl worker start --count 1
sleep 2
queuectl get test1  # Should show 'completed'
queuectl worker stop
```

#### 2. Failed Job with Retry
```bash
queuectl enqueue '{"id":"test2","command":"exit 1","max_retries":2}'
queuectl worker start --count 1
sleep 10  # Wait for retries
queuectl get test2  # Should show 'dead' after exhausting retries
queuectl worker stop
```

#### 3. Multiple Workers
```bash
for i in {1..10}; do
  queuectl enqueue "{\"id\":\"job$i\",\"command\":\"sleep 1\"}"
done
queuectl worker start --count 5
queuectl status  # Should show jobs being processed concurrently
queuectl worker stop
```

#### 4. Persistence Test
```bash
queuectl enqueue '{"id":"persist1","command":"echo test"}'
queuectl worker stop  # Ensure workers are stopped
# Kill the process or restart system
queuectl list --state pending  # Should still show persist1
```

#### 5. DLQ Flow
```bash
queuectl enqueue '{"id":"bad1","command":"nonexistent_command","max_retries":1}'
queuectl worker start --count 1
sleep 5
queuectl dlq list  # Should show bad1
queuectl dlq retry bad1  # Move back to pending
queuectl worker stop
```

---

## 🏛️ Architecture Details

### Components

#### 1. **CLI Layer** (`cli.py`)
- Parses commands and arguments
- Validates input
- Calls appropriate service methods
- Formats and displays output

#### 2. **Job Queue** (`queue.py`)
- Manages job CRUD operations
- Implements job state transitions
- Handles job locking (prevents duplicate processing)
- Persists jobs to database

#### 3. **Worker** (`worker.py`)
- Polls queue for pending jobs
- Executes job commands in subprocess
- Updates job state based on results
- Implements retry logic with exponential backoff
- Handles graceful shutdown signals

#### 4. **Storage** (`storage.py`)
- SQLite database for persistence
- Job table schema
- Configuration table
- Atomic operations with transactions

#### 5. **Configuration** (`config.py`)
- Manages system settings
- Provides defaults
- Validates configuration changes

### Database Schema

```sql
CREATE TABLE jobs (
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
);

CREATE TABLE config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
```

### Concurrency & Locking

**Problem:** Multiple workers must not process the same job.

**Solution:** Optimistic locking with atomic updates

```python
# Pseudo-code
UPDATE jobs 
SET state = 'processing', 
    locked_by = worker_pid,
    locked_at = NOW()
WHERE id = ? 
  AND state = 'pending' 
  AND locked_by IS NULL
```

Only one worker will successfully update (row-level lock in SQLite).

---

## 🤔 Design Decisions & Trade-offs

### Storage Choice: SQLite

**Why:**
- ✅ Built-in ACID transactions
- ✅ File-based (easy deployment)
- ✅ Supports concurrent reads
- ✅ No external service required

**Trade-off:**
- ❌ Limited concurrent writes (but acceptable for this scale)
- Alternative: JSON files (simpler but requires custom locking)

### Exponential Backoff

**Why:**
- ✅ Reduces load on failing services
- ✅ Industry-standard retry pattern
- ✅ Configurable base value

**Trade-off:**
- ❌ Long delays with high retry counts
- Mitigation: Cap max delay or use max_retries wisely

### Subprocess Execution

**Why:**
- ✅ True isolation (memory, CPU)
- ✅ Supports any shell command
- ✅ Timeout support

**Trade-off:**
- ❌ Higher overhead than threads
- Acceptable: Jobs are expected to be longer-running

### Graceful Shutdown

**Implementation:** Workers listen for SIGTERM/SIGINT
- Current job completes
- New jobs are not picked up
- Clean exit

**Trade-off:**
- ❌ Shutdown may take time if job is long-running
- Mitigation: Implement job timeouts

### CLI vs API

**Why CLI:**
- ✅ Simpler deployment
- ✅ Fits assignment requirements
- ✅ Easy to script and automate

**Future:** Could add HTTP API for web dashboard

---

## 🎥 Demo

**Watch the CLI in action:**

📹 [QueueCTL Demo Video](https://drive.google.com/your-demo-link)

*Duration: 3 minutes | Shows: job enqueue, workers, retries, DLQ*

---

## 🛠️ Development

### Project Structure

```
queuectl/
├── queuectl.py          # Main CLI entry point
├── queue/
│   ├── __init__.py
│   ├── job.py           # Job model
│   ├── queue.py         # Queue operations
│   ├── worker.py        # Worker implementation
│   ├── storage.py       # Database layer
│   └── config.py        # Configuration management
├── tests/
│   ├── test_queue.py
│   ├── test_worker.py
│   └── test_integration.py
├── pyproject.toml       # Poetry configuration
├── poetry.lock          # Dependency lock file
├── README.md
└── .gitignore
```

### Running in Development

```bash
# Install dependencies with Poetry
poetry install

# Run with debug logging
poetry run queuectl --debug worker start
```

---

## 🚧 Known Limitations

1. **Scale:** Designed for single-machine use (not distributed)
2. **Priority:** Jobs are processed FIFO (no priority queue)
3. **Scheduling:** No delayed/scheduled job support
4. **Monitoring:** No built-in metrics (use `status` command)

---

## 🌟 Future Enhancements

- [ ] Job priority queues
- [ ] Scheduled jobs (`run_at` timestamp)
- [ ] Job timeout enforcement
- [ ] Output logging to file
- [ ] Web dashboard for monitoring
- [ ] Metrics (jobs/sec, avg execution time)
- [ ] Job dependencies/chains
- [ ] Distributed workers (Redis/PostgreSQL backend)

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details

---

## 👤 Author

**Your Name**
- GitHub: [@yourusername](https://github.com/yourusername)
- Email: your.email@example.com

---

## 🙏 Acknowledgments

Built as part of the Backend Developer Internship Assignment.

---

## ✅ Submission Checklist

- [x] All required commands functional
- [x] Jobs persist after restart
- [x] Retry and backoff implemented correctly
- [x] DLQ operational
- [x] CLI user-friendly and documented
- [x] Code is modular and maintainable
- [x] Includes test scenarios
- [x] Comprehensive README
- [x] Demo video recorded

---

**Made with ❤️ for reliable background job processing**
#   q u e u e c t l  
 