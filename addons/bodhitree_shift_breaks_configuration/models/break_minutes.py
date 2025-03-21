from odoo import fields, models, api, _
from odoo.exceptions import UserError


class PlanningSlotTemplateInherited(models.Model):

    _inherit = "planning.slot.template"

    break_minutes = fields.Integer(string="Breaks(minutes)", default=0)
    duration = fields.Float("Duration (hours)")
    # Durration in hours no existe en la version 18

    @api.depends("duration")
    def _compute_end_break_minute(self):
        self.end_break_minute = False
        if self.duration:
            self.end_break_minute = 60.0 * self.duration

    @api.constrains("break_minutes")
    def _check_break_minutes(self):
        if self.break_minutes < 0 or self.break_minutes > 60 * self.duration:
            raise UserError(
                _(
                    'Please enter "Break (minutes)" between 0 and %d.'
                    % (60 * self.duration)
                )
            )
