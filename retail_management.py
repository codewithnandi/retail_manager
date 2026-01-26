import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import date

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

from reportlab.platypus import SimpleDocTemplate, Paragraph, Table
from reportlab.lib.styles import getSampleStyleSheet

# ---------------- DATABASE ----------------
conn = sqlite3.connect("retail.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS products(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
category TEXT,
price REAL,
stock INTEGER
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS sales(
id INTEGER PRIMARY KEY AUTOINCREMENT,
product TEXT,
quantity INTEGER,
subtotal REAL,
gst REAL,
total REAL,
date TEXT
)
""")
conn.commit()

# ---------------- GUI ----------------
root = tk.Tk()
root.title("Organized Retail Shopping Management")
root.geometry("900x550")

# ---------------- THEME ----------------
current_theme = "light"

themes = {
    "light": {
        "bg": "#f2f2f2",
        "header": "#2c3e50",
        "btn": "#2980b9",
        "fg": "black"
    },
    "dark": {
        "bg": "#1e1e1e",
        "header": "#111111",
        "btn": "#34495e",
        "fg": "white"
    }
}

def apply_theme():
    root.configure(bg=themes[current_theme]["bg"])

def toggle_theme():
    global current_theme
    current_theme = "dark" if current_theme == "light" else "light"
    admin_login()

def clear():
    for w in root.winfo_children():
        w.destroy()

# ---------------- ADMIN LOGIN ----------------
def admin_login():
    clear()
    apply_theme()
    t = themes[current_theme]

    tk.Label(
        root, text="Admin Login",
        font=("Arial", 20, "bold"),
        bg=t["header"], fg="white", height=2
    ).pack(fill="x")

    # Theme toggle button
    tk.Button(
        root,
        text="🌙 Dark Mode" if current_theme == "light" else "☀ Light Mode",
        command=toggle_theme,
        bg=t["btn"], fg="white"
    ).pack(pady=10)

    frame = tk.Frame(root, bg=t["bg"])
    frame.pack(pady=60)

    user = tk.Entry(frame, font=("Arial", 14))
    pwd = tk.Entry(frame, font=("Arial", 14), show="*")

    tk.Label(frame, text="Username", bg=t["bg"], fg=t["fg"]).pack()
    user.pack()
    tk.Label(frame, text="Password", bg=t["bg"], fg=t["fg"]).pack()
    pwd.pack()

    def login():
        if user.get() == "admin" and pwd.get() == "retail123":
            dashboard()
        else:
            messagebox.showerror("Error", "Invalid Admin Credentials")

    tk.Button(frame, text="Login", bg="#27ae60", fg="white", width=15, command=login).pack(pady=20)

# ---------------- DASHBOARD ----------------
def dashboard():
    clear()
    apply_theme()
    t = themes[current_theme]

    tk.Label(
        root, text="Retail Management Dashboard",
        font=("Arial", 20, "bold"),
        bg=t["header"], fg="white", height=2
    ).pack(fill="x")

    frame = tk.Frame(root, bg=t["bg"])
    frame.pack(pady=40)

    buttons = [
        ("Add Product", add_product),
        ("View Products", view_products),
        ("Generate Bill", generate_bill),
        ("Daily Sales Report", daily_sales),
        ("Sales Chart", sales_chart),
        ("Logout", admin_login)
    ]

    for text, cmd in buttons:
        tk.Button(
            frame, text=text,
            width=30, height=2,
            bg=t["btn"], fg="white",
            command=cmd
        ).pack(pady=6)

# ---------------- ADD PRODUCT ----------------
def add_product():
    clear()
    apply_theme()
    t = themes[current_theme]

    tk.Label(root, text="Add Product", font=("Arial", 18, "bold"),
             bg="#1abc9c", fg="white", height=2).pack(fill="x")

    frame = tk.Frame(root, bg=t["bg"])
    frame.pack(pady=40)

    name = tk.Entry(frame)
    price = tk.Entry(frame)
    stock = tk.Entry(frame)
    category = ttk.Combobox(frame, values=["Grocery", "Clothing", "Electronics", "Cosmetics", "Other"])

    for lbl, ent in [("Product Name", name), ("Category", category),
                     ("Price", price), ("Stock", stock)]:
        tk.Label(frame, text=lbl, bg=t["bg"], fg=t["fg"]).pack()
        ent.pack(pady=5)

    def save():
        cur.execute("INSERT INTO products VALUES(NULL,?,?,?,?)",
                    (name.get(), category.get(), price.get(), stock.get()))
        conn.commit()
        messagebox.showinfo("Success", "Product Added")
        dashboard()

    tk.Button(frame, text="Save", bg="#27ae60", fg="white", width=20, command=save).pack(pady=15)
    tk.Button(frame, text="Back", command=dashboard).pack()

# ---------------- VIEW PRODUCTS ----------------
def view_products():
    clear()
    apply_theme()
    t = themes[current_theme]

    tk.Label(root, text="Products", font=("Arial", 18, "bold"),
             bg="#9b59b6", fg="white", height=2).pack(fill="x")

    frame = tk.Frame(root, bg=t["bg"])
    frame.pack(pady=20)

    for p in cur.execute("SELECT * FROM products"):
        tk.Label(frame, text=f"{p[0]} | {p[1]} | {p[2]} | ₹{p[3]} | Stock:{p[4]}",
                 bg=t["bg"], fg=t["fg"]).pack(anchor="w")

    tk.Button(root, text="Back", command=dashboard).pack(pady=20)

# ---------------- BILLING ----------------
def generate_bill():
    clear()
    apply_theme()
    t = themes[current_theme]

    tk.Label(root, text="Generate Bill", font=("Arial", 18, "bold"),
             bg="#e67e22", fg="white", height=2).pack(fill="x")

    frame = tk.Frame(root, bg=t["bg"])
    frame.pack(pady=40)

    pid = tk.Entry(frame)
    qty = tk.Entry(frame)

    tk.Label(frame, text="Product ID", bg=t["bg"], fg=t["fg"]).pack()
    pid.pack()
    tk.Label(frame, text="Quantity", bg=t["bg"], fg=t["fg"]).pack()
    qty.pack()

    def bill():
        cur.execute("SELECT name,price,stock FROM products WHERE id=?", (pid.get(),))
        p = cur.fetchone()
        if not p or int(qty.get()) > p[2]:
            messagebox.showerror("Error", "Invalid Product / Stock")
            return

        subtotal = p[1] * int(qty.get())
        gst = subtotal * 0.18
        total = subtotal + gst

        cur.execute("UPDATE products SET stock=stock-? WHERE id=?", (qty.get(), pid.get()))
        cur.execute("INSERT INTO sales VALUES(NULL,?,?,?,?,?,?)",
                    (p[0], qty.get(), subtotal, gst, total, date.today().isoformat()))
        conn.commit()

        generate_pdf(p[0], qty.get(), subtotal, gst, total)
        messagebox.showinfo("Invoice", f"Total Amount: ₹{total}")
        dashboard()

    tk.Button(frame, text="Generate Bill", bg="#27ae60", fg="white", width=20, command=bill).pack(pady=15)
    tk.Button(frame, text="Back", command=dashboard).pack()

# ---------------- PDF ----------------
def generate_pdf(product, qty, subtotal, gst, total):
    doc = SimpleDocTemplate("invoice.pdf")
    styles = getSampleStyleSheet()
    content = [Paragraph("Retail Invoice", styles["Title"])]

    table = Table([
        ["Product", product],
        ["Quantity", qty],
        ["Subtotal", f"₹{subtotal}"],
        ["GST (18%)", f"₹{gst}"],
        ["Total", f"₹{total}"]
    ])
    content.append(table)
    doc.build(content)

# ---------------- SALES REPORT ----------------
def daily_sales():
    clear()
    apply_theme()
    t = themes[current_theme]

    tk.Label(root, text="Today's Sales", font=("Arial", 18, "bold"),
             bg="#c0392b", fg="white", height=2).pack(fill="x")

    frame = tk.Frame(root, bg=t["bg"])
    frame.pack(pady=20)

    total = 0
    for s in cur.execute("SELECT product,quantity,total FROM sales WHERE date=?", (date.today().isoformat(),)):
        total += s[2]
        tk.Label(frame, text=f"{s[0]} | Qty:{s[1]} | ₹{s[2]}",
                 bg=t["bg"], fg=t["fg"]).pack(anchor="w")

    tk.Label(frame, text=f"Total Sales Today: ₹{total}", bg=t["bg"], fg=t["fg"],
             font=("Arial", 12, "bold")).pack(pady=10)
    tk.Button(root, text="Back", command=dashboard).pack(pady=20)

# ---------------- SALES CHART ----------------
def sales_chart():
    data = cur.execute("SELECT date, SUM(total) FROM sales GROUP BY date").fetchall()
    if not data:
        messagebox.showinfo("Info", "No sales data")
        return

    dates = [d[0] for d in data]
    totals = [d[1] for d in data]

    plt.figure()
    plt.plot(dates, totals)
    plt.title("Daily Sales")
    plt.xlabel("Date")
    plt.ylabel("Total")
    plt.show()

# ---------------- START ----------------
admin_login()
root.mainloop()
