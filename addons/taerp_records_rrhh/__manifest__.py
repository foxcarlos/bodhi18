# -*- coding: utf-8 -*-
# © 2018 TechAsERP
# License CC BY-NC-ND 4.0 (https://creativecommons.org/licenses/by-nc-nd/4.0/).

{
    "name": "TechAsERP RH",
    "summary": "Allow load RH production to payroll",
    "version": "18.0.1.0",
    "category": "TAERP",
    "author": "TechAsERP",
    "license": "Other proprietary",
    "website": "https://techaserp.tech",
    "sequence": 10,
    "application": True,
    "installable": True,
    "auto_install": False,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "base",
        "hr_payroll",
        "hr_attendance"
    ],
    "data": [
        "security/hr_attendance_groups.xml",
        "views/work_entrys.xml",
        "views/hr_payslip.xml",
        "views/incomplate_attendence.xml",
        "views/over_time.xml",
        "data/hr.work.entry.type.csv",
        # "report/hr_attendance_report_views.xml",
        "security/ir.model.access.csv",
        "views/planning_slot.xml",
        "views/hr_payslip_lines_edit.xml",
        "views/attendance.xml",
    ],
    "assets": {
        "web.assets_qweb": [
            "taerp_records_rrhh/static/src/xml/**/*",
        ],
    },
}
