# 📚 QueueCTL - Documentation Index

## 🎯 Welcome to QueueCTL!

A production-grade CLI-based background job queue system with workers, retries, and DLQ support.

---

## 🚀 **START HERE** → [START_HERE.md](START_HERE.md)

**If you're new, read START_HERE.md first!** It will guide you through everything.

---

## 📖 Documentation Files

### For Getting Started

| File | Read When | Purpose |
|------|-----------|---------|
| **[START_HERE.md](START_HERE.md)** | **RIGHT NOW** | Quickest way to get started |
| **[SUMMARY.md](SUMMARY.md)** | After trying demo | Project overview & what was built |
| **[QUICKSTART.md](QUICKSTART.md)** | Need commands | Quick reference for all commands |

### For Understanding

| File | Read When | Purpose |
|------|-----------|---------|
| **[SETUP.md](SETUP.md)** | Want details | Complete setup & architecture guide |
| **[README.md](README.md)** | Full details | Comprehensive documentation (721 lines) |

### For Running

| File | Run When | Purpose |
|------|----------|---------|
| **demo.ps1** | Quick demo | PowerShell demo script |
| **demo.bat** | Quick demo | Windows CMD demo script |
| **demo.sh** | Quick demo | Linux/Mac demo script |

---

## 🎓 Recommended Learning Path

### 5-Minute Quick Start
```
1. Read START_HERE.md
2. Run: .\demo.ps1
3. Try a few commands
```

### 30-Minute Introduction
```
1. Read SUMMARY.md
2. Read QUICKSTART.md
3. Try all command examples
4. Run tests: poetry run pytest tests/
```

### 2-Hour Deep Dive
```
1. Read SETUP.md (architecture section)
2. Study the code in order:
   - queue/job.py
   - queue/storage.py
   - queue/queue.py
   - queue/worker.py
   - queuectl.py
3. Read tests in tests/
4. Read full README.md
```

---

## 📁 Project Structure

```
queuectl/
├── 📄 Documentation
│   ├── INDEX.md           ← You are here
│   ├── START_HERE.md      ← Read this first!
│   ├── SUMMARY.md         ← Project overview
│   ├── QUICKSTART.md      ← Command reference
│   ├── SETUP.md           ← Setup & architecture
│   └── README.md          ← Full documentation
│
├── 🎬 Demo Scripts
│   ├── demo.ps1           ← PowerShell demo
│   ├── demo.bat           ← Windows CMD demo
│   └── demo.sh            ← Linux/Mac demo
│
├── 💻 Application
│   ├── queuectl.py        ← Main CLI application
│   ├── queue/             ← Core package
│   │   ├── __init__.py
│   │   ├── job.py         ← Job model
│   │   ├── storage.py     ← Database layer
│   │   ├── queue.py       ← Queue operations
│   │   ├── worker.py      ← Worker logic
│   │   └── config.py      ← Configuration
│   └── tests/             ← Test suite
│       ├── test_job.py
│       ├── test_queue.py
│       └── test_worker.py
│
└── ⚙️ Configuration
    ├── pyproject.toml     ← Poetry config
    ├── queuectl.db        ← SQLite database
    └── .gitignore         ← Git ignore
```

---

## 🎯 Quick Links by Task

### I want to...

**...get started quickly**
→ Read [START_HERE.md](START_HERE.md) and run `.\demo.ps1`

**...understand what was built**
→ Read [SUMMARY.md](SUMMARY.md)

**...see all commands**
→ Read [QUICKSTART.md](QUICKSTART.md)

**...understand the architecture**
→ Read [SETUP.md](SETUP.md) (Architecture section)

**...read full documentation**
→ Read [README.md](README.md)

**...run tests**
→ `poetry run pytest tests/ -v`

**...add a job**
→ `poetry run python queuectl.py enqueue '{"id":"ID","command":"CMD"}'`

**...start workers**
→ `poetry run python queuectl.py worker start`

**...check status**
→ `poetry run python queuectl.py status`

---

## 📊 File Stats

| File | Lines | Purpose |
|------|-------|---------|
| START_HERE.md | 300+ | Getting started guide |
| SUMMARY.md | 350+ | Project overview |
| QUICKSTART.md | 250+ | Command reference |
| SETUP.md | 450+ | Setup & architecture |
| README.md | 721 | Full documentation |
| queuectl.py | 450+ | Main application |
| queue/*.py | 600+ | Core package |
| tests/*.py | 300+ | Test suite |

**Total Documentation: 2,000+ lines**
**Total Code: 1,500+ lines**

---

## 🎯 Features at a Glance

✅ Persistent job queue (SQLite)
✅ Multiple concurrent workers
✅ Automatic retry with exponential backoff
✅ Dead Letter Queue (DLQ)
✅ Complete CLI interface
✅ Graceful shutdown
✅ Cross-platform (Windows/Linux/Mac)
✅ Comprehensive tests
✅ Extensive documentation

---

## 🚀 Quick Commands

```bash
# Demo
.\demo.ps1

# Status
poetry run python queuectl.py status

# Add job
poetry run python queuectl.py enqueue '{"id":"job1","command":"echo test"}'

# Start worker
poetry run python queuectl.py worker start

# List jobs
poetry run python queuectl.py list --all

# Tests
poetry run pytest tests/
```

---

## 🎓 Documentation Overview

### START_HERE.md
- Quickest way to get started
- Demo script instructions
- Common use cases
- Troubleshooting
- **Read this first!**

### SUMMARY.md
- What was built
- Project stats
- Architecture overview
- Feature highlights
- Success criteria

### QUICKSTART.md
- All commands reference
- Job specification
- Configuration options
- Quick examples
- Testing guide

### SETUP.md
- Complete setup guide
- Architecture details
- Component descriptions
- Running examples
- Development guide

### README.md
- Comprehensive documentation
- Full feature list
- Detailed architecture
- Design decisions
- Advanced topics

---

## 💡 Tips

1. **New users**: Start with START_HERE.md
2. **Quick reference**: Use QUICKSTART.md
3. **Understanding**: Read SUMMARY.md
4. **Deep dive**: Study SETUP.md
5. **Complete info**: Reference README.md

---

## 🎉 You're Ready!

**Everything is built, tested, and documented.**

### Next Steps:
1. ✅ Read [START_HERE.md](START_HERE.md)
2. ✅ Run `.\demo.ps1`
3. ✅ Try some commands
4. ✅ Explore and enjoy!

---

**Happy Queueing! 🚀**
