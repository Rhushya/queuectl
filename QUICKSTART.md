# QueueCTL - Quick Start Guide

## 🚀 Installation & Setup

### 1. Install Dependencies

```bash
# Install dependencies using Poetry
poetry install
```

### 2. Initialize the Database

```bash
# Initialize QueueCTL
poetry run python queuectl.py init
```

## 📝 Basic Usage Examples

### Example 1: Simple Job

```bash
# Enqueue a simple echo job
poetry run python queuectl.py enqueue "{\"id\":\"job1\",\"command\":\"echo Hello World\"}"

# Start a worker
poetry run python queuectl.py worker start --count 1

# Check status
poetry run python queuectl.py status

# Get job details
poetry run python queuectl.py get job1

# Stop workers
poetry run python queuectl.py worker stop
```

### Example 2: Multiple Jobs with Multiple Workers

```bash
# Enqueue multiple jobs
poetry run python queuectl.py enqueue "{\"id\":\"job1\",\"command\":\"echo Task 1\"}"
poetry run python queuectl.py enqueue "{\"id\":\"job2\",\"command\":\"echo Task 2\"}"
poetry run python queuectl.py enqueue "{\"id\":\"job3\",\"command\":\"echo Task 3\"}"

# Start 2 workers to process jobs concurrently
poetry run python queuectl.py worker start --count 2

# Check status
poetry run python queuectl.py status

# List all jobs
poetry run python queuectl.py list --all

# Stop workers
poetry run python queuectl.py worker stop
```

### Example 3: Job with Custom Retries

```bash
# Enqueue a job with custom retry count
poetry run python queuectl.py enqueue "{\"id\":\"job4\",\"command\":\"python process.py\",\"max_retries\":5}"

# Start worker
poetry run python queuectl.py worker start

# Monitor the job
poetry run python queuectl.py get job4

# Stop worker
poetry run python queuectl.py worker stop
```

### Example 4: Testing Failure & Retry

```bash
# Create a job that will fail
poetry run python queuectl.py enqueue "{\"id\":\"fail1\",\"command\":\"exit 1\",\"max_retries\":2}"

# Start worker
poetry run python queuectl.py worker start

# Watch it retry (wait a few seconds)
# It will retry with exponential backoff: 2s, 4s

# Check status
poetry run python queuectl.py status

# After retries exhausted, check DLQ
poetry run python queuectl.py dlq list

# Stop worker
poetry run python queuectl.py worker stop
```

### Example 5: Dead Letter Queue (DLQ) Management

```bash
# Enqueue a failing job
poetry run python queuectl.py enqueue "{\"id\":\"bad1\",\"command\":\"nonexistent_command\",\"max_retries\":1}"

# Start worker
poetry run python queuectl.py worker start

# Wait for it to fail and move to DLQ (a few seconds)

# List DLQ jobs
poetry run python queuectl.py dlq list

# Retry a specific DLQ job
poetry run python queuectl.py dlq retry --job-id bad1

# Or retry all DLQ jobs
poetry run python queuectl.py dlq retry --all

# Clear DLQ
poetry run python queuectl.py dlq clear

# Stop worker
poetry run python queuectl.py worker stop
```

### Example 6: Configuration Management

```bash
# Show current configuration
poetry run python queuectl.py config show

# Set max retries
poetry run python queuectl.py config set max-retries 5

# Set backoff base (exponential backoff multiplier)
poetry run python queuectl.py config set backoff-base 3

# Set job timeout (seconds)
poetry run python queuectl.py config set job-timeout 600

# Show updated configuration
poetry run python queuectl.py config show
```

### Example 7: Worker Management

```bash
# Start 3 workers
poetry run python queuectl.py worker start --count 3

# List active workers
poetry run python queuectl.py worker list

# Stop all workers
poetry run python queuectl.py worker stop
```

## 🧪 Running Tests

```bash
# Run all tests
poetry run pytest tests/

# Run with coverage
poetry run pytest --cov=queue tests/

# Run verbose
poetry run pytest -v tests/

# Run specific test file
poetry run pytest tests/test_job.py -v
```

## 📁 Project Structure

```
queuectl/
├── queuectl.py          # Main CLI entry point
├── queue/               # Core package
│   ├── __init__.py      # Package initialization
│   ├── job.py           # Job model
│   ├── queue.py         # Queue operations
│   ├── worker.py        # Worker implementation
│   ├── storage.py       # SQLite storage layer
│   └── config.py        # Configuration management
├── tests/               # Test suite
│   ├── __init__.py
│   ├── test_job.py
│   ├── test_queue.py
│   └── test_worker.py
├── pyproject.toml       # Poetry configuration
├── README.md            # Full documentation
├── QUICKSTART.md        # This file
└── .gitignore
```

## 🎯 Common Commands Reference

| Command | Description |
|---------|-------------|
| `poetry run python queuectl.py init` | Initialize the system |
| `poetry run python queuectl.py enqueue "JSON"` | Add a job |
| `poetry run python queuectl.py get JOB_ID` | Get job details |
| `poetry run python queuectl.py list --all` | List all jobs |
| `poetry run python queuectl.py list --state pending` | List pending jobs |
| `poetry run python queuectl.py status` | Show queue status |
| `poetry run python queuectl.py worker start --count N` | Start N workers |
| `poetry run python queuectl.py worker stop` | Stop all workers |
| `poetry run python queuectl.py worker list` | List active workers |
| `poetry run python queuectl.py dlq list` | List DLQ jobs |
| `poetry run python queuectl.py dlq retry --job-id ID` | Retry DLQ job |
| `poetry run python queuectl.py dlq clear` | Clear DLQ |
| `poetry run python queuectl.py config show` | Show configuration |
| `poetry run python queuectl.py config set KEY VALUE` | Set config value |

## 💡 Tips

1. **Windows Users**: The commands work in both CMD and PowerShell
2. **JSON Escaping**: On Windows CMD, use double quotes. On PowerShell, escape with backticks if needed
3. **Background Workers**: Workers run in separate processes and continue even if you close the terminal
4. **Database**: All data is stored in `queuectl.db` SQLite file
5. **Persistence**: Jobs survive system restarts

## 🐛 Troubleshooting

**Workers not processing jobs?**
- Check if workers are running: `poetry run python queuectl.py worker list`
- Check job state: `poetry run python queuectl.py list --all`

**Database locked error?**
- Make sure only one worker is writing at a time
- SQLite handles concurrent reads well but writes are sequential

**Jobs stuck in processing?**
- This can happen if a worker crashes
- Manually update job state or restart workers

## 📚 Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check out the test files in `tests/` for more examples
- Customize the configuration for your needs
- Build your own jobs and workflows!

---

**Happy Queueing! 🎉**
