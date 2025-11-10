# Windows Quick Start Guide

**Get started in 3 minutes!**

---

## Prerequisites ✓

1. **Install Docker Desktop**: https://docs.docker.com/desktop/install/windows-install/
2. **Get API Key**: https://platform.openai.com/api-keys (OpenAI) or https://console.anthropic.com/ (Claude)

---

## Installation Commands

Open **PowerShell** or **Command Prompt** in the project folder:

### 1. Create Environment File
```cmd
copy .env.example .env
notepad .env
```

**Edit these lines in `.env`**:
```env
OPENAI_API_KEY=sk-your-actual-key-here
```
Save and close Notepad.

---

### 2. Build & Start (Choose One)

**Option A: Use the setup script** (recommended):
```cmd
setup.bat
```

**Option B: Manual Docker commands**:
```cmd
docker compose build
docker compose up -d
```

---

### 3. Access the System

Open in your browser:
- **Dashboard**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

---

## Common Commands

| Task | Command |
|------|---------|
| **Start services** | `docker compose up -d` |
| **Stop services** | `docker compose down` |
| **View logs** | `docker compose logs -f` |
| **Check status** | `docker compose ps` |
| **Restart** | `docker compose restart` |
| **Complete reset** | `docker compose down -v && docker compose up -d` |

---

## Quick Test

1. Go to http://localhost:3000
2. Click **"Create New Agent"**
3. Fill in:
   - Name: "Test Bot"
   - API: "OpenAI"
   - Model: "gpt-4"
   - Template: "Friendly Customer Support"
4. Click **"Create Agent"**
5. Type: "Hello!"
6. See the response ✨

---

## Troubleshooting

**Problem**: "Docker daemon is not running"
**Solution**: Open Docker Desktop and wait for it to start

**Problem**: Port already in use
**Solution**: Change ports in `.env`:
```env
FRONTEND_PORT=3001
API_PORT=8001
```

**Problem**: API key error
**Solution**: Double-check `.env` file has no extra spaces

**Problem**: Can't connect to backend
**Solution**:
```cmd
docker compose restart backend
docker compose logs backend
```

---

## Getting Help

- **Full Windows Guide**: [SETUP_WINDOWS.md](SETUP_WINDOWS.md)
- **General Docs**: [README.md](README.md)
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)

---

## What's Running?

After setup, you have:
- **Frontend** (React) on port 3000
- **Backend** (FastAPI) on port 8000
- **Database** (PostgreSQL + PGVector) on port 5432

All running in Docker containers!

---

**Next Steps**: Upload a knowledge base file and test RAG! 🚀
