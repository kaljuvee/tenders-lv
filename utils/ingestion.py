"""Data ingestion utilities for Latvia procurement notices."""
import requests
import logging
from datetime import datetime, timedelta
from .database import SessionLocal, ProcurementNotice, DataSyncLog

logger = logging.getLogger(__name__)


def fetch_procurement_data(date_str):
    """Fetch procurement data from Latvia open data API.
    
    Args:
        date_str: Date string in format YYYY/MM/DD-MM-YYYY
    
    Returns:
        List of procurement notices or None if error
    """
    url = f"https://open.iub.gov.lv/data/notice/{date_str}.json"
    try:
        logger.info(f"Fetching data from: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        logger.info(f"Successfully fetched {len(data)} records")
        return data
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            logger.warning(f"No data available for {date_str} (404)")
        else:
            logger.error(f"HTTP error fetching data: {e}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data: {e}")
        return None


def parse_datetime(date_str):
    """Parse datetime string from API."""
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except Exception as e:
        logger.debug(f"Error parsing datetime '{date_str}': {e}")
        return None


def ingest_notice(db, notice_data):
    """Ingest a single procurement notice into database.
    
    Args:
        db: Database session
        notice_data: Dictionary containing notice data
    
    Returns:
        tuple: (was_added, was_updated)
    """
    identifier = notice_data.get('identifier')
    if not identifier:
        return False, False
    
    # Check if notice already exists
    existing = db.query(ProcurementNotice).filter(
        ProcurementNotice.identifier == identifier
    ).first()
    
    notice_dict = {
        'identifier': identifier,
        'country_code': 'LV',
        'name': notice_data.get('name'),
        'description': notice_data.get('description'),
        'notice_type': notice_data.get('noticeType'),
        'procedure_type': notice_data.get('procedureType'),
        'main_nature_type': notice_data.get('mainNatureType'),
        'cpv_type': notice_data.get('cpvType'),
        'estimated_value': str(notice_data.get('estimatedValue', '')),
        'currency': notice_data.get('currency'),
        'organization_name': notice_data.get('organizationName'),
        'organization_city': notice_data.get('organizationCity'),
        'organization_identifier': notice_data.get('organizationIdentifier'),
        'contact_name': notice_data.get('contactName'),
        'contact_email': notice_data.get('contactEmail'),
        'contact_telephone': notice_data.get('contactTelephone'),
        'public_opening_date': parse_datetime(notice_data.get('publicOpeningDate')),
        'deadline_receipt_tenders_date': parse_datetime(notice_data.get('deadlineReceiptTendersDate')),
        'documents_url': notice_data.get('documentsURL'),
        'submission_url': notice_data.get('submissionURL'),
    }
    
    if existing:
        # Update existing record
        for key, value in notice_dict.items():
            setattr(existing, key, value)
        existing.updated_at = datetime.utcnow()
        return False, True  # Not added, but updated
    else:
        # Create new record
        new_notice = ProcurementNotice(**notice_dict)
        db.add(new_notice)
        return True, False  # Added, not updated


def sync_date(target_date):
    """Sync procurement data for a specific date.
    
    Args:
        target_date: datetime object for the date to sync
        
    Returns:
        dict: Sync results with status and counts
    """
    db = SessionLocal()
    
    day = target_date.strftime('%d')
    month = target_date.strftime('%m')
    year = target_date.strftime('%Y')
    date_str = f"{year}/{month}/{day}-{month}-{year}"
    
    logger.info(f"Starting sync for {date_str}")
    
    # Create sync log entry
    sync_log = DataSyncLog(status='in_progress')
    db.add(sync_log)
    db.commit()
    
    try:
        data = fetch_procurement_data(date_str)
        
        if data is None:
            sync_log.status = 'failed'
            sync_log.error_message = f'No data available for {date_str}'
            db.commit()
            db.close()
            return {
                'status': 'failed',
                'date': date_str,
                'error': 'No data available'
            }
        
        records_added = 0
        records_updated = 0
        records_processed = len(data)
        
        for notice_data in data:
            try:
                added, updated = ingest_notice(db, notice_data)
                if added:
                    records_added += 1
                elif updated:
                    records_updated += 1
            except Exception as e:
                logger.error(f"Error processing notice: {e}")
                continue
        
        db.commit()
        
        # Update sync log
        sync_log.status = 'success'
        sync_log.records_processed = records_processed
        sync_log.records_added = records_added
        sync_log.records_updated = records_updated
        db.commit()
        
        logger.info(f"✅ Sync completed for {date_str}: {records_processed} processed, {records_added} added, {records_updated} updated")
        
        return {
            'status': 'success',
            'date': date_str,
            'processed': records_processed,
            'added': records_added,
            'updated': records_updated
        }
        
    except Exception as e:
        sync_log.status = 'failed'
        sync_log.error_message = str(e)
        db.commit()
        logger.error(f"❌ Sync failed for {date_str}: {e}")
        return {
            'status': 'failed',
            'date': date_str,
            'error': str(e)
        }
    finally:
        db.close()


def sync_latest_data():
    """Sync latest available procurement data.
    
    Tries yesterday's data first (since today's file may not be published yet),
    then falls back to 2 days ago if yesterday's data is not available.
    
    Returns:
        dict: Sync results
    """
    logger.info("=" * 60)
    logger.info("Starting automated daily sync")
    logger.info("=" * 60)
    
    # Try yesterday first
    yesterday = datetime.now() - timedelta(days=1)
    result = sync_date(yesterday)
    
    if result['status'] == 'failed' and 'No data available' in result.get('error', ''):
        logger.info("Yesterday's data not available, trying 2 days ago...")
        two_days_ago = datetime.now() - timedelta(days=2)
        result = sync_date(two_days_ago)
    
    logger.info("=" * 60)
    logger.info(f"Sync completed with status: {result['status']}")
    logger.info("=" * 60)
    
    return result
