{
    "name": "Shift Breaks Configuration",
    "version": "18.0.1.0.0",
    "summary": """This module is helps to find breaks time during the shift""",
    "description": """This module is helps to find breaks time during the shift""",
    "depends": ["planning", "hr_attendance"],
    "sequence": -550,
    "category": "Tools",
    "data": ["views/break_minutes.xml", "views/minutes_for_breaks.xml"],
    "installable": True,
    "auto_install": False,
    "application": True,
}
