

from database import db
from models import employee_doc, activity_log_doc

# 1️⃣ Insert a new employee
new_emp = employee_doc("Alex", "alex@example.com", "Designer")
emp_result = db.employees.insert_one(new_emp)
print(f"✅ Added Employee: {new_emp['name']} (ID: {emp_result.inserted_id})")

# 2️⃣ Add an activity log
log = activity_log_doc(str(emp_result.inserted_id), "Logged in")
db.activity_logs.insert_one(log)

# 3️⃣ Fetch and display all employees
employees = db.employees.find()
print("\n👥 All Employees:")
for emp in employees:
    print(emp.get('_id'), emp.get('name'), emp.get('email'), emp.get('role'))
