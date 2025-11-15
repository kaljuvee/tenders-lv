"""Main FastHTML application for Latvia Procurement Monitor.

This is the entry point for the web application. It initializes the FastHTML app,
registers routes, and starts the server.
"""
from fasthtml.common import *
from utils.database import init_db
from routes.home import register_home_routes
from routes.procurements import register_procurement_routes
from routes.analytics import register_analytics_routes

# Initialize database
init_db()

# Create FastHTML app with custom CSS
app, rt = fast_app(
    hdrs=(
        Link(rel='stylesheet', href='https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap'),
        Link(rel='stylesheet', href='/static/styles.css'),
    ),
    pico=False
)

# Serve static files
@rt('/static/{fname:path}')
async def static(fname: str):
    """Serve static files from the static directory."""
    return FileResponse(f'static/{fname}')

# Register all routes
register_home_routes(rt)
register_procurement_routes(rt)
register_analytics_routes(rt)

# Run the app
if __name__ == '__main__':
    serve(port=5001)
