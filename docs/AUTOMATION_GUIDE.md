# Automated Sync Setup Guide

This guide explains how to set up automated daily synchronization of Latvia procurement data.

## Overview

The `sync_scheduler.py` script provides multiple ways to automate data synchronization:

1. **Cron Job** - Traditional Unix cron scheduling (recommended for servers)
2. **Systemd Service** - Continuous background process (recommended for production)
3. **Manual Execution** - Run on-demand for testing or backfilling

## Quick Start

### Option 1: Cron Job (Simplest)

Run the automated setup script:

```bash
cd /home/ubuntu/tenders-lv
chmod +x setup_cron.sh
./setup_cron.sh
```

This will:
- Create a cron job that runs daily at 2:00 AM
- Log all sync operations to `sync_cron.log`
- Automatically retry if data is not available

**Verify installation:**
```bash
crontab -l
```

You should see:
```
0 2 * * * cd /home/ubuntu/tenders-lv && /home/ubuntu/tenders-lv/venv/bin/python3 /home/ubuntu/tenders-lv/sync_scheduler.py once >> /home/ubuntu/tenders-lv/sync_cron.log 2>&1
```

### Option 2: Systemd Service (Production)

For production environments, use systemd for better process management:

```bash
# Copy service file to systemd directory
sudo cp tenders-sync.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable tenders-sync

# Start the service
sudo systemctl start tenders-sync

# Check status
sudo systemctl status tenders-sync
```

**View logs:**
```bash
# Live log viewing
sudo journalctl -u tenders-sync -f

# Or check the log file
tail -f /home/ubuntu/tenders-lv/sync_service.log
```

**Service management:**
```bash
# Stop the service
sudo systemctl stop tenders-sync

# Restart the service
sudo systemctl restart tenders-sync

# Disable auto-start on boot
sudo systemctl disable tenders-sync
```

## Manual Sync Commands

### Run Once
Execute a single sync and exit:
```bash
cd /home/ubuntu/tenders-lv
source venv/bin/activate
python3 sync_scheduler.py once
```

### Backfill Historical Data
Sync the last N days of data:
```bash
# Backfill last 7 days
python3 sync_scheduler.py backfill 7

# Backfill last 30 days
python3 sync_scheduler.py backfill 30
```

### Sync Specific Date Range
Sync data for a specific period:
```bash
python3 sync_scheduler.py range 2025-11-01 2025-11-15
```

### Run Continuous Scheduler
Run the scheduler in the foreground (useful for testing):
```bash
python3 sync_scheduler.py scheduler
```

## Sync Logic

The scheduler implements intelligent fallback logic:

1. **Primary**: Attempts to fetch yesterday's data (since today's file may not be published yet)
2. **Fallback**: If yesterday's data is unavailable (404), tries 2 days ago
3. **Logging**: All operations are logged with timestamps and results
4. **Error Handling**: Failures are logged but don't stop future sync attempts

## Monitoring

### Check Sync Status in Database

```python
from database import SessionLocal, DataSyncLog
from sqlalchemy import desc

db = SessionLocal()
recent_syncs = db.query(DataSyncLog).order_by(desc(DataSyncLog.created_at)).limit(10).all()

for sync in recent_syncs:
    print(f"{sync.created_at}: {sync.status} - {sync.records_added} added, {sync.records_updated} updated")
```

### View Logs

**Cron logs:**
```bash
tail -f /home/ubuntu/tenders-lv/sync_cron.log
```

**Systemd logs:**
```bash
sudo journalctl -u tenders-sync -n 100
```

**Application logs:**
```bash
tail -f /home/ubuntu/tenders-lv/sync_scheduler.log
```

## Troubleshooting

### Cron Job Not Running

**Check if cron service is running:**
```bash
sudo systemctl status cron
```

**Check cron logs:**
```bash
grep CRON /var/log/syslog
```

**Verify cron job syntax:**
```bash
crontab -l
```

**Test the command manually:**
```bash
cd /home/ubuntu/tenders-lv && /home/ubuntu/tenders-lv/venv/bin/python3 /home/ubuntu/tenders-lv/sync_scheduler.py once
```

### Systemd Service Fails

**Check service status:**
```bash
sudo systemctl status tenders-sync
```

**View detailed logs:**
```bash
sudo journalctl -u tenders-sync -n 50 --no-pager
```

**Check file permissions:**
```bash
ls -la /home/ubuntu/tenders-lv/sync_scheduler.py
ls -la /home/ubuntu/tenders-lv/venv/bin/python3
```

**Verify database connection:**
```bash
cd /home/ubuntu/tenders-lv
source venv/bin/activate
python3 -c "from database import SessionLocal; db = SessionLocal(); print('✅ Database connected')"
```

### No Data Available (404 Errors)

This is normal! The Latvia open data API publishes files with a delay. The scheduler automatically:
- Tries yesterday's data first
- Falls back to 2 days ago if yesterday is unavailable
- Logs the attempt and continues

**Manual check:**
```bash
# Check if yesterday's file exists
curl -I "https://open.iub.gov.lv/data/notice/2025/11/14-11-2025.json"
```

### Database Connection Errors

**Verify database URL:**
```bash
cd /home/ubuntu/tenders-lv
source venv/bin/activate
python3 -c "from database import DATABASE_URL; print(DATABASE_URL)"
```

**Test connection:**
```bash
python3 -c "from database import engine; conn = engine.connect(); print('✅ Connected'); conn.close()"
```

## Performance Considerations

### Sync Duration
- Single day: ~5-10 seconds (depending on record count)
- 7-day backfill: ~1 minute
- 30-day backfill: ~5 minutes

### Database Impact
- Uses upsert logic (insert new, update existing)
- Minimal impact on database performance
- Runs during low-traffic hours (2 AM)

### API Rate Limiting
- The script includes 1-second delays between requests during backfills
- No rate limiting observed from Latvia API
- Respectful usage pattern

## Best Practices

1. **Monitor regularly**: Check logs weekly to ensure syncs are successful
2. **Backfill after downtime**: If the service is down for multiple days, run a backfill
3. **Keep logs**: Rotate log files monthly to prevent disk space issues
4. **Test before production**: Run manual syncs to verify everything works
5. **Database backups**: Regular backups of PostgreSQL database

## Log Rotation

Create a logrotate configuration to prevent log files from growing too large:

```bash
sudo nano /etc/logrotate.d/tenders-sync
```

Add:
```
/home/ubuntu/tenders-lv/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    missingok
    create 0644 ubuntu ubuntu
}
```

## Deployment Checklist

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Test database connection
- [ ] Run initial sync: `python3 sync_scheduler.py once`
- [ ] Set up cron job OR systemd service
- [ ] Verify automated sync runs successfully
- [ ] Configure log rotation
- [ ] Set up monitoring/alerts (optional)
- [ ] Document any environment-specific settings

## Support

For issues or questions:
1. Check the logs first
2. Verify database connectivity
3. Test manual sync
4. Review this guide
5. Check GitHub issues: https://github.com/kaljuvee/tenders-lv/issues

---

**Last Updated**: 2025-11-15  
**Version**: 1.0
