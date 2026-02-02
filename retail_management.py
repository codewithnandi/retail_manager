import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from tkinter.font import Font
import sqlite3
from datetime import datetime, date
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import webbrowser
import os
from PIL import Image, ImageTk
import threading

# ---------------- DATABASE CLASS ---------------- 
class Database:
    def __init__(self):
        self.conn = sqlite3.connect("retail.db", check_same_thread=False)
        self.cur = self.conn.cursor()
        self.init_db()
    
    def init_db(self):
        # Products table
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS products(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            price REAL NOT NULL,
            stock INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Sales table
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS sales(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            subtotal REAL NOT NULL,
            gst REAL NOT NULL,
            total REAL NOT NULL,
            sale_date DATE NOT NULL,
            sale_time TIME NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
        """)
        
        # Categories table
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS categories(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            color TEXT DEFAULT '#808000'
        )
        """)
        
        # Insert default categories if not exists
        default_categories = [
            ("Grocery", "#808000"),
            ("Electronics", "#556B2F"),
            ("Clothing", "#6B8E23"),
            ("Cosmetics", "#8F9779"),
            ("Home & Kitchen", "#BCB88A"),
            ("Sports", "#C2B280"),
            ("Books", "#D2B48C"),
            ("Other", "#8B4513")
        ]
        
        for cat_name, color in default_categories:
            self.cur.execute("""
            INSERT OR IGNORE INTO categories (name, color) VALUES (?, ?)
            """, (cat_name, color))
        
        self.conn.commit()
    
    def execute_query(self, query, params=()):
        try:
            self.cur.execute(query, params)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Database error: {e}")
            return False
    
    def fetch_all(self, query, params=()):
        self.cur.execute(query, params)
        return self.cur.fetchall()
    
    def fetch_one(self, query, params=()):
        self.cur.execute(query, params)
        return self.cur.fetchone()
    
    def close(self):
        self.conn.close()

# ---------------- BEIGE-OLIVE COLOR SCHEME ---------------- 
COLORS = {
    'primary': '#556B2F',      # Dark Olive Green
    'secondary': '#8B4513',    # Saddle Brown
    'accent': '#808000',       # Olive
    'success': '#6B8E23',      # Olive Drab
    'warning': '#B8860B',      # Dark Goldenrod
    'danger': '#A0522D',       # Sienna
    'light': '#F5F5DC',        # Beige
    'dark': '#556B2F',         # Dark Olive Green
    'background': '#FAF0E6',   # Linen (light beige)
    'sidebar': '#8F9779',      # Sage Green
    'card': '#FFFFFF',         # White
    'highlight': '#BCB88A',    # Sage
    'border': '#D2B48C'        # Tan
}

# ---------------- LOGIN PAGE ---------------- 
class LoginPage:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.create_widgets()
    
    def create_widgets(self):
        # Main container
        self.main_frame = tk.Frame(self.parent, bg=COLORS['background'])
        self.main_frame.pack(fill='both', expand=True)
        
        # Left side - Branding/Image
        left_frame = tk.Frame(self.main_frame, bg=COLORS['primary'], width=400)
        left_frame.pack(side='left', fill='both', expand=True)
        left_frame.pack_propagate(False)
        
        # Branding content
        brand_label = tk.Label(left_frame, 
                              text="🛍️\nRetailPro\nManagement",
                              font=('Segoe UI', 32, 'bold'),
                              fg='white',
                              bg=COLORS['primary'],
                              justify='center')
        brand_label.pack(expand=True)
        
        tagline = tk.Label(left_frame,
                          text="Streamline Your Retail Operations\nWith Modern Tools",
                          font=('Segoe UI', 14),
                          fg=COLORS['light'],
                          bg=COLORS['primary'],
                          justify='center')
        tagline.pack(pady=(0, 100))
        
        # Right side - Login Form
        right_frame = tk.Frame(self.main_frame, bg='white', width=400)
        right_frame.pack(side='right', fill='both', expand=True)
        right_frame.pack_propagate(False)
        
        # Login form container
        form_container = tk.Frame(right_frame, bg='white')
        form_container.pack(expand=True)
        
        # Login title
        login_title = tk.Label(form_container,
                              text="Welcome Back",
                              font=('Segoe UI', 28, 'bold'),
                              fg=COLORS['primary'],
                              bg='white')
        login_title.pack(pady=(0, 10))
        
        login_subtitle = tk.Label(form_container,
                                 text="Sign in to your account",
                                 font=('Segoe UI', 14),
                                 fg=COLORS['secondary'],
                                 bg='white')
        login_subtitle.pack(pady=(0, 40))
        
        # Username field
        tk.Label(form_container,
                text="Username",
                font=('Segoe UI', 11),
                fg=COLORS['secondary'],
                bg='white',
                anchor='w').pack(fill='x', padx=80, pady=(10, 5))
        
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(form_container,
                                       textvariable=self.username_var,
                                       style='Modern.TEntry',
                                       font=('Segoe UI', 12))
        self.username_entry.pack(fill='x', padx=80, pady=(0, 20), ipady=8)
        self.username_entry.insert(0, "admin")
        self.username_entry.bind('<FocusIn>', lambda e: self.clear_placeholder(self.username_entry, "admin"))
        
        # Password field
        tk.Label(form_container,
                text="Password",
                font=('Segoe UI', 11),
                fg=COLORS['secondary'],
                bg='white',
                anchor='w').pack(fill='x', padx=80, pady=(10, 5))
        
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(form_container,
                                       textvariable=self.password_var,
                                       show="•",
                                       style='Modern.TEntry',
                                       font=('Segoe UI', 12))
        self.password_entry.pack(fill='x', padx=80, pady=(0, 30), ipady=8)
        self.password_entry.insert(0, "retail123")
        self.password_entry.bind('<FocusIn>', lambda e: self.clear_placeholder(self.password_entry, "retail123"))
        
        # Login button
        login_btn = ttk.Button(form_container,
                              text="Login →",
                              style='Primary.TButton',
                              command=self.authenticate)
        login_btn.pack(ipady=12, ipadx=30, pady=(0, 20))
        
        # Quick login hint
        hint_label = tk.Label(form_container,
                             text="Use: admin / retail123",
                             font=('Segoe UI', 10),
                             fg=COLORS['secondary'],
                             bg='white')
        hint_label.pack()
        
        # Bind Enter key to login
        self.parent.bind('<Return>', lambda e: self.authenticate())
    
    def clear_placeholder(self, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, 'end')
    
    def authenticate(self):
        username = self.username_var.get()
        password = self.password_var.get()
        
        if username == "admin" and password == "retail123":
            self.app.current_user = "admin"
            self.app.is_admin = True
            self.app.show_dashboard()
        else:
            messagebox.showerror("Login Failed", 
                                "Invalid credentials. Please try again.")
    
    def destroy(self):
        self.main_frame.destroy()

# ---------------- DASHBOARD PAGE ---------------- 
class DashboardPage:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.create_widgets()
    
    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.parent, bg=COLORS['primary'], height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame,
                text="📊 Dashboard Overview",
                font=('Segoe UI', 24, 'bold'),
                bg=COLORS['primary'],
                fg='white').pack(side='left', padx=30)
        
        # Current date
        date_label = tk.Label(header_frame,
                             text=datetime.now().strftime("%B %d, %Y"),
                             font=('Segoe UI', 12),
                             bg=COLORS['primary'],
                             fg=COLORS['light'])
        date_label.pack(side='right', padx=30)
        
        # Main content with scrollbar
        main_container = tk.Frame(self.parent, bg=COLORS['background'])
        main_container.pack(fill='both', expand=True)
        
        # Create a canvas and scrollbar
        self.canvas = tk.Canvas(main_container, bg=COLORS['background'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient='vertical', command=self.canvas.yview)
        
        # Create a frame inside the canvas
        self.scrollable_frame = tk.Frame(self.canvas, bg=COLORS['background'])
        
        # Configure the canvas
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack the canvas and scrollbar
        self.canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Create window in canvas for scrollable frame
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor='nw')
        
        # Bind events for scrolling
        self.scrollable_frame.bind('<Configure>', self.on_frame_configure)
        self.canvas.bind('<Configure>', self.on_canvas_configure)
        
        # Bind mouse wheel
        self.canvas.bind_all('<MouseWheel>', self.on_mousewheel)
        
        # Create content in scrollable frame
        self.create_content()
    
    def create_content(self):
        # Statistics cards
        stats_frame = tk.Frame(self.scrollable_frame, bg=COLORS['background'])
        stats_frame.pack(fill='x', padx=30, pady=30)
        
        # Fetch statistics
        total_products = self.app.db.fetch_one("SELECT COUNT(*) FROM products")[0] or 0
        total_sales = self.app.db.fetch_one("SELECT COUNT(*) FROM sales")[0] or 0
        today_sales = self.app.db.fetch_one("SELECT SUM(total) FROM sales WHERE sale_date = ?", 
                                          (date.today().isoformat(),))[0] or 0
        low_stock = self.app.db.fetch_one("SELECT COUNT(*) FROM products WHERE stock < 10")[0] or 0
        
        stats_data = [
            ("Total Products", total_products, COLORS['primary'], "📦"),
            ("Today's Sales", f"₹{today_sales:,.2f}", COLORS['success'], "💰"),
            ("Total Transactions", total_sales, COLORS['accent'], "🧾"),
            ("Low Stock Items", low_stock, COLORS['warning'], "⚠️")
        ]
        
        for i, (title, value, color, icon) in enumerate(stats_data):
            card = tk.Frame(stats_frame, bg='white', relief='flat', highlightthickness=2,
                          highlightbackground=COLORS['border'], highlightcolor=COLORS['border'])
            card.grid(row=0, column=i, padx=10, ipadx=20, ipady=20, sticky='nsew')
            
            tk.Label(card,
                    text=icon,
                    font=('Segoe UI', 24),
                    bg='white',
                    fg=color).pack()
            
            tk.Label(card,
                    text=str(value),
                    font=('Segoe UI', 28, 'bold'),
                    bg='white',
                    fg=COLORS['primary']).pack()
            
            tk.Label(card,
                    text=title,
                    font=('Segoe UI', 11),
                    bg='white',
                    fg=COLORS['secondary']).pack()
        
        # Quick actions
        actions_frame = tk.Frame(self.scrollable_frame, bg=COLORS['background'])
        actions_frame.pack(fill='x', padx=30, pady=20)
        
        tk.Label(actions_frame,
                text="Quick Actions",
                font=('Segoe UI', 18, 'bold'),
                bg=COLORS['background'],
                fg=COLORS['primary']).pack(anchor='w', pady=(0, 15))
        
        # Action buttons
        actions = [
            ("➕ Add Product", self.app.show_add_product, COLORS['success']),
            ("🧾 Generate Bill", self.app.show_generate_bill, COLORS['accent']),
            ("📦 View Products", self.app.show_view_products, COLORS['primary']),
            ("📈 View Reports", self.app.show_sales_report, COLORS['warning'])
        ]
        
        for text, command, color in actions:
            btn = tk.Button(actions_frame,
                          text=text,
                          font=('Segoe UI', 11, 'bold'),
                          bg=color,
                          fg='white',
                          bd=0,
                          padx=30,
                          pady=12,
                          cursor='hand2',
                          command=command)
            btn.pack(side='left', padx=5)
            btn.bind('<Enter>', lambda e, b=btn, c=color: b.config(bg=self.darken_color(c)))
            btn.bind('<Leave>', lambda e, b=btn, c=color: b.config(bg=c))
        
        # Recent sales table
        table_container = tk.Frame(self.scrollable_frame, bg=COLORS['background'])
        table_container.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Table header
        header = tk.Frame(table_container, bg=COLORS['background'])
        header.pack(fill='x', pady=(0, 10))
        
        tk.Label(header,
                text="Recent Sales",
                font=('Segoe UI', 18, 'bold'),
                bg=COLORS['background'],
                fg=COLORS['primary']).pack(side='left')
        
        tk.Button(header,
                 text="View All",
                 font=('Segoe UI', 10),
                 bg=COLORS['accent'],
                 fg='white',
                 padx=15,
                 pady=5,
                 cursor='hand2',
                 command=self.app.show_sales_report).pack(side='right')
        
        # Create table frame
        table_frame = tk.Frame(table_container, bg='white', relief='flat', highlightthickness=1,
                              highlightbackground=COLORS['border'])
        table_frame.pack(fill='both', expand=True)
        
        # Create table with scrollbar
        table_scroll = ttk.Scrollbar(table_frame)
        table_scroll.pack(side='right', fill='y')
        
        self.sales_tree = ttk.Treeview(table_frame, 
                                      yscrollcommand=table_scroll.set,
                                      height=10)
        table_scroll.config(command=self.sales_tree.yview)
        
        # Define columns
        self.sales_tree['columns'] = ('Product', 'Quantity', 'Amount', 'Date', 'Time')
        
        # Format columns
        self.sales_tree.column('#0', width=0, stretch=False)
        self.sales_tree.column('Product', width=200, anchor='w')
        self.sales_tree.column('Quantity', width=80, anchor='center')
        self.sales_tree.column('Amount', width=120, anchor='e')
        self.sales_tree.column('Date', width=100, anchor='center')
        self.sales_tree.column('Time', width=80, anchor='center')
        
        # Create headings
        self.sales_tree.heading('#0', text='')
        self.sales_tree.heading('Product', text='Product', anchor='w')
        self.sales_tree.heading('Quantity', text='Qty', anchor='center')
        self.sales_tree.heading('Amount', text='Amount (₹)', anchor='e')
        self.sales_tree.heading('Date', text='Date', anchor='center')
        self.sales_tree.heading('Time', text='Time', anchor='center')
        
        # Style the treeview
        style = ttk.Style()
        style.configure("Treeview", 
                       background="white",
                       foreground=COLORS['primary'],
                       fieldbackground="white",
                       rowheight=30)
        
        style.configure("Treeview.Heading",
                      background=COLORS['primary'],
                      foreground='white',
                      font=('Segoe UI', 10, 'bold'))
        
        self.sales_tree.pack(fill='both', expand=True)
        
        # Load recent sales
        self.load_recent_sales()
    
    def load_recent_sales(self):
        # Clear existing items
        for item in self.sales_tree.get_children():
            self.sales_tree.delete(item)
        
        # Fetch recent sales
        recent_sales = self.app.db.fetch_all("""
            SELECT product_name, quantity, total, sale_date, sale_time 
            FROM sales 
            ORDER BY id DESC 
            LIMIT 20
        """)
        
        # Insert sales data
        for sale in recent_sales:
            self.sales_tree.insert('', 'end', values=(
                sale[0],
                sale[1],
                f"₹{sale[2]:,.2f}",
                sale[3],
                sale[4]
            ))
    
    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_frame, width=event.width)
    
    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def darken_color(self, color):
        # Simple color darkening for hover effect
        if color.startswith('#'):
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            r = max(0, r - 30)
            g = max(0, g - 30)
            b = max(0, b - 30)
            return f'#{r:02x}{g:02x}{b:02x}'
        return color
    
    def refresh(self):
        self.load_recent_sales()
    
    def destroy(self):
        self.canvas.destroy()

# ---------------- ADD PRODUCT PAGE ---------------- 
class AddProductPage:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.create_widgets()
    
    def create_widgets(self):
        # Main container with scrollbar
        main_container = tk.Frame(self.parent, bg=COLORS['background'])
        main_container.pack(fill='both', expand=True)
        
        # Create a canvas and scrollbar
        self.canvas = tk.Canvas(main_container, bg=COLORS['background'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient='vertical', command=self.canvas.yview)
        
        # Create a frame inside the canvas
        self.scrollable_frame = tk.Frame(self.canvas, bg=COLORS['background'])
        
        # Configure the canvas
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack the canvas and scrollbar
        self.canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Create window in canvas for scrollable frame
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor='nw')
        
        # Bind events for scrolling
        self.scrollable_frame.bind('<Configure>', self.on_frame_configure)
        self.canvas.bind('<Configure>', self.on_canvas_configure)
        
        # Bind mouse wheel
        self.canvas.bind_all('<MouseWheel>', self.on_mousewheel)
        
        # Header
        header_frame = tk.Frame(self.scrollable_frame, bg=COLORS['primary'])
        header_frame.pack(fill='x', padx=30, pady=30)
        
        tk.Label(header_frame,
                text="➕ Add New Product",
                font=('Segoe UI', 24, 'bold'),
                bg=COLORS['primary'],
                fg='white').pack(pady=20)
        
        # Form container
        form_frame = tk.Frame(self.scrollable_frame, bg='white')
        form_frame.pack(fill='both', padx=30, pady=(0, 30))
        
        # Form fields
        fields = [
            ("Product Name", "text", True),
            ("Category", "combo", True),
            ("Price (₹)", "number", True),
            ("Stock Quantity", "number", True),
            ("Description", "textarea", False)
        ]
        
        self.product_vars = {}
        
        for i, (label, field_type, required) in enumerate(fields):
            # Field label
            label_text = f"{label} *" if required else label
            tk.Label(form_frame,
                    text=label_text,
                    font=('Segoe UI', 11, 'bold' if required else 'normal'),
                    bg='white',
                    fg=COLORS['primary'] if required else COLORS['secondary'],
                    anchor='w').grid(row=i*2, column=0, padx=40, pady=(20, 5), sticky='w')
            
            if field_type == "text":
                var = tk.StringVar()
                entry = ttk.Entry(form_frame, textvariable=var, font=('Segoe UI', 11), width=40)
                entry.grid(row=i*2+1, column=0, columnspan=2, padx=40, pady=(0, 10), sticky='w')
                self.product_vars[label] = var
                
            elif field_type == "number":
                var = tk.StringVar()
                entry = ttk.Entry(form_frame, textvariable=var, font=('Segoe UI', 11), width=40)
                entry.grid(row=i*2+1, column=0, columnspan=2, padx=40, pady=(0, 10), sticky='w')
                self.product_vars[label] = var
                
            elif field_type == "combo":
                var = tk.StringVar()
                categories = self.app.db.fetch_all("SELECT name FROM categories")
                combo = ttk.Combobox(form_frame, 
                                    textvariable=var, 
                                    values=[cat[0] for cat in categories],
                                    font=('Segoe UI', 11),
                                    width=38,
                                    state='readonly')
                combo.grid(row=i*2+1, column=0, columnspan=2, padx=40, pady=(0, 10), sticky='w')
                if categories:
                    combo.set(categories[0][0])
                self.product_vars[label] = var
                
            elif field_type == "textarea":
                var = tk.StringVar()
                text_widget = tk.Text(form_frame, font=('Segoe UI', 11), width=40, height=4)
                text_widget.grid(row=i*2+1, column=0, columnspan=2, padx=40, pady=(0, 10), sticky='w')
                text_widget.bind('<KeyRelease>', lambda e, tw=text_widget, v=var: v.set(tw.get("1.0", "end-1c")))
                self.product_vars[label] = var
        
        # Buttons
        btn_frame = tk.Frame(form_frame, bg='white')
        btn_frame.grid(row=len(fields)*2, column=0, columnspan=2, pady=40)
        
        tk.Button(btn_frame,
                 text="💾 Save Product",
                 font=('Segoe UI', 12, 'bold'),
                 bg=COLORS['success'],
                 fg='white',
                 padx=30,
                 pady=12,
                 cursor='hand2',
                 command=self.save_product).pack(side='left', padx=10)
        
        tk.Button(btn_frame,
                 text="🗑️ Clear Form",
                 font=('Segoe UI', 12),
                 bg=COLORS['warning'],
                 fg='white',
                 padx=30,
                 pady=12,
                 cursor='hand2',
                 command=self.clear_form).pack(side='left', padx=10)
        
        tk.Button(btn_frame,
                 text="← Back",
                 font=('Segoe UI', 12),
                 bg=COLORS['accent'],
                 fg='white',
                 padx=30,
                 pady=12,
                 cursor='hand2',
                 command=self.app.show_dashboard).pack(side='left', padx=10)
    
    def save_product(self):
        """Save product to database"""
        try:
            name = self.product_vars["Product Name"].get().strip()
            category = self.product_vars["Category"].get()
            price = self.product_vars["Price (₹)"].get().strip()
            stock = self.product_vars["Stock Quantity"].get().strip()
            
            # Validation
            if not name:
                messagebox.showwarning("Validation Error", "Product name is required!")
                return
            
            if not price or not price.replace('.', '', 1).isdigit():
                messagebox.showwarning("Validation Error", "Please enter a valid price!")
                return
            
            if not stock or not stock.isdigit():
                messagebox.showwarning("Validation Error", "Please enter a valid stock quantity!")
                return
            
            price_val = float(price)
            stock_val = int(stock)
            
            if price_val <= 0:
                messagebox.showwarning("Validation Error", "Price must be greater than zero!")
                return
            
            if stock_val < 0:
                messagebox.showwarning("Validation Error", "Stock quantity cannot be negative!")
                return
            
            # Save to database
            success = self.app.db.execute_query("""
                INSERT INTO products (name, category, price, stock) 
                VALUES (?, ?, ?, ?)
            """, (name, category, price_val, stock_val))
            
            if success:
                messagebox.showinfo("Success", "✅ Product added successfully!")
                self.clear_form()
            else:
                messagebox.showerror("Error", "Failed to save product. Please try again.")
            
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def clear_form(self):
        """Clear all form fields"""
        for var in self.product_vars.values():
            if isinstance(var, tk.StringVar):
                var.set("")
        
        # Reset category to first item
        categories = self.app.db.fetch_all("SELECT name FROM categories")
        if categories:
            self.product_vars["Category"].set(categories[0][0])
    
    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_frame, width=event.width)
    
    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def destroy(self):
        self.canvas.destroy()

# ---------------- VIEW PRODUCTS PAGE ---------------- 
class ViewProductsPage:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.create_widgets()
    
    def create_widgets(self):
        # Main container
        main_container = tk.Frame(self.parent, bg=COLORS['background'])
        main_container.pack(fill='both', expand=True)
        
        # Header
        header_frame = tk.Frame(main_container, bg=COLORS['primary'])
        header_frame.pack(fill='x', padx=30, pady=30)
        
        tk.Label(header_frame,
                text="📦 Product Inventory",
                font=('Segoe UI', 24, 'bold'),
                bg=COLORS['primary'],
                fg='white').pack(pady=20)
        
        # Search and filter section
        filter_frame = tk.Frame(main_container, bg=COLORS['background'])
        filter_frame.pack(fill='x', padx=30, pady=(0, 20))
        
        # Search box
        search_container = tk.Frame(filter_frame, bg=COLORS['light'], relief='sunken', bd=1)
        search_container.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_container,
                                    textvariable=self.search_var,
                                    font=('Segoe UI', 11),
                                    bg='white',
                                    relief='flat',
                                    bd=0)
        self.search_entry.pack(side='left', fill='both', expand=True, padx=10, pady=8)
        self.search_entry.insert(0, "Search products...")
        self.search_entry.bind('<FocusIn>', lambda e: self.clear_search_placeholder())
        self.search_entry.bind('<KeyRelease>', lambda e: self.filter_products())
        
        search_btn = tk.Button(search_container,
                              text="🔍",
                              font=('Segoe UI', 12),
                              bg=COLORS['accent'],
                              fg='white',
                              relief='flat',
                              bd=0,
                              cursor='hand2',
                              command=self.filter_products)
        search_btn.pack(side='right', padx=5)
        
        # Category filter
        tk.Label(filter_frame,
                text="Category:",
                font=('Segoe UI', 11),
                bg=COLORS['background'],
                fg=COLORS['secondary']).pack(side='left', padx=(0, 10))
        
        self.category_var = tk.StringVar(value="All")
        categories = ["All"] + [cat[0] for cat in self.app.db.fetch_all("SELECT name FROM categories")]
        category_combo = ttk.Combobox(filter_frame,
                                     textvariable=self.category_var,
                                     values=categories,
                                     font=('Segoe UI', 11),
                                     width=15,
                                     state='readonly')
        category_combo.pack(side='left', padx=(0, 20))
        category_combo.bind('<<ComboboxSelected>>', lambda e: self.filter_products())
        
        # Stock filter
        tk.Label(filter_frame,
                text="Stock:",
                font=('Segoe UI', 11),
                bg=COLORS['background'],
                fg=COLORS['secondary']).pack(side='left', padx=(0, 10))
        
        self.stock_var = tk.StringVar(value="All")
        stock_combo = ttk.Combobox(filter_frame,
                                  textvariable=self.stock_var,
                                  values=["All", "In Stock (>10)", "Low Stock (1-10)", "Out of Stock"],
                                  font=('Segoe UI', 11),
                                  width=15,
                                  state='readonly')
        stock_combo.pack(side='left')
        stock_combo.bind('<<ComboboxSelected>>', lambda e: self.filter_products())
        
        # Table container
        table_container = tk.Frame(main_container, bg=COLORS['background'])
        table_container.pack(fill='both', expand=True, padx=30, pady=(0, 30))
        
        # Create table with scrollbars
        table_frame = tk.Frame(table_container, bg='white', relief='flat', highlightthickness=1,
                              highlightbackground=COLORS['border'])
        table_frame.pack(fill='both', expand=True)
        
        # Create horizontal scrollbar
        x_scrollbar = ttk.Scrollbar(table_frame, orient='horizontal')
        x_scrollbar.pack(side='bottom', fill='x')
        
        # Create vertical scrollbar
        y_scrollbar = ttk.Scrollbar(table_frame)
        y_scrollbar.pack(side='right', fill='y')
        
        # Create treeview
        self.tree = ttk.Treeview(table_frame,
                                yscrollcommand=y_scrollbar.set,
                                xscrollcommand=x_scrollbar.set,
                                height=20)
        
        # Configure scrollbars
        y_scrollbar.config(command=self.tree.yview)
        x_scrollbar.config(command=self.tree.xview)
        
        # Define columns
        self.tree['columns'] = ('ID', 'Name', 'Category', 'Price', 'Stock', 'Status')
        
        # Format columns
        self.tree.column('#0', width=0, stretch=False)
        self.tree.column('ID', width=50, anchor='center', stretch=False)
        self.tree.column('Name', width=250, anchor='w', minwidth=200)
        self.tree.column('Category', width=120, anchor='center', stretch=False)
        self.tree.column('Price', width=100, anchor='e', stretch=False)
        self.tree.column('Stock', width=80, anchor='center', stretch=False)
        self.tree.column('Status', width=120, anchor='center', stretch=False)
        
        # Create headings
        self.tree.heading('#0', text='')
        self.tree.heading('ID', text='ID', anchor='center')
        self.tree.heading('Name', text='Product Name', anchor='center')
        self.tree.heading('Category', text='Category', anchor='center')
        self.tree.heading('Price', text='Price (₹)', anchor='center')
        self.tree.heading('Stock', text='Stock', anchor='center')
        self.tree.heading('Status', text='Status', anchor='center')
        
        # Style the treeview
        style = ttk.Style()
        style.configure("Treeview",
                       background="white",
                       foreground=COLORS['primary'],
                       fieldbackground="white",
                       rowheight=35,
                       font=('Segoe UI', 10))
        
        style.map('Treeview', background=[('selected', COLORS['accent'])])
        
        style.configure("Treeview.Heading",
                      background=COLORS['primary'],
                      foreground='white',
                      font=('Segoe UI', 11, 'bold'))
        
        # Pack treeview
        self.tree.pack(fill='both', expand=True)
        
        # Action buttons
        btn_frame = tk.Frame(table_container, bg=COLORS['background'])
        btn_frame.pack(fill='x', pady=20)
        
        tk.Button(btn_frame,
                 text="🔄 Refresh",
                 font=('Segoe UI', 11),
                 bg=COLORS['accent'],
                 fg='white',
                 padx=20,
                 pady=8,
                 cursor='hand2',
                 command=self.load_products).pack(side='left', padx=5)
        
        tk.Button(btn_frame,
                 text="📊 View Analytics",
                 font=('Segoe UI', 11),
                 bg=COLORS['success'],
                 fg='white',
                 padx=20,
                 pady=8,
                 cursor='hand2',
                 command=self.app.show_analytics).pack(side='left', padx=5)
        
        tk.Button(btn_frame,
                 text="← Back to Dashboard",
                 font=('Segoe UI', 11),
                 bg=COLORS['secondary'],
                 fg='white',
                 padx=20,
                 pady=8,
                 cursor='hand2',
                 command=self.app.show_dashboard).pack(side='right', padx=5)
        
        # Load initial products
        self.load_products()
    
    def clear_search_placeholder(self):
        if self.search_entry.get() == "Search products...":
            self.search_entry.delete(0, 'end')
    
    def load_products(self, search_query=""):
        """Load products into treeview"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Build query based on filters
        query = "SELECT id, name, category, price, stock FROM products WHERE 1=1"
        params = []
        
        # Apply search filter
        search_text = self.search_var.get()
        if search_text and search_text != "Search products...":
            query += " AND (name LIKE ? OR category LIKE ?)"
            params.extend([f"%{search_text}%", f"%{search_text}%"])
        
        # Apply category filter
        category = self.category_var.get()
        if category != "All":
            query += " AND category = ?"
            params.append(category)
        
        # Apply stock filter
        stock_filter = self.stock_var.get()
        if stock_filter == "In Stock (>10)":
            query += " AND stock > 10"
        elif stock_filter == "Low Stock (1-10)":
            query += " AND stock BETWEEN 1 AND 10"
        elif stock_filter == "Out of Stock":
            query += " AND stock = 0"
        
        query += " ORDER BY id DESC"
        
        # Fetch products
        products = self.app.db.fetch_all(query, params)
        
        # Insert products
        for product in products:
            stock = product[4]
            if stock > 20:
                status = "🟢 In Stock"
                status_color = COLORS['success']
            elif stock > 0:
                status = "🟡 Low Stock"
                status_color = COLORS['warning']
            else:
                status = "🔴 Out of Stock"
                status_color = COLORS['danger']
            
            item_id = self.tree.insert('', 'end', values=(
                product[0],
                product[1],
                product[2],
                f"₹{product[3]:,.2f}",
                stock,
                status
            ))
            
            # Color code rows based on stock
            if stock == 0:
                self.tree.item(item_id, tags=('out_of_stock',))
        
        # Configure tag colors
        self.tree.tag_configure('out_of_stock', background='#FFE4E1')
    
    def filter_products(self):
        """Filter products based on search and filters"""
        self.load_products()
    
    def destroy(self):
        self.tree.destroy()

# ---------------- GENERATE BILL PAGE ---------------- 
class GenerateBillPage:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.bill_items = []
        self.create_widgets()
    
    def create_widgets(self):
        # Main container
        main_container = tk.Frame(self.parent, bg=COLORS['background'])
        main_container.pack(fill='both', expand=True)
        
        # Header
        header_frame = tk.Frame(main_container, bg=COLORS['primary'])
        header_frame.pack(fill='x', padx=30, pady=30)
        
        tk.Label(header_frame,
                text="🧾 Generate Bill",
                font=('Segoe UI', 24, 'bold'),
                bg=COLORS['primary'],
                fg='white').pack(pady=20)
        
        # Two column layout
        columns_frame = tk.Frame(main_container, bg=COLORS['background'])
        columns_frame.pack(fill='both', expand=True, padx=30, pady=(0, 30))
        
        # Left column - Product selection
        left_frame = tk.Frame(columns_frame, bg='white', relief='flat', highlightthickness=2,
                             highlightbackground=COLORS['border'])
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 15))
        
        tk.Label(left_frame,
                text="➕ Add Products",
                font=('Segoe UI', 18, 'bold'),
                bg='white',
                fg=COLORS['primary']).pack(pady=20)
        
        # Product selection form
        form_frame = tk.Frame(left_frame, bg='white')
        form_frame.pack(fill='x', padx=20, pady=10)
        
        # Product dropdown
        tk.Label(form_frame,
                text="Select Product:",
                font=('Segoe UI', 11, 'bold'),
                bg='white',
                fg=COLORS['primary']).grid(row=0, column=0, sticky='w', pady=10)
        
        self.selected_product = tk.StringVar()
        self.load_products_combo()
        
        self.product_combo = ttk.Combobox(form_frame,
                                         textvariable=self.selected_product,
                                         font=('Segoe UI', 11),
                                         state='readonly',
                                         width=40)
        self.product_combo.grid(row=0, column=1, padx=10, pady=10, sticky='w')
        self.product_combo.bind('<<ComboboxSelected>>', self.on_product_select)
        
        # Quantity
        tk.Label(form_frame,
                text="Quantity:",
                font=('Segoe UI', 11, 'bold'),
                bg='white',
                fg=COLORS['primary']).grid(row=1, column=0, sticky='w', pady=10)
        
        self.quantity_var = tk.StringVar(value="1")
        self.quantity_entry = tk.Entry(form_frame,
                                      textvariable=self.quantity_var,
                                      font=('Segoe UI', 11),
                                      width=10)
        self.quantity_entry.grid(row=1, column=1, padx=10, pady=10, sticky='w')
        
        # Product info display
        self.info_frame = tk.Frame(form_frame, bg=COLORS['light'])
        self.info_frame.grid(row=2, column=0, columnspan=2, sticky='ew', pady=10)
        self.info_frame.grid_remove()
        
        # Add to bill button
        add_btn = tk.Button(form_frame,
                          text="➕ Add to Bill",
                          font=('Segoe UI', 12, 'bold'),
                          bg=COLORS['success'],
                          fg='white',
                          padx=30,
                          pady=10,
                          cursor='hand2',
                          command=self.add_to_bill)
        add_btn.grid(row=3, column=0, columnspan=2, pady=20)
        
        # Right column - Bill preview
        right_frame = tk.Frame(columns_frame, bg='white', relief='flat', highlightthickness=2,
                              highlightbackground=COLORS['border'])
        right_frame.pack(side='right', fill='both', expand=True)
        
        tk.Label(right_frame,
                text="📋 Bill Preview",
                font=('Segoe UI', 18, 'bold'),
                bg='white',
                fg=COLORS['primary']).pack(pady=20)
        
        # Bill items display
        bill_display_frame = tk.Frame(right_frame, bg='white')
        bill_display_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Create a canvas and scrollbar for bill items
        bill_canvas = tk.Canvas(bill_display_frame, bg='white', highlightthickness=0)
        bill_scrollbar = ttk.Scrollbar(bill_display_frame, orient='vertical', command=bill_canvas.yview)
        
        self.bill_items_frame = tk.Frame(bill_canvas, bg='white')
        
        bill_canvas.configure(yscrollcommand=bill_scrollbar.set)
        bill_canvas.pack(side='left', fill='both', expand=True)
        bill_scrollbar.pack(side='right', fill='y')
        
        bill_canvas.create_window((0, 0), window=self.bill_items_frame, anchor='nw')
        
        self.bill_items_frame.bind('<Configure>', 
                                  lambda e: bill_canvas.configure(scrollregion=bill_canvas.bbox("all")))
        
        # Bill summary
        summary_frame = tk.Frame(right_frame, bg=COLORS['light'])
        summary_frame.pack(fill='x', padx=20, pady=20)
        
        self.subtotal_var = tk.StringVar(value="₹0.00")
        self.gst_var = tk.StringVar(value="₹0.00")
        self.total_var = tk.StringVar(value="₹0.00")
        
        # Summary labels
        tk.Label(summary_frame,
                text="BILL SUMMARY",
                font=('Segoe UI', 14, 'bold'),
                bg=COLORS['light'],
                fg=COLORS['primary']).pack(pady=(10, 20))
        
        # Subtotal
        subtotal_frame = tk.Frame(summary_frame, bg=COLORS['light'])
        subtotal_frame.pack(fill='x', padx=20, pady=5)
        
        tk.Label(subtotal_frame,
                text="Subtotal:",
                font=('Segoe UI', 12),
                bg=COLORS['light'],
                fg=COLORS['secondary']).pack(side='left')
        
        tk.Label(subtotal_frame,
                textvariable=self.subtotal_var,
                font=('Segoe UI', 12, 'bold'),
                bg=COLORS['light'],
                fg=COLORS['primary']).pack(side='right')
        
        # GST
        gst_frame = tk.Frame(summary_frame, bg=COLORS['light'])
        gst_frame.pack(fill='x', padx=20, pady=5)
        
        tk.Label(gst_frame,
                text="GST (18%):",
                font=('Segoe UI', 12),
                bg=COLORS['light'],
                fg=COLORS['secondary']).pack(side='left')
        
        tk.Label(gst_frame,
                textvariable=self.gst_var,
                font=('Segoe UI', 12, 'bold'),
                bg=COLORS['light'],
                fg=COLORS['primary']).pack(side='right')
        
        # Total
        total_frame = tk.Frame(summary_frame, bg=COLORS['light'])
        total_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(total_frame,
                text="TOTAL:",
                font=('Segoe UI', 14, 'bold'),
                bg=COLORS['light'],
                fg=COLORS['success']).pack(side='left')
        
        tk.Label(total_frame,
                textvariable=self.total_var,
                font=('Segoe UI', 14, 'bold'),
                bg=COLORS['light'],
                fg=COLORS['success']).pack(side='right')
        
        # Action buttons at bottom
        btn_frame = tk.Frame(main_container, bg=COLORS['background'])
        btn_frame.pack(fill='x', padx=30, pady=(0, 30))
        
        tk.Button(btn_frame,
                 text="🧾 Save & Print Bill",
                 font=('Segoe UI', 12, 'bold'),
                 bg=COLORS['accent'],
                 fg='white',
                 padx=30,
                 pady=12,
                 cursor='hand2',
                 command=self.save_and_print_bill).pack(side='left', padx=5)
        
        tk.Button(btn_frame,
                 text="🗑️ Clear Bill",
                 font=('Segoe UI', 12),
                 bg=COLORS['warning'],
                 fg='white',
                 padx=30,
                 pady=12,
                 cursor='hand2',
                 command=self.clear_bill).pack(side='left', padx=5)
        
        tk.Button(btn_frame,
                 text="← Back to Dashboard",
                 font=('Segoe UI', 12),
                 bg=COLORS['secondary'],
                 fg='white',
                 padx=30,
                 pady=12,
                 cursor='hand2',
                 command=self.app.show_dashboard).pack(side='right', padx=5)
        
        # Initialize bill display
        self.update_bill_display()
    
    def load_products_combo(self):
        """Load products into combobox"""
        products = self.app.db.fetch_all("""
            SELECT id, name, price, stock 
            FROM products 
            WHERE stock > 0 
            ORDER BY name
        """)
        
        product_list = [f"{p[0]} - {p[1]} (₹{p[2]:.2f}) - Stock: {p[3]}" for p in products]
        self.product_combo['values'] = product_list
        
        if product_list:
            self.product_combo.set(product_list[0])
            self.on_product_select()
    
    def on_product_select(self, event=None):
        """Show product info when selected"""
        product_str = self.selected_product.get()
        if not product_str or " - " not in product_str:
            return
        
        try:
            # Parse product info
            parts = product_str.split(' - ')
            if len(parts) >= 3:
                price_part = parts[2].split(')')[0].replace('₹', '')
                price = float(price_part)
                
                # Update info frame
                for widget in self.info_frame.winfo_children():
                    widget.destroy()
                
                tk.Label(self.info_frame,
                        text=f"Price: ₹{price:.2f}",
                        font=('Segoe UI', 10),
                        bg=COLORS['light'],
                        fg=COLORS['primary']).pack(pady=5)
                
                self.info_frame.grid()
                
        except:
            pass
    
    def add_to_bill(self):
        """Add selected product to bill"""
        try:
            product_str = self.selected_product.get()
            if not product_str or " - " not in product_str:
                messagebox.showwarning("Selection Error", "Please select a product.")
                return
            
            # Parse product info
            parts = product_str.split(' - ')
            product_id = int(parts[0])
            product_name = parts[1]
            
            price_part = parts[2].split(')')[0].replace('₹', '')
            price = float(price_part)
            
            stock = int(parts[3].split(': ')[1])
            
            quantity = int(self.quantity_var.get())
            
            if quantity <= 0:
                messagebox.showwarning("Quantity Error", "Please enter a valid quantity.")
                return
            
            if quantity > stock:
                messagebox.showwarning("Stock Error", 
                                      f"Only {stock} units available in stock.")
                return
            
            # Check if product already in bill
            for i, item in enumerate(self.bill_items):
                if item['id'] == product_id:
                    new_qty = item['quantity'] + quantity
                    if new_qty > stock:
                        messagebox.showwarning("Stock Error", 
                                              f"Cannot add {quantity} more. Max available: {stock - item['quantity']}")
                        return
                    self.bill_items[i]['quantity'] = new_qty
                    self.update_bill_display()
                    return
            
            # Add new item
            self.bill_items.append({
                'id': product_id,
                'name': product_name,
                'price': price,
                'quantity': quantity
            })
            
            self.update_bill_display()
            
            # Reset quantity
            self.quantity_var.set("1")
            
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numbers.")
    
    def update_bill_display(self):
        """Update the bill display"""
        # Clear current display
        for widget in self.bill_items_frame.winfo_children():
            widget.destroy()
        
        if not self.bill_items:
            tk.Label(self.bill_items_frame,
                    text="No items in bill\nAdd products from the left panel",
                    font=('Segoe UI', 11),
                    bg='white',
                    fg=COLORS['secondary']).pack(pady=50)
            self.subtotal_var.set("₹0.00")
            self.gst_var.set("₹0.00")
            self.total_var.set("₹0.00")
            return
        
        # Header
        header_frame = tk.Frame(self.bill_items_frame, bg='white')
        header_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(header_frame,
                text="Item",
                font=('Segoe UI', 11, 'bold'),
                bg='white',
                fg=COLORS['primary']).pack(side='left', padx=(0, 150))
        
        tk.Label(header_frame,
                text="Qty",
                font=('Segoe UI', 11, 'bold'),
                bg='white',
                fg=COLORS['primary']).pack(side='left', padx=20)
        
        tk.Label(header_frame,
                text="Price",
                font=('Segoe UI', 11, 'bold'),
                bg='white',
                fg=COLORS['primary']).pack(side='left', padx=20)
        
        tk.Label(header_frame,
                text="Total",
                font=('Segoe UI', 11, 'bold'),
                bg='white',
                fg=COLORS['primary']).pack(side='right')
        
        tk.Frame(self.bill_items_frame, bg=COLORS['border'], height=1).pack(fill='x', pady=(0, 10))
        
        # Calculate totals
        subtotal = 0
        
        # Display items
        for idx, item in enumerate(self.bill_items):
            item_frame = tk.Frame(self.bill_items_frame, bg='white')
            item_frame.pack(fill='x', pady=5)
            
            item_total = item['price'] * item['quantity']
            subtotal += item_total
            
            # Item name with remove button
            name_frame = tk.Frame(item_frame, bg='white')
            name_frame.pack(side='left', padx=(0, 10))
            
            tk.Button(name_frame,
                     text="✕",
                     font=('Segoe UI', 9),
                     bg=COLORS['danger'],
                     fg='white',
                     bd=0,
                     padx=5,
                     cursor='hand2',
                     command=lambda i=idx: self.remove_item(i)).pack(side='left')
            
            name = item['name'][:20] + "..." if len(item['name']) > 20 else item['name']
            tk.Label(name_frame,
                    text=name,
                    font=('Segoe UI', 10),
                    bg='white',
                    fg=COLORS['dark']).pack(side='left', padx=5)
            
            # Quantity
            tk.Label(item_frame,
                    text=str(item['quantity']),
                    font=('Segoe UI', 10),
                    bg='white',
                    fg=COLORS['dark']).pack(side='left', padx=20)
            
            # Price
            tk.Label(item_frame,
                    text=f"₹{item['price']:.2f}",
                    font=('Segoe UI', 10),
                    bg='white',
                    fg=COLORS['dark']).pack(side='left', padx=20)
            
            # Total
            tk.Label(item_frame,
                    text=f"₹{item_total:.2f}",
                    font=('Segoe UI', 10, 'bold'),
                    bg='white',
                    fg=COLORS['primary']).pack(side='right')
        
        tk.Frame(self.bill_items_frame, bg=COLORS['border'], height=1).pack(fill='x', pady=10)
        
        # Calculate taxes and total
        gst = subtotal * 0.18
        total = subtotal + gst
        
        self.subtotal_var.set(f"₹{subtotal:,.2f}")
        self.gst_var.set(f"₹{gst:,.2f}")
        self.total_var.set(f"₹{total:,.2f}")
    
    def remove_item(self, index):
        """Remove item from bill"""
        if 0 <= index < len(self.bill_items):
            self.bill_items.pop(index)
            self.update_bill_display()
    
    def clear_bill(self):
        """Clear the current bill"""
        self.bill_items = []
        self.update_bill_display()
        self.load_products_combo()
        self.quantity_var.set("1")
    
    def save_and_print_bill(self):
        """Save bill to database and generate PDF"""
        if not self.bill_items:
            messagebox.showwarning("No Items", "Please add items to the bill first.")
            return
        
        try:
            # Calculate totals
            subtotal = sum(item['price'] * item['quantity'] for item in self.bill_items)
            gst = subtotal * 0.18
            total = subtotal + gst
            
            # Save each item to database
            sale_ids = []
            for item in self.bill_items:
                # Update stock
                self.app.db.execute_query("""
                    UPDATE products 
                    SET stock = stock - ? 
                    WHERE id = ?
                """, (item['quantity'], item['id']))
                
                # Record sale
                self.app.db.execute_query("""
                    INSERT INTO sales (product_id, product_name, quantity, subtotal, gst, total, sale_date, sale_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    item['id'],
                    item['name'],
                    item['quantity'],
                    item['price'] * item['quantity'],
                    item['price'] * item['quantity'] * 0.18,
                    item['price'] * item['quantity'] * 1.18,
                    date.today().isoformat(),
                    datetime.now().strftime("%H:%M:%S")
                ))
                
                # Get the sale ID
                sale_id = self.app.db.cur.lastrowid
                sale_ids.append(sale_id)
            
            # Generate PDF
            self.generate_pdf_invoice(subtotal, gst, total, sale_ids)
            
            # Show success message
            messagebox.showinfo("Success", 
                              f"✅ Bill saved successfully!\n\n"
                              f"Total Amount: ₹{total:,.2f}\n"
                              f"Items: {len(self.bill_items)}\n"
                              f"PDF invoice generated.")
            
            # Clear bill
            self.clear_bill()
            
            # Refresh dashboard
            if hasattr(self.app, 'dashboard_page'):
                self.app.dashboard_page.refresh()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save bill: {str(e)}")
    
    def generate_pdf_invoice(self, subtotal, gst, total, sale_ids):
        """Generate PDF invoice"""
        try:
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"invoice_{timestamp}.pdf"
            
            # Create PDF document
            doc = SimpleDocTemplate(filename, pagesize=letter)
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor(COLORS['primary']),
                spaceAfter=30
            )
            
            # Content
            content = []
            
            # Title
            content.append(Paragraph("RetailPro Invoice", title_style))
            
            # Store info
            store_info = [
                f"Invoice #: INV-{timestamp}",
                f"Date: {datetime.now().strftime('%B %d, %Y')}",
                f"Time: {datetime.now().strftime('%I:%M %p')}",
                ""
            ]
            
            for line in store_info:
                content.append(Paragraph(line, styles['Normal']))
            
            content.append(Spacer(1, 20))
            
            # Table data
            table_data = [['Product', 'Quantity', 'Unit Price', 'Total']]
            
            for item in self.bill_items:
                item_total = item['price'] * item['quantity']
                table_data.append([
                    item['name'],
                    str(item['quantity']),
                    f"₹{item['price']:.2f}",
                    f"₹{item_total:.2f}"
                ])
            
            # Add total row
            table_data.append(['', '', 'Subtotal:', f"₹{subtotal:.2f}"])
            table_data.append(['', '', 'GST (18%):', f"₹{gst:.2f}"])
            table_data.append(['', '', 'TOTAL:', f"₹{total:.2f}"])
            
            # Create table
            table = Table(table_data, colWidths=[250, 60, 80, 80])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(COLORS['primary'])),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-2, -4), colors.beige),
                ('GRID', (0, 0), (-1, -4), 1, colors.black),
                ('ALIGN', (0, 1), (0, -4), 'LEFT'),
                ('FONTNAME', (-2, -3), (-1, -1), 'Helvetica-Bold'),
                ('BACKGROUND', (-2, -3), (-1, -1), colors.HexColor(COLORS['light'])),
            ]))
            
            content.append(table)
            content.append(Spacer(1, 40))
            
            # Footer
            footer = Paragraph("Thank you for your business!<br/><br/>"
                              "Terms & Conditions:<br/>"
                              "1. Goods once sold will not be taken back.<br/>"
                              "2. All disputes are subject to jurisdiction.", 
                              styles['Normal'])
            content.append(footer)
            
            # Build PDF
            doc.build(content)
            
        except Exception as e:
            messagebox.showwarning("PDF Warning", f"Invoice saved but PDF generation failed: {str(e)}")
    
    def destroy(self):
        self.bill_items = []

# ---------------- SALES REPORT PAGE ---------------- 
class SalesReportPage:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.create_widgets()
    
    def create_widgets(self):
        # Main container with scrollbar
        main_container = tk.Frame(self.parent, bg=COLORS['background'])
        main_container.pack(fill='both', expand=True)
        
        # Create a canvas and scrollbar
        self.canvas = tk.Canvas(main_container, bg=COLORS['background'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient='vertical', command=self.canvas.yview)
        
        # Create a frame inside the canvas
        self.scrollable_frame = tk.Frame(self.canvas, bg=COLORS['background'])
        
        # Configure the canvas
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack the canvas and scrollbar
        self.canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Create window in canvas for scrollable frame
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor='nw')
        
        # Bind events for scrolling
        self.scrollable_frame.bind('<Configure>', self.on_frame_configure)
        self.canvas.bind('<Configure>', self.on_canvas_configure)
        
        # Bind mouse wheel
        self.canvas.bind_all('<MouseWheel>', self.on_mousewheel)
        
        # Header
        header_frame = tk.Frame(self.scrollable_frame, bg=COLORS['primary'])
        header_frame.pack(fill='x', padx=30, pady=30)
        
        tk.Label(header_frame,
                text="📈 Sales Reports",
                font=('Segoe UI', 24, 'bold'),
                bg=COLORS['primary'],
                fg='white').pack(pady=20)
        
        # Date range selector
        date_frame = tk.Frame(self.scrollable_frame, bg=COLORS['background'])
        date_frame.pack(fill='x', padx=30, pady=(0, 20))
        
        # From date
        tk.Label(date_frame,
                text="From Date:",
                font=('Segoe UI', 11),
                bg=COLORS['background'],
                fg=COLORS['secondary']).pack(side='left', padx=(0, 10))
        
        self.from_date_var = tk.StringVar(value=date.today().isoformat())
        from_date_entry = tk.Entry(date_frame,
                                  textvariable=self.from_date_var,
                                  font=('Segoe UI', 11),
                                  width=12)
        from_date_entry.pack(side='left', padx=(0, 30))
        
        # To date
        tk.Label(date_frame,
                text="To Date:",
                font=('Segoe UI', 11),
                bg=COLORS['background'],
                fg=COLORS['secondary']).pack(side='left', padx=(0, 10))
        
        self.to_date_var = tk.StringVar(value=date.today().isoformat())
        to_date_entry = tk.Entry(date_frame,
                                textvariable=self.to_date_var,
                                font=('Segoe UI', 11),
                                width=12)
        to_date_entry.pack(side='left', padx=(0, 30))
        
        # Generate report button
        tk.Button(date_frame,
                 text="Generate Report",
                 font=('Segoe UI', 11),
                 bg=COLORS['accent'],
                 fg='white',
                 padx=20,
                 pady=5,
                 cursor='hand2',
                 command=self.generate_report).pack(side='left')
        
        # Report statistics
        stats_frame = tk.Frame(self.scrollable_frame, bg=COLORS['background'])
        stats_frame.pack(fill='x', padx=30, pady=(0, 20))
        
        self.total_sales_var = tk.StringVar(value="₹0.00")
        self.total_items_var = tk.StringVar(value="0")
        self.avg_sale_var = tk.StringVar(value="₹0.00")
        self.num_transactions_var = tk.StringVar(value="0")
        
        stats_data = [
            ("Total Sales", self.total_sales_var, COLORS['success']),
            ("Items Sold", self.total_items_var, COLORS['accent']),
            ("Avg Sale", self.avg_sale_var, COLORS['primary']),
            ("Transactions", self.num_transactions_var, COLORS['warning'])
        ]
        
        for i, (title, var, color) in enumerate(stats_data):
            card = tk.Frame(stats_frame, bg='white', relief='flat', highlightthickness=1,
                          highlightbackground=COLORS['border'])
            card.grid(row=0, column=i, padx=5, ipadx=15, ipady=15, sticky='nsew')
            
            tk.Label(card,
                    text=title,
                    font=('Segoe UI', 10),
                    bg='white',
                    fg=COLORS['secondary']).pack()
            
            tk.Label(card,
                    textvariable=var,
                    font=('Segoe UI', 16, 'bold'),
                    bg='white',
                    fg=color).pack()
        
        # Sales table
        table_frame = tk.Frame(self.scrollable_frame, bg=COLORS['background'])
        table_frame.pack(fill='both', expand=True, padx=30, pady=(0, 30))
        
        # Create table with scrollbars
        table_container = tk.Frame(table_frame, bg='white', relief='flat', highlightthickness=1,
                                  highlightbackground=COLORS['border'])
        table_container.pack(fill='both', expand=True)
        
        # Create vertical scrollbar
        y_scrollbar = ttk.Scrollbar(table_container)
        y_scrollbar.pack(side='right', fill='y')
        
        # Create treeview
        self.sales_tree = ttk.Treeview(table_container,
                                      yscrollcommand=y_scrollbar.set,
                                      height=15)
        y_scrollbar.config(command=self.sales_tree.yview)
        
        # Define columns
        self.sales_tree['columns'] = ('ID', 'Date', 'Product', 'Qty', 'Subtotal', 'GST', 'Total')
        
        # Format columns
        self.sales_tree.column('#0', width=0, stretch=False)
        self.sales_tree.column('ID', width=50, anchor='center')
        self.sales_tree.column('Date', width=100, anchor='center')
        self.sales_tree.column('Product', width=200, anchor='w')
        self.sales_tree.column('Qty', width=60, anchor='center')
        self.sales_tree.column('Subtotal', width=100, anchor='e')
        self.sales_tree.column('GST', width=80, anchor='e')
        self.sales_tree.column('Total', width=100, anchor='e')
        
        # Create headings
        self.sales_tree.heading('#0', text='')
        self.sales_tree.heading('ID', text='ID', anchor='center')
        self.sales_tree.heading('Date', text='Date', anchor='center')
        self.sales_tree.heading('Product', text='Product', anchor='center')
        self.sales_tree.heading('Qty', text='Qty', anchor='center')
        self.sales_tree.heading('Subtotal', text='Subtotal', anchor='center')
        self.sales_tree.heading('GST', text='GST', anchor='center')
        self.sales_tree.heading('Total', text='Total', anchor='center')
        
        # Style the treeview
        style = ttk.Style()
        style.configure("Treeview",
                       background="white",
                       foreground=COLORS['primary'],
                       fieldbackground="white",
                       rowheight=30)
        
        style.configure("Treeview.Heading",
                      background=COLORS['primary'],
                      foreground='white',
                      font=('Segoe UI', 10, 'bold'))
        
        self.sales_tree.pack(fill='both', expand=True)
        
        # Action buttons
        btn_frame = tk.Frame(self.scrollable_frame, bg=COLORS['background'])
        btn_frame.pack(fill='x', padx=30, pady=(0, 30))
        
        tk.Button(btn_frame,
                 text="📊 View Analytics",
                 font=('Segoe UI', 11),
                 bg=COLORS['accent'],
                 fg='white',
                 padx=20,
                 pady=8,
                 cursor='hand2',
                 command=self.app.show_analytics).pack(side='left', padx=5)
        
        tk.Button(btn_frame,
                 text="🔄 Refresh",
                 font=('Segoe UI', 11),
                 bg=COLORS['success'],
                 fg='white',
                 padx=20,
                 pady=8,
                 cursor='hand2',
                 command=self.generate_report).pack(side='left', padx=5)
        
        tk.Button(btn_frame,
                 text="← Back to Dashboard",
                 font=('Segoe UI', 11),
                 bg=COLORS['secondary'],
                 fg='white',
                 padx=20,
                 pady=8,
                 cursor='hand2',
                 command=self.app.show_dashboard).pack(side='right', padx=5)
        
        # Generate initial report
        self.generate_report()
    
    def generate_report(self):
        """Generate sales report for selected date range"""
        try:
            from_date = self.from_date_var.get()
            to_date = self.to_date_var.get()
            
            # Clear existing items
            for item in self.sales_tree.get_children():
                self.sales_tree.delete(item)
            
            # Fetch sales data
            sales = self.app.db.fetch_all("""
                SELECT id, sale_date, product_name, quantity, subtotal, gst, total 
                FROM sales 
                WHERE sale_date BETWEEN ? AND ?
                ORDER BY sale_date DESC, id DESC
            """, (from_date, to_date))
            
            # Insert sales data
            total_sales = 0
            total_items = 0
            num_transactions = len(sales)
            
            for sale in sales:
                self.sales_tree.insert('', 'end', values=(
                    sale[0],
                    sale[1],
                    sale[2],
                    sale[3],
                    f"₹{sale[4]:,.2f}",
                    f"₹{sale[5]:,.2f}",
                    f"₹{sale[6]:,.2f}"
                ))
                
                total_sales += sale[6]
                total_items += sale[3]
            
            # Update statistics
            avg_sale = total_sales / num_transactions if num_transactions > 0 else 0
            
            self.total_sales_var.set(f"₹{total_sales:,.2f}")
            self.total_items_var.set(str(total_items))
            self.avg_sale_var.set(f"₹{avg_sale:,.2f}")
            self.num_transactions_var.set(str(num_transactions))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
    
    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_frame, width=event.width)
    
    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def destroy(self):
        self.canvas.destroy()

# ---------------- ANALYTICS PAGE ---------------- 
class AnalyticsPage:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.create_widgets()
    
    def create_widgets(self):
        # Main container with scrollbar
        main_container = tk.Frame(self.parent, bg=COLORS['background'])
        main_container.pack(fill='both', expand=True)
        
        # Create a canvas and scrollbar
        self.canvas = tk.Canvas(main_container, bg=COLORS['background'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient='vertical', command=self.canvas.yview)
        
        # Create a frame inside the canvas
        self.scrollable_frame = tk.Frame(self.canvas, bg=COLORS['background'])
        
        # Configure the canvas
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack the canvas and scrollbar
        self.canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Create window in canvas for scrollable frame
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor='nw')
        
        # Bind events for scrolling
        self.scrollable_frame.bind('<Configure>', self.on_frame_configure)
        self.canvas.bind('<Configure>', self.on_canvas_configure)
        
        # Bind mouse wheel
        self.canvas.bind_all('<MouseWheel>', self.on_mousewheel)
        
        # Header
        header_frame = tk.Frame(self.scrollable_frame, bg=COLORS['primary'])
        header_frame.pack(fill='x', padx=30, pady=30)
        
        tk.Label(header_frame,
                text="📊 Sales Analytics",
                font=('Segoe UI', 24, 'bold'),
                bg=COLORS['primary'],
                fg='white').pack(pady=20)
        
        # Chart type selector
        chart_frame = tk.Frame(self.scrollable_frame, bg=COLORS['background'])
        chart_frame.pack(fill='x', padx=30, pady=(0, 20))
        
        tk.Label(chart_frame,
                text="Select Chart Type:",
                font=('Segoe UI', 12, 'bold'),
                bg=COLORS['background'],
                fg=COLORS['primary']).pack(side='left', padx=(0, 20))
        
        # Chart type buttons
        btn_frame = tk.Frame(chart_frame, bg=COLORS['background'])
        btn_frame.pack(side='left')
        
        tk.Button(btn_frame,
                 text="📅 Daily Sales",
                 font=('Segoe UI', 10),
                 bg=COLORS['accent'],
                 fg='white',
                 padx=15,
                 pady=6,
                 cursor='hand2',
                 command=self.show_daily_chart).pack(side='left', padx=5)
        
        tk.Button(btn_frame,
                 text="🏷️ Category Sales",
                 font=('Segoe UI', 10),
                 bg=COLORS['success'],
                 fg='white',
                 padx=15,
                 pady=6,
                 cursor='hand2',
                 command=self.show_category_chart).pack(side='left', padx=5)
        
        tk.Button(btn_frame,
                 text="🏆 Top Products",
                 font=('Segoe UI', 10),
                 bg=COLORS['warning'],
                 fg='white',
                 padx=15,
                 pady=6,
                 cursor='hand2',
                 command=self.show_top_products).pack(side='left', padx=5)
        
        # Chart container
        self.chart_container = tk.Frame(self.scrollable_frame, bg='white', relief='flat', 
                                       highlightthickness=2, highlightbackground=COLORS['border'])
        self.chart_container.pack(fill='both', expand=True, padx=30, pady=(0, 20))
        
        # Action buttons
        btn_frame = tk.Frame(self.scrollable_frame, bg=COLORS['background'])
        btn_frame.pack(fill='x', padx=30, pady=(0, 30))
        
        tk.Button(btn_frame,
                 text="📄 View Sales Report",
                 font=('Segoe UI', 11),
                 bg=COLORS['accent'],
                 fg='white',
                 padx=20,
                 pady=8,
                 cursor='hand2',
                 command=self.app.show_sales_report).pack(side='left', padx=5)
        
        tk.Button(btn_frame,
                 text="← Back to Dashboard",
                 font=('Segoe UI', 11),
                 bg=COLORS['secondary'],
                 fg='white',
                 padx=20,
                 pady=8,
                 cursor='hand2',
                 command=self.app.show_dashboard).pack(side='right', padx=5)
        
        # Show default chart
        self.show_daily_chart()
    
    def show_daily_chart(self):
        """Show daily sales chart"""
        # Clear previous chart
        for widget in self.chart_container.winfo_children():
            widget.destroy()
        
        # Fetch daily sales data
        data = self.app.db.fetch_all("""
            SELECT sale_date, SUM(total) 
            FROM sales 
            WHERE sale_date >= date('now', '-30 days')
            GROUP BY sale_date 
            ORDER BY sale_date
        """)
        
        if not data:
            tk.Label(self.chart_container,
                    text="No sales data available for the last 30 days",
                    font=('Segoe UI', 14),
                    bg='white',
                    fg=COLORS['secondary']).pack(expand=True, pady=100)
            return
        
        dates = [d[0][5:] for d in data]  # Remove year from date
        totals = [d[1] for d in data]
        
        # Create matplotlib figure
        plt.rcParams.update({'font.size': 10})
        fig, ax = plt.subplots(figsize=(10, 5), dpi=100)
        
        # Use beige-olive color scheme
        bar_color = COLORS['accent']
        line_color = COLORS['primary']
        
        ax.bar(dates, totals, color=bar_color, alpha=0.7, label='Daily Sales')
        ax.plot(dates, totals, color=line_color, marker='o', linewidth=2, markersize=5)
        ax.set_title('Daily Sales Trend (Last 30 Days)', fontsize=14, fontweight='bold', color=COLORS['primary'])
        ax.set_xlabel('Date', color=COLORS['secondary'])
        ax.set_ylabel('Total Sales (₹)', color=COLORS['secondary'])
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, self.chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
    
    def show_category_chart(self):
        """Show sales by category chart"""
        # Clear previous chart
        for widget in self.chart_container.winfo_children():
            widget.destroy()
        
        # Fetch category data
        data = self.app.db.fetch_all("""
            SELECT p.category, SUM(s.total) 
            FROM sales s 
            JOIN products p ON s.product_id = p.id 
            GROUP BY p.category
            ORDER BY SUM(s.total) DESC
        """)
        
        if not data:
            tk.Label(self.chart_container,
                    text="No category sales data available",
                    font=('Segoe UI', 14),
                    bg='white',
                    fg=COLORS['secondary']).pack(expand=True, pady=100)
            return
        
        categories = [d[0] for d in data]
        totals = [d[1] for d in data]
        
        # Create matplotlib figure
        plt.rcParams.update({'font.size': 10})
        fig, ax = plt.subplots(figsize=(10, 5), dpi=100)
        
        # Use beige-olive color scheme
        colors_list = [COLORS['accent'], COLORS['success'], COLORS['warning'], 
                      COLORS['primary'], COLORS['secondary'], COLORS['border']]
        
        ax.pie(totals, labels=categories, autopct='%1.1f%%', 
               colors=colors_list[:len(categories)], startangle=90, textprops={'color': COLORS['primary']})
        ax.set_title('Sales Distribution by Category', fontsize=14, fontweight='bold', color=COLORS['primary'])
        ax.axis('equal')
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, self.chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
    
    def show_top_products(self):
        """Show top selling products"""
        # Clear previous chart
        for widget in self.chart_container.winfo_children():
            widget.destroy()
        
        # Fetch top products
        data = self.app.db.fetch_all("""
            SELECT product_name, SUM(quantity) as total_qty 
            FROM sales 
            GROUP BY product_id 
            ORDER BY total_qty DESC 
            LIMIT 10
        """)
        
        if not data:
            tk.Label(self.chart_container,
                    text="No product sales data available",
                    font=('Segoe UI', 14),
                    bg='white',
                    fg=COLORS['secondary']).pack(expand=True, pady=100)
            return
        
        products = [d[0][:15] + '...' if len(d[0]) > 15 else d[0] for d in data]
        quantities = [d[1] for d in data]
        
        # Create matplotlib figure
        plt.rcParams.update({'font.size': 10})
        fig, ax = plt.subplots(figsize=(10, 5), dpi=100)
        
        # Use beige-olive color scheme
        bar_color = COLORS['accent']
        
        bars = ax.barh(products, quantities, color=bar_color)
        ax.set_title('Top Selling Products', fontsize=14, fontweight='bold', color=COLORS['primary'])
        ax.set_xlabel('Quantity Sold', color=COLORS['secondary'])
        ax.set_facecolor('white')
        fig.patch.set_facecolor('white')
        
        # Add value labels on bars
        for bar in bars:
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2, 
                   f' {int(width)}', va='center', color=COLORS['primary'])
        
        plt.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, self.chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
    
    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_frame, width=event.width)
    
    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def destroy(self):
        self.canvas.destroy()

# ---------------- MAIN APPLICATION CLASS ----------------
class RetailManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🛒 Modern Retail Management System")
        self.root.geometry("1200x700")
        self.root.configure(bg=COLORS['background'])
        
        # Initialize database
        self.db = Database()
        
        # Current user state
        self.current_user = None
        self.is_admin = False
        
        # Current page reference
        self.current_page = None
        
        # Configure styles
        self.configure_styles()
        
        # Create sidebar
        self.create_sidebar()
        
        # Create main content area
        self.content_frame = tk.Frame(self.root, bg=COLORS['background'])
        self.content_frame.pack(side='right', fill='both', expand=True)
        
        # Show login screen initially
        self.show_login()
    
    def configure_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure button styles
        style.configure('Primary.TButton', 
                       background=COLORS['accent'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       font=('Segoe UI', 10, 'bold'))
        
        style.map('Primary.TButton',
                 background=[('active', self.darken_color(COLORS['accent']))])
        
        # Configure entry styles
        style.configure('Modern.TEntry',
                       fieldbackground='white',
                       bordercolor=COLORS['accent'],
                       lightcolor=COLORS['accent'],
                       darkcolor=COLORS['accent'])
    
    def create_sidebar(self):
        """Create sidebar navigation (initially hidden)"""
        self.sidebar = tk.Frame(self.root, bg=COLORS['sidebar'], width=0)
        self.sidebar.pack(side='left', fill='y')
        self.sidebar.pack_propagate(False)
        
        # Sidebar will be shown after login
    
    def show_sidebar(self):
        """Show sidebar after login"""
        self.sidebar.config(width=250)
        
        # User info
        user_frame = tk.Frame(self.sidebar, bg=COLORS['primary'], height=120)
        user_frame.pack(fill='x')
        user_frame.pack_propagate(False)
        
        tk.Label(user_frame,
                text="👤",
                font=('Segoe UI', 32),
                bg=COLORS['primary'],
                fg='white').pack(pady=(20, 5))
        
        tk.Label(user_frame,
                text="Administrator",
                font=('Segoe UI', 14, 'bold'),
                bg=COLORS['primary'],
                fg='white').pack()
        
        tk.Label(user_frame,
                text="RetailPro System",
                font=('Segoe UI', 10),
                bg=COLORS['primary'],
                fg=COLORS['light']).pack(pady=(0, 10))
        
        # Navigation menu
        nav_items = [
            ("📊 Dashboard", self.show_dashboard),
            ("➕ Add Product", self.show_add_product),
            ("📦 View Products", self.show_view_products),
            ("🧾 Generate Bill", self.show_generate_bill),
            ("📈 Sales Report", self.show_sales_report),
            ("📊 Analytics", self.show_analytics),
            ("⚙️ Settings", self.show_settings),
            ("🚪 Logout", self.logout)
        ]
        
        for icon_text, command in nav_items:
            btn = tk.Button(self.sidebar,
                          text=f"  {icon_text}",
                          font=('Segoe UI', 11),
                          bg=COLORS['sidebar'],
                          fg='white',
                          anchor='w',
                          bd=0,
                          padx=20,
                          pady=15,
                          cursor='hand2',
                          command=command)
            btn.pack(fill='x')
            btn.bind('<Enter>', lambda e, b=btn: b.config(bg=self.darken_color(COLORS['sidebar'])))
            btn.bind('<Leave>', lambda e, b=btn: b.config(bg=COLORS['sidebar']))
        
        # Footer
        tk.Label(self.sidebar,
                text=f"© RetailPro {datetime.now().year}",
                font=('Segoe UI', 9),
                bg=COLORS['sidebar'],
                fg=COLORS['light']).pack(side='bottom', pady=20)
    
    def hide_sidebar(self):
        """Hide sidebar for login screen"""
        self.sidebar.config(width=0)
    
    def show_login(self):
        """Show login page"""
        self.hide_sidebar()
        self.clear_content()
        self.login_page = LoginPage(self.content_frame, self)
    
    def show_dashboard(self):
        """Show dashboard page"""
        if not self.is_admin:
            self.show_login()
            return
        
        self.show_sidebar()
        self.clear_content()
        self.dashboard_page = DashboardPage(self.content_frame, self)
        self.current_page = 'dashboard'
    
    def show_add_product(self):
        """Show add product page"""
        if not self.is_admin:
            self.show_login()
            return
        
        self.clear_content()
        self.add_product_page = AddProductPage(self.content_frame, self)
        self.current_page = 'add_product'
    
    def show_view_products(self):
        """Show view products page"""
        if not self.is_admin:
            self.show_login()
            return
        
        self.clear_content()
        self.view_products_page = ViewProductsPage(self.content_frame, self)
        self.current_page = 'view_products'
    
    def show_generate_bill(self):
        """Show generate bill page"""
        if not self.is_admin:
            self.show_login()
            return
        
        self.clear_content()
        self.generate_bill_page = GenerateBillPage(self.content_frame, self)
        self.current_page = 'generate_bill'
    
    def show_sales_report(self):
        """Show sales report page"""
        if not self.is_admin:
            self.show_login()
            return
        
        self.clear_content()
        self.sales_report_page = SalesReportPage(self.content_frame, self)
        self.current_page = 'sales_report'
    
    def show_analytics(self):
        """Show analytics page"""
        if not self.is_admin:
            self.show_login()
            return
        
        self.clear_content()
        self.analytics_page = AnalyticsPage(self.content_frame, self)
        self.current_page = 'analytics'
    
    def show_settings(self):
        """Show settings page (simplified)"""
        if not self.is_admin:
            self.show_login()
            return
        
        self.clear_content()
        
        # Simple settings page
        settings_frame = tk.Frame(self.content_frame, bg=COLORS['background'])
        settings_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        tk.Label(settings_frame,
                text="⚙️ Settings",
                font=('Segoe UI', 24, 'bold'),
                bg=COLORS['background'],
                fg=COLORS['primary']).pack(pady=(0, 30))
        
        # Settings content
        settings_content = tk.Frame(settings_frame, bg='white')
        settings_content.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(settings_content,
                text="System Settings",
                font=('Segoe UI', 16, 'bold'),
                bg='white',
                fg=COLORS['primary']).pack(pady=(0, 20))
        
        # Simple settings options
        settings_options = [
            ("Business Name:", "RetailPro Store"),
            ("Tax Rate (%):", "18"),
            ("Currency Symbol:", "₹"),
            ("Receipt Footer:", "Thank you for shopping!")
        ]
        
        for i, (label, default) in enumerate(settings_options):
            tk.Label(settings_content,
                    text=label,
                    font=('Segoe UI', 11),
                    bg='white',
                    fg=COLORS['secondary']).grid(row=i, column=0, padx=20, pady=15, sticky='w')
            
            entry = tk.Entry(settings_content,
                           font=('Segoe UI', 11),
                           bg=COLORS['light'],
                           width=30)
            entry.grid(row=i, column=1, padx=20, pady=15, sticky='w')
            entry.insert(0, default)
        
        # Save button
        tk.Button(settings_content,
                 text="💾 Save Settings",
                 font=('Segoe UI', 12, 'bold'),
                 bg=COLORS['success'],
                 fg='white',
                 padx=30,
                 pady=10,
                 cursor='hand2',
                 command=lambda: messagebox.showinfo("Settings", "Settings saved successfully!")).grid(row=len(settings_options), column=0, columnspan=2, pady=40)
        
        # Back button
        tk.Button(settings_frame,
                 text="← Back to Dashboard",
                 font=('Segoe UI', 11),
                 bg=COLORS['accent'],
                 fg='white',
                 padx=20,
                 pady=8,
                 cursor='hand2',
                 command=self.show_dashboard).pack(side='bottom', pady=20)
    
    def logout(self):
        """Logout and return to login screen"""
        self.current_user = None
        self.is_admin = False
        self.hide_sidebar()
        self.show_login()
    
    def clear_content(self):
        """Clear the content frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def darken_color(self, color):
        """Darken a hex color for hover effects"""
        if color.startswith('#'):
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            r = max(0, r - 30)
            g = max(0, g - 30)
            b = max(0, b - 30)
            return f'#{r:02x}{g:02x}{b:02x}'
        return color
    
    def on_closing(self):
        """Handle application closing"""
        self.db.close()
        self.root.destroy()

# ---------------- MAIN EXECUTION ----------------
if __name__ == "__main__":
    root = tk.Tk()
    app = RetailManagementApp(root)
    
    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()