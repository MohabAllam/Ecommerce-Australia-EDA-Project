import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------------------------------------------------------
# Page Config & Custom CSS
# -----------------------------------------------------------------------------
st.set_page_config(layout='wide', page_title='Marketing Analytics', page_icon='📈')

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Background with soft animated mesh gradient effect */
    .stApp {
        background-color: #f0f4f8;
        background-image: 
            radial-gradient(at 40% 20%, hsla(228,100%,74%,0.15) 0px, transparent 50%),
            radial-gradient(at 80% 0%, hsla(189,100%,56%,0.15) 0px, transparent 50%),
            radial-gradient(at 0% 50%, hsla(355,100%,93%,0.15) 0px, transparent 50%),
            radial-gradient(at 80% 50%, hsla(340,100%,76%,0.15) 0px, transparent 50%),
            radial-gradient(at 0% 100%, hsla(22,100%,77%,0.15) 0px, transparent 50%),
            radial-gradient(at 80% 100%, hsla(242,100%,70%,0.15) 0px, transparent 50%),
            radial-gradient(at 0% 0%, hsla(343,100%,76%,0.15) 0px, transparent 50%);
        background-attachment: fixed;
    }
    
    /* Premium Header Typography */
    .main-header {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 800;
        font-size: 3.5rem;
        background: linear-gradient(135deg, #0f172a 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.05em;
        margin-bottom: 1rem;
        text-align: center;
        padding-top: 1rem;
        padding-bottom: 0.5rem;
    }
    .section-title {
        color: #0f172a;
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        margin-top: 2.5rem;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .section-title::before {
        content: "";
        display: inline-block;
        width: 8px;
        height: 24px;
        background: linear-gradient(to bottom, #3b82f6, #8b5cf6);
        border-radius: 4px;
    }

    /* Glassmorphism Cards */
    [data-testid="stPlotlyChart"], [data-testid="stDataFrame"], [data-testid="stMetric"], .stTabs [data-baseweb="tab-list"] {
        background: rgba(255, 255, 255, 0.6) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border-radius: 24px !important;
        padding: 20px !important;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.8) !important;
        transition: transform 0.3s ease, box-shadow 0.3s ease !important;
    }

    [data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 1) !important;
    }

    /* Override dataframe padding so it fits well inside the border */
    [data-testid="stDataFrame"] {
        padding: 10px !important;
    }

    /* Metric internal styling */
    [data-testid="stMetric"] label {
        color: #64748b !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }
    [data-testid="stMetric"] div {
        color: #0f172a !important;
        font-weight: 800 !important;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.6);
    }
    
    /* Clean up Streamlit default UI elements */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(148, 163, 184, 0.5);
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(100, 116, 139, 0.8);
    }
    
    /* Fade-in Animation */
    .block-container {
        animation: fadeIn 0.8s ease-out;
    }
    @keyframes fadeIn {
        0% { opacity: 0; transform: translateY(15px); }
        100% { opacity: 1; transform: translateY(0); }
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Data Loading & Processing
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv('cleaned_df.csv')
    df['order_date'] = pd.to_datetime(df['order_date'])
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("Data file 'cleaned_df.csv' not found.")
    st.stop()

# Header
st.markdown("<div class='main-header'>Marketing Report</div>", unsafe_allow_html=True)
# Banner Image Removed

# -----------------------------------------------------------------------------
# Sidebar Configuration
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("<h3 style='color: #0f172a; margin-bottom: 0;'>⚙️ Parameters</h3>", unsafe_allow_html=True)
    st.markdown("<hr style='margin-top: 0.5rem; margin-bottom: 1rem;'>", unsafe_allow_html=True)
    
    # City Filter
    all_cities = ['All Cities'] + sorted(df['city'].dropna().unique().tolist())
    selected_city_list = st.multiselect('📍 Target City', all_cities, default='All Cities')
    
    # Date Range Filter
    min_date = df['order_date'].min().date()
    max_date = df['order_date'].max().date()
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input('📅 Start Date', min_value=min_date, max_value=max_date, value=min_date)
    with col2:
        end_date = st.date_input('📅 End Date', min_value=min_date, max_value=max_date, value=max_date)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Top N Filter
    top_n = st.slider('📊 Top N Products to Display', min_value=5, max_value=30, value=10, step=1)

# Apply Filters
df_filtered = df.copy()

if 'All Cities' not in selected_city_list and len(selected_city_list) > 0:
    df_filtered = df_filtered[df_filtered['city'].isin(selected_city_list)]

df_filtered = df_filtered[
    (df_filtered['order_date'].dt.date >= start_date) & 
    (df_filtered['order_date'].dt.date <= end_date)
]

# -----------------------------------------------------------------------------
# Main Dashboard UI
# -----------------------------------------------------------------------------
st.markdown("<div class='section-title'>📄 Data Preview</div>", unsafe_allow_html=True)
if not df_filtered.empty:
    st.dataframe(df_filtered, use_container_width=True, hide_index=True)
else:
    st.info("No data available.")

st.markdown("<div class='section-title'>🏆 Top Products by Order Count</div>", unsafe_allow_html=True)
if not df_filtered.empty and 'product_name' in df_filtered.columns:
    plot_df = df_filtered['product_name'].value_counts().reset_index().head(top_n)
    plot_df.columns = ['product_name', 'count']
    plot_df = plot_df.sort_values('count', ascending=True)
    
    fig = px.bar(
        plot_df, 
        y='product_name', 
        x='count', 
        orientation='h',
        text_auto=True
    )
    fig.update_traces(
        marker_color='#3b82f6',
        marker_line_width=0, 
        opacity=0.85, 
        textposition='outside',
        textfont=dict(color='#0f172a', size=12)
    )
    fig.update_layout(
        xaxis_title="Orders Count",
        yaxis_title="",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=20, t=10, b=0),
        height=500,
        font=dict(family="Plus Jakarta Sans", color="#64748b")
    )
    fig.update_xaxes(showgrid=True, gridcolor='rgba(255,255,255,0.4)', zeroline=False)
    fig.update_yaxes(showgrid=False)
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
else:
    st.info("No data available for the selected filters.")