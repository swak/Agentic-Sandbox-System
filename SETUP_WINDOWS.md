# Windows Setup Guide - Agentic Sandbox System

This guide provides step-by-step Docker commands for setting up the Agentic Sandbox System on Windows.

---

## Prerequisites

### 1. Install Docker Desktop for Windows

Download and install from: https://docs.docker.com/desktop/install/windows-install/

**System Requirements**:
- Windows 10 64-bit: Pro, Enterprise, or Education (Build 19041 or higher)
- OR Windows 11 64-bit
- WSL 2 enabled
- 4GB RAM minimum (8GB recommended)
- 10GB free disk space

**After installation**:
1. Launch Docker Desktop
2. Wait for Docker Engine to start (icon in system tray will stop animating)
3. Verify installation in PowerShell or Command Prompt:
   ```cmd
   docker --version
   docker compose version
   ```

### 2. Get API Keys

You'll need at least one API key:

- **OpenAI**: https://platform.openai.com/api-keys
- **Anthropic (Claude)**: https://console.anthropic.com/

---

## Setup Instructions

### Step 1: Configure Environment Variables

1. **Create `.env` file** from the template:
   ```cmd
   copy .env.example .env
   ```

2. **Edit `.env` file** with Notepad or your preferred editor:
   ```cmd
   notepad .env
   ```

3. **Add your API keys**:
   ```env
   # At minimum, add one of these:
   OPENAI_API_KEY=sk-your-actual-openai-key-here
   ANTHROPIC_API_KEY=sk-ant-your-actual-anthropic-key-here
   ```

4. **Save and close** the file

---

### Step 2: Build Docker Images

Open **PowerShell** or **Command Prompt** in the project directory and run:

```cmd
docker compose build
```

This will:
- Build the backend (FastAPI) image (~5 minutes)
- Build the frontend (React) image (~3 minutes)
- Pull the PostgreSQL + PGVector image

**Expected output**:
```
[+] Building 245.2s (18/18) FINISHED
 => [backend] ...
 => [frontend] ...
```

---

### Step 3: Start Services

```cmd
docker compose up -d
```

The `-d` flag runs containers in detached mode (background).

**Expected output**:
```
[+] Running 3/3
 ✔ Container agentic-sandbox-db        Started
 ✔ Container agentic-sandbox-backend   Started
 ✔ Container agentic-sandbox-frontend  Started
```

---

### Step 4: Verify Services Are Running

```cmd
docker compose ps
```

**Expected output** (all should show "Up" or "running"):
```
NAME                        STATUS    PORTS
agentic-sandbox-db          Up        0.0.0.0:5432->5432/tcp
agentic-sandbox-backend     Up        0.0.0.0:8000->8000/tcp
agentic-sandbox-frontend    Up        0.0.0.0:3000->80/tcp
```

---

### Step 5: Check Service Health

#### Backend Health Check:
```cmd
curl http://localhost:8000/health
```

**Expected response**:
```json
{"status":"healthy","database":"connected","version":"1.0.0"}
```

If `curl` is not available, open in browser: http://localhost:8000/health

#### Database Health Check:
```cmd
docker compose exec db pg_isready -U agentuser -d agentsandbox
```

**Expected output**:
```
/var/run/postgresql:5432 - accepting connections
```

---

### Step 6: Access the Application

Open your web browser and navigate to:

- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (interactive Swagger UI)

---

## Usage Guide

### Creating Your First Agent

1. Open http://localhost:3000
2. Click **"Create New Agent"**
3. Fill out the form:
   - **Agent Name**: e.g., "Customer Support Bot"
   - **API Provider**: Select "OpenAI" or "Anthropic"
   - **Model**: Select model (e.g., "gpt-4", "claude-3-sonnet")
   - **Prompt Template**: Choose template or select "Custom"
   - **System Prompt**: Enter instructions for your agent
   - **Knowledge Base** (optional): Upload a TXT, JSON, PDF, or DOCX file
4. Click **"Create Agent"**

### Testing the Agent

1. You'll be redirected to the agent's chat page
2. Type a message in the input box
3. Press **Enter** or click **"Send"**
4. View the agent's response with metrics:
   - Response time
   - Tokens used
   - RAG context (if knowledge base uploaded)

### Uploading a Knowledge Base

Use the sample FAQ file:

1. Navigate to agent settings
2. Click **"Upload Knowledge Base"**
3. Select `configs/sample_faq.txt`
4. Wait for processing (you'll see chunk count)
5. Test with questions like "What's your return policy?"

---

## Common Docker Commands

### View Logs

**All services**:
```cmd
docker compose logs
```

**Specific service** (backend, frontend, or db):
```cmd
docker compose logs backend
docker compose logs frontend
docker compose logs db
```

**Follow logs in real-time** (like `tail -f`):
```cmd
docker compose logs -f backend
```

### Stop Services

```cmd
docker compose stop
```

Containers are stopped but not removed. Use `docker compose start` to restart.

### Start Services (after stopping)

```cmd
docker compose start
```

### Restart Services

```cmd
docker compose restart
```

Or restart a specific service:
```cmd
docker compose restart backend
```

### Stop and Remove Containers

```cmd
docker compose down
```

**To also remove volumes** (deletes database data):
```cmd
docker compose down -v
```

⚠️ **Warning**: This will delete all agents, conversations, and knowledge bases!

### Rebuild After Code Changes

If you modify backend or frontend code:

```cmd
docker compose down
docker compose build
docker compose up -d
```

Or rebuild specific service:
```cmd
docker compose build backend
docker compose up -d backend
```

### Access Container Shell

**Backend container**:
```cmd
docker compose exec backend /bin/bash
```

**Database container**:
```cmd
docker compose exec db psql -U agentuser -d agentsandbox
```

Inside database, you can run SQL:
```sql
\dt                          -- List tables
SELECT * FROM agents;        -- View agents
\q                           -- Quit
```

### View Container Resource Usage

```cmd
docker stats
```

Press `Ctrl+C` to exit.

---

## Troubleshooting

### Issue: "Docker daemon is not running"

**Solution**:
1. Open Docker Desktop
2. Wait for it to fully start (whale icon in system tray)
3. Try command again

---

### Issue: Port Already in Use

**Error**:
```
Error response from daemon: Ports are not available: exposing port TCP 0.0.0.0:3000 -> 0.0.0.0:0: listen tcp 0.0.0.0:3000: bind: An attempt was made to access a socket in a way forbidden by its access permissions.
```

**Solution 1**: Find and stop conflicting service
```cmd
netstat -ano | findstr :3000
netstat -ano | findstr :8000
netstat -ano | findstr :5432
```

**Solution 2**: Change ports in `.env`:
```env
FRONTEND_PORT=3001
API_PORT=8001
POSTGRES_PORT=5433
```

Then restart:
```cmd
docker compose down
docker compose up -d
```

---

### Issue: Database Connection Errors

**Error**: `FATAL: password authentication failed for user "agentuser"`

**Solution**:
1. Verify `.env` has correct credentials:
   ```env
   POSTGRES_USER=agentuser
   POSTGRES_PASSWORD=agentpass
   POSTGRES_DB=agentsandbox
   ```

2. Completely reset database:
   ```cmd
   docker compose down -v
   docker compose up -d
   ```

---

### Issue: API Key Errors

**Error**: `Invalid API key` or `401 Unauthorized`

**Solution**:
1. Verify API key in `.env` file
2. Check for extra spaces or quotes
3. Restart backend:
   ```cmd
   docker compose restart backend
   ```

4. Verify key is loaded:
   ```cmd
   docker compose exec backend printenv OPENAI_API_KEY
   ```

---

### Issue: Frontend Shows "Cannot Connect to API"

**Solution**:
1. Check backend is running:
   ```cmd
   docker compose ps
   ```

2. Test backend directly:
   ```cmd
   curl http://localhost:8000/health
   ```

3. Check backend logs:
   ```cmd
   docker compose logs backend
   ```

4. Restart frontend:
   ```cmd
   docker compose restart frontend
   ```

---

### Issue: Build Fails on Windows

**Error**: Line ending issues (CRLF vs LF)

**Solution**:
1. Configure Git to use LF:
   ```cmd
   git config --global core.autocrlf input
   ```

2. Re-clone repository or convert files:
   ```cmd
   git rm --cached -r .
   git reset --hard
   ```

---

### Issue: Slow Performance

**Solution**:
1. Increase Docker Desktop resources:
   - Open Docker Desktop
   - Settings → Resources
   - Increase CPUs to 4
   - Increase Memory to 8GB
   - Click "Apply & Restart"

2. Enable WSL 2 backend (if not already):
   - Settings → General
   - Check "Use the WSL 2 based engine"

---

## Complete Reset (Nuclear Option)

If everything is broken, start fresh:

```cmd
REM Stop and remove everything
docker compose down -v

REM Remove images
docker compose rm -f
docker rmi agentic-sandbox-backend agentic-sandbox-frontend

REM Rebuild from scratch
docker compose build --no-cache
docker compose up -d
```

---

## Development Workflow

### Making Backend Changes

1. Edit files in `backend/app/`
2. Rebuild and restart:
   ```cmd
   docker compose build backend
   docker compose up -d backend
   ```

3. View logs to verify:
   ```cmd
   docker compose logs -f backend
   ```

### Making Frontend Changes

1. Edit files in `frontend/src/`
2. Rebuild and restart:
   ```cmd
   docker compose build frontend
   docker compose up -d frontend
   ```

3. Clear browser cache and refresh

### Database Schema Changes

1. Edit `database/schema.sql`
2. Reset database:
   ```cmd
   docker compose down -v
   docker compose up -d
   ```

---

## Performance Tips

### 1. Use Volume Mounts for Development

Edit `docker-compose.yml` to add volume mounts:

```yaml
backend:
  volumes:
    - ./backend:/app
    - ./configs:/app/configs
```

This allows code changes without rebuilding.

### 2. Check Docker Desktop Settings

- **File Sharing**: Ensure project directory is shared
- **Resources**: Allocate at least 4GB RAM
- **WSL Integration**: Enable for better performance

### 3. Prune Unused Resources

Free up disk space:
```cmd
docker system prune -a --volumes
```

⚠️ This removes all unused images and volumes!

---

## Accessing Services from Other Devices

### On Your Local Network

1. Find your Windows IP address:
   ```cmd
   ipconfig
   ```
   Look for "IPv4 Address" (e.g., 192.168.1.100)

2. Update `.env`:
   ```env
   API_HOST=0.0.0.0
   REACT_APP_API_URL=http://192.168.1.100:8000
   ```

3. Restart services:
   ```cmd
   docker compose down
   docker compose up -d
   ```

4. Access from other device:
   - Frontend: `http://192.168.1.100:3000`
   - Backend: `http://192.168.1.100:8000`

---

## Backup and Restore

### Backup Database

```cmd
docker compose exec db pg_dump -U agentuser agentsandbox > backup.sql
```

### Restore Database

```cmd
docker compose exec -T db psql -U agentuser agentsandbox < backup.sql
```

### Backup Configurations

```cmd
xcopy configs configs_backup\ /E /I
```

---

## Next Steps

1. ✅ **Verify setup**: Visit http://localhost:3000
2. ✅ **Create first agent**: Follow the UI prompts
3. ✅ **Upload sample FAQ**: Use `configs/sample_faq.txt`
4. ✅ **Test RAG**: Ask "What's your return policy?"
5. ✅ **View logs**: Check conversation history
6. ✅ **Explore API docs**: Visit http://localhost:8000/docs

---

## Getting Help

### Check Logs
```cmd
docker compose logs -f
```

### Service Health
```cmd
docker compose ps
curl http://localhost:8000/health
```

### Database Connection
```cmd
docker compose exec db psql -U agentuser -d agentsandbox -c "SELECT 1;"
```

### Contact
- **Documentation**: See README.md and ARCHITECTURE.md
- **Issues**: Create GitHub issue
- **Community**: [Your community link]

---

## Production Deployment (Optional)

For production, consider:

1. **Use Docker Swarm or Kubernetes**
2. **Set strong passwords** in `.env`
3. **Enable HTTPS** with reverse proxy (nginx, Traefik)
4. **Use managed database** (AWS RDS, Azure Database)
5. **Set `DEBUG=false`** in `.env`
6. **Add authentication** (OAuth2)

---

## Summary of Key Commands

| Action | Command |
|--------|---------|
| **Setup** | `copy .env.example .env` → Edit `.env` |
| **Build** | `docker compose build` |
| **Start** | `docker compose up -d` |
| **Stop** | `docker compose down` |
| **Logs** | `docker compose logs -f` |
| **Status** | `docker compose ps` |
| **Restart** | `docker compose restart` |
| **Reset** | `docker compose down -v && docker compose up -d` |

---

**You're ready to go!** 🚀

Run these commands in order:
```cmd
copy .env.example .env
notepad .env
docker compose build
docker compose up -d
```

Then open: http://localhost:3000
