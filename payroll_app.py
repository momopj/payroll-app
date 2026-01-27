import csv
import os
from datetime import datetime

class Employee:
    def __init__(self, name, dob, gender, post, basic, att, ot, absnt, pension_bool):
        self.name = name
        self.post = post
        self.basic = basic
        self.att = att
        self.ot = ot
        self.pension_bool = pension_bool
        self.absnt = absnt
        self.dob = dob
        self.gender = gender
        self.calculate_payroll()

    def calculate_payroll(self):
        self.r_day = self.basic / 26
        self.earnings = self.att * self.r_day

        if self.pension_bool == True:
            self.pension =  0.05 * self.basic
        else:
            self.pension = 0

        self.gross = self.earnings + self.ot
        self.absnt_amnt = self.absnt * self.r_day
        self.taxable = self.gross - 170000
        if self.taxable < 0:
            self.paye_30 = 0
            self.paye_35 = 0
            self.paye_40 = 0
        else:
            if 0 <= self.taxable < 1400000:
                self.paye_30 = round((self.taxable) * 0.30, 2)
                self.paye_35 = 0
                self.paye_40 = 0
            if 1400000 <= self.taxable < 9830000:
                self.remainder = self.taxable - 1400000
                self.paye_35 = round((self.remainder) * 0.35, 2)
                self.paye_30 = round((1400000) * 0.30, 2)
                self.paye_40 = 0
            if 9830000 <= self.taxable:
                self.remainder = self.taxable - 9830000
                self.paye_40 = round((self.remainder) * 0.40, 2)
                self.paye_35 = round((9830000) * 0.35, 2)
                self.paye_30 = round((1400000) * 0.30, 2)
            
        self.total_paye = round(self.paye_30 + self.paye_35 + self.paye_40 , 2)
        self.net = round(self.gross - self.pension - self.total_paye - self.absnt_amnt, 2)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.calculate_payroll()

class PayrollSystem:
    def __init__(self, filename='payroll.csv'):
        self.filename = filename
        self.employees = []

    def add_employee(self, emp):
        self.employees.append(emp)

    @staticmethod
    def safe_float(value, default=0.0):
        try:
            return float(value)
        except (ValueError, TypeError):
            return default


    def save_to_csv(self):
        if not self.filename:
            return

        with open(self.filename, "w", newline="", encoding="utf-8") as file:
            fieldnames = [
                "NAME", "DOB", "GENDER", "POST", "PENSION?", "BASIC", "ATT", "ABSNT", "ABSNT_AMNT",
                "R/DAY", "OT", "PENSION", "EARNINGS", "GROSS", "TAXABLE",
                "PAYE-25%", "PAYE-30%", "TOTAL PAYE", "NET"
            ]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

            for emp in self.employees:
                writer.writerow({
                    "NAME": emp.name,
                    "DOB": emp.dob.strftime("%d.%m.%Y") if isinstance(emp.dob, datetime) else emp.dob,
                    "GENDER": emp.gender,
                    "POST": emp.post,
                    "PENSION?": emp.pension_bool,
                    "BASIC": emp.basic,
                    "ATT": emp.att,
                    "ABSNT": emp.absnt,
                    "ABSNT_AMNT": emp.absnt_amnt,
                    "R/DAY": emp.r_day,
                    "OT": emp.ot,
                    "PENSION": emp.pension,
                    "EARNINGS": emp.earnings,
                    "GROSS": emp.gross,
                    "TAXABLE": emp.taxable,
                    "PAYE-25%": emp.paye_25,
                    "PAYE-30%": emp.paye_30,
                    "TOTAL PAYE": emp.total_paye,
                    "NET": emp.net
                })


    def load_from_csv(self):
        self.employees = []
        try:
            with open(self.filename, 'r', encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Parse DOB safely, support multiple formats
                    dob = None
                    raw_dob = row.get("DOB", "").strip()
                    if raw_dob:
                        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%m/%d/%Y", "%d.%m.%Y", "%d-%b-%y"):
                            try:
                                dob = datetime.strptime(raw_dob, fmt)
                                break
                            except ValueError:
                                continue

                    # Safe float conversion for numeric fields
                    basic = PayrollSystem.safe_float(row.get("BASIC"))
                    att = PayrollSystem.safe_float(row.get("ATT"))
                    ot = PayrollSystem.safe_float(row.get("OT"))
                    absnt = PayrollSystem.safe_float(row.get("ABSNT"))

                    # Correct pension Boolean handling
                    pension_raw = str(row.get("PENSION?", "")).strip().lower()
                    pension_bool = pension_raw in ["true", "yes", "1"]

                    emp = Employee(
                        name=row.get("NAME", "Unknown"),
                        dob=dob,
                        gender=row.get("GENDER", ""),
                        post=row.get("POST", ""),
                        basic=basic,
                        att=att,
                        ot=ot,
                        absnt=absnt,
                        pension_bool=pension_bool
                    )
                    self.employees.append(emp)
        except FileNotFoundError:
            print("CSV file not found — starting fresh.")

    def find_employee(self, name):
        for emp in self.employees:
            if emp.name == name:
                return emp
        return None
    
    def delete_employee(self, name):
        emp = self.find_employee(name)
        if emp:
            self.employees.remove(emp)
            print(f"Employee '{name}' deleted.")
        else:
            print(f"Employee '{name}' not found.")

    
    def list_employees(self):
        if not self.employees:
            print("No employees to show.")
            return
        print("\n--- EMPLOYEE LIST ---")
        for emp in self.employees:
            print(f"{emp.name} ({emp.post}) - NET: {emp.net:.2f}")
        print()

def get_company_filename():
    company = input("Enter company name: ").strip().lower().replace(" ", "_")
    if not os.path.exists("companies"):
        os.makedirs("companies")
    filename = os.path.join("companies", f"{company}.csv")
    print(f"Using payroll file: {filename}")
    return filename
    
def main():
    filename = get_company_filename()
    payroll = PayrollSystem(filename)
    payroll.load_from_csv()

    while True:
        print("\n--- PAYROLL MENU ---")
        print("1. Add Employee")
        print("2. View Employees")
        print("3. Update Employee")
        print("4. Save to CSV")
        print("5. Load from CSV")
        print("6. Switch Company")
        print("7. Delete Employee")
        print("0. Exit")
        choice = input("Enter choice: ")

        if choice == "1":
            name = input("Name: ")
            try:
                year = int(input("Enter birth year: "))
                month = int(input("Enter birth month: "))
                day = int(input("Enter birth day: "))
                date_object = datetime(year, month, day)
            except ValueError:
                print("Invalid input. Please enter numbers for employees birth year, month and day.")
                continue
            dob = date_object
            gender = input("Gender: ")
            post = input("Post: ")
            basic = float(input("Basic salary: "))
            att = int(input("Days attended: "))
            ot = float(input("Overtime: "))
            absnt = float(input("Days absent: "))
            pension_percentage = float(input("Pension percentage (as decimal): "))
            emp = Employee(name, dob, gender, post, basic, att, ot, absnt, pension_percentage)
            payroll.add_employee(emp)
            print(f"Employee '{name}' added.")

        elif choice == "2":
            payroll.list_employees()

        elif choice == "3":
            name = input("Enter employee name to update: ")
            emp = payroll.find_employee(name)
            if emp:
                print("Leave blank to keep current value.")
                new_basic = input(f"New basic (current: {emp.basic}): ")
                new_att = input(f"New attendance (current: {emp.att}): ")
                new_ot = input(f"New overtime (current: {emp.ot}): ")
                new_absnt = input(f"New absent days (current: {emp.absnt}): ")

                updates = {}
                if new_basic: updates['basic'] = float(new_basic)
                if new_att: updates['att'] = int(new_att)
                if new_ot: updates['ot'] = float(new_ot)
                if new_absnt: updates['absnt'] = float(new_absnt)

                emp.update(**updates)
                print("Employee updated.")
            else:
                print("Employee not found.")

        elif choice == "4":
            payroll.save_to_csv()

        elif choice == "5":
            payroll.load_from_csv()

        elif choice == "6":
            filename = get_company_filename()
            payroll = PayrollSystem(filename)
            payroll.load_from_csv()

        elif choice == "7":
            name = input("Enter employee name to delete: ")
            payroll.delete_employee(name)


        elif choice == "0":
            print("Exiting payroll system. Goodbye!")
            break

        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()