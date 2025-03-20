from datetime import datetime

from odoo import fields, models, api, _, exceptions


class PlanningSlotInherited(models.Model):
    _inherit = "planning.slot"

    shift_type = fields.Selection(
        [
            ("day", "Day"),
            ("mixed", "Mixed"),
            ("night", "Night"),
            ("categ_one", "Especial 1"),
            ("categ_two", "Especial 2"),
        ],
        required=True,
    )
    is_holiday = fields.Boolean("Is Compulsory Holiday", default=False, copy=False)
    is_free = fields.Boolean("Is Free", default=False, copy=True)
    is_no_compuholiday = fields.Boolean(
        "Is No-Compulsory Holiday", default=False, copy=False
    )

    # @api.onchange("shift_type")
    # def onchange_shift_type(self):
    #     start_datetiem = datetime.strptime(str(self.start_datetime.date()), "%Y-%m-%d")
    #     end_datetime = datetime.strptime(
    #         str(self.start_datetime.date()) + " 23:59:59", "%Y-%m-%d %H:%M:%S"
    #     )
    #     slot = self.env["planning.slot"].search(
    #         [
    #             ("resource_id", "=", self.resource_id.id),
    #             ("start_datetime", ">=", start_datetiem),
    #             ("end_datetime", "<=", end_datetime),
    #             ("id", "not in", self.ids),
    #         ]
    #     )
    #     for rec in slot:
    #         if rec.shift_type:
    #             if rec.shift_type != self.shift_type:
    #                 raise exceptions.UserError(
    #                     _(
    #                         "The resource is in %s shift for the time period %s to %s"
    #                         % (rec.shift_type, rec.start_datetime, rec.end_datetime)
    #                     )
    #                 )
    #
    # @api.onchange("employee_id")
    # def onchange_employee(self):
    #     for slot in self:
    #         if slot.employee_id.default_shift_type:
    #             slot.shift_type = slot.employee_id.default_shift_type
