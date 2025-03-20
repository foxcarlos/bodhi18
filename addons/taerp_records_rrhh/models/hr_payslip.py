# -*- coding: utf-8 -*-
# © 2020 TechAsERP
# License CC BY-NC-ND 4.0 (https://creativecommons.org/licenses/by-nc-nd/4.0/).
import babel
from collections import defaultdict
from datetime import date, datetime, time
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from numpy import floor
from pytz import timezone
from pytz import utc

from odoo import api, fields, models, tools, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_utils

class Payslip(models.Model):
    _inherit = "hr.payslip"

    day_register = fields.Float("Number of Marks", readonly=False)

    def _get_worked_day_lines_values(self, domain=None):
        self.ensure_one()
        res = []
        hours_per_day = self._get_worked_day_lines_hours_per_day()
        work_hours = self.contract_id._get_work_hours(self.date_from, self.date_to, domain=domain)
        work_hours_ordered = sorted(work_hours.items(), key=lambda x: x[1])
        biggest_work = work_hours_ordered[-1][0] if work_hours_ordered else 0
        add_days_rounding = 0
        for work_entry_type_id, hours in work_hours_ordered:
            work_entry_type = self.env['hr.work.entry.type'].browse(work_entry_type_id)
            if not ((work_entry_type.code == 'WORK100') or (work_entry_type.code == 'WORK50')
                    or (work_entry_type.code == 'WORK300') or (work_entry_type.code == 'LEAVE110')
            or (work_entry_type.code == 'LEAVE130')
            or (work_entry_type.code == 'LEAVE140') or (work_entry_type.code == 'LEAVE150')
                    or (work_entry_type.code == 'LEAVE160')):
                days = round(hours / hours_per_day, 5) if hours_per_day else 0
                if work_entry_type_id == biggest_work:
                    days += add_days_rounding
                day_rounded = self._round_days(work_entry_type, days)
                add_days_rounding += (days - day_rounded)
                attendance_line = {
                    'sequence': work_entry_type.sequence,
                    'work_entry_type_id': work_entry_type_id,
                    'number_of_days': day_rounded,
                    'number_of_days_copy':day_rounded,
                    'number_of_hours': hours,
                }
                res.append(attendance_line)

        # compute leave days
        day_from = datetime.combine(fields.Date.from_string(self.date_from), time.min)
        day_to = datetime.combine(fields.Date.from_string(self.date_to), time.max)
        leaves = {}
        calendar = self.contract_id.resource_calendar_id
        tz = timezone(calendar.tz)


        attendance = self.env['bodhi.attendance.report'].search(
            [('check_in', '>=', self.date_from), ('check_in', '<=', self.date_to,),
             ('employee_id', '=', self.contract_id.employee_id.id)], order='check_in DESC')

        hours = 0
        day = 0
        extra_hours = 0
        extra_days = 0
        incomplete_days = 0
        incomplete_count = 0
        incomplete_hours = 0
        count_days_registers=0
        no_compulsory_holiday=0
        freeday=0
        compulsory_holiday=0
        extra_hours_holiday = 0
        extra_hours_holiday_no = 0
        extra_hours_free = 0

        values = set(map(lambda x: x.check_in.strftime('%j'), attendance))
        newlist = [[y for y in attendance if y.check_in.strftime('%j') == x] for x in values]
        for item in newlist:
            count_days_registers += 1
            for days in item:
                hours += days.worked_hours_rounded
                day+=days.worked_days
                extra_hours += days.overtime_hours
                incomplete_days += days.incomplete_days
                incomplete_count+=  days.incomplete_count
                incomplete_hours += days.incomplete_hours
                no_compulsory_holiday += days.no_compuholiday
                freeday += days.free_time
                compulsory_holiday += days.holiday
                extra_hours_holiday += days.holiday_overtime_hours
                extra_hours_holiday_no += days.holiday_no_overtime_hours
                extra_hours_free += days.free_overtime_hours

            day = round(day, 2)
            extra_hours = round(extra_hours, 2)
            hours = round(hours, 2)
            incomplete_days = round(incomplete_days, 2)
            incomplete_count = round(incomplete_count,2)
            incomplete_hours = round(incomplete_hours, 2)
            no_compulsory_holiday = round(no_compulsory_holiday, 2)
            extra_hours_holiday = round(extra_hours_holiday, 2)
            freeday = round(freeday, 2)
            extra_hours_free=round(extra_hours_free,2)
            compulsory_holiday = round(compulsory_holiday, 2)
            extra_days =0

        self.day_register = count_days_registers

        fix_horas, fix_extras = self.contract_id.employee_id.get_overtime(self.contract_id.employee_id.id, self.date_from, self.date_to)

        work_entry_type = self.env['hr.work.entry.type'].search([('code', '=', 'WORK105')])
        fix_attendance_line = {
            'sequence': work_entry_type.sequence,
            'work_entry_type_id': work_entry_type.id,
            'number_of_days': round(fix_horas / 8, 2),
            'number_of_days_copy': round(fix_horas / 8, 2),
            'number_of_hours': round(fix_horas, 2),
        }

        work_entry_type = self.env['hr.work.entry.type'].search([('code', '=', 'WORK165')])
        fix_extra_line = {
            'sequence': work_entry_type.sequence,
            'work_entry_type_id': work_entry_type.id,
            'number_of_days': round(fix_extras / 8, 2),
            'number_of_days_copy': round(fix_extras / 8, 2),
            'number_of_hours': round(fix_extras, 2),
        }

        work_entry_type = self.env['hr.work.entry.type'].search([('code', '=', 'WORK100')])
        attendance_line = {
            'sequence': work_entry_type.sequence,
            'work_entry_type_id': work_entry_type.id,
            'number_of_days': round(day,2),
            'number_of_days_copy':round(day,2),
            'number_of_hours': round(hours,2),
        }
        work_entry_type = self.env['hr.work.entry.type'].search([('code', '=', 'WORK300')])
        extra = {
            'name': "Horas Extras",
            'sequence': work_entry_type.sequence,
            'work_entry_type_id': work_entry_type.id,
            'number_of_days': round(extra_days,2),
            'number_of_days_copy': round(extra_days, 2),
            'number_of_hours': round(extra_hours,2),
        }
        work_entry_type = self.env['hr.work.entry.type'].search([('code', '=', 'WORK50')])
        incomplete = {
            'name': _("Días incompletos"),
            'sequence': work_entry_type.sequence,
            'work_entry_type_id': work_entry_type.id,
            'number_of_days': round(incomplete_count, 2),
            'number_of_days_copy': round(incomplete_days, 2),
            'number_of_hours': round(incomplete_hours, 2),
        }
        work_entry_type = self.env['hr.work.entry.type'].search([('code', '=', 'LEAVE130')])
        compulsory_holiday_line = {
            'name': _("Compulsory Holiday"),
            'sequence': work_entry_type.sequence,
            'work_entry_type_id': work_entry_type.id,
            'number_of_days': round(compulsory_holiday/8, 2),
            'number_of_days_copy': round(compulsory_holiday / 8, 2),
            'number_of_hours': round(compulsory_holiday, 2),
        }
        work_entry_type = self.env['hr.work.entry.type'].search([('code', '=', 'LEAVE140')])
        no_compulsory_holiday_line = {
            'name': _("Non-Compulsory Holiday"),
            'sequence': work_entry_type.sequence,
            'work_entry_type_id': work_entry_type.id,
            'number_of_days': round(no_compulsory_holiday/8, 2),
            'number_of_days_copy': round(no_compulsory_holiday / 8, 2),
            'number_of_hours': round(no_compulsory_holiday, 2),
        }

        work_entry_type = self.env['hr.work.entry.type'].search([('code', '=', 'LEAVE160')])
        freeday_worked_line = {
            'name': _("Time Off Worked"),
            'sequence': work_entry_type.sequence,
            'work_entry_type_id': work_entry_type.id,
            'number_of_days': round(freeday / 8, 2),
            'number_of_days_copy': round(freeday / 8, 2),
            'number_of_hours': round(freeday, 2),
        }

        work_entry_type = self.env['hr.work.entry.type'].search([('code', '=', 'WORK350')])
        extra_holiday = {
            'name': _("Holiday Extra Hours"),
            'sequence': work_entry_type.sequence,
            'work_entry_type_id': work_entry_type.id,
            'number_of_days': round(extra_hours_holiday / 8, 2),
            'number_of_days_copy': round(extra_hours_holiday / 8, 2),
            'number_of_hours': round(extra_hours_holiday, 2),
        }
        work_entry_type = self.env['hr.work.entry.type'].search([('code', '=', 'WORK325')])
        extra_holiday_no = {
            'name': _("Holiday Extra Hours"),
            'sequence': work_entry_type.sequence,
            'work_entry_type_id': work_entry_type.id,
            'number_of_days': round(extra_hours_holiday_no / 8, 2),
            'number_of_days_copy': round(extra_hours_holiday_no / 8, 2),
            'number_of_hours': round(extra_hours_holiday_no, 2),
        }

        planing_slot = self.env['planning.slot'].search([('resource_id', '=', self.contract_id.employee_id.resource_id.id),
                                                         ('start_datetime', '>=', day_from), ('start_datetime', '<=', day_to),
                                                         ('is_free', '=', True)])
        amount_free_d=0
        for slot in planing_slot  :
            amount_free_d+=(((slot.end_datetime-slot.start_datetime).seconds+60)/3600)//24
        amount_free_h=(amount_free_d-(freeday//8))*8
        amount_free_h=round(amount_free_h,2)

        work_entry_type = self.env['hr.work.entry.type'].search([('code', '=', 'LEAVE150')])
        freeday_line = {
            'name': _("Time Off"),
            'sequence': work_entry_type.sequence,
            'work_entry_type_id': work_entry_type.id,
            'number_of_days': round(amount_free_h / 8, 2),
            'number_of_days_copy': round(amount_free_h / 8, 2),
            'number_of_hours': round(amount_free_h, 2),
        }

        work_entry_type = self.env['hr.work.entry.type'].search([('code', '=', 'LEAVE155')])
        freeday_extra_line = {
            'name': _("Holiday Extra Hours"),
            'sequence': work_entry_type.sequence,
            'work_entry_type_id': work_entry_type.id,
            'number_of_days': round(extra_hours_free / 8, 2),
            'number_of_days_copy': round(extra_hours_free / 8, 2),
            'number_of_hours': round(extra_hours_free, 2),
        }

        res.append(freeday_extra_line)
        res.append(extra_holiday)
        res.append(extra_holiday_no)
        res.append(attendance_line)
        res.extend(leaves.values())
        res.append(extra)
        res.append(incomplete)
        res.append(no_compulsory_holiday_line)
        res.append(freeday_worked_line)
        res.append(freeday_line)
        res.append(compulsory_holiday_line)
        res.append(fix_attendance_line)
        res.append(fix_extra_line)

        return res

    @api.model
    def get_worked_day_lines(self, contracts, date_from, date_to):
        res = []
        # fill only if the contract as a working schedule linked
        for contract in contracts.filtered(lambda contract: contract.resource_calendar_id):
            day_from = datetime.combine(fields.Date.from_string(date_from), time.min)
            day_to = datetime.combine(fields.Date.from_string(date_to), time.max)

            # compute leave days
            leaves = {}
            calendar = contract.resource_calendar_id
            tz = timezone(calendar.tz)
            day_leave_intervals = contract.employee_id.list_leaves(day_from, day_to,
                                                                   calendar=contract.resource_calendar_id)
            for day, hours, leave in day_leave_intervals:
                holiday = leave.holiday_id
                current_leave_struct = leaves.setdefault(holiday.holiday_status_id, {
                    'name': holiday.holiday_status_id.name or _('Global Leaves'),
                    'sequence': 5,
                    'code': holiday.holiday_status_id.code or 'GLOBAL',
                    'number_of_days': 0.0,
                    'number_of_hours': 0.0,
                    'contract_id': contract.id,
                })
                current_leave_struct['number_of_hours'] += hours
                work_hours = calendar.get_work_hours_count(
                    tz.localize(datetime.combine(day, time.min)),
                    tz.localize(datetime.combine(day, time.max)),
                    compute_leaves=False,
                )
                if work_hours:
                    current_leave_struct['number_of_days'] += hours / 8

            # compute worked days
            attendance = self.env['hr.attendance'].search([('check_in', '>=', day_from), ('check_out', '<=', day_to)
                                                              , ('employee_id', '=', contract.employee_id.id)])
            hours=0
            day=0
            for item in attendance:
                hours+=item.worked_hours
                day+=floor(item.worked_hours/8)

            attendances = {
                'name': _("Tiempo laborado"),
                'sequence': 1,
                'code': 'WORK100',
                'number_of_days': day,
                'number_of_hours': hours,
                'contract_id': contract.id,
            }

            res.append(attendances)
            res.extend(leaves.values())
        return res