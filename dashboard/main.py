"""
Streamlit Dashboard for GSWS SLA Monitoring System
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import json

# Page configuration
st.set_page_config(
    page_title="GSWS SLA Monitoring Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API base URL
API_BASE_URL = st.sidebar.text_input("API Base URL", value="http://localhost:8000")

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

def fetch_data(endpoint: str):
    """Fetch data from API"""
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

def main():
    """Main dashboard function"""
    st.markdown('<h1 class="main-header">📊 GSWS SLA Monitoring Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar filters
    st.sidebar.header("Filters")
    district_filter = st.sidebar.selectbox("District", ["All"] + ["Visakhapatnam", "Vijayawada", "Guntur", "Nellore"])
    date_range = st.sidebar.selectbox("Date Range", ["Last 7 days", "Last 30 days", "Last 90 days", "Last year"])
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Predictions", "Analytics", "Root Cause Analysis"])
    
    with tab1:
        show_overview()
    
    with tab2:
        show_predictions()
    
    with tab3:
        show_analytics()
    
    with tab4:
        show_root_cause_analysis()

def show_overview():
    """Show overview dashboard"""
    st.header("📈 Overview")
    
    # Fetch summary
    summary = fetch_data("/api/v1/dashboard/summary")
    
    if summary:
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Services", summary.get("total_services", 0))
        
        with col2:
            st.metric("SLA Compliance", f"{summary.get('sla_compliance', 0):.1f}%")
        
        with col3:
            st.metric("Delayed Services", summary.get("total_delayed", 0))
        
        with col4:
            st.metric("Avg TAT (Hours)", f"{summary.get('average_tat_hours', 0):.1f}")
        
        # Risk predictions
        st.subheader("🔮 Risk Predictions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("High Risk", summary.get("high_risk_predictions", 0), delta=None)
        
        with col2:
            st.metric("Medium Risk", summary.get("medium_risk_predictions", 0), delta=None)
        
        with col3:
            st.metric("Low Risk", summary.get("low_risk_predictions", 0), delta=None)
        
        # Trends chart
        st.subheader("📊 Trends")
        trends_data = fetch_data("/api/v1/dashboard/trends?days=30")
        
        if trends_data and trends_data.get("trends"):
            # Create trend visualization
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=["Week 1", "Week 2", "Week 3", "Week 4"],
                y=[15, 18, 16, 14],
                mode='lines+markers',
                name='Delay Rate (%)',
                line=dict(color='red', width=2)
            ))
            fig.update_layout(
                title="Delay Rate Trend (Last 30 Days)",
                xaxis_title="Week",
                yaxis_title="Delay Rate (%)",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Unable to fetch dashboard data. Please ensure the API server is running.")

def show_predictions():
    """Show predictions dashboard"""
    st.header("🔮 Delay Predictions")
    
    # Fetch predictions
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/predict",
            json={"prediction_horizon_days": 7},
            timeout=10
        )
        response.raise_for_status()
        predictions_data = response.json()
    except Exception as e:
        st.error(f"Error fetching predictions: {e}")
        return
    
    if predictions_data and predictions_data.get("predictions"):
        predictions = predictions_data["predictions"]
        
        # Summary
        st.subheader("Prediction Summary")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Predictions", predictions_data.get("total_predictions", 0))
        
        with col2:
            st.metric("High Risk", predictions_data.get("high_risk_count", 0))
        
        with col3:
            st.metric("Avg Delay Probability", f"{predictions_data.get('summary', {}).get('average_delay_probability', 0)*100:.1f}%")
        
        # Filter high-risk predictions
        high_risk = [p for p in predictions if p.get("risk_level") in ["HIGH", "CRITICAL"]]
        
        if high_risk:
            st.subheader("⚠️ High Risk Services")
            df_high_risk = pd.DataFrame(high_risk)
            
            # Display table
            st.dataframe(
                df_high_risk[["service_id", "service_name", "district", "current_stage", 
                              "predicted_delay_probability", "predicted_delay_hours", "risk_level"]],
                use_container_width=True
            )
            
            # Risk distribution chart
            fig = px.pie(
                values=[predictions_data.get("high_risk_count", 0),
                       predictions_data.get("medium_risk_count", 0),
                       predictions_data.get("low_risk_count", 0)],
                names=["High Risk", "Medium Risk", "Low Risk"],
                title="Risk Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No high-risk predictions found.")
    else:
        st.warning("No predictions available.")

def show_analytics():
    """Show analytics dashboard"""
    st.header("📊 Analytics & Insights")
    
    # Fetch analytics
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/analytics",
            json={
                "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
                "end_date": datetime.now().isoformat()
            },
            timeout=10
        )
        response.raise_for_status()
        analytics = response.json()
    except Exception as e:
        st.error(f"Error fetching analytics: {e}")
        return
    
    if analytics:
        # Key metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Services", analytics.get("total_services", 0))
        
        with col2:
            st.metric("SLA Compliance", f"{analytics.get('overall_sla_compliance', 0):.1f}%")
        
        with col3:
            st.metric("Average TAT", f"{analytics.get('average_tat_hours', 0):.1f} hours")
        
        # District performance
        st.subheader("🏛️ District Performance")
        root_cause = analytics.get("root_cause_analysis", {})
        district_hotspots = root_cause.get("district_hotspots", [])
        
        if district_hotspots:
            df_districts = pd.DataFrame(district_hotspots)
            
            # Compliance chart
            fig = px.bar(
                df_districts,
                x="district",
                y="sla_compliance_percentage",
                title="SLA Compliance by District",
                labels={"sla_compliance_percentage": "SLA Compliance (%)", "district": "District"}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # District table
            st.dataframe(df_districts, use_container_width=True)
        
        # Service trends
        st.subheader("📈 Service Trends")
        service_trends = root_cause.get("service_trends", [])
        
        if service_trends:
            df_services = pd.DataFrame(service_trends)
            
            fig = px.scatter(
                df_services,
                x="total_requests",
                y="delay_rate",
                size="average_completion_hours",
                hover_data=["service_name"],
                title="Service Performance",
                labels={"delay_rate": "Delay Rate", "total_requests": "Total Requests"}
            )
            st.plotly_chart(fig, use_container_width=True)

def show_root_cause_analysis():
    """Show root cause analysis"""
    st.header("🔍 Root Cause Analysis")
    
    # Fetch hotspots
    hotspots = fetch_data("/api/v1/dashboard/hotspots")
    
    if hotspots:
        # Primary causes
        st.subheader("🎯 Primary Causes")
        primary_causes = hotspots.get("primary_causes", [])
        
        if primary_causes:
            for i, cause in enumerate(primary_causes, 1):
                with st.expander(f"Cause {i}: {cause.get('cause', 'Unknown')}"):
                    st.write(f"**Impact:** {cause.get('impact_percentage', 0):.1f}%")
                    st.write(f"**Affected Services:** {cause.get('affected_services', 0)}")
        else:
            st.info("No primary causes identified.")
        
        # Stage bottlenecks
        st.subheader("🚧 Stage Bottlenecks")
        bottlenecks = hotspots.get("stage_bottlenecks", [])
        
        if bottlenecks:
            df_bottlenecks = pd.DataFrame(bottlenecks)
            
            fig = px.bar(
                df_bottlenecks,
                x="stage",
                y="delay_percentage",
                title="Delay Percentage by Stage",
                labels={"delay_percentage": "Delay %", "stage": "Workflow Stage"}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(df_bottlenecks, use_container_width=True)
        
        # Recommendations
        st.subheader("💡 Recommendations")
        recommendations = hotspots.get("recommendations", [])
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                st.write(f"{i}. {rec}")
        else:
            st.info("No recommendations available.")
    else:
        st.warning("Unable to fetch root cause analysis data.")

if __name__ == "__main__":
    main()

