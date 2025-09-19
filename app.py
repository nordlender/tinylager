import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, g
import sqlite3

# Initialize Flask app
app = Flask(__name__)

# Use secret key from environment variable (set by main.py)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")
if not app.secret_key:
    raise ValueError("FLASK_SECRET_KEY environment variable not set!")

DATABASE = "orders.db"
# To see schemas, do sqlite3 orders.db .schema


# --- Funcs ---
def archive_orders():
    """
    Move fully returned orders into archive_orders and archive_items.
    """
    db = get_db()
    cur = db.cursor()

    # Get all active orders
    cur.execute("SELECT orderId FROM orders")
    all_orders = [row["orderId"] for row in cur.fetchall()]

    for orderId in all_orders:
        # Check if this order is fully returned
        cur.execute(
            """
            SELECT SUM(lent) as total_lent, SUM(returned) as total_returned
            FROM order_items
            WHERE orderId = ?
        """,
            (orderId,),
        )
        row = cur.fetchone()

        if row and row["total_lent"] == row["total_returned"]:
            # Insert into archive_orders
            cur.execute(
                "INSERT INTO archive_orders SELECT * FROM orders WHERE orderId = ?",
                (orderId,),
            )

            # Insert into archive_items
            cur.execute(
                """
                INSERT INTO archive_items (orderId, itemId, lent, returned)
                SELECT orderId, itemId, lent, returned
                FROM order_items
                WHERE orderId = ?
            """,
                (orderId,),
            )

            # Delete from active tables
            cur.execute("DELETE FROM orders WHERE orderId = ?", (orderId,))
            cur.execute("DELETE FROM order_items WHERE orderId = ?", (orderId,))

    db.commit()


def update_inventory(itemId, count):
    """
    Update inventory stock for a given itemId.
    Positive count -> add to stock (e.g. return)
    Negative count -> subtract from stock (e.g. new order)
    """
    db = get_db()
    cur = db.cursor()

    cur.execute(
        """
        UPDATE inventory
        SET stock = stock + ?
        WHERE itemId = ?
    """,
        (count, itemId),
    )

    db.commit()


def new_return(orderId, name, returned_items):
    """
    Create a new return record.
    - orderId: the original order
    - name: name of the person returning
    - returned_items: dict {itemId: returned_count}
    """
    db = get_db()
    cur = db.cursor()
    timestamp = datetime.now().isoformat(timespec="seconds")

    # Insert into returns
    cur.execute(
        "INSERT INTO returns (orderId, timestamp, name) VALUES (?, ?, ?)",
        (orderId, timestamp, name),
    )
    returnId = cur.lastrowid

    # Insert each returned item
    for itemId, returned in returned_items.items():
        if returned > 0:
            cur.execute(
                "INSERT INTO return_items (returnId, itemId, returned) VALUES (?, ?, ?)",
                (returnId, itemId, returned),
            )

    db.commit()
    return returnId


def set_returned(orderId):
    """
    Update the returned counts in order_items for a specific order.
    """
    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT itemId FROM order_items WHERE orderId = ?", (orderId,))
    items = [row["itemId"] for row in cur.fetchall()]

    for itemId in items:
        # Sum all returns for this item
        cur.execute(
            """
            SELECT SUM(ri.returned) as total_returned
            FROM return_items ri
            JOIN returns r ON ri.returnId = r.returnId
            WHERE r.orderId = ? AND ri.itemId = ?
        """,
            (orderId, itemId),
        )
        total_returned = cur.fetchone()["total_returned"] or 0

        # Update order_items
        cur.execute(
            "UPDATE order_items SET returned = ? WHERE orderId = ? AND itemId = ?",
            (total_returned, orderId, itemId),
        )

    db.commit()


# --- Database Helpers ---
def get_db():
    if "_database" not in g:
        g._database = sqlite3.connect(DATABASE)
        g._database.row_factory = sqlite3.Row
    return g._database


@app.teardown_appcontext
def close_db(exception):
    db = g.pop("_database", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DATABASE)
    db.execute("PRAGMA foreign_keys = ON")  # ensure foreign keys are enforced
    db.close()


# Initialize DB
with app.app_context():
    init_db()


@app.context_processor
def utility_processor():
    def get_order_items(orderId):
        """Gets the items in an order"""
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM order_items WHERE orderId = ?", (orderId,))
        return cur.fetchall()
    
    def get_archive_items(orderId):
        """Gets the items in an archived order"""
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM archive_items WHERE orderId = ?", (orderId,))
        return cur.fetchall()

    return dict(get_order_items=get_order_items, get_archive_items=get_archive_items)



#
#
# --- Routes ---
@app.route("/", methods=["GET", "POST"])
def index():
    db = get_db()
    cur = db.cursor()
    # Load inventory from database
    cur.execute("SELECT * FROM inventory")
    inventory_rows = cur.fetchall()
    inventory = {row["itemId"]: dict(row) for row in inventory_rows}

    if request.method == "POST":
        selected = {}
        for key, item in inventory.items():
            count = int(request.form.get(key, 0))
            if count > 0:
                selected[key] = {**item, "count": count}
        session["cart"] = selected
        return redirect(url_for("order_review"))

    return render_template("index.html", inventory=inventory)


@app.route("/order_review", methods=["GET", "POST"])
def order_review():
    cart = session.get("cart", {})

    if request.method == "POST":
        name = request.form.get("name")
        phone = request.form.get("phone")
        timestamp = datetime.now().isoformat(timespec="seconds")

        db = get_db()
        cur = db.cursor()

        cur.execute(
            "INSERT INTO orders (timestamp, name, phone) VALUES (?, ?, ?)",
            (timestamp, name, phone),
        )
        orderId = cur.lastrowid

        # Insert only items with count >= 1 and update stock
        for key, item in cart.items():
            count = int(request.form.get(key, item["count"]))
            if count < 1:
                continue  # skip items with 0 count
            cur.execute(
                "INSERT INTO order_items (orderId, itemId, lent, returned) VALUES (?, ?, ?, ?)",
                (orderId, key, count, 0),
            )
            update_inventory(key, -count)  # subtract from stock

        db.commit()
        session.pop("cart", None)
        return f"✅ Order #{orderId} stored successfully!"

    return render_template("order_review.html", cart=cart)


@app.route("/return", methods=["GET", "POST"])
def return_items():
    order = None
    error = None

    if request.method == "POST":
        orderId = request.form.get("orderId")
        db = get_db()
        cur = db.cursor()

        # Fetch order
        cur.execute("SELECT * FROM orders WHERE orderId = ?", (orderId,))
        order_data = cur.fetchone()
        if not order_data:
            error = f"Order #{orderId} not found."
            return render_template("return.html", order=None, error=error)

        # Fetch items in order
        cur.execute(
            """
            SELECT oi.itemId, oi.lent, oi.returned, i.title, i.img, i.description
            FROM order_items oi
            JOIN inventory i ON i.itemId = oi.itemId
            WHERE oi.orderId = ?
        """,
            (orderId,),
        )
        items = cur.fetchall()

        # Structure cart_return for template & session
        order = {}
        for item in items:
            order[item["itemId"]] = {
                "title": item["title"],
                "img": item["img"] if item["img"] else f"/media/{item['itemId']}.jpg",
                "desc": item["description"],
                "lent": item["lent"],
                "remaining": item["lent"] - item["returned"],
            }

        # Store in session for return_review
        session["cart_return"] = order
        session["return_orderId"] = orderId

        # Redirect to review page
        return redirect(url_for("return_review"))

    return render_template("return.html", order=None, error=error)


@app.route("/return_review", methods=["GET", "POST"])
def return_review():
    cart_return = session.get("cart_return", {})
    orderId = session.get("return_orderId")

    if not cart_return or not orderId:
        return redirect(url_for("return_items"))

    warning_items = []

    if request.method == "POST":
        name = request.form.get("name")

        # Collect returned amounts
        returned_items = {}
        for itemId in cart_return:
            returned_now = int(request.form.get(itemId, 0))
            returned_items[itemId] = returned_now
            if returned_now > cart_return[itemId]["remaining"]:
                warning_items.append(itemId)

        # If there are warnings, just re-render with the warning
        if warning_items and not request.form.get("proceed"):
            return render_template(
                "return_review.html",
                cart_return=cart_return,
                warning_items=warning_items,
                name=name,
            )

        # Proceed with inserting return
        new_return(orderId, name, returned_items)
        set_returned(orderId)

        # Update stock for each returned item
        for itemId, returned_now in returned_items.items():
            if returned_now > 0:
                update_inventory(itemId, returned_now)

        archive_orders()
        # Clear session
        session.pop("cart_return", None)
        session.pop("return_orderId", None)

        return redirect(url_for("completed"))

    return render_template(
        "return_review.html", cart_return=cart_return, warning_items=[], name=""
    )


@app.route("/completed")
def completed():
    """
    Page shown after an order or return is successfully submitted.
    """
    return render_template("completed.html")


@app.route("/orders")
def orders():
    db = get_db()
    cur = db.cursor()

    # Active orders
    cur.execute("SELECT * FROM orders ORDER BY orderId DESC")
    active_orders = cur.fetchall()

    # Archived orders
    cur.execute("SELECT * FROM archive_orders ORDER BY orderId DESC")
    archived_orders = cur.fetchall()

    return render_template(
        "orders.html", active_orders=active_orders, archived_orders=archived_orders
    )


# Only run if called directly (main.py will import this)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
