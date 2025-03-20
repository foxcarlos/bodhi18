from odoo import fields, models, api


class AttendanceSettingInherited(models.TransientModel):

    _inherit = 'res.config.settings'
    over_time_shift_type = fields.Boolean(string="Extra hours by Shift Type", default=False)
    over_time_start_from = fields.Date()
    average_hours_day_shift = fields.Selection([(str(y), str(y)) for y in range(1,25)], string='Average hours for Day Shift')
    average_hours_mixed_shift = fields.Selection([(str(y), str(y)) for y in range(1,25)], string='Average hours for Mixed Shift')
    average_hours_night_shift = fields.Selection([(str(y), str(y)) for y in range(1,25)], string='Average hours for Night Shift')

    @api.model
    def get_values(self):
        res = super(AttendanceSettingInherited, self).get_values()

        params = self.env['ir.config_parameter'].sudo()
        over_time_shift_type = params.get_param(
            'bodhitree_over_time_based_shift.over_time_shift_type')
        over_time_start_from = params.get_param(
            'bodhitree_over_time_based_shift.over_time_start_from')
        average_hours_day_shift = params.get_param(
            'bodhitree_over_time_based_shift.average_hours_day_shift')
        average_hours_mixed_shift = params.get_param(
            'bodhitree_over_time_based_shift.average_hours_mixed_shift')
        average_hours_night_shift = params.get_param(
            'bodhitree_over_time_based_shift.average_hours_night_shift')

        res.update(
            over_time_shift_type=over_time_shift_type,
            over_time_start_from=over_time_start_from,
            average_hours_day_shift=average_hours_day_shift,
            average_hours_mixed_shift=average_hours_mixed_shift,
            average_hours_night_shift=average_hours_night_shift

        )
        return res

    @api.model
    def set_values(self):
        super(AttendanceSettingInherited, self).set_values()

        self.env['ir.config_parameter'].sudo().set_param(
            "bodhitree_over_time_based_shift.over_time_shift_type", self.over_time_shift_type)
        self.env['ir.config_parameter'].sudo().set_param(
            "bodhitree_over_time_based_shift.over_time_start_from", self.over_time_start_from)
        self.env['ir.config_parameter'].sudo().set_param(
            "bodhitree_over_time_based_shift.average_hours_day_shift",
            self.average_hours_day_shift)
        self.env['ir.config_parameter'].sudo().set_param(
            "bodhitree_over_time_based_shift.average_hours_mixed_shift",
            self.average_hours_mixed_shift)
        self.env['ir.config_parameter'].sudo().set_param(
            "bodhitree_over_time_based_shift.average_hours_night_shift",
            self.average_hours_night_shift)





