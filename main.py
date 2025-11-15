"""Latvia Procurement Monitor - FastHTML Application."""
from fasthtml.common import *
from database import SessionLocal, ProcurementNotice, DataSyncLog, init_db
from sqlalchemy import func, desc, or_
from datetime import datetime
import os

# Custom CSS matching the original design
custom_css = Style("""
:root {
    --primary: oklch(45% 0.15 250);
    --primary-foreground: oklch(98% 0 0);
    --background: oklch(98% 0 0);
    --foreground: oklch(20% 0 0);
    --card: oklch(100% 0 0);
    --card-foreground: oklch(20% 0 0);
    --muted: oklch(95% 0.01 250);
    --muted-foreground: oklch(50% 0.01 250);
    --border: oklch(90% 0.01 250);
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background-color: var(--background);
    color: var(--foreground);
    line-height: 1.6;
}

.container {
    max-width: 1280px;
    margin: 0 auto;
    padding: 0 2rem;
}

header {
    background-color: var(--card);
    border-bottom: 1px solid var(--border);
    padding: 1rem 0;
    position: sticky;
    top: 0;
    z-index: 10;
}

.header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.logo {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--foreground);
    text-decoration: none;
}

.nav-links {
    display: flex;
    gap: 1.5rem;
}

.nav-links a {
    color: var(--muted-foreground);
    text-decoration: none;
    font-size: 0.875rem;
}

.nav-links a:hover, .nav-links a.active {
    color: var(--primary);
}

.hero {
    background: linear-gradient(to bottom, oklch(45% 0.15 250 / 0.05), var(--background));
    padding: 5rem 0;
    text-align: center;
}

.hero h1 {
    font-size: 3rem;
    font-weight: 700;
    margin-bottom: 1rem;
}

.hero p {
    font-size: 1.25rem;
    color: var(--muted-foreground);
    max-width: 48rem;
    margin: 0 auto 2rem;
}

.btn {
    display: inline-block;
    padding: 0.75rem 1.5rem;
    border-radius: 0.5rem;
    text-decoration: none;
    font-weight: 500;
    transition: all 0.2s;
}

.btn-primary {
    background-color: var(--primary);
    color: var(--primary-foreground);
}

.btn-primary:hover {
    opacity: 0.9;
}

.btn-outline {
    border: 1px solid var(--border);
    color: var(--foreground);
}

.btn-outline:hover {
    background-color: var(--muted);
}

.card {
    background-color: var(--card);
    border: 1px solid var(--border);
    border-radius: 0.5rem;
    padding: 1.5rem;
    margin-bottom: 1rem;
}

.card:hover {
    box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    transition: box-shadow 0.2s;
}

.card h3 {
    font-size: 1.125rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.card p {
    color: var(--muted-foreground);
    font-size: 0.875rem;
}

.grid {
    display: grid;
    gap: 2rem;
    margin: 2rem 0;
}

.grid-3 {
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
}

.badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 500;
    background-color: oklch(45% 0.15 250 / 0.1);
    color: var(--primary);
}

.search-form {
    display: grid;
    grid-template-columns: 2fr 1fr auto;
    gap: 1rem;
    margin-bottom: 2rem;
}

input, select {
    padding: 0.75rem;
    border: 1px solid var(--border);
    border-radius: 0.5rem;
    font-size: 1rem;
}

input:focus, select:focus {
    outline: 2px solid var(--primary);
    outline-offset: 2px;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    margin: 2rem 0;
}

.stat-card {
    background-color: var(--card);
    border: 1px solid var(--border);
    border-radius: 0.5rem;
    padding: 1.5rem;
}

.stat-value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--primary);
}

.stat-label {
    font-size: 0.875rem;
    color: var(--muted-foreground);
    margin-top: 0.5rem;
}

footer {
    margin-top: 4rem;
    padding: 2rem 0;
    border-top: 1px solid var(--border);
    text-align: center;
    color: var(--muted-foreground);
    font-size: 0.875rem;
}

.meta-info {
    display: flex;
    gap: 1.5rem;
    flex-wrap: wrap;
    color: var(--muted-foreground);
    font-size: 0.875rem;
    margin-top: 1rem;
}

.meta-info svg {
    display: inline-block;
    width: 1rem;
    height: 1rem;
    vertical-align: middle;
    margin-right: 0.25rem;
}

.pagination {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 1rem;
    margin: 2rem 0;
}

.detail-section {
    margin: 2rem 0;
}

.detail-section h2 {
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 1rem;
}

.detail-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
}

.detail-item {
    margin-bottom: 1rem;
}

.detail-label {
    font-weight: 500;
    font-size: 0.875rem;
    margin-bottom: 0.25rem;
}

.detail-value {
    color: var(--muted-foreground);
}
""")

# Initialize database
init_db()

# Create FastHTML app
app, rt = fast_app(
    hdrs=(
        Link(rel='stylesheet', href='https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap'),
        custom_css
    ),
    pico=False
)

def get_header(active=''):
    """Generate header navigation."""
    return Header(
        Div(
            Div(
                A("Latvia Procurement Monitor", href="/", cls="logo"),
                Div(
                    A("Home", href="/", cls="active" if active == 'home' else ""),
                    A("Browse Procurements", href="/procurements", cls="active" if active == 'procurements' else ""),
                    A("Analytics", href="/analytics", cls="active" if active == 'analytics' else ""),
                    cls="nav-links"
                ),
                cls="header-content"
            ),
            cls="container"
        )
    )

def get_footer():
    """Generate footer."""
    return Footer(
        Div(
            P("Data source: Procurement Monitoring Bureau (Iepirkumu uzraudzības birojs)"),
            P(A("Learn more about Latvia's open procurement data", 
                href="https://www.iub.gov.lv/en/open-data", target="_blank")),
            cls="container"
        )
    )

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

@rt('/procurements')
def procurements(search: str = '', notice_type: str = '', page: int = 1):
    """Procurement list page with search and filters."""
    db = SessionLocal()
    try:
        limit = 20
        offset = (page - 1) * limit
        
        # Build query
        query = db.query(ProcurementNotice)
        
        if search:
            search_filter = or_(
                ProcurementNotice.name.ilike(f'%{search}%'),
                ProcurementNotice.organization_name.ilike(f'%{search}%'),
                ProcurementNotice.cpv_type.ilike(f'%{search}%')
            )
            query = query.filter(search_filter)
        
        if notice_type and notice_type != 'all':
            query = query.filter(ProcurementNotice.notice_type == notice_type)
        
        total = query.count()
        notices = query.order_by(desc(ProcurementNotice.created_at)).offset(offset).limit(limit).all()
        total_pages = (total + limit - 1) // limit
        
        return Title("Browse Procurements"), get_header('procurements'), Main(
            Div(
                H1("Search Procurement Notices", style="margin: 2rem 0 1rem;"),
                
                # Search form
                Form(
                    Input(name="search", placeholder="Search by name, organization, or CPV code...", value=search),
                    Select(
                        Option("All Types", value="all", selected=(notice_type == 'all' or not notice_type)),
                        Option("Planned Contract", value="pil-planned-contract", selected=(notice_type == 'pil-planned-contract')),
                        Option("Contract", value="mk-contract", selected=(notice_type == 'mk-contract')),
                        Option("Discussion", value="sps-discussion", selected=(notice_type == 'sps-discussion')),
                        name="notice_type"
                    ),
                    Button("Search", type="submit", cls="btn btn-primary"),
                    method="get",
                    cls="search-form"
                ),
                
                P(f"Showing {offset + 1} - {min(offset + limit, total)} of {total} results", 
                  style="color: var(--muted-foreground); font-size: 0.875rem; margin-bottom: 1rem;"),
                
                # Results
                Div(*[
                    A(
                        Div(
                            Div(
                                H3(notice.name or "Untitled"),
                                Span(notice.notice_type or "Unknown", cls="badge") if notice.notice_type else "",
                                style="display: flex; justify-content: space-between; align-items: start; gap: 1rem;"
                            ),
                            P(notice.description[:200] + "..." if notice.description and len(notice.description) > 200 else notice.description or "No description"),
                            Div(
                                Span(f"🏢 {notice.organization_name}" if notice.organization_name else ""),
                                Span(f"📅 {notice.public_opening_date.strftime('%Y-%m-%d')}" if notice.public_opening_date else ""),
                                Span(f"€{float(notice.estimated_value):,.0f}" if notice.estimated_value and notice.estimated_value.replace('.','').isdigit() else ""),
                                cls="meta-info"
                            ),
                            cls="card"
                        ),
                        href=f"/procurement/{notice.id}",
                        style="text-decoration: none; color: inherit;"
                    )
                    for notice in notices
                ]) if notices else Div(
                    P("No procurement notices found. Try adjusting your search criteria."),
                    cls="card"
                ),
                
                # Pagination
                Div(
                    A("← Previous", href=f"/procurements?search={search}&notice_type={notice_type}&page={page-1}", 
                      cls="btn btn-outline" if page > 1 else "btn btn-outline", 
                      style="opacity: 0.5; pointer-events: none;" if page <= 1 else ""),
                    Span(f"Page {page} of {total_pages}"),
                    A("Next →", href=f"/procurements?search={search}&notice_type={notice_type}&page={page+1}", 
                      cls="btn btn-outline" if page < total_pages else "btn btn-outline",
                      style="opacity: 0.5; pointer-events: none;" if page >= total_pages else ""),
                    cls="pagination"
                ) if total_pages > 1 else "",
                
                cls="container"
            )
        ), get_footer()
    finally:
        db.close()

@rt('/procurement/{id}')
def procurement_detail(id: int):
    """Procurement detail page."""
    db = SessionLocal()
    try:
        notice = db.query(ProcurementNotice).filter(ProcurementNotice.id == id).first()
        
        if not notice:
            return Title("Not Found"), get_header(), Main(
                Div(
                    H1("Procurement Notice Not Found"),
                    P("The requested procurement notice could not be found."),
                    A("Back to List", href="/procurements", cls="btn btn-primary"),
                    cls="container",
                    style="text-align: center; padding: 4rem 0;"
                )
            ), get_footer()
        
        return Title(notice.name or "Procurement Detail"), get_header(), Main(
            Div(
                A("← Back to List", href="/procurements", cls="btn btn-outline", style="margin: 2rem 0 1rem;"),
                
                Div(
                    H1(notice.name or "Untitled"),
                    Span(notice.notice_type or "Unknown", cls="badge") if notice.notice_type else "",
                    P(notice.description or "No description available", style="margin-top: 1rem; color: var(--muted-foreground);"),
                    cls="card"
                ),
                
                Div(
                    H2("Procurement Details"),
                    Div(
                        Div(
                            Div("CPV Code", cls="detail-label"),
                            Div(notice.cpv_type or "N/A", cls="detail-value"),
                            cls="detail-item"
                        ) if notice.cpv_type else "",
                        Div(
                            Div("Procedure Type", cls="detail-label"),
                            Div(notice.procedure_type or "N/A", cls="detail-value"),
                            cls="detail-item"
                        ) if notice.procedure_type else "",
                        Div(
                            Div("Estimated Value", cls="detail-label"),
                            Div(f"€{float(notice.estimated_value):,.2f}" if notice.estimated_value and notice.estimated_value.replace('.','').isdigit() else "N/A", 
                                cls="detail-value", style="font-size: 1.5rem; font-weight: 600; color: var(--primary);"),
                            cls="detail-item"
                        ),
                        Div(
                            Div("Public Opening Date", cls="detail-label"),
                            Div(notice.public_opening_date.strftime('%Y-%m-%d %H:%M') if notice.public_opening_date else "N/A", cls="detail-value"),
                            cls="detail-item"
                        ),
                        Div(
                            Div("Deadline for Tenders", cls="detail-label"),
                            Div(notice.deadline_receipt_tenders_date.strftime('%Y-%m-%d %H:%M') if notice.deadline_receipt_tenders_date else "N/A", cls="detail-value"),
                            cls="detail-item"
                        ),
                        cls="detail-grid"
                    ),
                    cls="detail-section"
                ),
                
                Div(
                    H2("Contracting Authority"),
                    Div(
                        Div(
                            Div("Organization", cls="detail-label"),
                            Div(notice.organization_name or "N/A", cls="detail-value"),
                            cls="detail-item"
                        ),
                        Div(
                            Div("City", cls="detail-label"),
                            Div(notice.organization_city or "N/A", cls="detail-value"),
                            cls="detail-item"
                        ),
                        Div(
                            Div("Registration Number", cls="detail-label"),
                            Div(notice.organization_identifier or "N/A", cls="detail-value"),
                            cls="detail-item"
                        ),
                        cls="detail-grid"
                    ),
                    cls="detail-section"
                ),
                
                Div(
                    H2("Contact Information"),
                    Div(
                        Div(
                            Div("Contact Person", cls="detail-label"),
                            Div(notice.contact_name or "N/A", cls="detail-value"),
                            cls="detail-item"
                        ) if notice.contact_name else "",
                        Div(
                            Div("Email", cls="detail-label"),
                            A(notice.contact_email, href=f"mailto:{notice.contact_email}", cls="detail-value") if notice.contact_email else Div("N/A", cls="detail-value"),
                            cls="detail-item"
                        ),
                        Div(
                            Div("Telephone", cls="detail-label"),
                            A(notice.contact_telephone, href=f"tel:{notice.contact_telephone}", cls="detail-value") if notice.contact_telephone else Div("N/A", cls="detail-value"),
                            cls="detail-item"
                        ),
                        cls="detail-grid"
                    ),
                    cls="detail-section"
                ) if notice.contact_name or notice.contact_email or notice.contact_telephone else "",
                
                Div(
                    H2("External Links"),
                    Div(
                        A("View Procurement Documents →", href=notice.documents_url, target="_blank", cls="btn btn-primary", style="margin-right: 1rem;") if notice.documents_url else "",
                        A("Submission Portal →", href=notice.submission_url, target="_blank", cls="btn btn-outline") if notice.submission_url else "",
                    ),
                    cls="detail-section"
                ) if notice.documents_url or notice.submission_url else "",
                
                cls="container"
            )
        ), get_footer()
    finally:
        db.close()

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

# Run the app
serve(port=5001)
