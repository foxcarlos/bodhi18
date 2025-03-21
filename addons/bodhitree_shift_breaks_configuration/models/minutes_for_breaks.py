from odoo import fields, models, api


class PlanningSlotInherited(models.Model):

    _inherit = "planning.slot"
    minutes_for_breaks = fields.Integer(string="Minutes For Breaks")

    @api.onchange("template_id")
    def _onchange_template_id(self):
        self.minutes_for_breaks = self.template_id.break_minutes

    @api.depends(
        "start_datetime",
        "end_datetime",
        "resource_id.calendar_id",
        "company_id.resource_calendar_id",
        "allocated_percentage",
        "minutes_for_breaks",
    )
    def _compute_allocated_hours(self):
        super(PlanningSlotInherited, self)._compute_allocated_hours()
        for slot in self:
            slot.allocated_hours = slot.allocated_hours - (slot.minutes_for_breaks / 60)
