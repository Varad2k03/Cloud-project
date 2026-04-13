import streamlit as st
import pickle
import os

# =========================
# LOAD MODEL & ENCODER (optional, not used now)
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model_path = os.path.join(BASE_DIR, "ride_price_model.pkl")
encoder_path = os.path.join(BASE_DIR, "vehicle_encoder.pkl")

model = pickle.load(open(model_path, "rb"))
le = pickle.load(open(encoder_path, "rb"))

# =========================
# MYSQL CONNECTION (Railway)
# =========================
from db_config import get_connection

conn = get_connection()
cursor = conn.cursor()

# =========================
# UI
# =========================
st.set_page_config(page_title="Ride Price Predictor", page_icon="🚕")

st.title("🚕 Ride Price Prediction")
st.markdown("### Enter ride details to estimate fare")

distance = st.number_input("Ride Distance (km)", min_value=1.0)
vehicle = st.selectbox("Vehicle Type", [
    'Auto','Bike','eBike','Mini',
    'Prime Plus','Prime Sedan','Prime SUV'
])
driver_rating = st.slider("Driver Rating", 1.0, 5.0, 4.0)
customer_rating = st.slider("Customer Rating", 1.0, 5.0, 4.0)
v_tat = st.number_input("Vehicle Arrival Time (min)", min_value=0)
c_tat = st.number_input("Customer Wait Time (min)", min_value=0)

# =========================
# PREDICT
# =========================
if st.button("🚀 Predict Price"):

    # =========================
    # REAL-WORLD RULE PRICING 🔥
    # =========================

    # Base fare (higher)
    base_fare = 50
    
    # Price per km (better)
    price_per_km = 18
    
    # Minimum fare (important 🔥)
    minimum_fare = 120
    
    # Vehicle multipliers (more realistic)
    vehicle_factor = {
        'Auto': 1.0,
        'Bike': 0.7,
        'eBike': 0.75,
        'Mini': 1.3,
        'Prime Plus': 1.5,
        'Prime Sedan': 1.7,
        'Prime SUV': 2.0
    }
    
    # Base price
    rule_price = base_fare + (distance * price_per_km)
    
    # Apply vehicle factor
    rule_price *= vehicle_factor.get(vehicle, 1.0)
    
    # Apply minimum fare
    rule_price = max(rule_price, minimum_fare)
    
    # Driver rating effect
    rule_price *= (1 + (driver_rating - 3) * 0.05)
    
    # Surge pricing
    time_total = v_tat + c_tat
    if time_total > 20:
        rule_price *= 1.25

    # Final price
    final_price = rule_price

    # =========================
    # DISPLAY RESULT
    # =========================
    st.success(f"💰 Estimated Ride Price: ₹{final_price:.2f}")

    # =========================
    # STORE IN MYSQL
    # =========================
    query = """
    INSERT INTO predictions 
    (distance, vehicle, driver_rating, customer_rating, v_tat, c_tat, predicted_price)
    VALUES (%s,%s,%s,%s,%s,%s,%s)
    """

    values = (
        distance,
        vehicle,
        driver_rating,
        customer_rating,
        v_tat,
        c_tat,
        final_price
    )

    cursor.execute(query, values)
    conn.commit()

    st.info("📦 Data saved to database successfully!")
