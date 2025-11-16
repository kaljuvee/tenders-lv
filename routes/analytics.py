"""Analytics dashboard route with Plotly visualizations."""
from fasthtml.common import *
from sqlalchemy import func, desc, cast, Numeric
from utils.database import SessionLocal, ProcurementNotice
from . import get_header, get_footer
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta


def create_timeline_chart(db):
    """Create procurement volume timeline chart."""
    # Get daily counts for last 30 days
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    daily_data = db.query(
        func.date(ProcurementNotice.created_at).label('date'),
        func.count(ProcurementNotice.id).label('count')
    ).filter(
        ProcurementNotice.created_at >= thirty_days_ago
    ).group_by(
        func.date(ProcurementNotice.created_at)
    ).order_by('date').all()
    
    if not daily_data:
        return "<p>No data available for timeline</p>"
    
    dates = [str(d.date) for d in daily_data]
    counts = [d.count for d in daily_data]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=counts,
        mode='lines+markers',
        name='Procurements',
        line=dict(color='#4169E1', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title='Procurement Volume (Last 30 Days)',
        xaxis_title='Date',
        yaxis_title='Number of Procurements',
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Inter, sans-serif'),
        height=400,
        margin=dict(l=50, r=50, t=50, b=50)
    )
    
    fig.update_xaxes(showgrid=True, gridcolor='#E5E7EB')
    fig.update_yaxes(showgrid=True, gridcolor='#E5E7EB')
    
    return fig.to_html(include_plotlyjs='cdn', div_id='timeline-chart')


def create_cpv_distribution_chart(db):
    """Create CPV category distribution pie chart."""
    cpv_data = db.query(
        func.substring(ProcurementNotice.cpv_type, 1, 2).label('cpv_category'),
        func.count(ProcurementNotice.id).label('count')
    ).filter(
        ProcurementNotice.cpv_type.isnot(None)
    ).group_by(
        'cpv_category'
    ).order_by(
        desc('count')
    ).limit(10).all()
    
    if not cpv_data:
        return "<p>No CPV data available</p>"
    
    # CPV category names (first 2 digits)
    cpv_names = {
        '03': 'Agriculture',
        '09': 'Petroleum',
        '14': 'Mining',
        '15': 'Food',
        '18': 'Clothing',
        '22': 'Printing',
        '24': 'Chemicals',
        '30': 'Office Equipment',
        '31': 'Electrical Equipment',
        '32': 'Radio/TV Equipment',
        '33': 'Medical Equipment',
        '34': 'Transport Equipment',
        '35': 'Security Equipment',
        '37': 'Musical Instruments',
        '38': 'Lab Equipment',
        '39': 'Furniture',
        '41': 'Water',
        '42': 'Industrial Machinery',
        '43': 'Mining Machinery',
        '44': 'Construction',
        '45': 'Construction Work',
        '48': 'Software',
        '50': 'Repair Services',
        '51': 'Installation Services',
        '55': 'Hotel Services',
        '60': 'Transport Services',
        '63': 'Travel Services',
        '64': 'Postal Services',
        '65': 'Utilities',
        '66': 'Financial Services',
        '70': 'Real Estate',
        '71': 'Architectural Services',
        '72': 'IT Services',
        '73': 'Research Services',
        '75': 'Administration',
        '76': 'Oil/Gas Services',
        '77': 'Agriculture Services',
        '79': 'Business Services',
        '80': 'Education',
        '85': 'Health Services',
        '90': 'Sewage Services',
        '92': 'Recreation Services',
        '98': 'Other Services'
    }
    
    labels = [f"{d.cpv_category} - {cpv_names.get(d.cpv_category, 'Other')}" for d in cpv_data]
    values = [d.count for d in cpv_data]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker=dict(colors=px.colors.qualitative.Set3)
    )])
    
    fig.update_layout(
        title='Top 10 CPV Categories',
        font=dict(family='Inter, sans-serif'),
        height=500,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    return fig.to_html(include_plotlyjs='cdn', div_id='cpv-chart')


def create_value_by_org_chart(db):
    """Create top organizations by total estimated value chart."""
    # Get top organizations by value
    org_data = db.query(
        ProcurementNotice.organization_name,
        func.sum(
            cast(ProcurementNotice.estimated_value, Numeric)
        ).label('total_value'),
        func.count(ProcurementNotice.id).label('count')
    ).filter(
        ProcurementNotice.organization_name.isnot(None),
        ProcurementNotice.estimated_value.isnot(None),
        ProcurementNotice.estimated_value != '',
        ProcurementNotice.estimated_value.regexp_match(r'^\d+\.?\d*$')
    ).group_by(
        ProcurementNotice.organization_name
    ).order_by(
        desc('total_value')
    ).limit(15).all()
    
    if not org_data:
        return "<p>No value data available</p>"
    
    orgs = [d.organization_name[:40] + '...' if len(d.organization_name) > 40 else d.organization_name 
            for d in org_data]
    values = [float(d.total_value) for d in org_data]
    counts = [d.count for d in org_data]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=orgs[::-1],  # Reverse for better display
        x=values[::-1],
        orientation='h',
        marker=dict(
            color=values[::-1],
            colorscale='Blues',
            showscale=True,
            colorbar=dict(title="Value (€)")
        ),
        text=[f"€{v:,.0f}<br>{c} procurements" for v, c in zip(values[::-1], counts[::-1])],
        textposition='auto',
        hovertemplate='<b>%{y}</b><br>Total Value: €%{x:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Top 15 Organizations by Total Procurement Value',
        xaxis_title='Total Estimated Value (€)',
        yaxis_title='',
        font=dict(family='Inter, sans-serif'),
        height=600,
        margin=dict(l=250, r=50, t=50, b=50),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    fig.update_xaxes(showgrid=True, gridcolor='#E5E7EB')
    
    return fig.to_html(include_plotlyjs='cdn', div_id='value-chart')


def create_notice_type_chart(db):
    """Create notice type distribution bar chart."""
    notice_data = db.query(
        ProcurementNotice.notice_type,
        func.count(ProcurementNotice.id).label('count')
    ).filter(
        ProcurementNotice.notice_type.isnot(None)
    ).group_by(
        ProcurementNotice.notice_type
    ).order_by(
        desc('count')
    ).all()
    
    if not notice_data:
        return "<p>No notice type data available</p>"
    
    types = [d.notice_type for d in notice_data]
    counts = [d.count for d in notice_data]
    
    fig = go.Figure(data=[go.Bar(
        x=types,
        y=counts,
        marker=dict(
            color=counts,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Count")
        ),
        text=counts,
        textposition='auto',
        hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
    )])
    
    fig.update_layout(
        title='Procurement Notice Type Distribution',
        xaxis_title='Notice Type',
        yaxis_title='Number of Procurements',
        font=dict(family='Inter, sans-serif'),
        height=400,
        margin=dict(l=50, r=50, t=50, b=120),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    fig.update_xaxes(showgrid=False, tickangle=-45)
    fig.update_yaxes(showgrid=True, gridcolor='#E5E7EB')
    
    return fig.to_html(include_plotlyjs='cdn', div_id='notice-type-chart')


def register_analytics_routes(rt):
    """Register analytics routes.
    
    Args:
        rt: FastHTML route decorator
    """
    
    @rt('/analytics')
    def analytics():
        """Analytics dashboard page with Plotly visualizations."""
        db = SessionLocal()
        try:
            # Get summary statistics
            total_notices = db.query(func.count(ProcurementNotice.id)).scalar()
            
            # Count unique organizations
            unique_orgs = db.query(
                func.count(func.distinct(ProcurementNotice.organization_name))
            ).filter(
                ProcurementNotice.organization_name.isnot(None)
            ).scalar()
            
            # Calculate total estimated value
            total_value = db.query(
                func.sum(cast(ProcurementNotice.estimated_value, Numeric))
            ).filter(
                ProcurementNotice.estimated_value.isnot(None),
                ProcurementNotice.estimated_value != '',
                ProcurementNotice.estimated_value.regexp_match(r'^\d+\.?\d*$')
            ).scalar()
            
            # Count notices with deadlines in next 30 days
            upcoming_deadline = datetime.now() + timedelta(days=30)
            upcoming_count = db.query(
                func.count(ProcurementNotice.id)
            ).filter(
                ProcurementNotice.deadline_receipt_tenders_date.between(
                    datetime.now(),
                    upcoming_deadline
                )
            ).scalar()
            
            # Generate charts
            timeline_html = create_timeline_chart(db)
            cpv_html = create_cpv_distribution_chart(db)
            value_html = create_value_by_org_chart(db)
            notice_type_html = create_notice_type_chart(db)
            
            return Title("Analytics Dashboard"), get_header('analytics'), Main(
                Div(
                    H1("Procurement Analytics Dashboard", style="margin: 2rem 0 1rem;"),
                    P("Interactive insights and trends from Latvian public procurement data", 
                      style="color: var(--muted-foreground); margin-bottom: 2rem;"),
                    
                    # Summary stats
                    Div(
                        Div(
                            Div(f"{total_notices:,}", cls="stat-value"),
                            Div("Total Procurements", cls="stat-label"),
                            cls="stat-card"
                        ),
                        Div(
                            Div(f"{unique_orgs:,}", cls="stat-value"),
                            Div("Contracting Authorities", cls="stat-label"),
                            cls="stat-card"
                        ),
                        Div(
                            Div(f"€{float(total_value or 0):,.0f}", cls="stat-value"),
                            Div("Total Estimated Value", cls="stat-label"),
                            cls="stat-card"
                        ),
                        Div(
                            Div(f"{upcoming_count:,}", cls="stat-value"),
                            Div("Upcoming Deadlines (30d)", cls="stat-label"),
                            cls="stat-card"
                        ),
                        cls="stats-grid"
                    ),
                    
                    # Timeline chart
                    Div(
                        Div(NotStr(timeline_html), cls="card"),
                        style="margin: 2rem 0;"
                    ),
                    
                    # Two column layout for charts
                    Div(
                        Div(
                            Div(NotStr(cpv_html), cls="card"),
                            style="grid-column: 1;"
                        ),
                        Div(
                            Div(NotStr(notice_type_html), cls="card"),
                            style="grid-column: 2;"
                        ),
                        style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin: 2rem 0;"
                    ),
                    
                    # Value by organization chart
                    Div(
                        Div(NotStr(value_html), cls="card"),
                        style="margin: 2rem 0;"
                    ),
                    
                    cls="container"
                )
            ), get_footer()
        finally:
            db.close()
