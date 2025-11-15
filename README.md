# Latvia Procurement Monitor (FastHTML)

A FastHTML web application for monitoring and analyzing Latvian public procurement data from the Procurement Monitoring Bureau.

## Overview

This application provides real-time access to Latvia's public procurement notices with advanced search capabilities and analytics. Built with FastHTML for server-rendered hypermedia applications.

## Tech Stack

### Core Framework
- **FastHTML**: Python library combining Starlette, Uvicorn, and HTMX for server-rendered apps
- **Python 3.11+**: Modern Python with type hints
- **SQLAlchemy**: Database ORM for PostgreSQL
- **PostgreSQL**: Relational database (Render hosted)

### Key Features
- Server-side rendering with HTMX for dynamic updates
- Custom CSS matching original design (OKLCH color system)
- PostgreSQL with `tenders_lv` schema
- Daily data synchronization from Latvia's open data API
- Advanced search and filtering
- Analytics dashboard

## Database Schema

### Schema: `tenders_lv`

#### Table: `procurement_notices`
Stores all procurement notice data:
- **Identification**: `id`, `identifier`, `country_code`
- **Procurement Details**: `name`, `description`, `notice_type`, `procedure_type`, `cpv_type`
- **Organization**: `organization_name`, `organization_city`, `organization_identifier`
- **Financial**: `estimated_value`, `currency`
- **Dates**: `public_opening_date`, `deadline_receipt_tenders_date`
- **Contact**: `contact_name`, `contact_email`, `contact_telephone`
- **Links**: `documents_url`, `submission_url`
- **Metadata**: `created_at`, `updated_at`

#### Table: `data_sync_log`
Tracks data synchronization operations:
- `status`, `records_processed`, `records_added`, `records_updated`
- `error_message`, `created_at`

## Installation

### Prerequisites
- Python 3.11 or higher
- PostgreSQL database access

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/kaljuvee/tenders-lv.git
   cd tenders-lv
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variable** (optional, default is included)
   ```bash
   export DB_URL="postgresql://indurent_db_user:mORTX4lmewn7ZJsMiU7Ox7Qb8gnxPRgf@dpg-d40gneur433s738clpeg-a.frankfurt-postgres.render.com/indurent_db"
   ```

4. **Initialize database**
   ```python
   python -c "from database import init_db; init_db()"
   ```

5. **Run data ingestion**
   ```bash
   python ingest_data.py
   ```

6. **Start the application**
   ```bash
   python main.py
   ```

7. **Access the app**
   Open your browser to `http://localhost:5001`

## Usage

### Pages

1. **Home** (`/`): Overview with sync status and feature highlights
2. **Browse Procurements** (`/procurements`): Search and filter procurement notices
3. **Procurement Detail** (`/procurement/{id}`): Complete information for a single notice
4. **Analytics** (`/analytics`): Statistics and trends

### Data Ingestion

Run the ingestion script manually:
```bash
python ingest_data.py
```

The script fetches yesterday's data (since today's file may not be published yet) and:
- Inserts new procurement notices
- Updates existing notices
- Logs synchronization results

### Automated Sync

Set up a cron job for daily synchronization:
```bash
0 2 * * * cd /path/to/tenders-lv && python ingest_data.py
```

## Project Structure

```
tenders-lv/
├── main.py              # FastHTML application with routes and views
├── database.py          # SQLAlchemy models and database connection
├── ingest_data.py       # Data synchronization script
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## FastHTML Features Used

- **Server-side rendering**: All HTML generated on the server
- **FastTags (FT)**: Python functions that map directly to HTML elements
- **Custom CSS**: Inline styles matching original design
- **No JavaScript frameworks**: Pure HTML with HTMX for interactivity
- **Type-safe routing**: Function parameters become query parameters

## Data Source

- **Provider**: Latvia's Procurement Monitoring Bureau (Iepirkumu uzraudzības birojs)
- **API**: `https://open.iub.gov.lv/data/notice/{year}/{month}/{day}-{month}-{year}.json`
- **Format**: JSON files published daily
- **License**: Public domain (open data)

## Development

### Adding New Routes

```python
@rt('/new-route')
def new_route(param: str = ''):
    return Title("Page Title"), get_header(), Main(
        Div(
            H1("Content"),
            P(f"Parameter: {param}"),
            cls="container"
        )
    ), get_footer()
```

### Database Queries

```python
from database import SessionLocal, ProcurementNotice

db = SessionLocal()
try:
    notices = db.query(ProcurementNotice).filter(
        ProcurementNotice.country_code == 'LV'
    ).all()
finally:
    db.close()
```

## Deployment

### Render.com (Recommended)

1. Create a new Web Service
2. Connect your GitHub repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `python main.py`
5. Add environment variable `DB_URL` with your PostgreSQL connection string

### Railway

1. Create new project from GitHub
2. Add PostgreSQL database
3. Set start command: `python main.py`
4. Deploy

## Future Enhancements

- Real-time updates with HTMX polling
- CSV export functionality
- Email notifications for saved searches
- Interactive charts with Alpine.js
- Multi-country support
- Full-text search with PostgreSQL

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License

## Acknowledgments

- Data from Latvia's Procurement Monitoring Bureau
- Built with FastHTML by fast.ai
- Hosted on Render.com

---

**Note**: This is an independent project using publicly available open data. Not officially affiliated with Latvia's Procurement Monitoring Bureau.
