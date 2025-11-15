"""Home page route."""
from fasthtml.common import *
from sqlalchemy import desc
from utils.database import SessionLocal, DataSyncLog
from . import get_header, get_footer


def register_home_routes(rt):
    """Register home page routes.
    
    Args:
        rt: FastHTML route decorator
    """
    
    @rt('/')
    def index():
        """Home page."""
        db = SessionLocal()
        try:
            # Get latest sync status
            sync_status = db.query(DataSyncLog).order_by(desc(DataSyncLog.created_at)).first()
            
            return Title("Latvia Procurement Monitor"), get_header('home'), Main(
                Div(
                    Div(
                        H1("Monitor Latvian Public Procurement"),
                        P("Access and track public procurement notices from Latvia's Procurement Monitoring Bureau. Search through thousands of procurement opportunities updated daily."),
                        Div(
                            A("Browse Procurements", href="/procurements", cls="btn btn-primary"),
                            A("View Analytics", href="/analytics", cls="btn btn-outline"),
                            style="display: flex; gap: 1rem; justify-content: center; margin-top: 2rem;"
                        ),
                        cls="hero"
                    ),
                    
                    Div(
                        Div(
                            Div(
                                H3("📄 Daily Updates"),
                                P("Procurement notices are synchronized daily from the official open data service"),
                                cls="card"
                            ),
                            Div(
                                H3("🔍 Advanced Search"),
                                P("Filter by organization, notice type, date range, and CPV codes to find relevant opportunities"),
                                cls="card"
                            ),
                            Div(
                                H3("🏢 Organization Tracking"),
                                P("Track procurement activities by specific government organizations and contracting authorities"),
                                cls="card"
                            ),
                            cls="grid grid-3"
                        ),
                        cls="container"
                    ),
                    
                    # Sync status
                    Div(
                        Div(
                            H2("📊 Data Synchronization Status"),
                            P(f"Last Sync: {sync_status.created_at.strftime('%Y-%m-%d %H:%M:%S') if sync_status else 'Never'}"),
                            P(f"Status: {sync_status.status.upper() if sync_status else 'N/A'}"),
                            P(f"Records Processed: {sync_status.records_processed if sync_status else 0}"),
                            P(f"New Records: {sync_status.records_added if sync_status else 0}"),
                            P(f"Updated Records: {sync_status.records_updated if sync_status else 0}"),
                            cls="card"
                        ) if sync_status else "",
                        cls="container",
                        style="margin-top: 3rem;"
                    ),
                    cls="container"
                )
            ), get_footer()
        finally:
            db.close()
