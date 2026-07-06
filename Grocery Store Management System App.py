# saadi_groceries_management.py
import tkinter as tk
from tkinter import ttk, messagebox, PhotoImage
from tkinter.font import Font
import sqlite3
import os
import csv
from datetime import datetime

# --- Database Setup ---
class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect("saadi_groceries.db")
        self.create_tables()
        self.setup_default_users()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id TEXT PRIMARY KEY,
                item TEXT,
                quantity INTEGER,
                price REAL,
                total REAL,
                date TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                email TEXT PRIMARY KEY,
                password TEXT,
                role TEXT
            )
        """)
        self.conn.commit()

    def setup_default_users(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            # Your admin account
            cursor.execute(
                "INSERT INTO users VALUES (?,?,?)",
                ("mohtarm@saadi.com", "admin123", "admin")
            )
            self.conn.commit()

    def add_sale(self, sale_data):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO sales VALUES (?,?,?,?,?,?)", sale_data)
        self.conn.commit()

    def get_sales(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM sales")
        return cursor.fetchall()

    def delete_sale(self, sale_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM sales WHERE id=?", (sale_id,))
        self.conn.commit()

    def validate_user(self, email, password):
        cursor = self.conn.cursor()
        cursor.execute("SELECT password, role FROM users WHERE email=?", (email,))
        result = cursor.fetchone()
        return result if result and result[0] == password else None

    def add_user(self, email, password, role):
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users VALUES (?,?,?)",
                (email, password, role)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_users(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT email, role FROM users")
        return cursor.fetchall()

    def delete_user(self, email):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM users WHERE email=?", (email,))
        self.conn.commit()

# --- Modern Login Screen ---
class LoginScreen:
    def __init__(self, root, db, on_success_callback):
        self.root = root
        self.db = db
        self.on_success = on_success_callback
        
        # Configure main window
        self.root.title("Saadi Groceries - Login")
        self.root.geometry("800x600")
        self.root.configure(bg="#f8f9fa")
        
        # Try to load logo image
        try:
            self.logo_img = PhotoImage(file="grocery_logo.png")
            self.logo_img = self.logo_img.subsample(2, 2)
        except:
            self.logo_img = None
        
        self.setup_ui()

    def setup_ui(self):
        # Main container
        main_frame = tk.Frame(self.root, bg="white", bd=0, relief=tk.FLAT)
        main_frame.place(relx=0.5, rely=0.5, anchor="center", width=400, height=500)

        # Logo and header
        if self.logo_img:
            logo_label = tk.Label(main_frame, image=self.logo_img, bg="white")
            logo_label.pack(pady=(30,10))
        
        tk.Label(
            main_frame,
            text="SAADI GROCERIES",
            font=("Helvetica", 18, "bold"),
            bg="white",
            fg="#2c3e50"
        ).pack(pady=(0,5))

        tk.Label(
            main_frame,
            text="Welcome back",
            font=("Helvetica", 12),
            bg="white",
            fg="#7f8c8d"
        ).pack(pady=(0,30))

        # Email Entry
        email_frame = tk.Frame(main_frame, bg="white")
        email_frame.pack(pady=(0,15), padx=40, fill="x")
        
        tk.Label(
            email_frame,
            text="Email address",
            font=("Helvetica", 10),
            bg="white",
            fg="#34495e",
            anchor="w"
        ).pack(fill="x")
        
        self.email_entry = ttk.Entry(
            email_frame,
            font=("Helvetica", 12)
        )
        self.email_entry.pack(fill="x", pady=(5,0))

        # Password Entry
        password_frame = tk.Frame(main_frame, bg="white")
        password_frame.pack(pady=(0,5), padx=40, fill="x")
        
        tk.Label(
            password_frame,
            text="Password",
            font=("Helvetica", 10),
            bg="white",
            fg="#34495e",
            anchor="w"
        ).pack(fill="x")
        
        self.password_entry = ttk.Entry(
            password_frame,
            font=("Helvetica", 12),
            show="•"
        )
        self.password_entry.pack(fill="x", pady=(5,0))

        # Forgot password
        forgot_pass = tk.Label(
            main_frame,
            text="Forgot password?",
            font=("Helvetica", 9, "underline"),
            bg="white",
            fg="#3498db",
            cursor="hand2"
        )
        forgot_pass.pack(pady=(5,20))
        forgot_pass.bind("<Button-1>", lambda e: messagebox.showinfo("Info", "Contact admin to reset password"))

        # Login Button
        login_btn = tk.Button(
            main_frame,
            text="SIGN IN",
            font=("Helvetica", 12, "bold"),
            bg="#27ae60",
            fg="white",
            activebackground="#2ecc71",
            activeforeground="white",
            relief=tk.FLAT,
            bd=0,
            padx=30,
            pady=10,
            command=self.attempt_login
        )
        login_btn.pack(fill="x", padx=40, pady=(0,20))

        # Sign up prompt
        signup_frame = tk.Frame(main_frame, bg="white")
        signup_frame.pack()
        
        tk.Label(
            signup_frame,
            text="Don't have an account?",
            font=("Helvetica", 9),
            bg="white",
            fg="#7f8c8d"
        ).pack(side="left")
        
        signup_link = tk.Label(
            signup_frame,
            text="Sign up",
            font=("Helvetica", 9, "bold", "underline"),
            bg="white",
            fg="#3498db",
            cursor="hand2"
        )
        signup_link.pack(side="left", padx=5)
        signup_link.bind("<Button-1>", lambda e: messagebox.showinfo("Info", "Contact admin for new account"))

        # Focus and bindings
        self.email_entry.focus()
        self.root.bind("<Return>", lambda event: self.attempt_login())

    def attempt_login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        
        user = self.db.validate_user(email, password)
        if user:
            self.on_success(email, user[1])  # Pass email and role
        else:
            messagebox.showerror("Error", "Invalid credentials")

# --- Main Application ---
class GroceryStoreApp:
    def __init__(self, root):
        self.root = root
        self.db = DatabaseManager()  # Creates fresh database
        self.show_login()

    def show_login(self):
        self.clear_window()
        LoginScreen(
            root=self.root,
            db=self.db,
            on_success_callback=self.login_success
        )

    def login_success(self, email, role):
        self.current_user = email
        self.user_role = role
        self.setup_main_ui()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def setup_main_ui(self):
        self.clear_window()
        self.root.title(f"Saadi Groceries - {self.current_user}")
        self.root.geometry("1200x700")
        self.root.minsize(1000, 600)
        self.root.configure(bg="#f0f0f0")
        
        # Custom Style
        style = ttk.Style()
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TButton", 
                       font=("Arial", 10), 
                       background="#4CAF50", 
                       foreground="white",
                       padding=10)
        style.configure("Treeview", rowheight=25)
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        style.map("TButton", background=[("active", "#45a049")])

        # Header Frame
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill="x", padx=20, pady=10)

        ttk.Label(
            header_frame, 
            text=f"SAADI GROCERIES MANAGEMENT SYSTEM ({self.current_user})", 
            font=("Arial", 16, "bold")
        ).pack()

        # Main Content Frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Treeview Frame
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill="both", expand=True)

        # Treeview (Table)
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("ID", "Item", "Qty", "Price", "Total", "Date"),
            show="headings",
            selectmode="extended"
        )

        # Configure Columns
        columns = {
            "ID": {"width": 80, "anchor": "center"},
            "Item": {"width": 200, "anchor": "w"},
            "Qty": {"width": 80, "anchor": "center"},
            "Price": {"width": 100, "anchor": "e"},
            "Total": {"width": 100, "anchor": "e"},
            "Date": {"width": 120, "anchor": "center"}
        }

        for col, settings in columns.items():
            self.tree.heading(col, text=col)
            self.tree.column(col, **settings)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Layout
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Button Frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=10)

        # Buttons
        buttons = [
            ("Add Sale", self.add_sale),
            ("Delete Selected", self.delete_selected),
            ("Generate Report", self.generate_report),
            ("Logout", self.show_login)
        ]

        for text, command in buttons:
            ttk.Button(
                button_frame,
                text=text,
                command=command,
                style="TButton"
            ).pack(side="left", padx=5)

        # Admin-only features
        if self.user_role == "admin":
            ttk.Button(
                button_frame,
                text="Manage Users",
                command=self.manage_users,
                style="TButton"
            ).pack(side="left", padx=5)

        # Load initial data
        self.refresh_table()

    def refresh_table(self):
        self.tree.delete(*self.tree.get_children())
        for sale in self.db.get_sales():
            self.tree.insert("", "end", values=sale)

    def add_sale(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("Add New Sale")
        add_window.geometry("400x300")
        add_window.resizable(False, False)

        fields = [
            ("Item Name:", 30),
            ("Quantity:", 30),
            ("Price:", 30)
        ]

        entries = []
        for i, (text, width) in enumerate(fields):
            ttk.Label(add_window, text=text).grid(row=i, column=0, padx=10, pady=5, sticky="e")
            entry = ttk.Entry(add_window, width=width)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries.append(entry)

        def save_sale():
            values = [e.get().strip() for e in entries]
            if not all(values):
                messagebox.showerror("Error", "All fields are required!")
                return

            try:
                item, qty, price = values
                qty = int(qty)
                price = float(price)
                if qty <= 0 or price <= 0:
                    raise ValueError
                
                total = qty * price
                sale_id = str(int(max([row[0] for row in self.db.get_sales()] or ["0"])) + 1)
                sale_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                sale_data = (sale_id, item, qty, price, total, sale_date)
                
                self.db.add_sale(sale_data)
                self.refresh_table()
                add_window.destroy()
                messagebox.showinfo("Success", "Sale added successfully!")
            except ValueError:
                messagebox.showerror("Error", "Invalid input! Qty must be integer, price must be positive number.")

        ttk.Button(
            add_window,
            text="Save",
            command=save_sale,
            style="TButton"
        ).grid(row=len(fields), columnspan=2, pady=10)

    def delete_selected(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "No items selected!")
            return

        confirm = messagebox.askyesno(
            "Confirm Deletion", 
            f"Delete {len(selected_items)} selected item(s)?"
        )
        
        if confirm:
            for item in selected_items:
                sale_id = self.tree.item(item, "values")[0]
                self.db.delete_sale(sale_id)
            
            self.refresh_table()
            messagebox.showinfo("Success", f"Deleted {len(selected_items)} item(s).")

    def generate_report(self):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"saadi_sales_report_{timestamp}.csv"
            
            with open(filename, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Item", "Quantity", "Price", "Total", "Date"])
                writer.writerows(self.db.get_sales())
            
            messagebox.showinfo(
                "Success", 
                f"Report generated successfully!\nSaved as: {os.path.abspath(filename)}"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report:\n{str(e)}")

    def manage_users(self):
        manage_window = tk.Toplevel(self.root)
        manage_window.title("User Management")
        manage_window.geometry("600x400")

        # Treeview for users
        tree = ttk.Treeview(
            manage_window,
            columns=("Email", "Role"),
            show="headings"
        )
        tree.heading("Email", text="Email")
        tree.heading("Role", text="Role")
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Populate users
        for user in self.db.get_users():
            tree.insert("", "end", values=user)

        # Buttons
        button_frame = ttk.Frame(manage_window)
        button_frame.pack(fill="x", padx=10, pady=10)

        ttk.Button(
            button_frame,
            text="Add User",
            command=lambda: self.add_user(tree),
            style="TButton"
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Delete Selected",
            command=lambda: self.delete_user(tree),
            style="TButton"
        ).pack(side="left", padx=5)

    def add_user(self, tree):
        add_window = tk.Toplevel(self.root)
        add_window.title("Add New User")
        add_window.geometry("300x200")

        ttk.Label(add_window, text="Email:").pack(pady=5)
        email_entry = ttk.Entry(add_window)
        email_entry.pack(pady=5)

        ttk.Label(add_window, text="Password:").pack(pady=5)
        password_entry = ttk.Entry(add_window, show="*")
        password_entry.pack(pady=5)

        ttk.Label(add_window, text="Role:").pack(pady=5)
        role_var = tk.StringVar(value="cashier")
        ttk.Combobox(
            add_window,
            textvariable=role_var,
            values=["admin", "cashier"],
            state="readonly"
        ).pack(pady=5)

        def save_user():
            email = email_entry.get().strip()
            password = password_entry.get().strip()
            role = role_var.get()

            if not email or not password:
                messagebox.showerror("Error", "Email and password are required!")
                return

            if "@" not in email:
                messagebox.showerror("Error", "Please enter a valid email address!")
                return

            if self.db.add_user(email, password, role):
                tree.insert("", "end", values=(email, role))
                add_window.destroy()
                messagebox.showinfo("Success", "User added successfully!")
            else:
                messagebox.showerror("Error", "Email already exists!")

        ttk.Button(
            add_window,
            text="Save",
            command=save_user,
            style="TButton"
        ).pack(pady=10)

    def delete_user(self, tree):
        selected_items = tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "No users selected!")
            return

        emails = [tree.item(item, "values")[0] for item in selected_items]
        if self.current_user in emails:
            messagebox.showerror("Error", "You cannot delete your own account!")
            return

        confirm = messagebox.askyesno(
            "Confirm Deletion", 
            f"Delete {len(selected_items)} selected user(s)?"
        )
        
        if confirm:
            for email in emails:
                self.db.delete_user(email)
                tree.delete(selected_items[0])
            messagebox.showinfo("Success", f"Deleted {len(selected_items)} user(s).")

# --- Main Execution ---
if __name__ == "__main__":
    # Delete existing database to ensure fresh start
    if os.path.exists("saadi_groceries.db"):
        os.remove("saadi_groceries.db")
        
    root = tk.Tk()
    app = GroceryStoreApp(root)
    root.mainloop()