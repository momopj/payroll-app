import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkinter import filedialog
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

        self.status_label = tk.Label(self.root, text="No file loaded", fg="blue")
        self.status_label.pack(pady=5)


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
        columns = ['NAME', 'POST', 'BASIC', 'ATT', 'ABSNT', 'R/DAY', 'OT', 'EARNINGS']
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
        tk.Button(frame, text="Update Employee", command=self.update_employee).pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="Save to CSV", command=self.save_to_csv).pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="Save As New File", command=self.save_as_new_file).pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="Reload Data", command=self.reload_data).pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="Open File", command=self.open_existing_file).pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="Exit", command=self.exit_app).pack(side=tk.LEFT, padx=5)  

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

        self.status_label.config(text=f"Loaded: {os.path.basename(self.filename)}")

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        if not self.payroll:
            return
        for emp in self.payroll.employees:
            self.tree.insert("", "end", values=(emp.name, emp.post, emp.basic, emp.att, emp.absnt, emp.r_day, emp.ot, emp.net))

    def add_employee(self):
        if not self.payroll:
            messagebox.showerror("Error", "Load a company first")
            return

        try:
            name_val = simpledialog.askstring("Name", "Enter name:")
            if name_val is None or not name_val.strip():
                raise ValueError("No input for name")
            name = name_val.strip()
            

            post_val = simpledialog.askstring("Post", "Enter post:")
            if post_val is None or not post_val.strip():
                raise ValueError("No input for post")
            post = post_val.strip()

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

            ot_val = simpledialog.askfloat("Overtime", "Enter overtime:")
            if ot_val is None:
                raise ValueError("No input for overtime")
            if ot_val < 0:
                raise ValueError("Overtime cannot be negative")
            ot = float(ot_val)

            absnt_val = simpledialog.askfloat("Absent", "Enter days absent:")
            if absnt_val is None:
                raise ValueError("No input for absent days")
            if absnt_val < 0:
                raise ValueError("Absent days cannot be negative")
            absnt = float(absnt_val)

            pension_percentage_val = simpledialog.askfloat("Pension", "Enter pension percentage (as decimal):")
            if pension_percentage_val is None:
                raise ValueError("No input for pension percentage")
            if pension_percentage_val < 0 or pension_percentage_val > 1:
                raise ValueError("Pension percentage must be between 0 and 1")
            pension_percentage = float(pension_percentage_val)
            
        except Exception:
            messagebox.showerror("Input Error", "Invalid input")

            return

        emp = Employee(name, post, basic, att, ot, absnt, pension_percentage)
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

    def update_employee(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Select an employee to update")
            return

        current_values = self.tree.item(selected[0])["values"]
        name = current_values[0]

        # Find the employee object
        if self.payroll is None:
            messagebox.showerror("Error", "No company loaded.")
            return
        emp = next((e for e in self.payroll.employees if e.name == name), None)
        if not emp:
            messagebox.showerror("Error", "Employee not found")
            return

        try:
            post = simpledialog.askstring("Post", "Enter post:", initialvalue=emp.post)
            if not post:
                raise ValueError("Post required")

            basic = simpledialog.askfloat("Basic Salary", "Enter basic salary:", initialvalue=emp.basic)
            if basic is None:
                raise ValueError("Basic salary required")

            att = simpledialog.askfloat("Attendance", "Enter attendance (max 26):", initialvalue=emp.att)
            if att is None or att < 0 or att > 26:
                raise ValueError("Invalid attendance")

            ot = simpledialog.askfloat("Overtime", "Enter overtime:", initialvalue=emp.ot)
            if ot is None or ot < 0:
                raise ValueError("Invalid overtime")

            absnt = simpledialog.askfloat("Absent", "Enter days absent:", initialvalue=getattr(emp, 'absnt', 0))
            if absnt is None or absnt < 0:
                raise ValueError("Invalid absent days")

            pension_percentage = simpledialog.askfloat("Pension", "Enter pension % (0.0 to 1.0):", initialvalue=emp.pension_percentage)
            if pension_percentage is None or not (0 <= pension_percentage <= 1):
                raise ValueError("Invalid pension %")

        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
            return

        # Update the employee by replacing the object
        if self.payroll is not None:
            self.payroll.employees.remove(emp)
            updated_emp = Employee(emp.name, post, basic, att, ot, absnt, pension_percentage)
            self.payroll.add_employee(updated_emp)
            self.refresh_table()
        else:
            messagebox.showerror("Error", "No company loaded.")

    def open_existing_file(self):
        file_path = filedialog.askopenfilename(
            title="Open Payroll CSV",
            filetypes=[("CSV Files", "*.csv")],
            initialdir="companies"  # adjust if your files are elsewhere
        )

        if not file_path:
            return  # User cancelled

        self.filename = file_path
        self.payroll = PayrollSystem(self.filename)
        self.payroll.load_from_csv()
        self.refresh_table()

        self.status_label.config(text=f"Loaded: {os.path.basename(self.filename)}")
    
    def save_as_new_file(self):
        if not self.payroll or not self.payroll.employees:
            messagebox.showinfo("Info", "No data to save.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialdir="companies",
            title="Save Payroll As"
        )

        if not file_path:
            return  # Cancelled

        # Save using new filename
        self.filename = file_path
        self.payroll.filename = file_path
        self.payroll.save_to_csv()
        self.status_label.config(text=f"Saved As: {os.path.basename(file_path)}")

    def exit_app(self):
        if messagebox.askokcancel("Exit", "Do you really want to exit?"):
            self.root.destroy()



if __name__ == "__main__":
    root = tk.Tk()
    app = PayrollGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.exit_app)
    root.mainloop()
