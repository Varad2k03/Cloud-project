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
    base_fare = 30
    price_per_km = 15

    vehicle_factor = {
        'Auto': 1.0,
        'Bike': 0.8,
        'eBike': 0.85,
        'Mini': 1.2,
        'Prime Plus': 1.4,
        'Prime Sedan': 1.5,
        'Prime SUV': 1.8
    }

    # Base price
    rule_price = base_fare + (distance * price_per_km)

    # Vehicle multiplier
    rule_price *= vehicle_factor.get(vehicle, 1.0)

    # Driver rating adjustment
    rule_price *= (1 + (driver_rating - 3) * 0.05)

    # Optional surge pricing
    time_total = v_tat + c_tat
    if time_total > 30:
        rule_price *= 1.2

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
