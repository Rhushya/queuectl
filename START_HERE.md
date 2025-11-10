# 🚀 GET STARTED WITH QUEUECTL

## ✅ Your project is ready to use!

---

## 🎯 Quick Start (Choose One)

### Option 1: Run the Demo Script (Easiest!)

**Windows PowerShell:**
```powershell
.\demo.ps1
```

**Windows CMD:**
```cmd
demo.bat
```

**Linux/Mac:**
```bash
chmod +x demo.sh
./demo.sh
```

This will show you all features in action!

---

### Option 2: Manual Quick Test

```bash
# 1. Add a job
poetry run python queuectl.py enqueue '{"id":"hello","command":"echo Hello World"}'

# 2. Start a worker
poetry run python queuectl.py worker start

# 3. Check status (wait 2-3 seconds first)
poetry run python queuectl.py status

# 4. See the result
poetry run python queuectl.py get hello

# 5. Stop worker
poetry run python queuectl.py worker stop
```

---

## 📚 Documentation Guide

| File | When to Read It | What's Inside |
|------|----------------|---------------|
| **START_HERE.md** | RIGHT NOW! | This file - quickest way to start |
| **SUMMARY.md** | Next | Project overview & what was built |
| **QUICKSTART.md** | For reference | All commands at a glance |
| **SETUP.md** | For deep dive | Complete setup & architecture guide |
| **README.md** | For full docs | Comprehensive documentation (721 lines) |

**Recommended Reading Order:**
1. START_HERE.md (this file) ← You are here
2. Run demo.ps1 ← Try it!
3. SUMMARY.md ← Understand what was built
4. QUICKSTART.md ← Learn all commands
5. SETUP.md ← Deep dive into architecture

---

## 🎓 Learning Path

### Beginner (5 minutes)
1. ✅ Run `.\demo.ps1`
2. ✅ Read SUMMARY.md
3. ✅ Try 2-3 manual commands

### Intermediate (30 minutes)
1. Read QUICKSTART.md
2. Try all command examples
3. Run tests: `poetry run pytest tests/ -v`
4. Explore the database: `queuectl.db`

### Advanced (2 hours)
1. Read SETUP.md (architecture section)
2. Study the code:
   - `queue/job.py` - Job model
   - `queue/storage.py` - Database layer
   - `queue/queue.py` - Queue operations
   - `queue/worker.py` - Worker logic
   - `queuectl.py` - CLI application
3. Read the tests in `tests/`
4. Customize and extend!

---

## 💡 Common Use Cases

### Use Case 1: Process Multiple Tasks
```bash
# Add several jobs
poetry run python queuectl.py enqueue '{"id":"task1","command":"echo Task 1"}'
poetry run python queuectl.py enqueue '{"id":"task2","command":"echo Task 2"}'
poetry run python queuectl.py enqueue '{"id":"task3","command":"echo Task 3"}'

# Start multiple workers for parallel processing
poetry run python queuectl.py worker start --count 3

# Check progress
poetry run python queuectl.py status

# Stop when done
poetry run python queuectl.py worker stop
```

### Use Case 2: Handle Failures
```bash
# Add a job that will fail
poetry run python queuectl.py enqueue '{"id":"fail1","command":"exit 1","max_retries":2}'

# Start worker
poetry run python queuectl.py worker start

# Watch it retry (exponential backoff: 2s, 4s)
# After retries exhausted, check Dead Letter Queue
poetry run python queuectl.py dlq list

# Retry manually if needed
poetry run python queuectl.py dlq retry --job-id fail1

# Stop worker
poetry run python queuectl.py worker stop
```

### Use Case 3: Configure the System
```bash
# View current settings
poetry run python queuectl.py config show

# Increase max retries
poetry run python queuectl.py config set max-retries 5

# Increase backoff (longer delays between retries)
poetry run python queuectl.py config set backoff-base 3

# Increase timeout for long-running jobs
poetry run python queuectl.py config set job-timeout 600

# Verify changes
poetry run python queuectl.py config show
```

---

## 🔍 Understanding the Commands

### All Available Commands

```bash
# INITIALIZATION
poetry run python queuectl.py init                           # Initialize database

# JOB MANAGEMENT
poetry run python queuectl.py enqueue 'JSON'                 # Add a job
poetry run python queuectl.py get JOB_ID                     # Get job details
poetry run python queuectl.py list --all                     # List all jobs
poetry run python queuectl.py list --state STATE             # List jobs by state
poetry run python queuectl.py status                         # Show queue status

# WORKER MANAGEMENT
poetry run python queuectl.py worker start                   # Start 1 worker
poetry run python queuectl.py worker start --count N         # Start N workers
poetry run python queuectl.py worker list                    # List active workers
poetry run python queuectl.py worker stop                    # Stop all workers

# DEAD LETTER QUEUE
poetry run python queuectl.py dlq list                       # List failed jobs
poetry run python queuectl.py dlq retry --job-id ID          # Retry one job
poetry run python queuectl.py dlq retry --all                # Retry all
poetry run python queuectl.py dlq clear                      # Clear DLQ

# CONFIGURATION
poetry run python queuectl.py config show                    # Show config
poetry run python queuectl.py config set KEY VALUE           # Set config
```

### Job JSON Format

```json
{
  "id": "unique-job-id",        // Required: unique identifier
  "command": "echo hello",       // Required: shell command to run
  "max_retries": 3               // Optional: override default retries
}
```

**Examples:**
```bash
# Simple job
poetry run python queuectl.py enqueue '{"id":"job1","command":"echo test"}'

# Job with custom retries
poetry run python queuectl.py enqueue '{"id":"job2","command":"python script.py","max_retries":5}'

# Long-running job
poetry run python queuectl.py enqueue '{"id":"job3","command":"sleep 10"}'
```

---

## 🧪 Testing

```bash
# Run all tests
poetry run pytest tests/

# Run with verbose output
poetry run pytest tests/ -v

# Run with test coverage
poetry run pytest --cov=queue tests/

# Run specific test file
poetry run pytest tests/test_job.py -v
poetry run pytest tests/test_queue.py -v
poetry run pytest tests/test_worker.py -v
```

---

## 🎯 What You Can Do Now

✅ **Run the demo** - `.\demo.ps1`
✅ **Read the docs** - Start with SUMMARY.md
✅ **Try commands** - Use examples above
✅ **Run tests** - `poetry run pytest tests/`
✅ **Explore code** - Check out `queue/` directory
✅ **Customize** - Modify configs and add features

---

## 🐛 Troubleshooting

**Q: Command not found?**
A: Make sure to use `poetry run python queuectl.py ...`

**Q: Workers not processing?**
A: Check if workers are running with `poetry run python queuectl.py worker list`

**Q: Job stuck in processing?**
A: Stop workers and restart: `poetry run python queuectl.py worker stop` then start again

**Q: How to see what's in the database?**
A: Use SQLite viewer or run `poetry run python queuectl.py list --all`

**Q: Where are logs?**
A: Workers print to console. For production, redirect to files.

---

## 📞 Need Help?

1. **Quick Reference**: See QUICKSTART.md
2. **Detailed Guide**: See SETUP.md  
3. **Full Docs**: See README.md
4. **Code Examples**: See `tests/` directory
5. **Architecture**: See SETUP.md architecture section

---

## 🎉 You're All Set!

The project is:
- ✅ Fully implemented
- ✅ Well documented
- ✅ Tested
- ✅ Ready to use

**Next Step: Run the demo!**

```powershell
.\demo.ps1
```

Enjoy building with QueueCTL! 🚀

---

## 📋 Cheat Sheet

**Most Common Commands:**
```bash
# Check status
poetry run python queuectl.py status

# Add job
poetry run python queuectl.py enqueue '{"id":"ID","command":"COMMAND"}'

# Start worker
poetry run python queuectl.py worker start

# Stop worker
poetry run python queuectl.py worker stop

# List jobs
poetry run python queuectl.py list --all

# Check DLQ
poetry run python queuectl.py dlq list
```

**Save this for quick reference!**
