"""Procurement routes - list and detail pages."""
from fasthtml.common import *
from sqlalchemy import desc, or_
from utils.database import SessionLocal, ProcurementNotice
from . import get_header, get_footer


def register_procurement_routes(rt):
    """Register procurement-related routes.
    
    Args:
        rt: FastHTML route decorator
    """
    
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
