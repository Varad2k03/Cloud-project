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

    vehicle_encoded = le.transform([vehicle])[0]

    time_total = v_tat + c_tat
    distance_rating = distance * driver_rating
    distance_time = distance / (time_total + 1)

    prediction = model.predict([[
        distance,
        vehicle_encoded,
        driver_rating,
        customer_rating,
        time_total,
        distance_rating,
        distance_time
    ]])[0]

    st.success(f"Predicted Price: ₹{prediction:.2f}")

    # =========================
    # STORE IN MYSQL
    # =========================
    query = """
    INSERT INTO predictions 
    (distance, vehicle, driver_rating, customer_rating, v_tat, c_tat, predicted_price)
    VALUES (%s,%s,%s,%s,%s,%s,%s)
    """

    values = (distance, vehicle, driver_rating, customer_rating, v_tat, c_tat, prediction)

    cursor.execute(query, values)
    conn.commit()
