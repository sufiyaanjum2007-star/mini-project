from flask import Flask, request, redirect, render_template_string
import sqlite3

app = Flask(__name__)
DB = "market.db"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                farmer TEXT,
                phone TEXT,
                crop TEXT,
                price REAL,
                quantity REAL,
                location TEXT,
                date_added TEXT DEFAULT CURRENT_DATE
            )
        """)

PAGE = """
<!DOCTYPE html>
<html>
<head>
  <title>Local Farmer Market Information System</title>
  <style>
    body { font-family: Arial; margin: 30px; background: #f4f9f4; }
    h1 { color: #2e7d32; }
    form { margin-bottom: 20px; }
    input { padding: 8px; margin: 4px; }
    button { padding: 8px 16px; background: #2e7d32; color: white; border: none; cursor: pointer; }
    table { border-collapse: collapse; width: 100%; background: white; }
    th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
    th { background: #2e7d32; color: white; }
  </style>
</head>
<body>
  <h1>Local Farmer Market Information System</h1>

  <h3>Search Produce</h3>
  <form method="get" action="/">
    <input name="q" placeholder="Crop or location" value="{{ q }}">
    <button type="submit">Search</button>
  </form>

  <h3>Add Your Produce (Farmers)</h3>
  <form method="post" action="/add">
    <input name="farmer" placeholder="Farmer name" required>
    <input name="phone" placeholder="Phone number" required>
    <input name="crop" placeholder="Crop (e.g. Tomato)" required>
    <input name="price" type="number" step="0.01" placeholder="Price per kg" required>
    <input name="quantity" type="number" step="0.1" placeholder="Quantity (kg)" required>
    <input name="location" placeholder="Village / Town" required>
    <button type="submit">Add</button>
  </form>

  <h3>Available Produce</h3>
  <table>
    <tr>
      <th>Crop</th><th>Price/kg (Rs)</th><th>Quantity (kg)</th>
      <th>Farmer</th><th>Phone</th><th>Location</th><th>Date</th>
    </tr>
    {% for p in products %}
    <tr>
      <td>{{ p.crop }}</td><td>{{ p.price }}</td><td>{{ p.quantity }}</td>
      <td>{{ p.farmer }}</td><td>{{ p.phone }}</td><td>{{ p.location }}</td><td>{{ p.date_added }}</td>
    </tr>
    {% else %}
    <tr><td colspan="7">No produce found.</td></tr>
    {% endfor %}
  </table>
</body>
</html>
"""

@app.route("/")
def home():
    q = request.args.get("q", "").strip()
    with get_db() as conn:
        if q:
            like = f"%{q}%"
            products = conn.execute(
                "SELECT * FROM products WHERE crop LIKE ? OR location LIKE ? ORDER BY price",
                (like, like),
            ).fetchall()
        else:
            products = conn.execute("SELECT * FROM products ORDER BY id DESC").fetchall()
    return render_template_string(PAGE, products=products, q=q)

@app.route("/add", methods=["POST"])
def add():
    f = request.form
    with get_db() as conn:
        conn.execute(
            "INSERT INTO products (farmer, phone, crop, price, quantity, location) VALUES (?,?,?,?,?,?)",
            (f["farmer"], f["phone"], f["crop"], f["price"], f["quantity"], f["location"]),
        )
    return redirect("/")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)