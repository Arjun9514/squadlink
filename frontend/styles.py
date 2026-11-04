"""Custom CSS and styling components for SquadLink."""

CUSTOM_CSS = """
<style>
/* Main app container background */
.stApp {
    background-color: #F7F8FC;
    color: #1A1B2F;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

/* Hide default streamlit header decoration */
header[data-testid="stHeader"] {
    background-color: transparent;
}

/* App Header styling */
.squadlink-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 0 1.5rem 0;
    border-bottom: 1px solid #E5E7EB;
    margin-bottom: 1.5rem;
}

.squadlink-brand {
    display: flex;
    align-items: center;
    gap: 12px;
}

.brand-dots {
    display: flex;
    align-items: center;
    gap: 5px;
}

.brand-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    display: inline-block;
}

.dot-1 { background-color: #FF2E63; }
.dot-2 { background-color: #FF4B72; }
.dot-3 { background-color: #FF6584; }
.dot-4 { background-color: #FF859B; }
.dot-5 { 
    background-color: transparent; 
    border: 2px solid #FF2E63; 
    box-sizing: border-box;
}

.brand-title {
    font-size: 1.85rem;
    font-weight: 800;
    color: #1A1B2F;
    letter-spacing: -0.5px;
    margin: 0;
}

.squadlink-user-badge {
    display: flex;
    align-items: center;
    gap: 16px;
    color: #6B7280;
    font-size: 0.9rem;
    font-family: monospace;
}

/* Card container */
.sl-card {
    background-color: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 24px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.sl-card-title {
    font-size: 1.35rem;
    font-weight: 700;
    color: #1A1B2F;
    margin-bottom: 8px;
}

.sl-card-subtitle {
    font-size: 0.95rem;
    color: #6B7280;
    margin-bottom: 20px;
}

/* Metric card */
.sl-metric-card {
    background-color: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 12px;
    padding: 16px 20px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
    min-height: 100px;
}

.sl-metric-title {
    font-size: 0.85rem;
    font-weight: 600;
    color: #6B7280;
    text-transform: capitalize;
    margin-bottom: 6px;
}

.sl-metric-value {
    font-size: 2.2rem;
    font-weight: 800;
    color: #1A1B2F;
    line-height: 1.1;
}

/* Status badges */
.badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.badge-open {
    background-color: #DEF7EC;
    color: #03543F;
}

.badge-full {
    background-color: #FDE8E8;
    color: #9B1C1C;
}

.badge-in_progress {
    background-color: #FEF08A;
    color: #854D0E;
}

.badge-completed {
    background-color: #F3F4F6;
    color: #4B5563;
}

.badge-role {
    background-color: #E0E7FF;
    color: #3730A3;
}

/* Primary buttons */
div.stButton > button:first-child {
    background-color: #E63956;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    padding: 0.5rem 1.25rem;
    transition: all 0.2s ease;
}

div.stButton > button:first-child:hover {
    background-color: #D81B60;
    color: #FFFFFF;
    border: none;
    box-shadow: 0 4px 12px rgba(230, 57, 86, 0.3);
}

/* Secondary outline button */
div.stButton > button[kind="secondary"] {
    background-color: #FFFFFF;
    color: #4B5563;
    border: 1px solid #D1D5DB;
}

div.stButton > button[kind="secondary"]:hover {
    background-color: #F9FAFB;
    border-color: #9CA3AF;
    color: #111827;
}

/* Form inputs & selectboxes styling */
div[data-baseweb="select"] > div {
    border-radius: 8px;
    background-color: #EEF0F8;
    border: 1px solid transparent;
}

div[data-baseweb="select"] > div:hover {
    border-color: #CBD5E1;
}

div[data-baseweb="input"] > div {
    border-radius: 8px;
    background-color: #EEF0F8;
}

/* Custom styled tabs */
div[data-testid="stTabs"] button[role="tab"] {
    font-size: 1rem;
    font-weight: 500;
    color: #4B5563;
    padding: 10px 18px;
}

div[data-testid="stTabs"] button[aria-selected="true"] {
    color: #E63956 !important;
    font-weight: 700 !important;
    border-bottom: 2px solid #E63956 !important;
}

/* Tables styling */
div[data-testid="stTable"], div[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid #E5E7EB;
}
</style>
"""


def render_brand_header(user_info="root@localhost / squadlink", show_logout=True):
    """Render top brand header with 5-dot logo and connection info."""
    dots_html = """
    <div class="brand-dots">
        <span class="brand-dot dot-1"></span>
        <span class="brand-dot dot-2"></span>
        <span class="brand-dot dot-3"></span>
        <span class="brand-dot dot-4"></span>
        <span class="brand-dot dot-5"></span>
    </div>
    """
    return f"""
    <div class="squadlink-header">
        <div class="squadlink-brand">
            {dots_html}
            <span class="brand-title">SquadLink</span>
        </div>
        <div class="squadlink-user-badge">
            <span>{user_info}</span>
        </div>
    </div>
    """


def render_metric_card(title: str, value):
    """Render HTML metric card matching the screenshots."""
    return f"""
    <div class="sl-metric-card">
        <div class="sl-metric-title">{title}</div>
        <div class="sl-metric-value">{value}</div>
    </div>
    """
