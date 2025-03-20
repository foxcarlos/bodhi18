# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import datetime

from odoo import models,fields, api


class ResourceCalendarLeaves(models.Model):
    _inherit = "resource.calendar.leaves"

    @api.onchange('date_from')
    def onchange_compute_date(self):
        for item in self:
            item.date = item.date_from.date()

    @api.depends('date_from')
    def _compute_date(self):
        for item in self:
            item.date = item.date_from.date()

    date = fields.Date('Start Date', required=True,store=True,
                            compute="_compute_date")

    @api.model
    def create(self, vals):
        if 'date_from' in vals.keys():
            date = datetime.datetime.strptime(str(vals['date_from']), "%Y-%m-%d %H:%M:%S")
        vals.update({'date':date.date().strftime("%Y-%m-%d")})
        res = super(ResourceCalendarLeaves,self).create(vals)
        return res
