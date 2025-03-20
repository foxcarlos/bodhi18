# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import pytz
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, exceptions, _
from odoo.tools import float_round

class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    attendance_break_state = fields.Selection(related='employee_id.attendance_break_state', readonly=True,
        groups="hr_attendance.group_hr_attendance_kiosk,hr_attendance.group_hr_attendance")

    last_attendance_break_id = fields.Many2one(related='employee_id.last_attendance_break_id', readonly=True,
                                         groups="hr_attendance.group_hr_attendance_kiosk,hr_attendance.group_hr_attendance")


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    attendance_break_state = fields.Selection(
        string="Attendance Break Status", compute='_compute_attendance_state',
        selection=[('break_out', "Break out"), ('break_in', "Break in")], store=True,
        groups="hr_attendance.group_hr_attendance_kiosk,hr_attendance.group_hr_attendance")

    last_attendance_break_id = fields.Many2one(
        'hr.attendance', compute='_compute_last_attendance_id', store=True,
        groups="hr_attendance.group_hr_attendance_kiosk,hr_attendance.group_hr_attendance")



    @api.depends('attendance_ids')
    def _compute_last_attendance_id(self):
        for employee in self:
            employee.last_attendance_id = self.env['hr.attendance'].search([
                ('employee_id', '=', employee.id), ('type', '=', 'normal')
            ], limit=1)
            employee.last_attendance_break_id = self.env['hr.attendance'].search([
                ('employee_id', '=', employee.id), ('type', '=', 'break')
            ], limit=1)


    @api.depends('last_attendance_id.check_in', 'last_attendance_id.check_out',
                 'last_attendance_break_id.check_in', 'last_attendance_break_id.check_out',
                 'last_attendance_id')
    def _compute_attendance_state(self):
        for employee in self:
            att = employee.last_attendance_id.sudo()
            employee.attendance_state = att and not att.check_out and 'checked_in' or 'checked_out'

            att = employee.last_attendance_break_id.sudo()
            employee.attendance_break_state = att and not att.check_out and 'break_in' or 'break_out'

    def _attendance_action_change(self):
        """ Check In/Check Out action
            Check In: create a new attendance record
            Check Out: modify check_out field of appropriate attendance record
        """
        self.ensure_one()
        action_date = fields.Datetime.now()

        if self.attendance_state != 'checked_in':
            vals = {
                'employee_id': self.id,
                'check_in': action_date,
                'type': 'normal',
            }
            return self.env['hr.attendance'].create(vals)
        attendance = self.env['hr.attendance'].search([('employee_id', '=', self.id), ('type', '=', 'normal'), ('check_out', '=', False)], limit=1)
        if attendance:
            attendance.check_out = action_date
        else:
            raise exceptions.UserError(_('Cannot perform check out on %(empl_name)s, could not find corresponding check in. '
                'Your attendances have probably been modified manually by human resources.') % {'empl_name': self.sudo().name, })
        return attendance

    def _attendance_break_action_change(self):
        self.ensure_one()
        action_date = fields.Datetime.now()

        if self.attendance_break_state != 'break_in':
            vals = {
                'employee_id': self.id,
                'check_in': action_date,
                'type': 'break',
            }
            return self.env['hr.attendance'].create(vals)
        attendance = self.env['hr.attendance'].search([('employee_id', '=', self.id), ('type', '=', 'break'), ('check_out', '=', False)], limit=1)
        if attendance:
            attendance.check_out = action_date
        else:
            raise exceptions.UserError(_('Cannot perform break out on %(empl_name)s, could not find corresponding break in. '
                'Your attendances have probably been modified manually by human resources.') % {'empl_name': self.sudo().name, })
        return attendance

    def attendance_break_manual(self, next_action, entered_pin=None):
        self.ensure_one()
        attendance_user_and_no_pin = self.user_has_groups(
            'hr_attendance.group_hr_attendance_user,'
            '!hr_attendance.group_hr_attendance_use_pin')
        can_check_without_pin = attendance_user_and_no_pin or (self.user_id == self.env.user and entered_pin is None)
        if can_check_without_pin or entered_pin is not None and entered_pin == self.sudo().pin:
            return self._attendance_break_action(next_action)
        return {'warning': _('Wrong PIN')}

    def _attendance_break_action(self, next_action):
        self.ensure_one()
        employee = self.sudo()
        action_message = self.env["ir.actions.actions"]._for_xml_id("hr_attendance.hr_attendance_action_greeting_message")
        action_message['previous_attendance_change_date'] = employee.last_attendance_break_id and (employee.last_attendance_break_id.check_out or employee.last_attendance_break_id.check_in) or False
        action_message['employee_name'] = employee.name
        action_message['barcode'] = employee.barcode
        action_message['next_action'] = next_action
        action_message['hours_today'] = employee.hours_today

        if employee.user_id:
            modified_attendance = employee.with_user(employee.user_id)._attendance_break_action_change()
        else:
            modified_attendance = employee._attendance_break_action_change()
        action_message['attendance'] = modified_attendance.read()[0]
        action_message['total_overtime'] = employee.total_overtime
        return {'action': action_message}

    @api.model
    def attendance_break_scan(self, barcode,type='normal'):
        """ Receive a barcode scanned from the Kiosk Mode and change the attendances of corresponding employee.
            Returns either an action or a warning.
        """
        employee = self.sudo().search([('barcode', '=', barcode)], limit=1)
        if employee:
            if type=='normal':
                return employee._attendance_action('hr_attendance.hr_attendance_action_kiosk_mode')
            else:
                return employee._attendance_break_action('hr_attendance.hr_attendance_action_kiosk_mode')
        return {'warning': _("No employee corresponding to Badge ID '%(barcode)s.'") % {'barcode': barcode}}

class User(models.Model):
    _inherit = ['res.users']

    attendance_break_state = fields.Selection(related='employee_id.attendance_break_state')

    last_attendance_break_id = fields.Many2one(related='employee_id.last_attendance_break_id')