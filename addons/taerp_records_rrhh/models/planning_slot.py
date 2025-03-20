from datetime import datetime, timedelta

import pytz

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

    @api.onchange("employee_id", "start_datetime", "end_datetime")
    def onchange_holiday(self):
        for slot in self:
            contracts_list = slot.employee_id._get_contracts(
                slot.start_datetime, slot.end_datetime
            )
            contracts = contracts_list[0] if contracts_list else False
            if contracts:
                datetime_search = (
                    slot.start_datetime.astimezone(pytz.timezone(self.env.user.tz))
                    .replace(hour=0, minute=0, second=0)
                    .astimezone(pytz.timezone("UTC"))
                )
                time_off = self.env["resource.calendar.leaves"].search(
                    [
                        ("resource_id", "=", False),
                        ("calendar_id", "=", contracts.resource_calendar_id.id),
                        ("date", "=", datetime_search.date()),
                    ]
                )
                if time_off:
                    if time_off.work_entry_type_id.id == 7:
                        slot.is_holiday = True
                        slot.is_no_compuholiday = False
                        slot.write({"is_holiday": True, "is_no_compuholiday": False})
                    elif time_off.work_entry_type_id.id == 10:
                        slot.is_holiday = False
                        slot.is_no_compuholiday = True
                        slot.write({"is_holiday": False, "is_no_compuholiday": True})
                    else:
                        slot.is_holiday = False
                        slot.is_no_compuholiday = False
                        slot.write({"is_holiday": False, "is_no_compuholiday": False})
                else:
                    slot.is_holiday = False
                    slot.is_no_compuholiday = False
                    slot.write({"is_holiday": False, "is_no_compuholiday": False})

    @api.onchange("is_free")
    def onchange_is_free(self):
        for slot in self:
            if slot.is_free:
                slot.write({"allocated_hours": 0, "minutes_for_breaks": 0})
