CREATE TABLE predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    distance FLOAT,
    vehicle VARCHAR(50),
    driver_rating FLOAT,
    customer_rating FLOAT,
    v_tat FLOAT,
    c_tat FLOAT,
    predicted_price FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);