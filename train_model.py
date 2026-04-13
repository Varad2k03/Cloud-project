import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import pickle

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder

# =========================
# LOAD DATA
# =========================
df = pd.read_excel("Bookings.xlsx")

# =========================
# SELECT COLUMNS
# =========================
df = df[[
    'Ride_Distance',
    'Vehicle_Type',
    'Driver_Ratings',
    'Customer_Rating',
    'V_TAT',
    'C_TAT',
    'Booking_Value'
]]

# =========================
# HANDLE MISSING VALUES
# =========================
df.fillna(df.median(numeric_only=True), inplace=True)
df['Vehicle_Type'].fillna(df['Vehicle_Type'].mode()[0], inplace=True)

# =========================
# REMOVE OUTLIERS
# =========================
df = df[df['Ride_Distance'] > 2]
df = df[df['Booking_Value'] < df['Booking_Value'].quantile(0.95)]

# =========================
# ENCODE VEHICLE TYPE
# =========================
vehicle_types = [
    'Auto','Bike','eBike','Mini',
    'Prime Plus','Prime Sedan','Prime SUV'
]

le = LabelEncoder()
le.fit(vehicle_types)
df['Vehicle_Type'] = le.transform(df['Vehicle_Type'])

# =========================
# FEATURE ENGINEERING
# =========================
df['Time_Total'] = df['V_TAT'] + df['C_TAT']
df['Distance_Rating'] = df['Ride_Distance'] * df['Driver_Ratings']
df['Distance_Time'] = df['Ride_Distance'] / (df['Time_Total'] + 1)

# =========================
# FEATURES & TARGET
# =========================
X = df[[
    'Ride_Distance',
    'Vehicle_Type',
    'Driver_Ratings',
    'Customer_Rating',
    'Time_Total',
    'Distance_Rating',
    'Distance_Time'
]]

y = df['Booking_Value']

# =========================
# TRAIN MODEL
# =========================
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = RandomForestRegressor(
    n_estimators=400,
    max_depth=10,
    random_state=42
)

model.fit(X_train, y_train)

# =========================
# SAVE MODEL
# =========================
pickle.dump(model, open("ride_price_model.pkl", "wb"))
pickle.dump(le, open("vehicle_encoder.pkl", "wb"))

print("✅ Model & Encoder Saved")