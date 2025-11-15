"""Routes package for tenders-lv application."""
from fasthtml.common import *


def get_header(active=''):
    """Generate header navigation.
    
    Args:
        active: Active page identifier ('home', 'procurements', 'analytics')
    """
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
