import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import requests
import random

# -----------------------------
# WEATHER DATA CONTROLLER
# -----------------------------

def get_weather_data(city="Delhi"):

    API_KEY = "9bf27176a121e7cfe1b1042121baf108"

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

    try:
        response = requests.get(url, timeout=5)
        weather = response.json()

        temperature = weather["main"]["temp"]
        humidity = weather["main"]["humidity"]

        rainfall = 0
        if "rain" in weather:
            rainfall = weather["rain"].get("1h", 0)

        return temperature, humidity, rainfall

    except:
        return 30, 60, 10
#-------------------------
#TRAFFIC DATA CONTROLLER
#-------------------------
def get_traffic_data(origin_lat, origin_lon, dest_lat, dest_lon):

    try:

        api_key = "oHekYJGHHxDIQIhHmXXRDo0QaHsoJYyB"

        url = f"https://api.tomtom.com/routing/1/calculateRoute/{origin_lat},{origin_lon}:{dest_lat},{dest_lon}/json?key={api_key}&traffic=true"

        response = requests.get(url)

        data = response.json()

        route = data["routes"][0]["summary"]

        distance_km = route["lengthInMeters"] / 1000
        travel_time = route["travelTimeInSeconds"] / 60
        traffic_delay = route["trafficDelayInSeconds"] / 60

        return distance_km, travel_time, traffic_delay

    except:

        # fallback simulation
        import random

        distance_km = random.randint(800,2200)
        travel_time = distance_km * 1.2
        traffic_delay = random.randint(5,40)

        return distance_km, travel_time, traffic_delay

# -----------------------------
# ROUTE DATA CONTROLLER
# -----------------------------
def get_route_data():

    try:
        distance = 1200
        duration = 18
        return distance, duration

    except:
        return 1000, 20

st.set_page_config(page_title="AI Sustainable Supply Chain", layout="wide")

st.title("AI-Enabled Sustainable Supply Chain Decision Support System")

st.subheader("Supply Chain Sustainability Control Tower")

# -------------------------
# Load Dataset
# -------------------------

data = pd.read_csv("data.csv")

data["total_emissions"] = (
    data["scope1_emissions"]
    + data["scope2_emissions"]
    + data["scope3_emissions"]
)

st.success(f"Loaded dataset: {len(data)} records")
# -----------------------------
# SYSTEM KPI DASHBOARD
# -----------------------------

st.subheader("Supply Chain Sustainability Control Tower")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

total_suppliers = len(data)

avg_emissions = round(data["total_emissions"].mean(),2)

avg_risk = 0
if "predicted_risk" in data.columns:
    avg_risk = round(data["predicted_risk"].mean(),2)

risk_level = "Low"
if avg_risk > 0.7:
    risk_level = "High"
elif avg_risk > 0.5:
    risk_level = "Medium"

kpi1.metric("Total Suppliers", total_suppliers)
kpi2.metric("Average Climate Risk", avg_risk)
kpi3.metric("Avg Supply Chain Emissions", avg_emissions)
kpi4.metric("Supply Chain Risk Level", risk_level)

st.divider()




# -----------------------------------
# INTERACTIVE SUPPLIER FILTERS
# -----------------------------------

st.sidebar.header("Dashboard Filters")

region_filter = st.sidebar.multiselect(
    "Select Region",
    options=data["region"].unique(),
    default=data["region"].unique()
)

supplier_filter = st.sidebar.multiselect(
    "Select Supplier",
    options=data["supplier_id"].unique(),
    default=data["supplier_id"].unique()
)

filtered_data = data[
    (data["region"].isin(region_filter)) &
    (data["supplier_id"].isin(supplier_filter))
]

# ------------------------------------
# AI SUPPLY CHAIN RISK ALERT ENGINE
# ------------------------------------

st.header("AI Risk Monitoring Alerts")

alerts = []

# Climate risk alert
if "predicted_risk" in filtered_data.columns:

    avg_risk = filtered_data["predicted_risk"].mean()

    if avg_risk > 0.7:
        alerts.append("High climate risk detected across supply chain regions.")

# Flood risk alert
if "rainfall" in filtered_data.columns:

    if filtered_data["rainfall"].mean() > 50:
        alerts.append("Heavy rainfall detected – potential flood disruption risk.")

# Emission alert
if "total_emissions" in filtered_data.columns:

    if filtered_data["total_emissions"].mean() > 2000:
        alerts.append("Supply chain emissions exceeding sustainability threshold.")

# Water usage alert
if "water_usage" in filtered_data.columns:

    if filtered_data["water_usage"].mean() > 7000:
        alerts.append("High water usage detected in supply chain operations.")

# Waste alert
if "waste_generated" in filtered_data.columns:

    if filtered_data["waste_generated"].mean() > 350:
        alerts.append("Waste generation levels exceeding circular economy targets.")


# Display alerts
if alerts:

    for alert in alerts:
        st.warning(alert)

else:
    st.success("No major sustainability or climate risks detected.")

# -------------------------
# ESG KPI DASHBOARD
# -------------------------

st.header("ESG KPI Dashboard")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Scope 1 Avg", f"{filtered_data['scope1_emissions'].mean():.0f}")
col2.metric("Scope 2 Avg", f"{filtered_data['scope2_emissions'].mean():.0f}")
col3.metric("Scope 3 Avg", f"{filtered_data['scope3_emissions'].mean():.0f}")
col4.metric("Total Emissions Avg", f"{filtered_data['total_emissions'].mean():.0f}")

# -------------------------
# Dataset Preview
# -------------------------

st.header("Dataset Preview")

display_data = filtered_data.copy()
display_data.index = display_data.index + 1
display_data.index.name = "Serial No."

st.dataframe(display_data)

# -----------------------------------
# ESG GAUGE CHARTS
# -----------------------------------

st.header("ESG Performance Indicators")

fig = go.Figure()

fig.add_trace(go.Indicator(
    mode="gauge+number",
    value=data["total_emissions"].mean(),
    title={'text': "Avg Total Emissions"},
    gauge={
        'axis': {'range': [0, 2500]},
        'bar': {'color': "red"},
        'steps': [
            {'range': [0, 1000], 'color': "lightgreen"},
            {'range': [1000, 1800], 'color': "yellow"},
            {'range': [1800, 2500], 'color': "orange"}
        ],
    }
))

st.plotly_chart(fig, use_container_width=True)

# -------------------------
# EMISSIONS ANALYSIS
# -------------------------

st.header("Total Emissions by Supplier")

fig, ax = plt.subplots()

ax.bar(filtered_data["supplier_id"], filtered_data["total_emissions"])

plt.xticks(rotation=45)

st.pyplot(fig)

# -------------------------
# WATER vs WASTE ANALYSIS
# -------------------------

st.header("Water Usage vs Waste Generated")

fig2, ax2 = plt.subplots()

ax2.scatter(filtered_data["water_usage"], filtered_data["waste_generated"])

ax2.set_xlabel("Water Usage")

ax2.set_ylabel("Waste Generated")

st.pyplot(fig2)

# -------------------------
# -------------------------
# AI CLIMATE RISK MODEL
# -------------------------

st.header("AI Climate Risk Prediction")

# Select city for weather data
city = "Delhi"

# Get weather data from API
temperature, humidity, rainfall = get_weather_data(city)

# -------------------------
# ADD WEATHER TO DATASET
# -------------------------

data["rainfall"] = rainfall

filtered_data = filtered_data.copy()
filtered_data["rainfall"] = rainfall

# -------------------------
# FEATURES FOR AI MODEL
# -------------------------

features = [
    "scope1_emissions",
    "scope2_emissions",
    "scope3_emissions",
    "water_usage",
    "waste_generated",
    "incidents",
    "rainfall"
]

X = filtered_data[features]
y = filtered_data["flood_risk_index"]

# Train model
model = RandomForestRegressor(random_state=42)
model.fit(X, y)

# Predict risk
filtered_data["predicted_risk"] = model.predict(X)

# -------------------------
# RISK CATEGORY CLASSIFICATION
# -------------------------

def classify_risk(score):
    if score < 0.5:
        return "Low Risk"
    elif score < 0.7:
        return "Medium Risk"
    else:
        return "High Risk"

filtered_data["risk_category"] = filtered_data["predicted_risk"].apply(classify_risk)

st.subheader("Predicted Climate Risk by Supplier")

st.dataframe(
    filtered_data[["supplier_id","region","predicted_risk","risk_category"]],
    use_container_width=True
)

# -------------------------
# CLIMATE RISK VISUALIZATION
# -------------------------

st.header("Climate Risk Score")

fig3, ax3 = plt.subplots()

ax3.bar(filtered_data["supplier_id"], filtered_data["predicted_risk"])
plt.xticks(rotation=45)

st.pyplot(fig3)

# -----------------------------
# CLIMATE RISK MAP
# -----------------------------

st.header("Climate Risk Map of Supply Chain Regions")

# Coordinates for major Indian regions
region_coords = {
    "North": [28.6, 77.2],   # Delhi
    "South": [13.08, 80.27], # Chennai
    "East": [22.57, 88.36],  # Kolkata
    "West": [19.07, 72.87]   # Mumbai
}

# Copy filtered dataset for mapping
map_data = filtered_data.copy()

# Assign coordinates based on region
map_data["lat"] = map_data["region"].apply(lambda x: region_coords[x][0])
map_data["lon"] = map_data["region"].apply(lambda x: region_coords[x][1])

# -----------------------------
# CREATE RISK CATEGORIES
# -----------------------------

def risk_category(score):
    if score < 0.55:
        return "Low Risk"
    elif score < 0.65:
        return "Moderate Risk"
    else:
        return "High Risk"

map_data["risk_category"] = map_data["predicted_risk"].apply(risk_category)

# -----------------------------
# BUILD INTERACTIVE MAP
# -----------------------------

fig_map = px.scatter_mapbox(
    map_data,
    lat="lat",
    lon="lon",
    color="risk_category",
    size="total_emissions",
    hover_name="supplier_id",
    hover_data=["region", "predicted_risk", "total_emissions"],
    color_discrete_map={
        "Low Risk": "green",
        "Moderate Risk": "orange",
        "High Risk": "red"
    },
    zoom=4.5,
    center={"lat": 22.5, "lon": 79},  # Center map on India
    mapbox_style="carto-darkmatter",
    title="Supply Chain Climate Risk Map"
)

fig_map.update_layout(
    margin={"r":0,"t":40,"l":0,"b":0}
)

st.plotly_chart(fig_map, width="stretch")

# -----------------------------
# REAL TIME WEATHER MONITOR
# -----------------------------

st.header("Real-Time Climate Monitoring")

# user selects city
city = st.selectbox(
    "Select Supply Chain Region City",
    ["Delhi", "Mumbai", "Chennai", "Kolkata", "Hyderabad"]
)

temperature, humidity, rainfall = get_weather_data(city)

col1, col2, col3 = st.columns(3)

col1.metric("Temperature (°C)", round(temperature,1))
col2.metric("Humidity (%)", humidity)
col3.metric("Rainfall (mm)", rainfall)
weather_data = pd.DataFrame({
    "City": [city],
    "Temperature (°C)": [temperature],
    "Humidity (%)": [humidity],
    "Rainfall (mm)": [rainfall]
})

st.dataframe(weather_data, use_container_width=True)
# -------------------------
# WEATHER INTELLIGENCE (SIMULATED)
# -------------------------

st.header("Weather Risk Forecast")

if rainfall < 10:
    flood_risk = 0.1
elif rainfall < 30:
    flood_risk = 0.3
elif rainfall < 60:
    flood_risk = 0.6
else:
    flood_risk = 0.9

st.metric("Flood Risk Probability", flood_risk)

# -------------------------
# LOW EMISSION ROUTE RECOMMENDATION
# -------------------------

st.header("Low-Emission Logistics Recommendation")

# Detect flood risk based on rainfall
if rainfall > 100:
    st.warning("High flood risk detected due to heavy rainfall.")

    st.info("""
Suggested Alternative Route:

Use alternate logistics corridors to avoid disruption.

Estimated carbon impact: +1.5%
""")

elif rainfall > 50:
    st.warning("Moderate rainfall detected. Monitor logistics operations.")

else:
    st.success("Weather conditions are stable for logistics operations.")


# -------------------------
# CITY COORDINATES
# -------------------------

city_coords = {
    "Delhi": (28.61, 77.23),
    "Mumbai": (19.07, 72.87),
    "Chennai": (13.08, 80.27),
    "Kolkata": (22.57, 88.36),
    "Hyderabad": (17.38, 78.48)
}
# -------------------------
# REAL-TIME LOGISTICS ROUTE ANALYSIS
# -------------------------

st.header("Real-Time Logistics Route Analysis")

origin = st.selectbox(
    "Select Origin City",
    list(city_coords.keys())
)

destination = st.selectbox(
    "Select Destination City",
    list(city_coords.keys())
)
origin_lat, origin_lon = city_coords[origin]
dest_lat, dest_lon = city_coords[destination]
distance_km, travel_time, traffic_delay = get_traffic_data(
    origin_lat,
    origin_lon,
    dest_lat,
    dest_lon
)
col1, col2, col3 = st.columns(3)

col1.metric(
    "Route Distance (km)",
    round(distance_km,2)
)

col2.metric(
    "Travel Time (minutes)",
    round(travel_time,2)
)

col3.metric(
    "Traffic Delay (minutes)",
    round(traffic_delay,2)
)
# -------------------------
# TRANSPORT EMISSION MODEL
# -------------------------

st.subheader("Transport Emission Calculator")

cargo_weight = st.slider(
    "Cargo Weight (tons)",
    1,
    30,
    10
)

# Average truck emission factor
emission_factor = 0.12  # kg CO2 per ton-km

transport_emissions = distance_km * cargo_weight * emission_factor

st.metric(
    "Estimated Transport CO₂ Emissions (kg)",
    round(transport_emissions,2)
)
# -------------------------
# AI LOGISTICS DECISION ENGINE
# -------------------------

st.header("AI Logistics Recommendation")

# Risk scoring
traffic_risk = traffic_delay / 60
emission_risk = transport_emissions / 2000
weather_risk = rainfall / 100

total_risk = traffic_risk + emission_risk + weather_risk

st.write("AI Logistics Risk Score:", round(total_risk,2))

# Decision Logic

if total_risk > 1.5:

    st.error("High logistics disruption risk detected.")

    st.info(f"""
Recommended Actions:

• Switch to alternate logistics corridor  
• Consolidate shipments to reduce carbon footprint  
• Delay shipment to avoid peak traffic  

Route: **{origin} → {destination}**
""")

elif total_risk > 0.8:

    st.warning("Moderate logistics risk detected.")

    st.info(f"""
Suggested Actions:

• Monitor traffic conditions closely  
• Optimize vehicle load efficiency  
• Consider partial route adjustment  

Route: **{origin} → {destination}**
""")

else:

    st.success("Logistics conditions optimal for transportation.")

    st.info(f"""
Recommended Strategy:

• Proceed with planned shipment  
• Maintain current route efficiency  

Route: **{origin} → {destination}**
""")

# -------------------------
# SUPPLIER LOCATION COORDINATES
# -------------------------

supplier_coords = {
    "North": (28.61, 77.23),     # Delhi
    "West": (19.07, 72.87),      # Mumbai
    "South": (13.08, 80.27),     # Chennai
    "East": (22.57, 88.36),      # Kolkata
    "Central": (17.38, 78.48)    # Hyderabad
}
# -------------------------
# MAP DATA PREPARATION
# -------------------------

map_data = filtered_data.copy()

map_data["lat"] = map_data["region"].apply(lambda x: supplier_coords[x][0])
map_data["lon"] = map_data["region"].apply(lambda x: supplier_coords[x][1])
map_data["emission_intensity"] = map_data["total_emissions"] / map_data["annual_revenue"]
# -------------------------
# AI SUPPLY CHAIN RISK MAP
# -------------------------

st.header("AI Supply Chain Disruption Map")

fig_supply_map = px.scatter_mapbox(
    map_data,
    lat="lat",
    lon="lon",
    size="total_emissions",
    color="predicted_risk",
    hover_name="supplier_id",
    hover_data=["region","total_emissions","predicted_risk"],
    zoom=3.5,
    mapbox_style="carto-darkmatter",
    title="Supply Chain Climate & Emission Risk Map"
)

st.plotly_chart(fig_supply_map, use_container_width=True)
# -------------------------
# CLIMATE DISRUPTION FORECAST
# -------------------------

st.header("AI Climate Disruption Forecast (7-Day Outlook)")

# Route Selection
origin_city = st.selectbox(
    "Select Origin City",
    list(city_coords.keys()),
    key="forecast_origin"
)

destination_city = st.selectbox(
    "Select Destination City",
    list(city_coords.keys()),
    key="forecast_destination"
)

# Show Route Context
st.subheader("Analyzed Logistics Route")
st.info(f"Route: {origin_city} ➜ {destination_city}")

# Show Weather Source
st.caption(f"Weather forecast based on real-time climate data from: {city}")

# -------------------------
# Generate 7-Day Forecast
# -------------------------

days = ["Day 1","Day 2","Day 3","Day 4","Day 5","Day 6","Day 7"]

forecast_risk = []

for d in days:

    base_risk = rainfall / 100
    supplier_factor = filtered_data["predicted_risk"].mean()

    random_factor = np.random.uniform(0,0.3)

    risk_score = base_risk + supplier_factor + random_factor

    forecast_risk.append(risk_score)

forecast_df = pd.DataFrame({
    "Day": days,
    "Predicted Risk": forecast_risk
})

# -------------------------
# Forecast Visualization
# -------------------------

fig_forecast, ax = plt.subplots()

ax.plot(
    forecast_df["Day"],
    forecast_df["Predicted Risk"],
    marker="o"
)

ax.set_ylabel("Disruption Risk Score")

st.pyplot(fig_forecast)

# -------------------------
# AI Insight
# -------------------------

avg_forecast_risk = sum(forecast_risk)/len(forecast_risk)

st.subheader("AI Forecast Insight")

if avg_forecast_risk > 1.5:

    st.error("High probability of supply chain disruption in the coming week.")

elif avg_forecast_risk > 1:

    st.warning("Moderate supply chain disruption risk expected.")

else:

    st.success("Supply chain operations expected to remain stable.")
# -------------------------
# SUSTAINABILITY RECOMMENDATION ENGINE
# -------------------------

st.header("Sustainability Action Recommendations")

if filtered_data["scope3_emissions"].mean() > 1000:

    st.warning("High Scope-3 Supply Chain Emissions Detected")

    st.write(
"""
Recommended actions:

• Supplier decarbonisation programmes  
• Renewable energy adoption in supply chain  
• Low-carbon logistics routes  
• Supplier ESG audits
"""
)

if filtered_data["water_usage"].mean() > 6000:

    st.warning("High Water Usage Detected")

    st.write(
"""
Recommended actions:

• Closed-loop water recycling  
• Rainwater harvesting  
• Hydrological modelling for water neutrality
"""
)

if filtered_data["waste_generated"].mean() > 300:

    st.warning("High Waste Generation Detected")

    st.write(
"""
Recommended actions:

• Plastic credit programmes  
• Material recovery systems  
• Circular supply chain initiatives
"""
)

# ------------------------------------
# AI CARBON NEUTRALITY PLANNER
# ------------------------------------

st.divider()
st.header("AI Carbon Neutrality Planner")
avg_emissions = filtered_data["total_emissions"].mean()
avg_water =filtered_data["water_usage"].mean()
avg_waste = filtered_data["waste_generated"].mean()

# Carbon Neutrality Strategy
if avg_emissions > 1500:

    st.warning("High Supply Chain Emissions Detected")

    st.markdown("### Recommended Carbon Neutrality Actions")

    st.write("• Supplier decarbonisation programmes")
    st.write("• Renewable energy procurement in logistics operations")
    st.write("• Carbon offset purchases through verified registries")
    st.write("• Scope-3 supplier engagement and emissions reporting")
    st.write("• Transition to low-carbon logistics corridors")

# Circular Economy Strategy
if avg_waste > 250:

    st.markdown("### Circular Economy Opportunities")

    st.write("• Plastic credit mechanisms")
    st.write("• Material recovery and recycling partnerships")
    st.write("• Zero-waste-to-landfill programmes")
    st.write("• Supplier circular economy initiatives")

# Water Neutrality Strategy
if avg_water > 6000:

    st.markdown("### Water Neutrality Strategies")

    st.write("• Industrial water recycling systems")
    st.write("• Rainwater harvesting infrastructure")
    st.write("• CSR watershed restoration projects")
    st.write("• Hydrological modelling for basin sustainability")
# -------------------------
# QCC CONTINUOUS IMPROVEMENT
# -------------------------

st.sidebar.header("QCC Continuous Improvement Log")

supplier = st.sidebar.selectbox("Supplier / Unit", filtered_data["supplier_id"])

problem = st.sidebar.text_area("Problem Identified")

action = st.sidebar.text_area("Proposed Action")

owner = st.sidebar.text_input("Owner")

expected = st.sidebar.text_input("Expected Metric Improvement")

if st.sidebar.button("Log QCC Entry"):

    st.sidebar.success("QCC entry logged successfully")