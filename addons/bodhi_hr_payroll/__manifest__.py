{
    "name": "Bodhi HR Payroll, Planning, Attendance, Employees",
    "summary": """Bodhi-Tree Customisation for the modules, Payroll, Planning, Attendance, Employees, etc.""",
    "author": "Nativo, Carlos Alberto Garcia Diaz, Odoo Community Association (OCA)",
    "website": "",
    "category": "Human Resources/Employees",
    "version": "18.0.0.0",
    "depends": [
        "base",
        "hr",
        "planning",
        "hr_attendance",
    ],
    "data": [
        # "security/ir.model.access.csv",
        "views/hr_employee_views.xml",
    ],
    "application": False,
    "installable": True,
    "development_status": "Alpha",
    "images": ["static/description/icon.png"],
    "maintainers": ["foxcarlos@gmail.com"],
    "external_dependencies": {
        # "python": ["paramiko"],
    },
    # "post_init_hook": "_account_post_init",
    "license": "LGPL-3",
}


