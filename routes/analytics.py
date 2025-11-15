"""Analytics dashboard route."""
from fasthtml.common import *
from sqlalchemy import func, desc
from utils.database import SessionLocal, ProcurementNotice
from . import get_header, get_footer


def register_analytics_routes(rt):
    """Register analytics routes.
    
    Args:
        rt: FastHTML route decorator
    """
    
    @rt('/analytics')
    def analytics():
        """Analytics dashboard page."""
        db = SessionLocal()
        try:
            # Get summary statistics
            total_notices = db.query(func.count(ProcurementNotice.id)).scalar()
            
            # Get top organizations
            top_orgs = db.query(
                ProcurementNotice.organization_name,
                func.count(ProcurementNotice.id).label('count')
            ).filter(
                ProcurementNotice.organization_name.isnot(None)
            ).group_by(
                ProcurementNotice.organization_name
            ).order_by(
                desc('count')
            ).limit(10).all()
            
            # Get notice types distribution
            notice_types = db.query(
                ProcurementNotice.notice_type,
                func.count(ProcurementNotice.id).label('count')
            ).filter(
                ProcurementNotice.notice_type.isnot(None)
            ).group_by(
                ProcurementNotice.notice_type
            ).all()
            
            return Title("Analytics"), get_header('analytics'), Main(
                Div(
                    H1("Procurement Analytics", style="margin: 2rem 0 1rem;"),
                    P("Insights and trends from Latvian public procurement data", style="color: var(--muted-foreground); margin-bottom: 2rem;"),
                    
                    # Summary stats
                    Div(
                        Div(
                            Div(total_notices, cls="stat-value"),
                            Div("Total Notices", cls="stat-label"),
                            cls="stat-card"
                        ),
                        Div(
                            Div(len(top_orgs), cls="stat-value"),
                            Div("Active Organizations", cls="stat-label"),
                            cls="stat-card"
                        ),
                        Div(
                            Div(len(notice_types), cls="stat-value"),
                            Div("Notice Types", cls="stat-label"),
                            cls="stat-card"
                        ),
                        cls="stats-grid"
                    ),
                    
                    # Top organizations
                    Div(
                        H2("Top Contracting Authorities", style="margin: 2rem 0 1rem;"),
                        Div(*[
                            Div(
                                Div(
                                    Span(org.organization_name, style="font-weight: 500;"),
                                    Span(f"{org.count} procurements", cls="badge"),
                                    style="display: flex; justify-content: space-between; align-items: center;"
                                ),
                                cls="card"
                            )
                            for org in top_orgs
                        ]),
                        cls="detail-section"
                    ),
                    
                    # Notice types
                    Div(
                        H2("Notice Type Distribution", style="margin: 2rem 0 1rem;"),
                        Div(*[
                            Div(
                                Div(
                                    Span(nt.notice_type, style="font-weight: 500;"),
                                    Span(f"{nt.count} notices", cls="badge"),
                                    style="display: flex; justify-content: space-between; align-items: center;"
                                ),
                                cls="card"
                            )
                            for nt in notice_types
                        ]),
                        cls="detail-section"
                    ),
                    
                    cls="container"
                )
            ), get_footer()
        finally:
            db.close()
