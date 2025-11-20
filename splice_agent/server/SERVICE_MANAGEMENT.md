# Chart Agent API - Service Management

## Quick Commands

### Using Shell Script (Simple)

```bash
# Start service
python chart_service.py

# Stop service
./stop_service.sh
```

### Using Python Manager (Advanced)

```bash
# Start service (background)
python manage.py start

# Stop service
python manage.py stop

# Restart service
python manage.py restart

# Check status
python manage.py status
```

## Development Workflow

### Option 1: Interactive (Recommended for Development)

```bash
# Start with auto-reload (see logs in terminal)
cd chart_agent/server
python chart_service.py

# Stop with Ctrl+C
```

**Pros:**
- See logs in real-time
- Auto-reload on code changes
- Easy debugging

**Cons:**
- Terminal stays occupied
- Stops when terminal closes

### Option 2: Background Service

```bash
# Start in background
python manage.py start

# Check if running
python manage.py status

# View logs (if redirected to file)
tail -f logs/chart_service.log

# Stop when done
python manage.py stop
```

**Pros:**
- Terminal free for other work
- Service persists after terminal closes

**Cons:**
- No live log viewing
- Harder to debug

## Production Deployment

### Using systemd (Linux)

Create `/etc/systemd/system/chart-agent.service`:

```ini
[Unit]
Description=Chart Agent API
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/agentic-ai-lab/chart_agent/server
Environment="OPENAI_API_KEY=your-key"
ExecStart=/path/to/python chart_service.py
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

Commands:
```bash
sudo systemctl start chart-agent
sudo systemctl stop chart-agent
sudo systemctl restart chart-agent
sudo systemctl status chart-agent
sudo systemctl enable chart-agent  # Start on boot
```

### Using Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY chart_agent/ ./chart_agent/
COPY data/ ./data/

# Expose port
EXPOSE 8003

# Run service
CMD ["python", "chart_agent/server/chart_service.py"]
```

Commands:
```bash
# Build image
docker build -t chart-agent .

# Run container
docker run -d \
  --name chart-agent \
  -p 8003:8003 \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/output:/app/output \
  chart-agent

# Stop container
docker stop chart-agent

# View logs
docker logs -f chart-agent

# Restart
docker restart chart-agent
```

### Using Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  chart-agent:
    build: .
    ports:
      - "8003:8003"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./data:/app/data
      - ./output:/app/output
    restart: unless-stopped
```

Commands:
```bash
# Start service
docker-compose up -d

# Stop service
docker-compose down

# View logs
docker-compose logs -f

# Restart
docker-compose restart
```

### Using PM2 (Node.js Process Manager)

```bash
# Install PM2
npm install -g pm2

# Start service
pm2 start chart_service.py --name chart-agent --interpreter python

# Stop service
pm2 stop chart-agent

# Restart service
pm2 restart chart-agent

# View status
pm2 status

# View logs
pm2 logs chart-agent

# Start on boot
pm2 startup
pm2 save
```

## Graceful Shutdown

The service handles shutdown signals properly:

1. **SIGTERM** (graceful) - Finishes current requests, then stops
2. **SIGINT** (Ctrl+C) - Same as SIGTERM
3. **SIGKILL** (force) - Immediate stop (use as last resort)

### Shutdown Sequence

```python
# In lifespan context manager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting...")
    yield
    # Shutdown - runs when service stops
    logger.info("Shutting down...")
    # Cleanup: close connections, save state, etc.
```

## Health Checks

### Manual Check

```bash
curl http://localhost:8003/health
```

### Automated Monitoring

```bash
# Simple health check script
while true; do
  if ! curl -sf http://localhost:8003/health > /dev/null; then
    echo "Service down! Restarting..."
    python manage.py restart
  fi
  sleep 60
done
```

### With systemd

```ini
[Service]
# Restart if health check fails
ExecStartPost=/bin/bash -c 'sleep 5 && curl -sf http://localhost:8003/health'
Restart=on-failure
```

## Troubleshooting

### Port Already in Use

```bash
# Find what's using port 8003
lsof -i :8003

# Kill the process
kill -9 $(lsof -ti:8003)

# Or use the stop script
./stop_service.sh
```

### Service Won't Stop

```bash
# Force kill
kill -9 $(lsof -ti:8003)

# Or
pkill -9 -f chart_service.py
```

### Check Logs

```bash
# If running in terminal, logs appear there

# If using systemd
journalctl -u chart-agent -f

# If using Docker
docker logs -f chart-agent

# If using PM2
pm2 logs chart-agent
```

## Best Practices

### Development
- ✅ Use `python chart_service.py` with auto-reload
- ✅ Keep terminal open to see logs
- ✅ Use Ctrl+C to stop

### Testing
- ✅ Use `python manage.py start/stop`
- ✅ Check status with `python manage.py status`
- ✅ Test graceful shutdown

### Production
- ✅ Use systemd, Docker, or PM2
- ✅ Enable auto-restart on failure
- ✅ Set up health checks
- ✅ Configure log rotation
- ✅ Use environment variables for secrets
- ✅ Run behind reverse proxy (nginx)
- ✅ Enable HTTPS

## Summary

| Method | Use Case | Pros | Cons |
|--------|----------|------|------|
| `python chart_service.py` | Development | Live logs, auto-reload | Terminal occupied |
| `./stop_service.sh` | Quick stop | Simple, fast | Shell script only |
| `python manage.py` | Testing | Full control, status checks | Requires Python |
| systemd | Linux production | Auto-start, robust | Linux only |
| Docker | Any platform | Isolated, portable | Overhead |
| PM2 | Node.js environments | Easy, powerful | Requires Node.js |

Choose based on your deployment environment and requirements!
