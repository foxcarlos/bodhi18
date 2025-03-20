# -*- coding: utf-8 -*-
# © 2020 TechAsERP
# License CC BY-NC-ND 4.0 (https://creativecommons.org/licenses/by-nc-nd/4.0/).


from odoo import fields, models

class HrPayslipWorkedDays(models.Model):
    _inherit = 'hr.payslip.worked_days'

    number_of_days_copy = fields.Float(string='Number of Days')

