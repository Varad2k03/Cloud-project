import streamlit as st
import pickle
import os

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
st.title("🚕 Ride Price Prediction")

distance = st.number_input("Ride Distance (km)", min_value=1.0)
vehicle = st.selectbox("Vehicle Type", [
    'Auto','Bike','eBike','Mini',
    'Prime Plus','Prime Sedan','Prime SUV'
])
driver_rating = st.slider("Driver Rating", 1.0, 5.0)
customer_rating = st.slider("Customer Rating", 1.0, 5.0)
v_tat = st.number_input("Vehicle TAT")
c_tat = st.number_input("Customer TAT")

# =========================
# PREDICT
# =========================
if st.button("Predict Price"):

    # =========================
    # FEATURE ENGINEERING
    # =========================
    vehicle_encoded = le.transform([vehicle])[0]

    time_total = v_tat + c_tat
    distance_rating = distance * driver_rating
    distance_time = distance / (time_total + 1)

    # =========================
    # ML PREDICTION
    # =========================
    ml_price = model.predict([[
        distance,
        vehicle_encoded,
        driver_rating,
        customer_rating,
        time_total,
        distance_rating,
        distance_time
    ]])[0]

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

    # Base rule price
    rule_price = base_fare + (distance * price_per_km)

    # Apply vehicle multiplier
    rule_price *= vehicle_factor.get(vehicle, 1.0)

    # Driver rating adjustment
    rule_price *= (1 + (driver_rating - 3) * 0.05)

    # Optional: surge pricing
    if time_total > 30:
        rule_price *= 1.2

    # =========================
    # FINAL HYBRID PRICE 🔥
    # =========================
    final_price = (0.3 * ml_price) + (0.7 * rule_price)

    # =========================
    # DISPLAY RESULT
    # =========================
    st.success(f"💰 Estimated Ride Price: ₹{final_price:.2f}")

    # Optional breakdown (looks professional 🔥)
    with st.expander("📊 Price Breakdown"):
        st.write(f"ML Prediction: ₹{ml_price:.2f}")
        st.write(f"Rule-based Price: ₹{rule_price:.2f}")

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
        final_price   # 🔥 store corrected price
    )

    cursor.execute(query, values)
    conn.commit()
