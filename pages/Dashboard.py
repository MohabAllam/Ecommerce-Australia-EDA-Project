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

st.markdown("<div class='section-title'>Dashboard KPI's</div>", unsafe_allow_html=True)

num_of_customers = df['customer_name'].nunique()
num_of_orders = df['sales_id'].nunique()
total_revenue = df['total_price'].sum()
avg_order_value = df['total_price'].mean()
avg_delivery_days = int(df['delivery_days'].mean().round())

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric('Total Customers', num_of_customers)

with col2:
    st.metric('Total Orders', num_of_orders)

with col3:
    st.metric('Total Revenue', total_revenue)

with col4:
    st.metric('Avg Order Value', round(avg_order_value, 2))

with col5:
    st.metric('Avg Delivery', avg_delivery_days)


# Insights
df_sorted = df.sort_values(by= 'order_date')

# 1- Sales Insights

st.markdown("<div class='section-title'>Sales Insights</div>", unsafe_allow_html=True)

# Total Rveneu trend per month
plot_df= df_sorted.groupby('month')['total_price'].sum().reset_index()
st.plotly_chart(px.line(data_frame= plot_df, x= 'month', y= 'total_price', markers= True, title= 'Total Revenue Trend per month',
                        labels= {'month' : 'Month', 'total_price' : 'Total Revenue'}), use_container_width=True)

# Total Rveneu trend per month per product type
plot_df= df_sorted.groupby(['month', 'product_type'])['total_price'].sum().reset_index()
st.plotly_chart(px.line(data_frame= plot_df, x= 'month', y= 'total_price', color= 'product_type', markers= True, title= 'Total Revenue Trend per month per Product Type',
                        labels= {'month' : 'Month', 'total_price' : 'Total Revenue'}), use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    plot_df = df.groupby('product_type')['sales_id'].count().sort_values(ascending = False).reset_index()
    st.plotly_chart(px.bar(data_frame= plot_df, x= 'product_type', y= 'sales_id', title= 'Total Orders per Product Category',
                           labels= {'product_type' : 'Product Type', 'sales_id' : 'Total Orders'}, text_auto= True), use_container_width=True)
    
with col2:
    plot_df = df.groupby('product_type')['total_price'].sum().sort_values(ascending = False).reset_index()
    st.plotly_chart(px.bar(data_frame= plot_df, x= 'product_type', y= 'total_price', title= 'Total Revenue per Product Category',
                           labels= {'product_type' : 'Product Type', 'total_price' : 'Total Revenue'}, text_auto= True), use_container_width=True)
    

# 2- Customer Analysis

st.markdown("<div class='section-title'>Customer Analysis</div>", unsafe_allow_html=True)

col1, col2= st.columns(2)

with col1:
    plot_df = df['state'].value_counts().sort_values().reset_index()
    st.plotly_chart(px.bar(data_frame= plot_df, y= 'state', x= 'count', text_auto= True,
                           labels= {'count' : 'Number of Orders', 'state' : 'State'}, title= 'Orders Percentage per State'), use_container_width=True)

with col2:
    plot_df = df['age group'].value_counts().reset_index()
    st.plotly_chart(px.pie(data_frame= plot_df, names= 'age group', values= 'count', title= 'Total Orders per each Age Group', hole= 0.6), use_container_width=True)

# 3- Product Analysis

st.markdown("<div class='section-title'>Product Preference Analysis</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    plot_df = df.groupby(['colour', 'age group'])['sales_id'].count().reset_index()
    st.plotly_chart(px.bar(data_frame= plot_df, x= 'colour', y= 'sales_id', color= 'age group', barmode= 'group',
                           labels= {'colour' : 'Colour', 'sales_id' : 'Count'}, title= 'Count of orders per each group for different colors'), use_container_width=True)

with col2:
    plot_df = df['size'].value_counts().reset_index()
    st.plotly_chart(px.pie(data_frame= plot_df, names= 'size', values= 'count', title= 'Percentage of each size volume', hole= 0.6), use_container_width=True)