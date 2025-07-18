import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import os
from datetime import datetime
from payroll_app import Employee, PayrollSystem

class PayrollGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Payroll Management System")
        self.root.geometry("1000x600")

        # Apply ttk theme
        style = ttk.Style()
        style.theme_use("clam")  # Other options: 'alt', 'vista', 'default'

        self.filename = None
        self.payroll = None

        # Menu Bar
        self.create_menu()

        # Middle Frame (Employee Table)
        self.setup_table()

        # Bottom Frame (Buttons)
        self.setup_buttons()

        # Status Bar
        self.status_label = ttk.Label(self.root, text="No file loaded", relief=tk.SUNKEN, anchor="w")
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open", command=self.open_existing_file)
        file_menu.add_command(label="Save", command=self.save_to_csv)
        file_menu.add_command(label="Save As", command=self.save_as_new_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_app)
        menubar.add_cascade(label="File", menu=file_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=lambda: messagebox.showinfo("About", "Payroll System v2.0"))
        menubar.add_cascade(label="Help", menu=help_menu)

    def setup_table(self):
        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        columns = ['NAME', 'DOB', 'GENDER', 'POST', 'BASIC', 'ATT', 'ABSNT', 'OT', 'NET']
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=100)

        # Add Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

    def setup_buttons(self):
        frame = ttk.Frame(self.root)
        frame.pack(fill=tk.X, pady=10)

        ttk.Button(frame, text="Add Employee", command=self.add_employee, width=18).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame, text="Update Employee", command=self.update_employee, width=18).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame, text="Delete Employee", command=self.delete_employee, width=18).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame, text="Reload Data", command=self.reload_data, width=18).pack(side=tk.LEFT, padx=5)

    def refresh_table(self):
        self.tree.delete(*self.tree.get_children())
        if not self.payroll:
            return
        for emp in self.payroll.employees:
            dob_display = emp.dob.strftime("%Y-%m-%d") if isinstance(emp.dob, datetime) else str(emp.dob)
            self.tree.insert("", "end", values=(
                emp.name, dob_display, emp.gender, emp.post,
                emp.basic, emp.att, emp.absnt, emp.ot, emp.net
            ))

    def add_employee(self):
        if not self.payroll:
            messagebox.showerror("Error", "Load a company first", parent=self.root)
            return

        try:
            name_val = simpledialog.askstring("Name", "Enter name:", parent=self.root)
            if not name_val:
                raise ValueError("No input for name")
            name = name_val.strip()
            print(f"Name: {name}")

            year = simpledialog.askinteger("Year", "Enter birth year:", parent=self.root)
            month = simpledialog.askinteger("Month", "Enter birth month:", parent=self.root)
            day = simpledialog.askinteger("Day", "Enter birth day:", parent=self.root)
            if year is None or month is None or day is None:
                raise ValueError("Invalid DOB: year, month, and day must be provided")
            dob = datetime(int(year), int(month), int(day))
            print(f"DOB: {dob}")

            gender = simpledialog.askstring("Gender", "Enter Gender:", parent=self.root)
            if not gender:
                raise ValueError("No input for gender")

            post = simpledialog.askstring("Post", "Enter post:", parent=self.root)
            if not post:
                raise ValueError("No input for post")

            basic = simpledialog.askfloat("Basic", "Enter basic salary:", parent=self.root)
            if basic is None:
                raise ValueError("No input for basic")

            att = simpledialog.askfloat("Attendance", "Days attended (max 26):", parent=self.root)
            if att is None or not (0 <= att <= 26):
                raise ValueError("Invalid attendance")

            ot = simpledialog.askfloat("Overtime", "Enter overtime:", parent=self.root)
            if ot is None or ot < 0:
                raise ValueError("Invalid overtime")

            absnt = simpledialog.askfloat("Absent", "Enter days absent:", parent=self.root)
            if absnt is None or absnt < 0:
                raise ValueError("Invalid absent")

            pension_bool = messagebox.askyesno("Pension", "Does this employee have a pension?", parent=self.root)

            print(f"Creating Employee: {name}, {post}, {basic}")
            emp = Employee(name, dob, gender, post, basic, att, ot, absnt, pension_bool)
            self.payroll.add_employee(emp)
            self.refresh_table()
            print("Employee added and table refreshed.")

        except Exception as e:
            messagebox.showerror("Input Error", str(e))
            print(f"Error adding employee: {e}")


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

        if self.payroll is None:
            messagebox.showerror("Error", "No company loaded.")
            return

        # Find the employee object
        emp = next((e for e in self.payroll.employees if e.name == name), None)
        if not emp:
            messagebox.showerror("Error", "Employee not found")
            return

        # Ask user what to update
        options = [
            "Post", "Basic Salary", "Attendance", "Overtime",
            "Absent Days", "Pension Status", "Date of Birth"
        ]
        field = simpledialog.askstring("Update Field", f"Choose field to update:\n{', '.join(options)}")

        if not field:
            return

        field = field.lower()

        try:
            if field == "post":
                new_val = simpledialog.askstring("Post", "Enter new post:", initialvalue=emp.post)
                emp.post = new_val

            elif field == "basic salary":
                new_val = simpledialog.askfloat("Basic Salary", "Enter new basic salary:", initialvalue=emp.basic)
                if new_val is None:
                    raise ValueError("No input for basic salary")
                emp.basic = float(new_val)

            elif field == "attendance":
                new_val = simpledialog.askfloat("Attendance", "Enter new attendance:", initialvalue=emp.att)
                if new_val is None:
                    raise ValueError("No input for attendance")
                if new_val < 0 or new_val > 26:
                    raise ValueError("Attendance must be between 0 and 26")
            elif field == "overtime":
                new_val = simpledialog.askfloat("Overtime", "Enter new overtime hours:", initialvalue=emp.ot)
                if new_val is None:
                    raise ValueError("No input for overtime")
            elif field == "absent days":
                new_val = simpledialog.askfloat("Absent", "Enter new absent days:", initialvalue=emp.absnt)
                if new_val is None:
                    raise ValueError("No input for absent days")
                emp.absnt = float(new_val)

            elif field == "absent days":
                new_val = simpledialog.askfloat("Absent", "Enter new absent days:", initialvalue=emp.absnt)
            elif field == "date of birth":
                year = simpledialog.askinteger("Year", "Enter year:")
                month = simpledialog.askinteger("Month", "Enter month:")
                day = simpledialog.askinteger("Day", "Enter day:")
                if year is None or month is None or day is None:
                    raise ValueError("All date of birth fields must be provided")
                emp.dob = datetime(year, month, day)

            elif field == "date of birth":
                year = simpledialog.askinteger("Year", "Enter year:")
                month = simpledialog.askinteger("Month", "Enter month:")
                day = simpledialog.askinteger("Day", "Enter day:")
                if year is None or month is None or day is None:
                    raise ValueError("All date of birth fields must be provided")
                emp.dob = datetime(year, month, day)

            else:
                messagebox.showerror("Error", "Invalid field selected.")
                return

            # Recalculate values
            emp.calculate_payroll()

            self.refresh_table()

        except Exception as e:
            messagebox.showerror("Update Error", str(e))


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
