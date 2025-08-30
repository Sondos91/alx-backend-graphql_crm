# CRM Celery Tasks and Celery Beat Setup

This document provides comprehensive setup and usage instructions for the Celery task system in the ALX Backend GraphQL CRM project.

## Overview

The CRM system now includes Celery for asynchronous task processing and Celery Beat for scheduled task execution. This setup works alongside the existing django-crontab system.

## Features

- **Weekly CRM Reports**: Automatically generated every Monday at 6:00 AM
- **GraphQL Integration**: Uses GraphQL queries to fetch CRM data
- **Comprehensive Logging**: All reports logged to `/tmp/crm_report_log.txt`
- **Redis Backend**: Fast and reliable message broker
- **Scheduled Execution**: Celery Beat handles task scheduling

## Prerequisites

### 1. Install Redis

#### macOS (using Homebrew):
```bash
brew install redis
brew services start redis
```

#### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

#### Windows:
Download and install Redis from [https://redis.io/download](https://redis.io/download)

### 2. Verify Redis Installation
```bash
redis-cli ping
# Should return: PONG
```

### 3. Install Python Dependencies
```bash
pip3 install -r requirements.txt
```

## Setup Instructions

### 1. Run Django Migrations
```bash
python3 manage.py migrate
```

### 2. Start Celery Worker
```bash
# Start the Celery worker in a new terminal
celery -A crm worker -l info
```

### 3. Start Celery Beat
```bash
# Start Celery Beat scheduler in another terminal
celery -A crm beat -l info
```

### 4. Verify Setup
Check that both processes are running:
```bash
# Check Celery worker
ps aux | grep "celery.*worker"

# Check Celery Beat
ps aux | grep "celery.*beat"
```

## Configuration

### Celery Settings (alx_backend_graphql/settings.py)
```python
# Celery Configuration
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# Celery Beat Schedule
CELERY_BEAT_SCHEDULE = {
    'generate-crm-report': {
        'task': 'crm.tasks.generate_crm_report',
        'schedule': crontab(day_of_week='mon', hour=6, minute=0),
    },
}
```

### Task Schedule
- **CRM Report Generation**: Every Monday at 6:00 AM
- **Format**: `crontab(day_of_week='mon', hour=6, minute=0)`

## Available Tasks

### 1. generate_crm_report
- **Purpose**: Generates weekly CRM summary report
- **Schedule**: Every Monday at 6:00 AM
- **Output**: Logs to `/tmp/crm_report_log.txt`
- **Data Collected**:
  - Total number of customers
  - Total number of orders
  - Total revenue from all orders

## Manual Task Execution

### Test the CRM Report Task
```bash
# Start Django shell
python3 manage.py shell

# Import and execute the task
from crm.tasks import generate_crm_report
result = generate_crm_report.delay()
print(f"Task ID: {result.id}")

# Check task status
print(f"Task ready: {result.ready()}")
print(f"Task result: {result.get()}")
```

### Execute Task Synchronously
```bash
python3 manage.py shell -c "from crm.tasks import generate_crm_report; result = generate_crm_report(); print(result)"
```

## Monitoring and Logs

### 1. Task Logs
- **Location**: `/tmp/crm_report_log.txt`
- **Format**: `YYYY-MM-DD HH:MM:SS - Report: X customers, Y orders, $Z revenue`
- **Example**:
```
2025-08-30 10:50:00 - Report: 7 customers, 1 orders, $199.99 revenue
------------------------------------------------------------
```

### 2. Celery Worker Logs
- **Level**: Info (`-l info`)
- **Output**: Terminal where worker is running
- **Shows**: Task execution, success/failure, timing

### 3. Celery Beat Logs
- **Level**: Info (`-l info`)
- **Output**: Terminal where beat is running
- **Shows**: Task scheduling, execution triggers

## Troubleshooting

### Common Issues

#### 1. Redis Connection Error
```
Error: Connection refused to Redis
```
**Solution**: Ensure Redis is running
```bash
brew services start redis  # macOS
sudo systemctl start redis-server  # Linux
```

#### 2. Task Not Executing
```
Task scheduled but not running
```
**Solution**: Check both worker and beat are running
```bash
# Terminal 1: Start worker
celery -A crm worker -l info

# Terminal 2: Start beat
celery -A crm beat -l info
```

#### 3. GraphQL Connection Error
```
Error: Cannot connect to GraphQL endpoint
```
**Solution**: Ensure Django server is running
```bash
python3 manage.py runserver
```

#### 4. Import Errors
```
ModuleNotFoundError: No module named 'celery'
```
**Solution**: Install dependencies
```bash
pip3 install -r requirements.txt
```

### Debug Mode
For detailed debugging, increase log levels:
```bash
# Worker with debug logging
celery -A crm worker -l debug

# Beat with debug logging
celery -A crm beat -l debug
```

## Performance Optimization

### 1. Worker Processes
```bash
# Use multiple worker processes
celery -A crm worker -l info --concurrency=4
```

### 2. Redis Persistence
```bash
# Enable Redis persistence (in redis.conf)
save 900 1
save 300 10
save 60 10000
```

### 3. Task Timeout
```bash
# Set task timeout in settings.py
CELERY_TASK_SOFT_TIME_LIMIT = 300  # 5 minutes
CELERY_TASK_TIME_LIMIT = 600       # 10 minutes
```

## Integration with Existing System

### Coexistence with django-crontab
- **django-crontab**: Handles system-level cron jobs (heartbeat, stock updates)
- **Celery Beat**: Handles application-level scheduled tasks (CRM reports)
- **No Conflicts**: Both systems work independently

### Current Cron Jobs
1. **Heartbeat Logger**: Every 5 minutes (`*/5 * * * *`)
2. **Stock Update**: Every 12 hours (`0 */12 * * *`)
3. **CRM Report**: Every Monday at 6:00 AM (Celery Beat)

## Production Deployment

### 1. Supervisor Configuration
```ini
[program:crm_celery_worker]
command=celery -A crm worker -l info
directory=/path/to/your/project
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/celery/worker.log

[program:crm_celery_beat]
command=celery -A crm beat -l info
directory=/path/to/your/project
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/celery/beat.log
```

### 2. Systemd Services
Create systemd service files for automatic startup on boot.

### 3. Monitoring
- Use Flower for Celery monitoring: `pip install flower`
- Monitor Redis memory usage
- Set up log rotation for `/tmp/crm_report_log.txt`

## Support and Maintenance

### Regular Tasks
1. **Monitor Redis memory usage**
2. **Check log file sizes**
3. **Verify task execution schedules**
4. **Update dependencies regularly**

### Backup and Recovery
- Backup Redis data directory
- Monitor `/tmp/crm_report_log.txt` for errors
- Keep Celery worker and beat logs

## Conclusion

The Celery integration provides a robust, scalable solution for scheduled CRM report generation while maintaining compatibility with the existing django-crontab system. The setup ensures reliable task execution, comprehensive logging, and easy monitoring.

For additional support or questions, refer to the main project README or the Celery documentation.
