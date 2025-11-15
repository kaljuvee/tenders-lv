"""Automated daily sync scheduler for Latvia procurement notices.

This module provides automated scheduling capabilities for daily data synchronization.
It can be run as a standalone scheduler or configured as a cron job.
"""
import schedule
import time
import logging
from datetime import datetime, timedelta
from .ingestion import sync_date, sync_latest_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sync_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def sync_date_range(start_date, end_date):
    """Sync procurement data for a date range.
    
    Args:
        start_date: datetime object for start date
        end_date: datetime object for end date
        
    Returns:
        list: List of sync results for each date
    """
    logger.info(f"Starting bulk sync from {start_date.date()} to {end_date.date()}")
    
    results = []
    current_date = start_date
    
    while current_date <= end_date:
        result = sync_date(current_date)
        results.append(result)
        current_date += timedelta(days=1)
        
        # Small delay to avoid overwhelming the API
        time.sleep(1)
    
    # Summary
    total_processed = sum(r.get('processed', 0) for r in results)
    total_added = sum(r.get('added', 0) for r in results)
    total_updated = sum(r.get('updated', 0) for r in results)
    successful = sum(1 for r in results if r['status'] == 'success')
    
    logger.info("=" * 60)
    logger.info("BULK SYNC SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Date range: {start_date.date()} to {end_date.date()}")
    logger.info(f"Successful syncs: {successful}/{len(results)}")
    logger.info(f"Total processed: {total_processed}")
    logger.info(f"Total added: {total_added}")
    logger.info(f"Total updated: {total_updated}")
    logger.info("=" * 60)
    
    return results


def run_scheduler():
    """Run the automated scheduler that syncs data daily at 2 AM."""
    logger.info("Starting automated sync scheduler")
    logger.info("Scheduled to run daily at 2:00 AM")
    
    # Schedule the sync job
    schedule.every().day.at("02:00").do(sync_latest_data)
    
    # Run once immediately on startup
    logger.info("Running initial sync...")
    sync_latest_data()
    
    # Keep the scheduler running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'once':
            # Run sync once and exit
            sync_latest_data()
            
        elif command == 'backfill':
            # Backfill data for the last N days
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
            end_date = datetime.now() - timedelta(days=1)
            start_date = end_date - timedelta(days=days-1)
            sync_date_range(start_date, end_date)
            
        elif command == 'range':
            # Sync specific date range: python -m utils.scheduler range 2025-11-01 2025-11-15
            if len(sys.argv) < 4:
                print("Usage: python -m utils.scheduler range START_DATE END_DATE")
                print("Example: python -m utils.scheduler range 2025-11-01 2025-11-15")
                sys.exit(1)
            start_date = datetime.strptime(sys.argv[2], '%Y-%m-%d')
            end_date = datetime.strptime(sys.argv[3], '%Y-%m-%d')
            sync_date_range(start_date, end_date)
            
        elif command == 'scheduler':
            # Run continuous scheduler
            run_scheduler()
            
        else:
            print("Unknown command. Available commands:")
            print("  once       - Run sync once and exit")
            print("  backfill N - Backfill last N days (default: 7)")
            print("  range START END - Sync date range (format: YYYY-MM-DD)")
            print("  scheduler  - Run continuous scheduler (daily at 2 AM)")
    else:
        # Default: run once
        sync_latest_data()
