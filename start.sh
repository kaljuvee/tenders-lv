#!/bin/bash
# Startup script for Latvia Procurement Monitor (FastHTML)

echo "🚀 Starting Latvia Procurement Monitor..."

# Activate virtual environment
source venv/bin/activate

# Check if database is initialized
python3 -c "from database import SessionLocal, ProcurementNotice; db = SessionLocal(); count = db.query(ProcurementNotice).count(); print(f'✅ Database connected: {count} procurement notices'); db.close()"

# Start the FastHTML application
echo "🌐 Starting web server on http://localhost:5001"
python3 main.py
