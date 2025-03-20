from odoo import api, fields, models


class EmployeeInherited(models.Model):
    _inherit = "hr.employee"

    default_shift_type = fields.Selection(
        [
            ("day", "Day"),
            ("mixed", "Mixed"),
            ("night", "Night"),
            ("categ_one", "Especial 1"),
            ("categ_two", "Especial 2"),
        ],
        required=True,
    )


class EmployeeInheritedPublic(models.Model):
    _inherit = "hr.employee.public"

    default_shift_type = fields.Selection(
        [
            ("day", "Day"),
            ("mixed", "Mixed"),
            ("night", "Night"),
            ("categ_one", "Especial 1"),
            ("categ_two", "Especial 2"),
        ],
        required=True,
    )
