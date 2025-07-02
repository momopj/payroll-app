import csv
import os
from turtle import pen

class Employee:
    def __init__(self, name, post, basic, att, ot, pension_percentage):
        self.name = name
        self.post = post
        self.basic = basic
        self.att = att
        self.ot = ot
        self.pension_percentage = pension_percentage
        self.calculate_payroll()

    def calculate_payroll(self):
        self.r_day = round(self.basic / 26, 2)
        self.earnings = self.att * self.r_day
        self.pension = self.pension_percentage * self.basic
        self.gross = self.earnings + self.ot
        self.taxable = self.gross - 150000

        if self.taxable <= 0:
            self.paye_25 = 0
            self.paye_30 = 0
            self.taxable = 0
        else:
            if self.taxable <= 300000:
                self.paye_25 = round(self.taxable * 0.25, 2)
                self.paye_30 = 0
            else:
                self.paye_25 = round(300000 * 0.25, 2)
                self.paye_30 = round((self.taxable - 300000) * 0.30, 2)
            
        self.total_paye = round(self.paye_25 + self.paye_30, 2)
        self.net = round(self.gross - self.total_paye, 2)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.calculate_payroll()

    def to_dict(self):
        return {
            'NAME': self.name,
            'POST': self.post,
            'BASIC': self.basic,
            'ATT': self.att,
            'R/DAY': self.r_day,
            'OT': self.ot,
            'EARNINGS': self.earnings,
            'GROSS': self.gross,
            'PENSION_%': self.pension_percentage,
            'PENSION': self.pension,
            'TAXABLE': self.taxable,
            'PAYE-25%': self.paye_25,
            'PAYE-30%': self.paye_30,
            'TOTAL PAYE': self.total_paye,
            'NET': self.net
        }


class PayrollSystem:
    def __init__(self, filename='payroll.csv'):
        self.filename = filename
        self.employees = []

    def add_employee(self, emp):
        self.employees.append(emp)

    def save_to_csv(self):
        if not self.employees:
            print("No employees to save.")
            return

        with open(self.filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.employees[0].to_dict().keys())
            writer.writeheader()
            for emp in self.employees:
                writer.writerow(emp.to_dict())

    def load_from_csv(self):
        self.employees = []
        try:
            with open(self.filename, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    emp = Employee(
                        name=row['NAME'],
                        post=row['POST'],
                        basic=float(row['BASIC']),
                        att=float(row['ATT']),
                        ot=float(row['OT']),
                        pension_percentage=float(row.get('PENSION_%', 0))
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
            post = input("Post: ")
            basic = float(input("Basic salary: "))
            att = int(input("Days attended: "))
            ot = float(input("Overtime: "))
            pension_percentage = float(input("Pension percentage (as decimal): "))
            emp = Employee(name, post, basic, att, ot, pension_percentage)
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

                updates = {}
                if new_basic: updates['basic'] = float(new_basic)
                if new_att: updates['att'] = int(new_att)
                if new_ot: updates['ot'] = float(new_ot)

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