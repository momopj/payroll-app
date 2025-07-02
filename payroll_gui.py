import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
from turtle import pen

from payroll_app import Employee  # Reuse your existing logic
try:
    from payroll_app import PayrollSystem
except ImportError:
    # If PayrollSystem is not defined, try importing the correct class or show an error
    raise ImportError("PayrollSystem class not found in payroll_app.py. Please define it or correct the import.")

class PayrollGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Payroll System - GUI")

        self.filename = None
        self.payroll = None

        self.setup_company_selector()
        self.setup_table()
        self.setup_buttons()

    def setup_company_selector(self):
        frame = tk.Frame(self.root)
        frame.pack(pady=10)

        tk.Label(frame, text="Company Name:").pack(side=tk.LEFT)
        self.company_entry = tk.Entry(frame)
        self.company_entry.pack(side=tk.LEFT, padx=5)

        tk.Button(frame, text="Load Company", command=self.load_company).pack(side=tk.LEFT)

    def setup_table(self):
        columns = ['NAME', 'POST', 'BASIC', 'ATT', 'R/DAY', 'OT', 'EARNINGS']
        self.tree = ttk.Treeview(root, columns=columns, show='headings')

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack(pady=10, fill=tk.BOTH, expand=True)

    def setup_buttons(self):
        frame = tk.Frame(self.root)
        frame.pack(pady=10)

        tk.Button(frame, text="Add Employee", command=self.add_employee).pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="Delete Employee", command=self.delete_employee).pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="Save to CSV", command=self.save_to_csv).pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="Reload Data", command=self.reload_data).pack(side=tk.LEFT, padx=5)

    def load_company(self):
        company = self.company_entry.get().strip().lower().replace(" ", "_")
        if not company:
            messagebox.showerror("Error", "Enter a company name")
            return

        os.makedirs("companies", exist_ok=True)
        self.filename = os.path.join("companies", f"{company}.csv")
        self.payroll = PayrollSystem(self.filename)
        self.payroll.load_from_csv()
        self.refresh_table()

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        if not self.payroll:
            return
        for emp in self.payroll.employees:
            self.tree.insert("", "end", values=(emp.name, emp.post, emp.basic, emp.att, emp.r_day, emp.ot, emp.net))

    def add_employee(self):
        if not self.payroll:
            messagebox.showerror("Error", "Load a company first")
            return

        try:
            name = simpledialog.askstring("Name", "Enter name:")

            post = simpledialog.askstring("Post", "Enter post:")

            basic_val = simpledialog.askfloat("Basic", "Enter basic salary:")
            if basic_val is None:
                raise ValueError("No input for basic salary")
            basic = float(basic_val)

            att_val = simpledialog.askfloat("Attendance", "Days attended:")
            if att_val is None:
                raise ValueError("No input for attendance")
            if att_val < 0:
                raise ValueError("Attendance cannot be negative")
            if att_val > 26:
                raise ValueError("Attendance cannot exceed 26 days")
            att = float(att_val)

            ot_val = simpledialog.askstring("Overtime", "Enter overtime:")
            if ot_val is None:
                raise ValueError("No input for overtime")
            ot = float(ot_val)

            pension_percentage = simpledialog.askfloat("Pension", "Enter pension percentage (as decimal):")
        except Exception:
            messagebox.showerror("Input Error", "Invalid input")

            return

        emp = Employee(name, post, basic, att, ot, pension_percentage)
        self.payroll.add_employee(emp)
        self.refresh_table()

    def delete_employee(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Select an employee to delete")
            return

        name = self.tree.item(selected[0])["values"][0]
        if self.payroll is not None:
            self.payroll.delete_employee(name)
            self.refresh_table()
        else:
            messagebox.showerror("Error", "No company loaded.")

    def save_to_csv(self):
        if self.payroll:
            self.payroll.save_to_csv()

    def reload_data(self):
        if self.payroll:
            self.payroll.load_from_csv()
            self.refresh_table()

if __name__ == "__main__":
    root = tk.Tk()
    app = PayrollGUI(root)
    root.mainloop()
