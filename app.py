from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
import re

app = Flask(__name__)
app.secret_key = "foodiehub-change-this-secret-key"
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "foodiehub.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL COLLATE NOCASE,
        password TEXT NOT NULL,
        phone TEXT,
        role TEXT NOT NULL DEFAULT 'customer',
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    );

    CREATE TABLE IF NOT EXISTS foods (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        image TEXT,
        is_available INTEGER NOT NULL DEFAULT 1,
        FOREIGN KEY(category_id) REFERENCES categories(id)
    );

    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        total REAL NOT NULL,
        status TEXT NOT NULL DEFAULT 'Placed',
        payment_method TEXT NOT NULL DEFAULT 'Cash on Delivery',
        address TEXT NOT NULL,
        landmark TEXT,
        city TEXT NOT NULL,
        pincode TEXT NOT NULL,
        latitude TEXT,
        longitude TEXT,
        notes TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        food_id INTEGER NOT NULL,
        food_name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL,
        FOREIGN KEY(order_id) REFERENCES orders(id) ON DELETE CASCADE,
        FOREIGN KEY(food_id) REFERENCES foods(id)
    );
    """)

    categories = ["Pizza", "Burgers", "Biryani", "Starters", "Drinks", "Desserts"]
    for name in categories:
        conn.execute("INSERT OR IGNORE INTO categories(name) VALUES (?)", (name,))

    food_seed = [
        ("Pizza", "Margherita Pizza", "Classic tomato, mozzarella and Italian herbs.", 249, "🍕"),
        ("Pizza", "Farmhouse Pizza", "Onion, capsicum, tomato and fresh vegetables.", 329, "🍕"),
        ("Burgers", "Classic Chicken Burger", "Crispy chicken, lettuce, cheese and house sauce.", 199, "🍔"),
        ("Burgers", "Veg Supreme Burger", "Veg patty with cheese, lettuce and signature sauce.", 169, "🍔"),
        ("Biryani", "Chicken Biryani", "Aromatic basmati rice, chicken and traditional spices.", 279, "🍛"),
        ("Biryani", "Veg Biryani", "Fragrant basmati rice with vegetables and spices.", 229, "🍛"),
        ("Starters", "French Fries", "Crispy golden fries with seasoning.", 119, "🍟"),
        ("Starters", "Chicken 65", "Crispy spicy chicken bites.", 219, "🍗"),
        ("Drinks", "Fresh Lime Soda", "Refreshing lime soda served chilled.", 79, "🥤"),
        ("Drinks", "Cold Coffee", "Creamy chilled coffee.", 129, "☕"),
        ("Desserts", "Chocolate Brownie", "Warm chocolate brownie.", 149, "🍫"),
        ("Desserts", "Gulab Jamun", "Soft milk-solid dumplings in sugar syrup.", 99, "🍮"),
    ]
    for category, name, desc, price, image in food_seed:
        cat = conn.execute("SELECT id FROM categories WHERE name=?", (category,)).fetchone()
        exists = conn.execute("SELECT id FROM foods WHERE name=?", (name,)).fetchone()
        if not exists:
            conn.execute(
                """INSERT INTO foods(category_id,name,description,price,image)
                   VALUES (?,?,?,?,?)""",
                (cat["id"], name, desc, price, image)
            )

    admin = conn.execute("SELECT id FROM users WHERE email=?", ("admin@foodiehub.com",)).fetchone()
    if not admin:
        conn.execute(
            """INSERT INTO users(name,email,password,phone,role,created_at)
               VALUES (?,?,?,?,?,?)""",
            ("FoodieHub Admin", "admin@foodiehub.com",
             generate_password_hash("Admin@123"), "9999999999", "admin",
             datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
    conn.commit()
    conn.close()

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login to continue.", "warning")
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped

def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get("role") != "admin":
            flash("Admin access required.", "danger")
            return redirect(url_for("home"))
        return view(*args, **kwargs)
    return wrapped

@app.context_processor
def inject_globals():
    cart = session.get("cart", {})
    return {"cart_count": sum(cart.values()), "current_user": session.get("user_name")}

@app.route("/")
def home():
    conn = get_db()
    categories = conn.execute("SELECT * FROM categories ORDER BY name").fetchall()
    featured = conn.execute(
        "SELECT f.*, c.name category FROM foods f JOIN categories c ON c.id=f.category_id "
        "WHERE f.is_available=1 ORDER BY f.id LIMIT 8"
    ).fetchall()
    conn.close()
    return render_template("index.html", categories=categories, featured=featured)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not name or not email or not password:
            flash("Please fill all required fields.", "danger")
            return render_template("register.html")
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            flash("Please enter a valid email address.", "danger")
            return render_template("register.html")
        if len(password) < 6:
            flash("Password must contain at least 6 characters.", "danger")
            return render_template("register.html")
        if password != confirm:
            flash("Passwords do not match.", "danger")
            return render_template("register.html")

        conn = get_db()
        try:
            conn.execute(
                """INSERT INTO users(name,email,password,phone,role,created_at)
                   VALUES (?,?,?,?,?,?)""",
                (name, email, generate_password_hash(password), phone, "customer",
                 datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            flash("An account with this email already exists. Please login.", "warning")
            return redirect(url_for("login"))
        conn.close()
        flash("Registration successful. You can now login.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email=? COLLATE NOCASE", (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["role"] = user["role"]
            session["email"] = user["email"]
            flash(f"Welcome back, {user['name']}!", "success")
            next_url = request.args.get("next")
            return redirect(next_url if next_url and next_url.startswith("/") else url_for("home"))

        flash("Invalid email or password. Please check your credentials.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))

@app.route("/menu")
def menu():
    category = request.args.get("category", "").strip()
    search = request.args.get("search", "").strip()
    conn = get_db()
    categories = conn.execute("SELECT * FROM categories ORDER BY name").fetchall()
    query = """SELECT f.*, c.name category FROM foods f
               JOIN categories c ON c.id=f.category_id
               WHERE f.is_available=1"""
    params = []
    if category:
        query += " AND c.name=?"
        params.append(category)
    if search:
        query += " AND (f.name LIKE ? OR f.description LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    query += " ORDER BY f.id DESC"
    foods = conn.execute(query, params).fetchall()
    conn.close()
    return render_template("menu.html", foods=foods, categories=categories,
                           selected_category=category, search=search)

@app.post("/cart/add/<int:food_id>")
@login_required
def add_to_cart(food_id):
    conn = get_db()
    food = conn.execute("SELECT * FROM foods WHERE id=? AND is_available=1", (food_id,)).fetchone()
    conn.close()
    if not food:
        flash("Food item is unavailable.", "danger")
        return redirect(url_for("menu"))
    cart = session.get("cart", {})
    key = str(food_id)
    cart[key] = int(cart.get(key, 0)) + 1
    session["cart"] = cart
    flash(f"{food['name']} added to your cart.", "success")
    return redirect(request.referrer or url_for("menu"))

@app.route("/cart")
@login_required
def cart():
    return render_cart()

def render_cart():
    cart = session.get("cart", {})
    items, subtotal = [], 0
    conn = get_db()
    for food_id, qty in cart.items():
        food = conn.execute("SELECT * FROM foods WHERE id=?", (int(food_id),)).fetchone()
        if food and food["is_available"]:
            line_total = food["price"] * int(qty)
            subtotal += line_total
            items.append({"food": food, "quantity": int(qty), "line_total": line_total})
    conn.close()
    delivery_fee = 40 if subtotal > 0 and subtotal < 499 else 0
    total = subtotal + delivery_fee
    return render_template("cart.html", items=items, subtotal=subtotal,
                           delivery_fee=delivery_fee, total=total)

@app.post("/cart/update")
@login_required
def update_cart():
    cart = session.get("cart", {})
    for key, value in request.form.items():
        if key.startswith("qty_"):
            food_id = key.replace("qty_", "")
            try:
                qty = max(0, min(20, int(value)))
            except ValueError:
                qty = 1
            if qty == 0:
                cart.pop(food_id, None)
            else:
                cart[food_id] = qty
    session["cart"] = cart
    flash("Cart updated.", "success")
    return redirect(url_for("cart"))

@app.post("/cart/remove/<int:food_id>")
@login_required
def remove_from_cart(food_id):
    cart = session.get("cart", {})
    cart.pop(str(food_id), None)
    session["cart"] = cart
    flash("Item removed from cart.", "success")
    return redirect(url_for("cart"))

@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    cart = session.get("cart", {})
    if not cart:
        flash("Your cart is empty.", "warning")
        return redirect(url_for("menu"))

    conn = get_db()
    items, subtotal = [], 0
    for food_id, qty in cart.items():
        food = conn.execute("SELECT * FROM foods WHERE id=? AND is_available=1", (int(food_id),)).fetchone()
        if food:
            qty = int(qty)
            subtotal += food["price"] * qty
            items.append((food, qty))
    delivery_fee = 40 if subtotal < 499 else 0
    total = subtotal + delivery_fee

    if request.method == "POST":
        address = request.form.get("address", "").strip()
        landmark = request.form.get("landmark", "").strip()
        city = request.form.get("city", "").strip()
        pincode = request.form.get("pincode", "").strip()
        latitude = request.form.get("latitude", "").strip()
        longitude = request.form.get("longitude", "").strip()
        notes = request.form.get("notes", "").strip()
        payment = request.form.get("payment_method", "Cash on Delivery")

        if not address or not city or not re.match(r"^\d{6}$", pincode):
            conn.close()
            flash("Please enter a complete address and valid 6-digit pincode.", "danger")
            return render_template("checkout.html", items=items, subtotal=subtotal,
                                   delivery_fee=delivery_fee, total=total)

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur = conn.execute(
            """INSERT INTO orders
               (user_id,total,status,payment_method,address,landmark,city,pincode,latitude,longitude,notes,created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (session["user_id"], total, "Placed", payment, address, landmark, city,
             pincode, latitude, longitude, notes, now)
        )
        order_id = cur.lastrowid
        for food, qty in items:
            conn.execute(
                """INSERT INTO order_items(order_id,food_id,food_name,quantity,price)
                   VALUES (?,?,?,?,?)""",
                (order_id, food["id"], food["name"], qty, food["price"])
            )
        conn.commit()
        conn.close()
        session["cart"] = {}
        return redirect(url_for("order_success", order_id=order_id))

    conn.close()
    return render_template("checkout.html", items=items, subtotal=subtotal,
                           delivery_fee=delivery_fee, total=total)

@app.route("/order-success/<int:order_id>")
@login_required
def order_success(order_id):
    conn = get_db()
    order = conn.execute("SELECT * FROM orders WHERE id=? AND user_id=?",
                         (order_id, session["user_id"])).fetchone()
    conn.close()
    if not order:
        return redirect(url_for("home"))
    return render_template("order_success.html", order=order)

@app.route("/orders")
@login_required
def orders():
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM orders WHERE user_id=? ORDER BY id DESC",
        (session["user_id"],)
    ).fetchall()
    conn.close()
    return render_template("orders.html", orders=rows)

@app.route("/admin")
@admin_required
def admin():
    conn = get_db()
    stats = {
        "users": conn.execute("SELECT COUNT(*) c FROM users WHERE role='customer'").fetchone()["c"],
        "foods": conn.execute("SELECT COUNT(*) c FROM foods WHERE is_available=1").fetchone()["c"],
        "orders": conn.execute("SELECT COUNT(*) c FROM orders").fetchone()["c"],
        "revenue": conn.execute("SELECT COALESCE(SUM(total),0) s FROM orders WHERE status!='Cancelled'").fetchone()["s"],
    }
    recent = conn.execute(
        """SELECT o.*, u.name customer, u.email FROM orders o
           JOIN users u ON u.id=o.user_id ORDER BY o.id DESC LIMIT 10"""
    ).fetchall()
    conn.close()
    return render_template("admin.html", stats=stats, recent=recent)

@app.route("/admin/foods", methods=["GET", "POST"])
@admin_required
def admin_foods():
    conn = get_db()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        price = request.form.get("price", "0")
        category_id = request.form.get("category_id")
        image = request.form.get("image", "🍽️").strip() or "🍽️"
        try:
            price = float(price)
        except ValueError:
            price = 0
        if name and category_id and price > 0:
            conn.execute(
                """INSERT INTO foods(category_id,name,description,price,image)
                   VALUES (?,?,?,?,?)""",
                (category_id, name, description, price, image)
            )
            conn.commit()
            flash("Food item added successfully.", "success")
        else:
            flash("Enter valid food details.", "danger")
    foods = conn.execute(
        "SELECT f.*, c.name category FROM foods f JOIN categories c ON c.id=f.category_id ORDER BY f.id DESC"
    ).fetchall()
    categories = conn.execute("SELECT * FROM categories ORDER BY name").fetchall()
    conn.close()
    return render_template("admin_foods.html", foods=foods, categories=categories)

@app.post("/admin/foods/toggle/<int:food_id>")
@admin_required
def toggle_food(food_id):
    conn = get_db()
    conn.execute("UPDATE foods SET is_available=CASE WHEN is_available=1 THEN 0 ELSE 1 END WHERE id=?", (food_id,))
    conn.commit()
    conn.close()
    flash("Food availability updated.", "success")
    return redirect(url_for("admin_foods"))

@app.post("/admin/orders/<int:order_id>/status")
@admin_required
def update_order_status(order_id):
    status = request.form.get("status")
    allowed = {"Placed", "Preparing", "Out for Delivery", "Delivered", "Cancelled"}
    if status not in allowed:
        flash("Invalid status.", "danger")
        return redirect(url_for("admin"))
    conn = get_db()
    conn.execute("UPDATE orders SET status=? WHERE id=?", (status, order_id))
    conn.commit()
    conn.close()
    flash("Order status updated.", "success")
    return redirect(url_for("admin"))

@app.get("/api/location")
@login_required
def location_api():
    return jsonify({"message": "Location is captured in the checkout form using your browser's location permission."})

@app.errorhandler(404)
def not_found(error):
    return render_template("error.html", code=404, message="Page not found."), 404

@app.errorhandler(500)
def server_error(error):
    return render_template("error.html", code=500, message="Something went wrong on the server."), 500

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
