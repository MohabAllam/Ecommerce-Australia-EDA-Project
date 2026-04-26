import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------------------------------------------------------
# Page Config & Custom CSS
# -----------------------------------------------------------------------------
st.set_page_config(layout='wide', page_title='EDA', page_icon='📈')

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

# Add Title
st.markdown("<div class='main-header'>Shopping Ecommerce EDA</div>", unsafe_allow_html=True)

# Banner Image Removed

@st.cache_data
def load_data():
    return pd.read_csv('cleaned_df.csv')

df = load_data()

# Add tabs
tab1, tab2, tab3 = st.tabs(['Numerical', 'Categorical', 'Custom'])

with tab1:
    st.markdown("<div class='section-title'>Univariate Numerical</div>", unsafe_allow_html=True)

    num_cols = df.select_dtypes(include= 'number').columns.drop('sales_id')

    for col in num_cols:
        st.plotly_chart(px.histogram(data_frame= df, x= col, title= col), use_container_width=True)

with tab2:
    st.markdown("<div class='section-title'>Univariate Categorical</div>", unsafe_allow_html=True)

    cat_cols = df.select_dtypes(include= 'object').columns.drop(['customer_name', 'order_date',	'delivery_date'])

    for col in cat_cols:
        st.plotly_chart(px.histogram(data_frame= df, x= col, title= col).update_xaxes(categoryorder = 'max descending'), use_container_width=True)

with tab3:
    # Select column
    column = st.selectbox('Column', df.columns)

    # Select Chart
    chart = st.selectbox('Chart', ['Histogram', 'Pie'])

    if st.button('Show Chart'):
        if chart == 'Histogram':
            st.plotly_chart(px.histogram(data_frame= df, y= column, title= column), use_container_width=True)
        elif chart == 'Pie':
            st.plotly_chart(px.pie(data_frame= df, names= column, title= column), use_container_width=True)
