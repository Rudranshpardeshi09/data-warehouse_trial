import streamlit as st
import pandas as pd
from data_models import load_and_process_data
import visualizations as vis

# Setup page configuration
st.set_page_config(
    page_title="Data Warehouse Pro Dashboard",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Premium CSS Styling
st.markdown("""
<style>
    /* Dark aesthetic overrides */
    .stApp {
        background-color: #0e1117;
        color: #e0e0e0;
    }
    .st-emotion-cache-1y4p8pa {
        padding-top: 2rem;
    }
    h1, h2, h3 {
        color: #448aff !important;
        font-family: 'Inter', sans-serif;
    }
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
    }
    /* Mermaid diagram backgrounds */
    pre {
        background-color: #1a1c23 !important;
        border-radius: 10px !important;
        border: 1px solid #333 !important;
    }
    /* Metrics */
    div[data-testid="stMetricValue"] {
        color: #69f0ae !important;
    }
</style>
""", unsafe_allow_html=True)

# Load data models
@st.cache_data
def get_data():
    return load_and_process_data("patients.csv")

try:
    dw_data = get_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Helpers
def denormalize_star():
    fact = dw_data['Fact_Admissions']
    dp = dw_data['Dim_Patient']
    ds = dw_data['Dim_Service']
    dd = dw_data['Dim_Date']
    # Merge Date on arrival_date_id
    res = fact.merge(dp, on='patient_id', how='left').merge(ds, on='service_id', how='left').merge(dd, left_on='arrival_date_id', right_on='date_id', how='left')
    return res

# --- SIDEBAR NAVIGATION ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3200/3200924.png", width=60)
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", 
    ["1. Concepts Overview", 
     "2. Schema Designs", 
     "3. OLAP Operations"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Developed By:** Rudransh Pardeshi")
st.sidebar.markdown("Demonstrating core Data Warehousing techniques using synthetic patient flow data.")

# --- PAGE 1: CONCEPTS OVERVIEW ---
if page == "1. Concepts Overview":
    st.title("🧊 Data Warehousing Concepts")
    st.markdown("""
    Welcome to the Data Warehouse interactive dashboard. 
    Here, we transform raw transaction processing data (OLTP) into analytical objects suitable for **OLAP** (Online Analytical Processing).
    """)
    
    st.subheader("Raw Data Preview (patients.csv)")
    raw_df = pd.read_csv("patients.csv")
    st.dataframe(raw_df.head(10), use_container_width=True)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Records", len(raw_df))
    col2.metric("Unique Patients", raw_df['patient_id'].nunique())
    col3.metric("Available Services", raw_df['service'].nunique())

    st.markdown("### Data Flow Architecture")
    vis.render_etl_flow_diagram()

# --- PAGE 2: SCHEMA DESIGNS ---
elif page == "2. Schema Designs":
    st.title("🧩 Schema Designs")
    
    tab1, tab2, tab3 = st.tabs(["⭐ Star Schema", "❄️ Snowflake Schema", "🌌 Fact Constellation"])
    
    with tab1:
        st.header("Star Schema")
        st.markdown("The simplest modeling technique: a single Fact table surrounded by un-normalized Dimensions.")
        vis.render_star_schema_diagram()
        
        st.markdown("**Fact_Admissions Sample**")
        st.dataframe(dw_data['Fact_Admissions'].head(), use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Dim_Patient Sample**")
            st.dataframe(dw_data['Dim_Patient'].head(), use_container_width=True)
        with col2:
            st.markdown("**Dim_Service Sample**")
            st.dataframe(dw_data['Dim_Service'].head(), use_container_width=True)
            
    with tab2:
        st.header("Snowflake Schema")
        st.markdown("Normalizing dimension tables to save space and maintain integrity. Notice how `Dim_Service` links out to a new `Dim_Department` table.")
        vis.render_snowflake_schema_diagram()
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Dim_Service (Showing FK to Dept)**")
            st.dataframe(dw_data['Dim_Service'].head(), use_container_width=True)
        with col2:
            st.markdown("**Dim_Department (Normalized)**")
            st.dataframe(dw_data['Dim_Department'].head(), use_container_width=True)

    with tab3:
        st.header("Fact Constellation (Galaxy Schema)")
        st.markdown("Multiple Fact tables sharing the same conformed dimensions. Here, we add a `Fact_Billing` table alongside Admissions.")
        vis.render_fact_constellation_diagram()
        
        st.markdown("**Fact_Billing Sample**")
        st.dataframe(dw_data['Fact_Billing'].head(), use_container_width=True)


# --- PAGE 3: OLAP OPERATIONS ---
elif page == "3. OLAP Operations":
    st.title("⚡ OLAP Techniques")
    st.markdown("Interact with the Data Warehouse models using common OLAP operations.")
    
    op_tab = st.selectbox("Select OLAP Operation", ["Cube (3D Aggregation)", "Slicing (Filtering by one dimension)", "Dicing (Filtering by multiple dimensions)"])
    
    df_star = denormalize_star()
    
    if op_tab == "Cube (3D Aggregation)":
        st.subheader("Interactive 3D Data Cube")
        vis.render_cube_concept_diagram()
        
        measure = st.radio("Select Measure to Visualise", ["Average Satisfaction", "Average Stay Length"], horizontal=True)
        
        if measure == "Average Satisfaction":
            # Grouping by 3 Dimensions
            cube = df_star.groupby(['service_name', 'age_group', 'quarter'])['satisfaction'].mean().reset_index()
            st.plotly_chart(vis.plot_animated_3d_cube(cube, 'satisfaction'), use_container_width=True)
        else:
            cube = df_star.groupby(['service_name', 'age_group', 'quarter'])['length_of_stay'].mean().reset_index()
            st.plotly_chart(vis.plot_animated_3d_cube(cube, 'length_of_stay'), use_container_width=True)

    elif op_tab == "Slicing (Filtering by one dimension)":
        st.subheader("Slicing")
        vis.render_slice_concept_diagram()
        
        service_slice = st.selectbox("Slice by Service Dimension:", dw_data['Dim_Service']['service_name'].tolist())
        
        # Apply slice
        sliced_df = df_star[df_star['service_name'] == service_slice]
        
        st.metric(f"Records after slicing by {service_slice}", len(sliced_df))
        st.plotly_chart(vis.plot_slice_stay_length(sliced_df, service_slice), use_container_width=True)

    elif op_tab == "Dicing (Filtering by multiple dimensions)":
        st.subheader("Dicing")
        vis.render_dice_concept_diagram()
        
        col1, col2 = st.columns(2)
        with col1:
            services = st.multiselect("Select Services (Dim_Service):", dw_data['Dim_Service']['service_name'].tolist(), default=dw_data['Dim_Service']['service_name'].tolist()[:2])
        with col2:
            age_groups = st.multiselect("Select Age Groups (Dim_Patient):", dw_data['Dim_Patient']['age_group'].unique().tolist(), default=dw_data['Dim_Patient']['age_group'].unique().tolist()[:2])
            
        if services and age_groups:
            diced_df = df_star[(df_star['service_name'].isin(services)) & (df_star['age_group'].isin(age_groups))]
            st.metric("Records after dicing", len(diced_df))
            st.plotly_chart(vis.plot_dice_scatter(diced_df), use_container_width=True)
        else:
            st.warning("Please select at least one value for both dimensions to dice the data.")
