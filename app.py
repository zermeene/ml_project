"""
Streamlit Frontend for Air Quality Intelligence System
"""
import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Air Quality Intelligence",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Base URL
API_URL = "http://127.0.0.1:8000"

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stAlert {
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🌍 Air Quality Intelligence System</h1>', unsafe_allow_html=True)
st.markdown("**AI-powered air quality prediction and analysis**")

# Check API health
def check_api_health():
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

# Sidebar
with st.sidebar:
    st.header("🎛️ Navigation")
    page = st.radio(
        "Select Page",
        ["🏠 Home", "🔮 AQI Prediction", "📊 PM2.5 Prediction", "📈 Batch Analysis", "ℹ️ About"]
    )
    
    st.divider()
    
    # API Status
    st.subheader("🔌 API Status")
    if check_api_health():
        st.success("✅ Connected")
    else:
        st.error("❌ Disconnected")
        st.warning("Start the API server:\n`uvicorn src.api:app --reload`")
    
    st.divider()
    
    # Info
    st.info("**📚 Quick Tips**\n\n"
            "- Good: AQI 0-50\n"
            "- Moderate: AQI 51-100\n"
            "- Unhealthy: AQI 101-150\n"
            "- Very Unhealthy: 151+")

# HOME PAGE
if page == "🏠 Home":
    st.header("Welcome to Air Quality Intelligence System")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="🎯 Classifier Accuracy",
            value="100%",
            delta="Perfect Score"
        )
    
    with col2:
        st.metric(
            label="📊 Regression R² Score",
            value="0.924",
            delta="Excellent"
        )
    
    with col3:
        st.metric(
            label="🌐 Cities Analyzed",
            value="10",
            delta="Global Coverage"
        )
    
    st.divider()
    
    st.subheader("🚀 Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🔮 AQI Category Prediction**
        - Predict air quality category
        - Real-time analysis
        - Multiple pollutant support
        
        **📊 PM2.5 Concentration Prediction**
        - Forecast PM2.5 levels
        - Weather-based predictions
        - High accuracy models
        """)
    
    with col2:
        st.markdown("""
        **📈 Batch Analysis**
        - Analyze multiple locations
        - Comparative insights
        - Export results
        
        **🎯 Advanced ML Models**
        - Random Forest Classifier
        - Gradient Boosting Regressor
        - K-Means Clustering
        """)
    
    st.divider()
    
    st.subheader("📊 System Architecture")
    
    st.markdown("""
    ```
    Data Input → Feature Engineering → ML Models → Predictions → API → Frontend
    ```
    """)

# AQI PREDICTION PAGE
elif page == "🔮 AQI Prediction":
    st.header("🔮 Air Quality Index (AQI) Prediction")
    st.markdown("Predict the AQI category based on pollutant measurements and weather conditions.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🌫️ Pollutant Levels")
        pm25 = st.slider("PM2.5 (μg/m³)", 0.0, 500.0, 55.3, 0.1)
        pm10 = st.slider("PM10 (μg/m³)", 0.0, 600.0, 102.5, 0.1)
        no2 = st.slider("NO2 (μg/m³)", 0.0, 400.0, 45.2, 0.1)
        so2 = st.slider("SO2 (μg/m³)", 0.0, 300.0, 12.8, 0.1)
        co = st.slider("CO (mg/m³)", 0.0, 500.0, 85.3, 0.1)
        o3 = st.slider("O3 (μg/m³)", 0.0, 400.0, 65.4, 0.1)
    
    with col2:
        st.subheader("🌤️ Weather Conditions")
        temperature = st.slider("Temperature (°C)", -50.0, 60.0, 25.5, 0.1)
        humidity = st.slider("Humidity (%)", 0.0, 100.0, 65.0, 0.1)
        wind_speed = st.slider("Wind Speed (m/s)", 0.0, 50.0, 3.2, 0.1)
        
        st.subheader("🕐 Time Information")
        hour = st.slider("Hour of Day", 0, 23, 14)
        day_of_week = st.selectbox("Day of Week", 
                                   ["Monday", "Tuesday", "Wednesday", "Thursday", 
                                    "Friday", "Saturday", "Sunday"])
        month = st.selectbox("Month", 
                           ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
    
    # Convert inputs
    day_map = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3,
               "Friday": 4, "Saturday": 5, "Sunday": 6}
    month_map = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
                 "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}
    
    if st.button("🔮 Predict AQI Category", type="primary", use_container_width=True):
        with st.spinner("Predicting..."):
            try:
                payload = {
                    "PM2_5": pm25,
                    "PM10": pm10,
                    "NO2": no2,
                    "SO2": so2,
                    "CO": co,
                    "O3": o3,
                    "temperature": temperature,
                    "humidity": humidity,
                    "wind_speed": wind_speed,
                    "hour": hour,
                    "day_of_week": day_map[day_of_week],
                    "month": month_map[month]
                }
                
                response = requests.post(f"{API_URL}/predict/aqi", json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    st.success("✅ Prediction Complete!")
                    
                    # Display main result
                    st.markdown(f"### Predicted Category: **{result['aqi_category']}**")
                    st.markdown(f"**Confidence:** {result['confidence']*100:.2f}%")
                    
                    # Display all probabilities
                    st.subheader("📊 Probability Distribution")
                    
                    probs_df = pd.DataFrame({
                        'Category': list(result['probabilities'].keys()),
                        'Probability': [v*100 for v in result['probabilities'].values()]
                    })
                    
                    fig = px.bar(probs_df, x='Category', y='Probability',
                                color='Probability',
                                color_continuous_scale='RdYlGn_r',
                                title='AQI Category Probabilities')
                    fig.update_layout(yaxis_title="Probability (%)")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Color-coded result
                    category = result['aqi_category']
                    if category == "Good":
                        st.success(f"🟢 **{category}**: Air quality is satisfactory!")
                    elif category == "Moderate":
                        st.info(f"🟡 **{category}**: Air quality is acceptable.")
                    elif category in ["Unhealthy for Sensitive", "Unhealthy"]:
                        st.warning(f"🟠 **{category}**: Consider limiting outdoor activities.")
                    else:
                        st.error(f"🔴 **{category}**: Health alert! Avoid outdoor activities.")
                else:
                    st.error(f"❌ Error: {response.status_code}")
            except Exception as e:
                st.error(f"❌ Connection Error: {str(e)}")
                st.info("Make sure the API server is running:\n`uvicorn src.api:app --reload`")

# PM2.5 PREDICTION PAGE
elif page == "📊 PM2.5 Prediction":
    st.header("📊 PM2.5 Concentration Prediction")
    st.markdown("Forecast PM2.5 levels based on weather conditions and other pollutants.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🌫️ Other Pollutants")
        no2 = st.slider("NO2 (μg/m³)", 0.0, 400.0, 45.2, 0.1)
        so2 = st.slider("SO2 (μg/m³)", 0.0, 300.0, 12.8, 0.1)
        co = st.slider("CO (mg/m³)", 0.0, 500.0, 85.3, 0.1)
        o3 = st.slider("O3 (μg/m³)", 0.0, 400.0, 65.4, 0.1)
    
    with col2:
        st.subheader("🌤️ Weather Conditions")
        temperature = st.slider("Temperature (°C)", -50.0, 60.0, 25.5, 0.1)
        humidity = st.slider("Humidity (%)", 0.0, 100.0, 65.0, 0.1)
        wind_speed = st.slider("Wind Speed (m/s)", 0.0, 50.0, 3.2, 0.1)
        
        st.subheader("🕐 Time Information")
        hour = st.slider("Hour of Day", 0, 23, 14)
        day_of_week = st.selectbox("Day of Week", 
                                   ["Monday", "Tuesday", "Wednesday", "Thursday", 
                                    "Friday", "Saturday", "Sunday"])
        month = st.selectbox("Month", 
                           ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
    
    day_map = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3,
               "Friday": 4, "Saturday": 5, "Sunday": 6}
    month_map = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
                 "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}
    
    if st.button("📊 Predict PM2.5 Level", type="primary", use_container_width=True):
        with st.spinner("Predicting..."):
            try:
                payload = {
                    "NO2": no2,
                    "SO2": so2,
                    "CO": co,
                    "O3": o3,
                    "temperature": temperature,
                    "humidity": humidity,
                    "wind_speed": wind_speed,
                    "hour": hour,
                    "day_of_week": day_map[day_of_week],
                    "month": month_map[month]
                }
                
                response = requests.post(f"{API_URL}/predict/pm25", json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    st.success("✅ Prediction Complete!")
                    
                    pm25_value = result['predicted_pm25']
                    
                    # Display result with gauge
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.metric(
                            label="Predicted PM2.5",
                            value=f"{pm25_value:.2f} μg/m³"
                        )
                        
                        # Health implication
                        if pm25_value <= 12:
                            st.success("🟢 Good")
                        elif pm25_value <= 35.4:
                            st.info("🟡 Moderate")
                        elif pm25_value <= 55.4:
                            st.warning("🟠 Unhealthy for Sensitive")
                        elif pm25_value <= 150.4:
                            st.warning("🟠 Unhealthy")
                        else:
                            st.error("🔴 Very Unhealthy")
                    
                    with col2:
                        # Gauge chart
                        fig = go.Figure(go.Indicator(
                            mode="gauge+number",
                            value=pm25_value,
                            domain={'x': [0, 1], 'y': [0, 1]},
                            title={'text': "PM2.5 Level (μg/m³)"},
                            gauge={
                                'axis': {'range': [None, 200]},
                                'bar': {'color': "darkblue"},
                                'steps': [
                                    {'range': [0, 12], 'color': "lightgreen"},
                                    {'range': [12, 35.4], 'color': "yellow"},
                                    {'range': [35.4, 55.4], 'color': "orange"},
                                    {'range': [55.4, 150.4], 'color': "red"},
                                    {'range': [150.4, 200], 'color': "darkred"}
                                ],
                                'threshold': {
                                    'line': {'color': "black", 'width': 4},
                                    'thickness': 0.75,
                                    'value': pm25_value
                                }
                            }
                        ))
                        fig.update_layout(height=300)
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error(f"❌ Error: {response.status_code}")
            except Exception as e:
                st.error(f"❌ Connection Error: {str(e)}")
                st.info("Make sure the API server is running:\n`uvicorn src.api:app --reload`")

# BATCH ANALYSIS PAGE
elif page == "📈 Batch Analysis":
    st.header("📈 Batch Analysis")
    st.markdown("Compare air quality predictions for multiple scenarios.")
    
    st.subheader("Enter Multiple Scenarios")
    
    num_scenarios = st.number_input("Number of scenarios", min_value=1, max_value=5, value=2)
    
    scenarios = []
    
    for i in range(num_scenarios):
        with st.expander(f"Scenario {i+1}", expanded=(i==0)):
            col1, col2 = st.columns(2)
            
            with col1:
                pm25 = st.number_input(f"PM2.5", 0.0, 500.0, 50.0, key=f"pm25_{i}")
                pm10 = st.number_input(f"PM10", 0.0, 600.0, 100.0, key=f"pm10_{i}")
                no2 = st.number_input(f"NO2", 0.0, 400.0, 40.0, key=f"no2_{i}")
            
            with col2:
                so2 = st.number_input(f"SO2", 0.0, 300.0, 10.0, key=f"so2_{i}")
                co = st.number_input(f"CO", 0.0, 500.0, 80.0, key=f"co_{i}")
                o3 = st.number_input(f"O3", 0.0, 400.0, 60.0, key=f"o3_{i}")
            
            scenarios.append({
                "PM2_5": pm25, "PM10": pm10, "NO2": no2,
                "SO2": so2, "CO": co, "O3": o3,
                "temperature": 25.0, "humidity": 60.0, "wind_speed": 3.0,
                "hour": 12, "day_of_week": 2, "month": 6
            })
    
    if st.button("🔄 Analyze All Scenarios", type="primary", use_container_width=True):
        with st.spinner("Analyzing..."):
            try:
                response = requests.post(f"{API_URL}/predict/batch", json=scenarios)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    st.success(f"✅ Analyzed {result['count']} scenarios!")
                    
                    # Create comparison dataframe
                    comparison_data = []
                    for i, pred in enumerate(result['predictions']):
                        comparison_data.append({
                            'Scenario': f"Scenario {i+1}",
                            'Category': pred['aqi_category'],
                            'Confidence': pred['confidence'] * 100
                        })
                    
                    df = pd.DataFrame(comparison_data)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("📊 Results Table")
                        st.dataframe(df, use_container_width=True)
                    
                    with col2:
                        st.subheader("📈 Confidence Comparison")
                        fig = px.bar(df, x='Scenario', y='Confidence',
                                    color='Category',
                                    title='Prediction Confidence by Scenario')
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error(f"❌ Error: {response.status_code}")
            except Exception as e:
                st.error(f"❌ Connection Error: {str(e)}")

# ABOUT PAGE
elif page == "ℹ️ About":
    st.header("ℹ️ About This Project")
    
    st.markdown("""
    ## 🌍 Air Quality Intelligence System
    
    A complete MLOps pipeline for air quality prediction and analysis.
    
    ### 🎯 Features
    - **AQI Classification**: Predict air quality categories
    - **PM2.5 Regression**: Forecast particulate matter levels
    - **Batch Analysis**: Compare multiple scenarios
    - **Real-time Predictions**: Fast API-based inference
    
    ### 🤖 Machine Learning Models
    1. **Random Forest Classifier** (100% accuracy)
       - Predicts AQI categories
       - 5 classes: Good, Moderate, Unhealthy for Sensitive, Unhealthy, Very Unhealthy
    
    2. **Gradient Boosting Regressor** (R² = 0.924)
       - Forecasts PM2.5 concentrations
       - Weather-based predictions
    
    3. **K-Means Clustering**
       - Groups cities by pollution patterns
       - 3 clusters identified
    
    ### 🛠️ Technology Stack
    - **Backend**: FastAPI, Prefect
    - **Frontend**: Streamlit
    - **ML**: Scikit-learn, Pandas, NumPy
    - **Deployment**: Docker, Docker Compose
    - **Testing**: Pytest
    - **CI/CD**: GitHub Actions
    
    ### 📊 Dataset
    - **Size**: 7,300 records
    - **Time span**: 2 years
    - **Cities**: 10 global cities
    - **Features**: 16 pollutant and weather measurements
    
    ### 👨‍💻 Developer
    **Bingbang** - BS AI, GIKI
    
    AI321L Machine Learning - MLOps Project
    
    ### 📚 Documentation
    - [GitHub Repository](#)
    - [Project Report](#)
    - [API Documentation](http://127.0.0.1:8000/docs)
    
    ---
    
    **Version**: 1.0.0  
    **Last Updated**: December 2025
    """)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🌍 Air Quality Intelligence System | Built with ❤️ using Streamlit & FastAPI</p>
</div>
""", unsafe_allow_html=True)
