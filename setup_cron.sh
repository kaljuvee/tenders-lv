#!/bin/bash
# Setup cron job for automated daily sync

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON_PATH="$SCRIPT_DIR/venv/bin/python3"
SYNC_SCRIPT="$SCRIPT_DIR/sync_scheduler.py"

echo "Setting up automated daily sync..."
echo "Script directory: $SCRIPT_DIR"

# Create cron job entry
CRON_JOB="0 2 * * * cd $SCRIPT_DIR && $PYTHON_PATH $SYNC_SCRIPT once >> $SCRIPT_DIR/sync_cron.log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "$SYNC_SCRIPT"; then
    echo "⚠️  Cron job already exists. Removing old entry..."
    crontab -l 2>/dev/null | grep -v "$SYNC_SCRIPT" | crontab -
fi

# Add new cron job
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo "✅ Cron job installed successfully!"
echo ""
echo "The sync will run daily at 2:00 AM"
echo "Logs will be written to: $SCRIPT_DIR/sync_cron.log"
echo ""
echo "To view current cron jobs:"
echo "  crontab -l"
echo ""
echo "To remove the cron job:"
echo "  crontab -e  (then delete the line containing sync_scheduler.py)"
echo ""
echo "To test the sync manually:"
echo "  cd $SCRIPT_DIR && $PYTHON_PATH $SYNC_SCRIPT once"
