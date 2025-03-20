# -*- coding: utf-8 -*-
# © 2020 TechAsERP
# License CC BY-NC-ND 4.0 (https://creativecommons.org/licenses/by-nc-nd/4.0/).
import datetime

import pytz


from odoo import models, fields, api, exceptions, _
from odoo.tools import format_datetime

class Attendance(models.Model):
    _inherit = "hr.attendance"

    type = fields.Selection(selection=[
        ('normal', 'Working Time'),
        ('break', 'Break'),
    ], string='Type', required=True, store=True,
        default="normal", change_default=True)

    check_in = fields.Datetime(string="Check In", default=fields.Datetime.now, required=False)
    planing_check_in = fields.Datetime(string="Check In", default=fields.Datetime.now, required=False)

    outside = fields.Boolean(string='Outside', default=False, copy=False)

    expected_check_in = fields.Datetime(string="Check In", default=fields.Datetime.now, required=False)
    time_diff_check_in = fields.Float("Free Extra Hours", readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        res = super(Attendance,self).create(vals_list)
        res._update_overtime()
        res.update_realdate_break()
        res.calculate_time_diference()
        return res

    def calculate_time_diference(self):
        for record in self:
            if record.type=='normal':

                local = pytz.utc.localize(record.check_in,
                                          is_dst=None).astimezone(pytz.timezone(self.env.user.tz))

                date_allowed=local.date()
                date_top=datetime.datetime.combine(date_allowed, datetime.time(23,59,59))
                date_top=pytz.timezone(self.env.user.tz).localize(date_top,
                                                         is_dst=None).astimezone(pytz.utc)
                date_floor= datetime.datetime.combine(date_allowed, datetime.time(0, 0, 0))
                date_floor=pytz.timezone(self.env.user.tz).localize(date_floor,
                                                         is_dst=None).astimezone(pytz.utc)
                last_attendance_before_check_in = self.env['hr.attendance'].search([
                    ('employee_id', '=', record.employee_id.id),
                    ('check_in', '<=', date_top),
                    ('check_in', '>=', date_floor),
                    ('type', '=', 'normal'),
                    ('id', '!=', record.id),
                ], order='check_in desc', limit=1)
                if not last_attendance_before_check_in:
                    planing_slots = self.env['planning.slot'].search([
                        ('resource_id', '=', record.employee_id.resource_id.id),
                        ('start_datetime', '<=',date_top ),
                        ('start_datetime', '>=', date_floor),
                        ('state', '=', 'published'),
                    ], order='start_datetime ASC', limit=1)
                    if planing_slots:
                        if planing_slots.start_datetime:
                            if record.check_in:
                                time_delta= planing_slots.start_datetime-record.check_in
                                record.time_diff_check_in=time_delta.total_seconds() / 60
                            else:
                                record.time_diff_check_in =0
                        else:
                            record.time_diff_check_in =0
                    else:
                        record.time_diff_check_in =0

    def update_realdate_break(self):
        for record in self:
            if record.type=='break':
                last_attendance_before_check_in = self.env['hr.attendance'].search([
                    ('employee_id', '=', record.employee_id.id),
                    ('check_in', '<=', record.check_in),
                    ('type', '=', 'normal'),
                    ('id', '!=', record.id),
                ], order='check_in desc', limit=1)
                time_difference = record.check_in - last_attendance_before_check_in.check_in
                total_hours = time_difference.total_seconds() / 3600
                if total_hours < 24:
                    record.planing_check_in=last_attendance_before_check_in.check_in
                else:
                    record.planing_check_in =record.check_in

    @api.constrains('check_in', 'check_out', 'employee_id','type')
    def _check_validity(self):
        """ Verifies the validity of the attendance record compared to the others from the same employee.
            For the same employee we must have :
                * maximum 1 "open" attendance record (without check_out)
                * no overlapping time slices with previous employee records
        """
        for attendance in self:


            if not attendance.outside:
                # we take the latest attendance before our check_in time and check it doesn't overlap with ours
                last_attendance_before_check_in = self.env['hr.attendance'].search([
                    ('employee_id', '=', attendance.employee_id.id),
                    ('check_in', '<=', attendance.check_in),
                    ('type', '=', attendance.type),
                    ('id', '!=', attendance.id),
                ], order='check_in desc', limit=1)

                if last_attendance_before_check_in and last_attendance_before_check_in.check_out and last_attendance_before_check_in.check_out > attendance.check_in:
                    raise exceptions.ValidationError(
                        _("Cannot create new attendance record for %(empl_name)s, the employee was already checked in on %(datetime)s") % {
                            'empl_name': attendance.employee_id.name,
                            'datetime': format_datetime(self.env, attendance.check_in, dt_format=False),
                        })

                if not attendance.check_out:
                    # if our attendance is "open" (no check_out), we verify there is no other "open" attendance
                    no_check_out_attendances = self.env['hr.attendance'].search([
                        ('employee_id', '=', attendance.employee_id.id),
                        ('check_out', '=', False),
                        ('type', '=', attendance.type),
                        ('id', '!=', attendance.id),
                        ('check_in', '=', attendance.check_in),
                    ], order='check_in desc', limit=1)
                    if no_check_out_attendances:
                        raise exceptions.ValidationError(
                            _("Cannot create new attendance record for %(empl_name)s, the employee hasn't checked out since %(datetime)s") % {
                                'empl_name': attendance.employee_id.name,
                                'datetime': format_datetime(self.env, no_check_out_attendances.check_in, dt_format=False),
                            })
                else:
                    # we verify that the latest attendance with check_in time before our check_out time
                    # is the same as the one before our check_in time computed before, otherwise it overlaps
                    last_attendance_before_check_out = self.env['hr.attendance'].search([
                        ('employee_id', '=', attendance.employee_id.id),
                        ('check_in', '<', attendance.check_out),
                        ('type', '=', attendance.type),
                        ('id', '!=', attendance.id),
                    ], order='check_in desc', limit=1)

                    if last_attendance_before_check_out and last_attendance_before_check_in != last_attendance_before_check_out:
                        raise exceptions.ValidationError(
                            _("Cannot create new attendance record for %(empl_name)s, the employee was already checked in on %(datetime)s") % {
                                'empl_name': attendance.employee_id.name,
                                'datetime': format_datetime(self.env, last_attendance_before_check_out.check_in,
                                                            dt_format=False),
                            })

    @api.model
    def create_atendence(self, dict):
        if isinstance(dict['User ID'],str) == True:
            dict['User ID']=int(dict['User ID'])
        employee = self.env['hr.employee'].search([('barcode', '=', dict['User ID'])])
        datetime_var = datetime.datetime.strptime(dict['Verify Date'],'%Y-%m-%d %H:%M:%S')
        local = pytz.timezone(self.env.user.tz)
        local_dt = local.localize(datetime.datetime.fromordinal(datetime_var.toordinal()), is_dst=None)
        utc_dt = local_dt.astimezone(pytz.utc)
        entry=datetime.datetime.fromordinal(datetime_var.toordinal()) + datetime.timedelta(hours=(datetime_var.hour+utc_dt.hour),minutes=(datetime_var.minute),seconds=(datetime_var.second))
        if employee:
            if dict['Verify State'] in (0,3,4):
                attendance = self.env['hr.attendance'].search([('check_in', '=', entry),
                                                               ('type', '=',
                                                                'break' if dict['Verify State'] in (3, 4) else 'normal')
                                                                  , ('employee_id', '=', employee.id)],
                                                              order='check_in desc', limit=1)
                if not attendance:
                    attendance = self.env['hr.attendance'].create(
                        {
                            'employee_id': employee.id,
                            'check_in': entry,
                            'outside': True,
                            'type': 'break' if dict['Verify State'] in (3, 4) else 'normal'
                        }
                    )
            else:
                attendance = self.env['hr.attendance'].search([('check_in', '<', entry),
                                                               ('type', '=',
                                                                'break' if dict['Verify State'] in (2, 5) else 'normal')
                                                                  , ('employee_id', '=', employee.id)],
                                                              order='check_in desc', limit=1)
                if not attendance.check_out==entry:
                    attendance = attendance.write(
                        {
                            'check_out': entry,
                            'outside': True,
                            'type':'break' if dict['Verify State'] in (2, 5) else 'normal'
                        }
                    )
        return True