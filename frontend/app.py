"""Streamlit frontend for Workflow Intelligence Platform."""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json
import os

# Page configuration
st.set_page_config(
    page_title="Workflow Intelligence Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling
st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .risk-critical {
        background-color: #ffebee;
    }
    .risk-high {
        background-color: #fff3e0;
    }
    .risk-medium {
        background-color: #f3e5f5;
    }
    .risk-low {
        background-color: #e8f5e9;
    }
    </style>
""", unsafe_allow_html=True)

# API Configuration - Use environment variable for deployment, default to localhost for development
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Session state initialization
if "workspace_generated" not in st.session_state:
    st.session_state.workspace_generated = False
if "last_workspace_id" not in st.session_state:
    st.session_state.last_workspace_id = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboard"


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def check_api_health():
    """Check if backend API is available."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def workspace_exists():
    """Check if a workspace with data exists."""
    try:
        response = requests.get(f"{API_BASE_URL}/workspace/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("status") == "ready"
    except:
        pass
    return False


def get_analytics(endpoint):
    """Fetch analytics data from backend."""
    try:
        response = requests.get(f"{API_BASE_URL}/analytics/{endpoint}", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching {endpoint}: {str(e)}")
        return None


def get_insights(focus_area="overall", depth="standard"):
    """Fetch AI insights from backend."""
    try:
        payload = {
            "focus_area": focus_area,
            "include_recommendations": True,
            "depth_level": depth
        }
        response = requests.post(f"{API_BASE_URL}/ai/summary", json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching insights: {str(e)}")
        return None


def generate_workspace(params):
    """Generate a new workspace."""
    try:
        response = requests.post(f"{API_BASE_URL}/workspace/generate", json=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error generating workspace: {str(e)}")
        return None


def render_metric_card(label, value, subtitle="", icon=""):
    """Render a metric card."""
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown(f"# {icon}")
    with col2:
        st.markdown(f"### {label}")
        st.markdown(f"# {value}")
        if subtitle:
            st.markdown(f"*{subtitle}*")


# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/workflow.png", width=80)
    st.title("Workflow Intelligence")
    st.markdown("---")
    
    # Navigation
    page = st.radio(
        "Navigation",
        ["Dashboard", "Workspace", "Analytics", "Insights", "Export", "Settings"],
        index=["Dashboard", "Workspace", "Analytics", "Insights", "Export", "Settings"].index(st.session_state.current_page)
    )
    st.session_state.current_page = page
    
    st.markdown("---")
    
    # API Status
    api_health = check_api_health()
    if api_health:
        st.success("✅ Backend Connected")
    else:
        st.error("❌ Backend Disconnected")
        st.info("Start backend with: `python -m uvicorn backend.main:app --reload`")
    
    st.markdown("---")
    
    # Current Workspace Info
    with st.expander("Workspace Info"):
        if st.session_state.workspace_generated:
            st.success(f"Workspace ID: {st.session_state.last_workspace_id[:8]}...")
            
            # Fetch workspace status
            try:
                response = requests.get(f"{API_BASE_URL}/workspace/status", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if "statistics" in data:
                        st.json(data["statistics"])
            except:
                st.info("Workspace status unavailable")
        else:
            st.info("No workspace generated yet")


# ============================================================================
# MAIN CONTENT
# ============================================================================

if page == "Dashboard":
    st.title("📊 Operational Dashboard")
    
    if not api_health:
        st.error("⚠️ Backend API is not available. Please start the backend server.")
        st.code("python -m uvicorn backend.main:app --reload", language="bash")
    elif not workspace_exists():
        # Welcome screen when no workspace exists
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            # 👋 Welcome to Workflow Intelligence Platform
            
            This is a production-grade AI-powered workflow analytics platform. To get started, you'll need to generate some workspace data.
            
            ### Quick Start
            1. Navigate to the **Workspace** tab in the left sidebar
            2. Select your workspace size (Startup, Medium, or Enterprise)
            3. Click **"Generate Workspace"** to create sample data
            4. Return here to see your dashboard with live analytics
            
            ### What You'll See
            - **Key Metrics**: Overview of your team's performance
            - **Task Distribution**: Visual breakdown of task statuses and priorities
            - **AI Insights**: Intelligent analysis and recommendations
            - **Analytics**: Deep dive into productivity metrics
            """)
        
        with col2:
            st.markdown("### Generate Now")
            if st.button("Go to Workspace", use_container_width=True, key="ws_nav"):
                st.session_state.current_page = "Workspace"
                st.rerun()
            
            st.markdown("---")
            st.markdown("### Templates")
            st.markdown("""
            **Startup** (20-30 people)
            Small team setup
            
            **Medium** (50-100 people)
            Growing organization
            
            **Enterprise** (100-500 people)
            Large-scale operations
            """)
    else:
        # KPI Row
        st.subheader("Key Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        # Fetch all analytics
        emp_data = get_analytics("employees")
        proj_data = get_analytics("projects")
        task_data = get_analytics("tasks")
        risk_data = get_analytics("risks")
        
        if emp_data:
            with col1:
                render_metric_card(
                    "Total Employees",
                    emp_data["data"]["summary"]["total_employees"],
                    "Active workforce",
                    "👥"
                )
        
        if proj_data:
            with col2:
                healthy = proj_data["data"]["summary"]["healthy_projects"]
                total = proj_data["data"]["summary"]["total_projects"]
                render_metric_card(
                    "Project Health",
                    f"{healthy}/{total}",
                    "Healthy projects",
                    "✅"
                )
        
        if task_data:
            with col3:
                render_metric_card(
                    "Task Completion",
                    f"{task_data['data']['summary']['completion_rate']*100:.1f}%",
                    "of all tasks",
                    "📋"
                )
        
        if risk_data:
            with col4:
                render_metric_card(
                    "Risk Level",
                    risk_data["data"]["risk_level"].upper(),
                    f"Score: {risk_data['data']['risk_score']:.2f}",
                    "⚠️"
                )
        
        st.markdown("---")
        
        # Charts Row
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Task Status Distribution")
            if task_data:
                status_data = task_data["data"]["status_distribution"]
                fig = go.Figure(data=[
                    go.Pie(
                        labels=list(status_data.keys()),
                        values=list(status_data.values()),
                        hole=0.3
                    )
                ])
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Task Priority Distribution")
            if task_data:
                priority_data = task_data["data"]["priority_distribution"]
                fig = go.Figure(data=[
                    go.Bar(x=list(priority_data.keys()), y=list(priority_data.values()))
                ])
                fig.update_layout(
                    height=400,
                    xaxis_title="Priority",
                    yaxis_title="Count"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # AI Insights
        st.markdown("---")
        st.subheader("🤖 AI-Powered Insights")
        
        insights = get_insights(focus_area="overall", depth="standard")
        if insights:
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.metric(
                    "Overall Risk Score",
                    f"{insights['risk_score']:.2f}",
                    f"Level: {insights.get('title', 'Analysis')}"
                )
            
            with col2:
                st.write("**Key Insights:**")
                for i, insight in enumerate(insights["insights"][:3], 1):
                    st.markdown(f"{i}. {insight}")
            
            if insights.get("recommendations"):
                st.write("**Recommendations:**")
                for i, rec in enumerate(insights["recommendations"], 1):
                    st.info(f"{i}. {rec}")


elif page == "Workspace":
    st.title("🏢 Workspace Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Generate New Workspace")
        
        with st.form("workspace_form"):
            num_employees = st.slider("Number of Employees", 5, 500, 50)
            num_projects = st.slider("Number of Projects", 1, 200, 20)
            num_teams = st.slider("Number of Teams", 1, 50, 5)
            tasks_per_project = st.slider("Tasks per Project", 1, 100, 15)
            workload_intensity = st.slider("Workload Intensity", 0.1, 1.0, 0.7)
            completion_rate = st.slider("Task Completion Rate", 0.0, 1.0, 0.7)
            
            submitted = st.form_submit_button("Generate Workspace", use_container_width=True)
        
        if submitted:
            with st.spinner("Generating workspace..."):
                params = {
                    "num_employees": num_employees,
                    "num_projects": num_projects,
                    "num_teams": num_teams,
                    "tasks_per_project": tasks_per_project,
                    "workload_intensity": workload_intensity,
                    "completion_rate": completion_rate,
                }
                
                result = generate_workspace(params)
                
                if result and result.get("success"):
                    st.success(f"✅ {result['message']}")
                    st.session_state.workspace_generated = True
                    st.session_state.last_workspace_id = result["workspace_id"]
                    
                    # Display statistics
                    st.json(result["statistics"])
    
    with col2:
        st.subheader("Workspace Templates")
        
        templates = {
            "Small Startup": {
                "num_employees": 15,
                "num_projects": 5,
                "num_teams": 2,
                "tasks_per_project": 10,
                "workload_intensity": 0.8,
                "completion_rate": 0.85,
            },
            "Medium Company": {
                "num_employees": 50,
                "num_projects": 20,
                "num_teams": 5,
                "tasks_per_project": 15,
                "workload_intensity": 0.7,
                "completion_rate": 0.7,
            },
            "Large Enterprise": {
                "num_employees": 200,
                "num_projects": 100,
                "num_teams": 15,
                "tasks_per_project": 20,
                "workload_intensity": 0.6,
                "completion_rate": 0.65,
            },
        }
        
        for template_name, params in templates.items():
            if st.button(f"Use {template_name}", use_container_width=True):
                with st.spinner(f"Generating {template_name} workspace..."):
                    result = generate_workspace(params)
                    if result and result.get("success"):
                        st.success(f"✅ {result['message']}")
                        st.session_state.workspace_generated = True
                        st.session_state.last_workspace_id = result["workspace_id"]
                        st.json(result["statistics"])


elif page == "Analytics":
    st.title("📈 Advanced Analytics")
    
    if not api_health:
        st.error("Backend API is not available")
    else:
        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            ["Employees", "Projects", "Tasks", "Productivity", "Risks"]
        )
        
        with tab1:
            st.subheader("Employee Analytics")
            emp_data = get_analytics("employees")
            if emp_data:
                # Summary
                summary = emp_data["data"]["summary"]
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Employees", summary["total_employees"])
                col2.metric("Avg Workload", f"{summary['average_workload']:.1f}")
                col3.metric("Completion Rate", f"{summary['average_completion_rate']*100:.1f}%")
                col4.metric("Total Tasks", summary["total_tasks"])
                
                # Employee table
                df = pd.DataFrame(emp_data["data"]["employees"])
                st.dataframe(df, use_container_width=True)
        
        with tab2:
            st.subheader("Project Analytics")
            proj_data = get_analytics("projects")
            if proj_data:
                summary = proj_data["data"]["summary"]
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Projects", summary["total_projects"])
                col2.metric("Healthy", summary["healthy_projects"])
                col3.metric("At Risk", summary["at_risk_projects"])
                col4.metric("Avg Health", f"{summary['average_health']*100:.1f}%")
                
                df = pd.DataFrame(proj_data["data"]["projects"])
                st.dataframe(df, use_container_width=True)
        
        with tab3:
            st.subheader("Task Analytics")
            task_data = get_analytics("tasks")
            if task_data:
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Tasks", task_data["data"]["summary"]["total_tasks"])
                col2.metric("Open Tasks", task_data["data"]["summary"]["open_tasks"])
                col3.metric("Overdue", task_data["data"]["overdue_tasks"])
                col4.metric("Unassigned", task_data["data"]["unassigned_tasks"])
                
                st.json(task_data["data"])
        
        with tab4:
            st.subheader("Productivity Metrics")
            prod_data = get_analytics("productivity")
            if prod_data:
                summary = prod_data["data"]["summary"]
                col1, col2, col3 = st.columns(3)
                col1.metric("High Performers", summary["high_performers"])
                col2.metric("On Track", summary["on_track"])
                col3.metric("At Risk", summary["at_risk"])
                
                df = pd.DataFrame(prod_data["data"]["metrics"])
                st.dataframe(df, use_container_width=True)
        
        with tab5:
            st.subheader("Risk Analysis")
            risk_data = get_analytics("risks")
            if risk_data:
                col1, col2, col3 = st.columns(3)
                col1.metric("Risk Level", risk_data["data"]["risk_level"])
                col2.metric("Risk Score", f"{risk_data['data']['risk_score']:.2f}")
                col3.metric("Risks Identified", risk_data["data"]["summary"]["total_risks_identified"])
                
                st.write("**Overloaded Employees:**")
                if risk_data["data"]["overloaded_employees"]:
                    df = pd.DataFrame(risk_data["data"]["overloaded_employees"])
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No overloaded employees detected")
                
                st.write("**Projects with Deadline Risk:**")
                if risk_data["data"]["projects_with_deadline_risk"]:
                    df = pd.DataFrame(risk_data["data"]["projects_with_deadline_risk"])
                    st.dataframe(df, use_container_width=True)


elif page == "Insights":
    st.title("🤖 AI-Powered Insights")
    
    if not api_health:
        st.error("Backend API is not available")
    else:
        # Insight focus area selector
        focus_area = st.selectbox(
            "Select Focus Area",
            ["overall", "employees", "projects", "risks", "productivity"]
        )
        
        depth_level = st.select_slider(
            "Insight Depth",
            options=["quick", "standard", "detailed"],
            value="standard"
        )
        
        if st.button("Generate Insights", type="primary", use_container_width=True):
            with st.spinner("Generating insights..."):
                insights = get_insights(focus_area, depth_level)
                
                if insights:
                    # Header
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Insight Type", insights["focus_area"].upper())
                    with col2:
                        st.metric("Risk Score", f"{insights['risk_score']:.2f}")
                    with col3:
                        st.metric("Generated", insights["generated_at"][:10])
                    
                    st.markdown("---")
                    
                    # Insights
                    st.subheader("📌 Key Insights")
                    for i, insight in enumerate(insights["insights"], 1):
                        st.markdown(f"**{i}.** {insight}")
                    
                    # Recommendations
                    if insights.get("recommendations"):
                        st.markdown("---")
                        st.subheader("💡 Recommendations")
                        for i, rec in enumerate(insights["recommendations"], 1):
                            st.info(f"**{i}.** {rec}")
                    
                    # Metadata
                    if insights.get("metadata"):
                        st.markdown("---")
                        st.subheader("📊 Analysis Details")
                        st.json(insights["metadata"])


elif page == "Export":
    st.title("💾 Data Export")
    
    if not workspace_exists():
        st.warning("⚠️ No workspace data available for export. Please generate a workspace first.")
        if st.button("Go to Workspace", use_container_width=True):
            st.session_state.current_page = "Workspace"
            st.rerun()
    else:
        st.markdown("""
        Download your workspace data in multiple formats for use in other tools, 
        spreadsheets, databases, or further analysis.
        """)
        
        st.markdown("---")
        
        # Download buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("📋 CSV Export")
            st.markdown("Download as comma-separated values file for Excel, Google Sheets, or data analysis")
            try:
                response = requests.get(f"{API_BASE_URL}/export/csv", timeout=30)
                if response.status_code == 200:
                    st.download_button(
                        label="📥 Download CSV",
                        data=response.text,
                        file_name="workflow_data.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                else:
                    st.error("Failed to fetch CSV data")
            except Exception as e:
                st.error(f"Error: {str(e)}")
        
        with col2:
            st.subheader("📊 Excel Export")
            st.markdown("Download as Excel spreadsheet with multiple sheets for analysis")
            try:
                response = requests.get(f"{API_BASE_URL}/export/excel", timeout=30)
                if response.status_code == 200:
                    st.download_button(
                        label="📥 Download Excel",
                        data=response.content,
                        file_name="workflow_data.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                else:
                    st.error("Failed to fetch Excel data")
            except Exception as e:
                st.error(f"Error: {str(e)}")
        
        with col3:
            st.subheader("📄 JSON Export")
            st.markdown("Download as JSON format for APIs, databases, or advanced processing")
            try:
                response = requests.get(f"{API_BASE_URL}/export/json", timeout=30)
                if response.status_code == 200:
                    st.download_button(
                        label="📥 Download JSON",
                        data=response.text,
                        file_name="workflow_data.json",
                        mime="application/json",
                        use_container_width=True
                    )
                else:
                    st.error("Failed to fetch JSON data")
            except Exception as e:
                st.error(f"Error: {str(e)}")
        
        st.markdown("---")
        
        st.subheader("ℹ️ Export Information")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **CSV Format**
            - Compatible with Excel, Sheets
            - Tabular structure
            - Easy to share
            - Best for: Reports, presentations
            """)
        
        with col2:
            st.markdown("""
            **Excel Format**
            - Multiple sheets per data type
            - Professional formatting
            - Easy analysis in Excel
            - Best for: Detailed analysis, sharing
            """)
        
        with col3:
            st.markdown("""
            **JSON Format**
            - Structured data format
            - Hierarchical relationships
            - API compatible
            - Best for: Integration, databases
            """)
        
        st.markdown("---")
        st.subheader("📋 What's Included in All Exports")
        st.markdown("""
        - **Employees**: ID, name, task counts, completion rates
        - **Projects**: Project details, health scores, task counts
        - **Tasks**: Status distribution, priority distribution
        - **Productivity**: Velocity metrics, efficiency scores
        - **Risks**: Risk levels and distribution
        - **Metadata**: Complete timestamps and export info
        """)


elif page == "Settings":
    st.title("⚙️ Settings & Configuration")
    
    st.subheader("Backend Configuration")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**API Endpoint:**")
        st.code(API_BASE_URL)
        
        st.write("**API Status:**")
        if check_api_health():
            st.success("✅ Connected")
        else:
            st.error("❌ Disconnected")
    
    with col2:
        st.write("**Documentation:**")
        st.markdown(f"[Swagger Docs]({API_BASE_URL}/docs)")
        st.markdown(f"[ReDoc]({API_BASE_URL}/redoc)")
    
    st.markdown("---")
    
    st.subheader("About")
    st.markdown("""
    ### Workflow Intelligence Platform
    
    An AI-powered operational analytics and insights platform for workflow management.
    
    **Version:** 1.0.0  
    **Status:** Production Ready
    
    **Features:**
    - 📊 Advanced analytics on employees, projects, and tasks
    - 🤖 AI-powered insights and recommendations
    - ⚠️ Risk analysis and bottleneck detection
    - 📈 Interactive visualizations
    - 💾 Data export capabilities
    
    **Built with:**
    - FastAPI (Backend)
    - Streamlit (Frontend)
    - Pandas + Plotly (Analytics)
    - Faker (Data Generation)
    """)
