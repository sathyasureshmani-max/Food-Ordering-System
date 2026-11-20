# FoodieHub - Realistic Food Ordering System

A Flask + SQLite mini-project with customer registration/login, menu search, cart, checkout, delivery address/location capture, order history and an admin dashboard.

## Run
1. Open the project in VS Code.
2. Create/activate a virtual environment.
3. Install dependencies:
   `pip install -r requirements.txt`
4. Start:
   `python app.py`
5. Open `http://127.0.0.1:5000`

## Admin demo
Email: admin@foodiehub.com
Password: Admin@123

## Important
Customer accounts use hashed passwords. A customer must login with the same email and password used during registration.

Checkout supports manual delivery address and optional browser geolocation. The browser may ask for location permission. If permission is denied, manual address entry still works.

This is an academic project and does not process real online payments.
