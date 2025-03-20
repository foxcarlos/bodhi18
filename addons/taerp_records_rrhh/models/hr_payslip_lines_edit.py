from odoo import api, fields, models, _
from odoo.exceptions import UserError
# from odoo.addons.hr_payroll.models.browsable_object import (
#     BrowsableObject,
#     InputLine,
#     WorkedDays,
#     Payslips,
# )


class HrPayrollEditPayslipWorkedDaysLine(models.TransientModel):
    _inherit = "hr.payroll.edit.payslip.worked.days.line"

    number_of_days_copy = fields.Float(string="Number of Days")

    def _export_to_worked_days_line(self):
        return [
            {
                "name": line.name,
                "sequence": line.sequence,
                "code": line.code,
                "work_entry_type_id": line.work_entry_type_id.id,
                "number_of_days": line.number_of_days,
                "number_of_days_copy": line.number_of_days,
                "number_of_hours": line.number_of_hours,
                "amount": line.amount,
                "payslip_id": line.slip_id.id,
            }
            for line in self
        ]
