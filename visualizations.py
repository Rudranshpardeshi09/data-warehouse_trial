import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

def render_mermaid(mermaid_code, height=400):
    html = f"""
    <div style="background-color: transparent;">
        <script type="module">
          import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
          mermaid.initialize({{ 
              startOnLoad: true, 
              theme: 'dark', 
              fontFamily: 'Inter' 
          }});
        </script>
        <pre class="mermaid">
        {mermaid_code}
        </pre>
    </div>
    """
    components.html(html, height=height)

# --- CONCEPTUAL DATA FLOW DIAGRAMS ---

def render_etl_flow_diagram():
    mermaid_code = """
    graph LR
    classDef source fill:#ffadad,stroke:#333,stroke-width:2px,color:#000;
    classDef process fill:#fdffb6,stroke:#333,stroke-width:2px,color:#000;
    classDef dw fill:#9bf6ff,stroke:#333,stroke-width:2px,color:#000;
    classDef rep fill:#caffbf,stroke:#333,stroke-width:2px,color:#000;
    
    A[(patients.csv<br/>Raw Data)]:::source -->|ETL Processing| B(Clean & Transform):::process
    B --> C[(Data Warehouse<br/>Star/Snowflake Models)]:::dw
    C -->|Queries| D{{OLAP Dashboard<br/>Charts & Visuals}}:::rep
    """
    render_mermaid(mermaid_code, height=200)

def render_cube_concept_diagram():
    mermaid_code = """
    graph TD
    classDef data fill:#9bf6ff,stroke:#333,stroke-width:2px,color:#000;
    classDef action fill:#ffd6a5,stroke:#333,stroke-width:2px,color:#000;
    
    A[(Fact Table)]:::data --> B[Group by Service]
    C[(Dim Service)]:::data --> B
    D[(Dim Age Group)]:::data --> E[Group by Age]
    F[(Dim Quarter)]:::data --> G[Group by Quarter]
    
    B:::action --> H{3D Data Cube<br/>Aggregations}
    E:::action --> H
    G:::action --> H
    """
    render_mermaid(mermaid_code, height=350)

def render_slice_concept_diagram():
    mermaid_code = """
    graph LR
    classDef data fill:#9bf6ff,stroke:#333,stroke-width:2px,color:#000;
    classDef action fill:#ffd6a5,stroke:#333,stroke-width:2px,color:#000;
    classDef res fill:#caffbf,stroke:#333,stroke-width:2px,color:#000;
    
    A[3D Data Cube]:::data -->|Lock Dimension:<br/>Service = 'Surgery'| B(Slice Operation):::action
    B --> C[2D Data Slice<br/>Age vs Quarter]:::res
    """
    render_mermaid(mermaid_code, height=150)

def render_dice_concept_diagram():
    mermaid_code = """
    graph LR
    classDef data fill:#9bf6ff,stroke:#333,stroke-width:2px,color:#000;
    classDef action fill:#ffd6a5,stroke:#333,stroke-width:2px,color:#000;
    classDef res fill:#caffbf,stroke:#333,stroke-width:2px,color:#000;
    
    A[3D Data Cube]:::data -->|Filter 1:<br/>Service in ICU, Surgery| B(Dice Operation):::action
    B -->|Filter 2:<br/>Age in 18-34, 35-54| C[Smaller 3D Sub-Cube]:::res
    """
    render_mermaid(mermaid_code, height=150)

# --- SCHEMA DIAGRAMS ---

def render_star_schema_diagram():
    mermaid_code = """
    graph TD
    classDef fact fill:#ff5252,stroke:#333,stroke-width:2px,color:#fff;
    classDef dim fill:#448aff,stroke:#333,stroke-width:2px,color:#fff;
    
    FA[Fact_Admissions]:::fact
    DP[Dim_Patient]:::dim
    DD[Dim_Date]:::dim
    DS[Dim_Service]:::dim
    
    DP --- FA
    DD --- FA
    DS --- FA
    """
    render_mermaid(mermaid_code, height=250)

def render_snowflake_schema_diagram():
    mermaid_code = """
    graph TD
    classDef fact fill:#ff5252,stroke:#333,stroke-width:2px,color:#fff;
    classDef dim fill:#448aff,stroke:#333,stroke-width:2px,color:#fff;
    classDef dim_norm fill:#69f0ae,stroke:#333,stroke-width:2px,color:#000;
    
    FA[Fact_Admissions]:::fact
    DP[Dim_Patient]:::dim
    DD[Dim_Date]:::dim
    DS[Dim_Service]:::dim
    DDept[Dim_Department]:::dim_norm
    
    DP --- FA
    DD --- FA
    DS --- FA
    DDept --- DS
    """
    render_mermaid(mermaid_code, height=350)

def render_fact_constellation_diagram():
    mermaid_code = """
    graph TD
    classDef fact fill:#ff5252,stroke:#333,stroke-width:2px,color:#fff;
    classDef dim fill:#448aff,stroke:#333,stroke-width:2px,color:#fff;
    
    FA[Fact_Admissions]:::fact
    FB[Fact_Billing]:::fact
    DP[Dim_Patient]:::dim
    DD[Dim_Date]:::dim
    DS[Dim_Service]:::dim
    
    DP --- FA
    DP --- FB
    DD --- FA
    DD --- FB
    DS --- FA
    DS --- FB
    """
    render_mermaid(mermaid_code, height=350)

# --- CHARTS ---

def plot_animated_3d_cube(cube_df, measure_col):
    fig = px.scatter_3d(
        cube_df, 
        x='service_name', 
        y='age_group', 
        z='quarter',
        color=measure_col, 
        size=measure_col,
        size_max=40,
        opacity=0.8,
        title=f'Interactive Data Cube (3D): {measure_col.replace("_", " ").title()}',
        color_continuous_scale=px.colors.sequential.Viridis
    )
    
    fig.update_layout(
        template="plotly_dark", 
        title_x=0.5,
        scene=dict(
            xaxis=dict(title='Service', backgroundcolor="rgb(20, 24, 30)"),
            yaxis=dict(title='Age', backgroundcolor="rgb(20, 24, 30)"),
            zaxis=dict(title='Quarter', backgroundcolor="rgb(20, 24, 30)"),
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.5)
            )
        ),
        margin=dict(l=0, r=0, b=0, t=50)
    )
    return fig

def plot_slice_stay_length(slice_df, dimension_value):
    fig = px.histogram(
        slice_df, 
        x='length_of_stay', 
        nbins=20,
        title=f'Slice Analysis: Stay Length dist for {dimension_value}',
        color_discrete_sequence=['#448aff'],
        marginal="box"
    )
    fig.update_layout(template="plotly_dark", title_x=0.5)
    return fig

def plot_dice_scatter(dice_df):
    fig = px.scatter(
        dice_df,
        x='length_of_stay',
        y='satisfaction',
        color='service_name',
        size='age',
        hover_data=['name'],
        title='Dice Analysis: Satisfaction vs Stay Length',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_layout(template="plotly_dark", title_x=0.5)
    return fig
