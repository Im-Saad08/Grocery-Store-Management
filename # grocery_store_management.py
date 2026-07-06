# grocery_store_management.py
import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
from datetime import datetime

class GroceryStoreApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Grocery Store Management System")
        self.root.geometry("1000x600")
        self.root.minsize(800, 500)  # Prevent window from being too small
        self.root.configure(bg="#FFFF00")
        
        # Initialize data
        self.sold_items = []
        self.load_initial_data()
        
        # GUI Setup
        self.setup_ui()
        
    def load_initial_data(self):
        """Load data from CSV or use sample data."""
        if os.path.exists("sales_data.csv"):
            try:
                with open("sales_data.csv", mode="r", newline="") as file:
                    reader = csv.reader(file)
                    next(reader)  # Skip header row
                    self.sold_items = [tuple(row) for row in reader]
            except Exception as e:
                messagebox.showwarning("Warning", f"Could not load data: {str(e)}")
                self.sold_items = []
        
        if not self.sold_items:  # Default sample data
            self.sold_items = [
                ("101", "Apples", "5", "1.50", "7.50", datetime.now().strftime("%Y-%m-%d")),
                ("102", "Bread", "2", "3.00", "6.00", datetime.now().strftime("%Y-%m-%d")),
                ("103", "Milk", "1", "2.50", "2.50", datetime.now().strftime("%Y-%m-%d"))
            ]

    def setup_ui(self):
        """Create the main UI components."""
        # Custom Style
        style = ttk.Style()
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TButton", font=("Times New Roman", 10), background="#4CAF50", foreground="yellow")
        style.configure("Treeview", rowheight=25)  # Better row spacing
        style.map("TButton", background=[("active", "#45a049")])
        
        # Header Frame
        header_frame = ttk.Frame(self.root, style="TFrame")
        header_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(
            header_frame, 
            text="GROCERY STORE MANAGEMENT SYSTEM", 
            font=("Arial", 16, "bold"), 
            background="#f0f0f0"
        ).pack()
        
        # Treeview Frame
        tree_frame = ttk.Frame(self.root, style="TFrame")
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Treeview (Table)
        self.tree = ttk.Treeview(
            tree_frame, 
            columns=("ID", "Item", "Quantity", "Price", "Total", "Date"), 
            show="headings",
            selectmode="extended"
        )
        
        # Configure Columns
        columns = {
            "ID": {"width": 50, "anchor": "center"},
            "Item": {"width": 150, "anchor": "w"},
            "Quantity": {"width": 80, "anchor": "center"},
            "Price": {"width": 100, "anchor": "e"},
            "Total": {"width": 100, "anchor": "e"},
            "Date": {"width": 120, "anchor": "center"}
        }
        
        for col, settings in columns.items():
            self.tree.heading(col, text=col)
            self.tree.column(col, **settings)
        
        self.tree.pack(fill="both", expand=True, side="left")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        # Populate table
        self.refresh_table()
        
        # Button Frame
        button_frame = ttk.Frame(self.root, style="TFrame")
        button_frame.pack(fill="x", padx=20, pady=10)
        
        buttons = [
            ("Add Sale", self.add_sale),
            ("Delete Selected", self.delete_selected),
            ("Generate Report", self.generate_report),
            ("Exit", self.root.quit)
        ]
        
        for text, command in buttons[:-1]:  # Left-aligned buttons
            ttk.Button(
                button_frame, 
                text=text, 
                command=command,
                style="TButton"
            ).pack(side="left", padx=5, pady=5)
        
        # Exit button (right-aligned)
        ttk.Button(
            button_frame, 
            text=buttons[-1][0], 
            command=buttons[-1][1],
            style="TButton"
        ).pack(side="right", padx=5, pady=5)
    
    def refresh_table(self):
        """Update the Treeview with current data."""
        self.tree.delete(*self.tree.get_children())
        for item in self.sold_items:
            self.tree.insert("", "end", values=item)
    
    def add_sale(self):
        """Open a popup to add a new sale."""
        add_window = tk.Toplevel(self.root)
        add_window.title("Add New Sale")
        add_window.geometry("400x300")
        add_window.resizable(False, False)
        add_window.configure(bg="#f0f0f0")
        
        fields = [
            ("Item Name:", 30),
            ("Quantity:", 30),
            ("Price ($):", 30)
        ]
        
        entries = []
        for text, width in fields:
            ttk.Label(add_window, text=text, background="#f0f0f0").pack(pady=5)
            entry = ttk.Entry(add_window, width=width)
            entry.pack(pady=5)
            entries.append(entry)
        
        def save_sale():
            """Validate inputs and save to data."""
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
                new_id = str(int(self.sold_items[-1][0]) + 1) if self.sold_items else "101"
                sale_date = datetime.now().strftime("%Y-%m-%d")
                new_sale = (new_id, item, str(qty), f"{price:.2f}", f"{total:.2f}", sale_date)
                
                self.sold_items.append(new_sale)
                self.refresh_table()
                add_window.destroy()
                messagebox.showinfo("Success", "Sale added successfully!")
            except ValueError:
                messagebox.showerror("Error", "Invalid input! Quantity must be a positive integer, price must be a positive number.")
        
        ttk.Button(
            add_window, 
            text="Save", 
            command=save_sale,
            style="TButton"
        ).pack(pady=20)
    
    def delete_selected(self):
        """Delete selected items from the table."""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "No items selected!")
            return
        
        confirm = messagebox.askyesno(
            "Confirm Deletion", 
            f"Delete {len(selected_items)} selected item(s)?"
        )
        
        if confirm:
            deleted_ids = {self.tree.item(item, "values")[0] for item in selected_items}
            self.sold_items = [x for x in self.sold_items if x[0] not in deleted_ids]
            self.refresh_table()
            messagebox.showinfo("Success", f"Deleted {len(selected_items)} item(s).")
    
    def generate_report(self):
        """Export data to CSV."""
        try:
            with open("sales_data.csv", mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Item", "Quantity", "Price", "Total", "Date"])
                writer.writerows(self.sold_items)
            messagebox.showinfo(
                "Success", 
                f"Report generated successfully!\nFile saved as: {os.path.abspath('sales_data.csv')}"
            )
        except PermissionError:
            messagebox.showerror("Error", "Permission denied! Close the CSV file if it's open.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = GroceryStoreApp(root)
    root.mainloop()