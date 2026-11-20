# FoodieHub – Food Ordering System

## 1. Project Title and Brief Description

**FoodieHub** is a web-based Food Ordering System developed using Python Flask and SQLite. It allows customers to browse food items, search and filter menus, add items to a shopping cart, and place orders online.

The application also provides an administrator dashboard to manage food availability and update order statuses.

## 2. Problem Statement and Objectives

### Problem Statement

Traditional food ordering methods may require customers to visit restaurants or contact them directly to view menus and place orders. This process can be time-consuming and inconvenient.

FoodieHub provides a simple web-based platform that allows customers to browse available food items, manage their cart, and place orders through a single application.

### Objectives

- To develop a user-friendly online food ordering application.
- To provide customer registration and login functionality.
- To display food items with their prices and categories.
- To implement food search, category filtering, and price sorting.
- To allow customers to add, update, and remove cart items.
- To provide online order placement and order history.
- To provide administrative facilities for managing food items and orders.
- To use Git and GitHub for version control and project management.

## 3. Features / Modules Implemented

### 3.1 User Registration
- Allows new customers to create an account.
- Validates user details, email format, and password.
- Checks password confirmation.

### 3.2 User Login and Logout
- Allows registered users to log in.
- Verifies passwords securely using password hashing.
- Maintains user sessions.
- Provides logout functionality.

### 3.3 Food Menu
- Displays available food items.
- Organizes food items into categories.
- Supports searching food items by name or description.
- Provides category filtering.
- Supports sorting food prices from low to high and high to low.

### 3.4 Shopping Cart
- Allows customers to add food items to the cart.
- Allows customers to update item quantities.
- Allows customers to remove items.
- Automatically calculates subtotal and delivery charges.

### 3.5 Checkout and Order Placement
- Collects customer delivery details.
- Validates address, city, and six-digit pincode.
- Calculates the total order amount.
- Saves order details in the database.

### 3.6 Order History
- Displays previously placed orders.
- Shows order information and status.

### 3.7 Admin Dashboard
- Displays customer, food, order, and revenue information.
- Allows administrators to add food items.
- Allows administrators to enable or disable food availability.
- Allows administrators to update order statuses.

## 4. Technology Stack and Tools Used

| Technology / Tool | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web application framework |
| SQLite | Database management |
| HTML | Web page structure |
| CSS | Web page styling |
| Jinja2 | Dynamic HTML template rendering |
| Werkzeug | Password hashing and verification |
| Git | Version control |
| GitHub | Remote repository hosting |
| Visual Studio Code | Code editing and development |

## 5. Prerequisites and Installation Steps

### Prerequisites

The following software is required:

- Windows 10/11 or compatible operating system.
- Python 3.x.
- Git.
- Visual Studio Code or another code editor.
- Google Chrome, Microsoft Edge, or another modern browser.
- Internet connection for cloning and accessing the GitHub repository.

### Installation Steps

**Step 1: Clone the GitHub Repository**

Open the terminal and execute:

```bash
git clone https://github.com/sathyasureshmani-max/Food-Ordering-System.git
```

**Step 2: Navigate to the Project Folder**

```bash
cd Food-Ordering-System
```

**Step 3: Create a Virtual Environment**

```bash
python -m venv venv
```

**Step 4: Activate the Virtual Environment**

For Windows:

```bash
venv\Scripts\activate
```

**Step 5: Install Dependencies**

```bash
pip install -r requirements.txt
```

If Flask is not included in the requirements file, install it using:

```bash
pip install Flask
```

## 6. Instructions to Run the Application

**Step 1:** Open the project directory in Visual Studio Code.

**Step 2:** Activate the virtual environment.

**Step 3:** Install the required dependencies.

**Step 4:** Run the Flask application:

```bash
python app.py
```

**Step 5:** Open a web browser and visit:

```text
http://127.0.0.1:5000/
```

The application initializes the SQLite database automatically when `app.py` is executed directly.

## 7. Sample Inputs and Outputs

| Operation | Sample Input | Expected Output |
|---|---|---|
| Registration | Name, email, password | Account created successfully |
| Login | Registered email and password | User logged in |
| Food Search | Pizza | Matching food items displayed |
| Price Sorting | Price High to Low | Food items sorted by descending price |
| Add to Cart | Select a food item | Item added to shopping cart |
| Update Cart | Change quantity to 2 | Cart total recalculated |
| Checkout | Address, city, six-digit pincode | Order placed successfully |
| Order History | Open My Orders | Previously placed orders displayed |

## 8. Testing Performed and Results

The application should be tested using the following test cases:

| Test Case | Description | Expected Result |
|---|---|---|
| TC01 | Open home page | Home page loads successfully |
| TC02 | Register a new customer | Customer account is created |
| TC03 | Login with valid credentials | User login is successful |
| TC04 | Search for food items | Matching items are displayed |
| TC05 | Filter by food category | Selected category items are displayed |
| TC06 | Sort food prices | Items are arranged according to selected price order |
| TC07 | Add items to cart | Selected items appear in the cart |
| TC08 | Update or remove cart items | Cart is updated correctly |
| TC09 | Place an order | Order details are saved |
| TC10 | Access admin dashboard | Authorized administrator can access dashboard |

**Testing Status:** Record the actual result of each test after executing it. Include screenshots of successful tests in the assignment report.


## 9. Known Limitations and Future Enhancements

### Known Limitations

- The application uses SQLite as its database.
- Online payment gateway integration is not implemented.
- The application currently runs using Flask's development server.
- Additional security configuration is required before production deployment.

### Future Enhancements

- Integration of online payment gateways.
- Real-time order tracking.
- Email and SMS order notifications.
- Improved administrator food management.
- Deployment to a cloud hosting platform.
- Additional security and automated testing features.

## 10. Git and GitHub Repository

**GitHub Repository:**

https://github.com/sathyasureshmani-max/Food-Ordering-System

### Version Control

Git was used to manage project versions and track source-code changes.

A separate feature branch was created:

```bash
git switch -c feature/food-ordering
```

The food price-sorting feature was implemented and committed:

```bash
git add app.py templates/menu.html
git commit -m "Add food price sorting feature"
```

The feature branch was pushed to GitHub:

```bash
git push -u origin feature/food-ordering
```

A pull request was created and successfully merged into the `main` branch.

