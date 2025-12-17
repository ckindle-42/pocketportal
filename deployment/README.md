# Deployment Configuration

This directory contains platform-specific deployment configurations for running PocketPortal as a system service.

## Directory Structure

```
deployment/
├── linux/          # Linux systemd service configuration
│   └── pocketportal.service
├── macos/          # macOS launchd configuration
│   └── com_telegram_agent.plist
└── README.md       # This file
```

## Linux (systemd)

### Installation

1. **Copy the service file:**
   ```bash
   sudo cp deployment/linux/pocketportal.service /etc/systemd/system/
   ```

2. **Edit the service file** to match your installation:
   ```bash
   sudo nano /etc/systemd/system/pocketportal.service
   ```

   Update these fields:
   - `User=` - Your username
   - `WorkingDirectory=` - Path to your PocketPortal installation
   - `ExecStart=` - Path to your Python executable and main script

3. **Reload systemd and enable the service:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable pocketportal.service
   sudo systemctl start pocketportal.service
   ```

4. **Check status:**
   ```bash
   sudo systemctl status pocketportal.service
   ```

### Management Commands

```bash
# Start service
sudo systemctl start pocketportal.service

# Stop service
sudo systemctl stop pocketportal.service

# Restart service
sudo systemctl restart pocketportal.service

# View logs
sudo journalctl -u pocketportal.service -f

# Disable autostart
sudo systemctl disable pocketportal.service
```

## macOS (launchd)

### Installation

1. **Copy the plist file:**
   ```bash
   cp deployment/macos/com_telegram_agent.plist ~/Library/LaunchAgents/
   ```

2. **Edit the plist file** to match your installation:
   ```bash
   nano ~/Library/LaunchAgents/com_telegram_agent.plist
   ```

   Update these fields:
   - `WorkingDirectory` - Path to your PocketPortal installation
   - `ProgramArguments` - Path to your Python executable and script

3. **Load the service:**
   ```bash
   launchctl load ~/Library/LaunchAgents/com_telegram_agent.plist
   ```

4. **Check status:**
   ```bash
   launchctl list | grep telegram
   ```

### Management Commands

```bash
# Load service
launchctl load ~/Library/LaunchAgents/com_telegram_agent.plist

# Unload service
launchctl unload ~/Library/LaunchAgents/com_telegram_agent.plist

# View logs
tail -f ~/Library/Logs/telegram_agent.log
```

## Docker

For containerized deployments, see the main `Dockerfile` in the root directory.

```bash
# Build image
docker build -t pocketportal:latest .

# Run container
docker run -d --name pocketportal \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/data:/app/data \
  pocketportal:latest
```

## Health Checks

PocketPortal includes a built-in health check endpoint that can be used with monitoring tools or orchestration systems.

The `AgentCoreV2.health_check()` method returns:
- Overall status: `healthy`, `degraded`, or `unhealthy`
- Component-level status for:
  - EventBus
  - ExecutionEngine (LLM backends)
  - ModelRegistry
  - ContextManager
  - ToolRegistry

### Example: systemd Health Check

Add to your service file:

```ini
[Service]
# Restart if health check fails
ExecStartPost=/bin/bash -c 'sleep 10 && python3 -c "import asyncio; from pocketportal.core import create_agent_core; asyncio.run(create_agent_core({}).health_check())"'
```

## Logs

### Linux (systemd)
```bash
# Follow logs in real-time
sudo journalctl -u pocketportal.service -f

# View recent logs
sudo journalctl -u pocketportal.service -n 100

# Logs from specific date
sudo journalctl -u pocketportal.service --since "2024-01-01"
```

### macOS (launchd)
```bash
# Standard output
tail -f ~/Library/Logs/telegram_agent.log

# Standard error
tail -f ~/Library/Logs/telegram_agent_error.log
```

## Security Considerations

1. **File Permissions**: Ensure service files are owned by root (Linux) or your user (macOS)
2. **Secrets Management**: Never hardcode API tokens in service files
3. **Environment Variables**: Use `EnvironmentFile=` (systemd) or `EnvironmentVariables` (launchd)
4. **Network Security**: Consider firewall rules if exposing web interface

## Troubleshooting

### Service won't start

1. Check permissions on the working directory
2. Verify Python path is correct
3. Ensure all dependencies are installed
4. Check logs for specific error messages

### Service crashes on boot

1. Verify configuration file exists and is valid
2. Check database file permissions (`data/context.db`)
3. Ensure LLM backend (Ollama) is running
4. Review health check results

### High memory usage

1. Reduce `max_context_messages` in config
2. Enable context summarization
3. Limit concurrent interface connections
4. Monitor with `get_stats()` method

## Additional Resources

- [systemd Documentation](https://www.freedesktop.org/software/systemd/man/systemd.service.html)
- [launchd Documentation](https://www.launchd.info/)
- [PocketPortal Documentation](../docs/)
