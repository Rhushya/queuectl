# 🎉 QueueCTL - Complete Setup & Running Guide

## ✅ Project Successfully Created!

All files have been created and the project is ready to use!

---

## 📁 Project Structure

```
queuectl/
├── queuectl.py              # Main CLI entry point ⭐
├── queue/                   # Core package
│   ├── __init__.py          # Package initialization
│   ├── job.py               # Job model (dataclass with state management)
│   ├── queue.py             # Queue operations (enqueue, claim, DLQ)
│   ├── worker.py            # Worker implementation (job execution)
│   ├── storage.py           # SQLite storage layer (persistence)
│   └── config.py            # Configuration management
├── tests/                   # Test suite
│   ├── __init__.py
│   ├── test_job.py          # Job model tests
│   ├── test_queue.py        # Queue operations tests
│   └── test_worker.py       # Worker tests
├── pyproject.toml           # Poetry configuration ⭐
├── queuectl.db              # SQLite database (created after init)
├── README.md                # Full documentation
├── QUICKSTART.md            # Quick start guide
├── SETUP.md                 # This file
├── demo.bat                 # Windows CMD demo script
├── demo.ps1                 # PowerShell demo script
└── .gitignore               # Git ignore rules
```

---

## 🚀 Getting Started (3 Steps)

### Step 1: Verify Installation ✓

Dependencies are already installed! The project uses:
- Python 3.8+
- Poetry for dependency management
- SQLite for database (built-in)
- pytest for testing

### Step 2: Initialize Database ✓

Already done! The database `queuectl.db` has been created.

### Step 3: Try It Out!

**Option A: Run the Demo Script (Recommended)**

For PowerShell:
```powershell
.\demo.ps1
```

For CMD:
```cmd
demo.bat
```

**Option B: Manual Commands**

Add a job:
```bash
poetry run python queuectl.py enqueue "{\"id\":\"test1\",\"command\":\"echo Hello\"}"
```

Start a worker:
```bash
poetry run python queuectl.py worker start --count 1
```

Check status:
```bash
poetry run python queuectl.py status
```

Stop workers:
```bash
poetry run python queuectl.py worker stop
```

---

## 📚 Available Commands

### Job Management
```bash
# Enqueue a job
poetry run python queuectl.py enqueue '{"id":"job1","command":"echo test"}'

# Get job details
poetry run python queuectl.py get job1

# List all jobs
poetry run python queuectl.py list --all

# List jobs by state
poetry run python queuectl.py list --state pending
poetry run python queuectl.py list --state completed

# Show queue status
poetry run python queuectl.py status
```

### Worker Management
```bash
# Start 1 worker
poetry run python queuectl.py worker start

# Start multiple workers
poetry run python queuectl.py worker start --count 3

# List active workers
poetry run python queuectl.py worker list

# Stop all workers
poetry run python queuectl.py worker stop
```

### Dead Letter Queue (DLQ)
```bash
# List DLQ jobs
poetry run python queuectl.py dlq list

# Retry specific DLQ job
poetry run python queuectl.py dlq retry --job-id job1

# Retry all DLQ jobs
poetry run python queuectl.py dlq retry --all

# Clear DLQ
poetry run python queuectl.py dlq clear
```

### Configuration
```bash
# Show configuration
poetry run python queuectl.py config show

# Set max retries
poetry run python queuectl.py config set max-retries 5

# Set backoff base
poetry run python queuectl.py config set backoff-base 2

# Set job timeout (seconds)
poetry run python queuectl.py config set job-timeout 300
```

---

## 🧪 Running Tests

```bash
# Run all tests
poetry run pytest tests/

# Run with verbose output
poetry run pytest tests/ -v

# Run with coverage
poetry run pytest --cov=queue tests/

# Run specific test file
poetry run pytest tests/test_job.py -v
```

---

## 💡 Usage Examples

### Example 1: Simple Job Queue

```bash
# Add some jobs
poetry run python queuectl.py enqueue '{"id":"job1","command":"echo Task 1"}'
poetry run python queuectl.py enqueue '{"id":"job2","command":"echo Task 2"}'
poetry run python queuectl.py enqueue '{"id":"job3","command":"echo Task 3"}'

# Start a worker
poetry run python queuectl.py worker start

# Check status
poetry run python queuectl.py status

# Stop worker
poetry run python queuectl.py worker stop
```

### Example 2: Job with Retries

```bash
# Job that will fail and retry
poetry run python queuectl.py enqueue '{"id":"fail1","command":"exit 1","max_retries":3}'

# Start worker and watch it retry
poetry run python queuectl.py worker start

# After retries exhausted, check DLQ
poetry run python queuectl.py dlq list

# Stop worker
poetry run python queuectl.py worker stop
```

### Example 3: Multiple Workers

```bash
# Add 10 jobs
for i in {1..10}; do
  poetry run python queuectl.py enqueue "{\"id\":\"job$i\",\"command\":\"echo Task $i\"}"
done

# Start 3 workers to process concurrently
poetry run python queuectl.py worker start --count 3

# Check status
poetry run python queuectl.py status
poetry run python queuectl.py worker list

# Stop all workers
poetry run python queuectl.py worker stop
```

---

## 🏗️ Architecture Overview

### Components

1. **Job Model** (`queue/job.py`)
   - Dataclass with state machine
   - States: pending → processing → completed/failed/dead
   - Tracks attempts, errors, timestamps

2. **Storage Layer** (`queue/storage.py`)
   - SQLite database for persistence
   - Atomic job claiming (prevents duplicate processing)
   - Configuration storage

3. **Queue Manager** (`queue/queue.py`)
   - Job CRUD operations
   - DLQ management
   - Status reporting

4. **Worker** (`queue/worker.py`)
   - Background process execution
   - Exponential backoff retry logic
   - Graceful shutdown handling

5. **CLI** (`queuectl.py`)
   - Command-line interface
   - Worker process management
   - User-friendly output

### Job Lifecycle

```
┌─────────┐
│ pending │──┐
└─────────┘  │
             ▼
        ┌────────────┐
        │ processing │
        └────────────┘
             │
      ┌──────┴──────┐
      ▼             ▼
┌───────────┐  ┌────────┐
│ completed │  │ failed │
└───────────┘  └────────┘
                    │
              ┌─────┴─────┐
              │ retry?    │
              └─────┬─────┘
                 ▼     ▼
            pending  ┌──────┐
                     │ dead │
                     └──────┘
```

### Retry Logic

- **Exponential Backoff**: delay = backoff_base ^ attempts
- Example with base=2:
  - 1st retry: 2¹ = 2 seconds
  - 2nd retry: 2² = 4 seconds
  - 3rd retry: 2³ = 8 seconds

---

## 🔧 Configuration Options

| Key | Default | Description |
|-----|---------|-------------|
| `max-retries` | 3 | Maximum retry attempts before DLQ |
| `backoff-base` | 2 | Exponential backoff base multiplier |
| `worker-count` | 1 | Default number of workers |
| `job-timeout` | 300 | Job execution timeout (seconds) |

---

## 🎯 Features Implemented

✅ **Core Features**
- [x] Persistent job queue (SQLite)
- [x] Multiple concurrent workers
- [x] Automatic retry with exponential backoff
- [x] Dead Letter Queue (DLQ)
- [x] Job state tracking
- [x] Graceful worker shutdown

✅ **CLI Commands**
- [x] Job enqueue/get/list
- [x] Worker start/stop/list
- [x] DLQ list/retry/clear
- [x] Configuration management
- [x] Queue status reporting

✅ **Advanced Features**
- [x] Atomic job claiming (no duplicate processing)
- [x] Configurable retry policies
- [x] Job timeout support
- [x] Background worker processes
- [x] Cross-platform support (Windows/Linux/Mac)

✅ **Testing**
- [x] Unit tests for Job model
- [x] Integration tests for Queue
- [x] Worker execution tests
- [x] Test coverage setup

---

## 📖 Documentation

- **README.md** - Comprehensive documentation with architecture details
- **QUICKSTART.md** - Quick reference guide
- **SETUP.md** - This file (setup and running instructions)
- **Code Comments** - Inline documentation in all modules

---

## 🐛 Troubleshooting

### Issue: "Module not found" error
**Solution**: Make sure you're using `poetry run python queuectl.py`

### Issue: Workers not processing jobs
**Solution**: 
1. Check if workers are running: `poetry run python queuectl.py worker list`
2. Check job state: `poetry run python queuectl.py list --all`
3. Restart workers if needed

### Issue: Database locked
**Solution**: SQLite allows only one writer at a time. This is normal and handled automatically.

### Issue: Job stuck in "processing"
**Solution**: If a worker crashes, the job may stay in processing state. Stop all workers and restart them.

---

## 🎓 Learning Resources

### Understanding the Code

1. Start with `queue/job.py` - See how jobs are modeled
2. Read `queue/storage.py` - Understand persistence
3. Check `queue/queue.py` - Learn queue operations
4. Study `queue/worker.py` - See job execution
5. Explore `queuectl.py` - CLI implementation

### Running Examples

1. Run the demo script: `.\demo.ps1` or `demo.bat`
2. Try the examples in QUICKSTART.md
3. Read the tests in `tests/` directory
4. Experiment with different configurations

---

## 🚀 Next Steps

1. **Try the Demo**: Run `.\demo.ps1` to see it in action
2. **Read QUICKSTART.md**: Learn all available commands
3. **Run Tests**: `poetry run pytest tests/ -v`
4. **Customize**: Modify configurations to fit your needs
5. **Build**: Create your own jobs and workflows!

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Read the full README.md
3. Review the test files for examples
4. Check the code comments

---

## 📄 License

MIT License - See LICENSE file for details

---

**🎉 You're all set! Happy queueing!** 🎉

Run `.\demo.ps1` to see QueueCTL in action!
