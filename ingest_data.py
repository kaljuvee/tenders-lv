"""Data ingestion script for Latvia procurement notices."""
import requests
from datetime import datetime, timedelta
from database import SessionLocal, ProcurementNotice, DataSyncLog
from sqlalchemy import func

def fetch_procurement_data(date_str):
    """Fetch procurement data from Latvia open data API.
    
    Args:
        date_str: Date string in format YYYY/MM/DD-MM-YYYY
    
    Returns:
        List of procurement notices or None if error
    """
    url = f"https://open.iub.gov.lv/data/notice/{date_str}.json"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def parse_datetime(date_str):
    """Parse datetime string from API."""
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except:
        return None

def ingest_notice(db, notice_data):
    """Ingest a single procurement notice into database."""
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

def sync_latest_data():
    """Sync latest procurement data from API."""
    db = SessionLocal()
    
    # Use yesterday's date since today's file may not be available yet
    yesterday = datetime.now() - timedelta(days=1)
    day = yesterday.strftime('%d')
    month = yesterday.strftime('%m')
    year = yesterday.strftime('%Y')
    date_str = f"{year}/{month}/{day}-{month}-{year}"
    
    print(f"Fetching data for {date_str}...")
    
    # Create sync log entry
    sync_log = DataSyncLog(status='in_progress')
    db.add(sync_log)
    db.commit()
    
    try:
        data = fetch_procurement_data(date_str)
        
        if data is None:
            sync_log.status = 'failed'
            sync_log.error_message = 'Failed to fetch data from API'
            db.commit()
            return
        
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
                print(f"Error processing notice: {e}")
                continue
        
        db.commit()
        
        # Update sync log
        sync_log.status = 'success'
        sync_log.records_processed = records_processed
        sync_log.records_added = records_added
        sync_log.records_updated = records_updated
        db.commit()
        
        print(f"✅ Sync completed: {records_processed} processed, {records_added} added, {records_updated} updated")
        
    except Exception as e:
        sync_log.status = 'failed'
        sync_log.error_message = str(e)
        db.commit()
        print(f"❌ Sync failed: {e}")
    finally:
        db.close()

if __name__ == '__main__':
    sync_latest_data()
