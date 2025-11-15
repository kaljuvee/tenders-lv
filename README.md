# Latvia Procurement Monitor

A FastHTML web application for monitoring Latvian public procurement using data from the Procurement Monitoring Bureau's open data API.

## Features

- **Daily Data Sync**: Automated synchronization with Latvia's official procurement data
- **Advanced Search**: Filter by organization, notice type, CPV codes, and more
- **Analytics Dashboard**: Insights into procurement trends and top contracting authorities
- **Responsive Design**: Clean, modern interface with OKLCH color system
- **Server-Side Rendering**: Fast initial page loads and excellent SEO

## Tech Stack

- **Framework**: [FastHTML](https://fastht.ml/) - Python library for building web applications
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Data Source**: [Latvia Procurement Monitoring Bureau Open Data API](https://www.iub.gov.lv/en/open-data)
- **Styling**: Custom CSS with OKLCH colors (matching original React design)

## Project Structure

```
tenders-lv/
├── app.py                  # Main application entry point
├── sync.py                 # CLI for data synchronization
├── requirements.txt        # Python dependencies
├── README.md              # This file
│
├── utils/                 # Utility modules
│   ├── __init__.py       # Package exports
│   ├── database.py       # Database models and connection
│   ├── ingestion.py      # Data fetching and processing
│   └── scheduler.py      # Automated sync scheduling
│
├── routes/                # Route handlers
│   ├── __init__.py       # Common components (header, footer)
│   ├── home.py           # Home page route
│   ├── procurements.py   # Procurement list and detail routes
│   └── analytics.py      # Analytics dashboard route
│
├── static/                # Static assets
│   └── styles.css        # Custom CSS (OKLCH color system)
│
├── docs/                  # Documentation
│   ├── AUTOMATION_GUIDE.md        # Sync automation setup
│   ├── AUTOMATION_SUMMARY.md      # Quick reference
│   ├── FASTHTML_MIGRATION.md      # Migration from React
│   └── PERFORMANCE_COMPARISON.md  # React vs FastHTML analysis
│
├── setup_cron.sh          # Automated cron job setup
└── tenders-sync.service   # Systemd service configuration
```

## FastHTML Project Structure Best Practices

### Directory Organization

**1. Application Entry Point (`app.py` or `main.py`)**
- Keep it minimal - only app initialization and route registration
- Import route handlers from separate modules
- Configure static file serving
- Set up middleware and error handlers

**2. Utils Directory (`utils/`)**
- Database models and connection management
- Data processing and business logic
- External API integrations
- Scheduled tasks and background jobs
- Helper functions and utilities

**3. Routes Directory (`routes/`)**
- One file per logical section (home, auth, admin, etc.)
- Each file exports a `register_*_routes(rt)` function
- Keep route handlers focused on HTTP concerns
- Delegate business logic to utils

**4. Static Directory (`static/`)**
- CSS files
- JavaScript (if needed)
- Images and media
- Fonts
- Other static assets

**5. Templates (if using separate HTML)**
- For complex applications, consider `templates/` directory
- FastHTML works well with inline templates, but separate files can improve organization

**6. Docs Directory (`docs/`)**
- API documentation
- Setup guides
- Architecture decisions
- Migration notes

### Code Organization Principles

**Separation of Concerns**
```python
# ✅ Good: Separate database, logic, and routes
# utils/database.py
class User(Base):
    __tablename__ = 'users'
    ...

# utils/auth.py
def authenticate_user(email, password):
    ...

# routes/auth.py
def register_auth_routes(rt):
    @rt('/login')
    def login(email: str, password: str):
        user = authenticate_user(email, password)
        ...
```

**Route Registration Pattern**
```python
# routes/feature.py
def register_feature_routes(rt):
    @rt('/feature')
    def feature_list():
        ...
    
    @rt('/feature/{id}')
    def feature_detail(id: int):
        ...

# app.py
from routes.feature import register_feature_routes
app, rt = fast_app()
register_feature_routes(rt)
```

**Reusable Components**
```python
# routes/__init__.py
def get_header(active=''):
    return Header(...)

def get_footer():
    return Footer(...)

# Use in route handlers
from . import get_header, get_footer
```

### File Naming Conventions

- **Modules**: `snake_case.py` (e.g., `user_management.py`)
- **Classes**: `PascalCase` (e.g., `UserAccount`)
- **Functions**: `snake_case` (e.g., `get_user_by_id`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_PAGE_SIZE`)

### Import Organization

```python
# 1. Standard library
import os
from datetime import datetime

# 2. Third-party packages
from fasthtml.common import *
from sqlalchemy import func

# 3. Local modules
from utils.database import SessionLocal
from utils.helpers import format_date
```

## Installation

### Prerequisites

- Python 3.11+
- PostgreSQL database
- Virtual environment (recommended)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/kaljuvee/tenders-lv.git
   cd tenders-lv
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure database**
   
   The database URL is configured in `utils/database.py`. You can override it with an environment variable:
   ```bash
   export DB_URL="postgresql://user:password@host/database"
   ```

5. **Initialize database**
   ```bash
   python3 -c "from utils.database import init_db; init_db()"
   ```

6. **Run initial data sync**
   ```bash
   python3 sync.py once
   ```

7. **Start the application**
   ```bash
   python3 app.py
   ```

8. **Access the application**
   
   Open your browser to `http://localhost:5001`

## Data Synchronization

### Manual Sync

```bash
# Sync latest data (yesterday or 2 days ago)
python3 sync.py once

# Backfill last 7 days
python3 sync.py backfill 7

# Sync specific date range
python3 sync.py range 2025-11-01 2025-11-15
```

### Automated Sync

**Option 1: Cron Job (Recommended for servers)**
```bash
./setup_cron.sh
```

**Option 2: Systemd Service (Recommended for production)**
```bash
sudo cp tenders-sync.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable tenders-sync
sudo systemctl start tenders-sync
```

See [docs/AUTOMATION_GUIDE.md](docs/AUTOMATION_GUIDE.md) for detailed setup instructions.

## Development

### Running in Development Mode

FastHTML supports hot reload:
```bash
python3 app.py
```

### Project Structure Guidelines

1. **Keep `app.py` minimal** - Only app initialization and route registration
2. **Business logic in `utils/`** - Database operations, data processing, external APIs
3. **Route handlers in `routes/`** - HTTP request/response handling
4. **Static assets in `static/`** - CSS, JS, images
5. **Documentation in `docs/`** - Guides, API docs, architecture notes

### Adding New Features

1. **Create database model** in `utils/database.py`
2. **Add business logic** in appropriate `utils/*.py` file
3. **Create route handler** in `routes/feature.py`
4. **Register routes** in `app.py`
5. **Add styles** to `static/styles.css` if needed

Example:
```python
# utils/database.py
class NewFeature(Base):
    __tablename__ = 'new_features'
    ...

# utils/feature_logic.py
def process_feature(data):
    ...

# routes/feature.py
def register_feature_routes(rt):
    @rt('/feature')
    def feature_page():
        ...

# app.py
from routes.feature import register_feature_routes
register_feature_routes(rt)
```

## Deployment

### Docker (Recommended)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5001
CMD ["python3", "app.py"]
```

### Traditional Hosting

1. Set up Python 3.11+ environment
2. Install dependencies: `pip install -r requirements.txt`
3. Configure database connection
4. Set up automated sync (cron or systemd)
5. Run with process manager (systemd, supervisor, or PM2)

### Environment Variables

- `DB_URL`: PostgreSQL connection string (optional, defaults to Render database)
- `PORT`: Server port (default: 5001)

## Documentation

- [Automation Guide](docs/AUTOMATION_GUIDE.md) - Detailed sync automation setup
- [Automation Summary](docs/AUTOMATION_SUMMARY.md) - Quick reference for automation
- [FastHTML Migration](docs/FASTHTML_MIGRATION.md) - Migration notes from React/TypeScript
- [Performance Comparison](docs/PERFORMANCE_COMPARISON.md) - React vs FastHTML analysis

## Performance

- **Initial Page Load**: 200-400ms (vs 1500-2500ms for React version)
- **Data Transfer**: 33 KB (vs 390 KB for React version)
- **Memory Usage**: 70-110 MB total (vs 270-430 MB for React version)
- **Concurrent Users**: ~1000 per instance (vs ~500 for React version)

See [docs/PERFORMANCE_COMPARISON.md](docs/PERFORMANCE_COMPARISON.md) for detailed metrics.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Data provided by [Latvia Procurement Monitoring Bureau](https://www.iub.gov.lv/en/)
- Built with [FastHTML](https://fastht.ml/) by Answer.AI
- Inspired by the need for transparent public procurement monitoring

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/kaljuvee/tenders-lv/issues
- Documentation: See `docs/` directory

---

**Last Updated**: 2025-11-15  
**Version**: 2.0.0 (Refactored with modular structure)
