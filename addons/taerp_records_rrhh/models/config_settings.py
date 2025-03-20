from odoo import fields, models, api


class AttendanceSettingInherited(models.TransientModel):

    _inherit = 'res.config.settings'

    over_time_shift_type = fields.Boolean(string="Extra hours by Shift Type", default=False)
    over_time_start_from = fields.Date()
    average_hours_day_shift = fields.Selection([(str(y), str(y)) for y in range(1, 25)],
                                               string='Average hours for Day Shift')
    average_hours_mixed_shift = fields.Selection([(str(y), str(y)) for y in range(1, 25)],
                                                 string='Average hours for Mixed Shift')
    average_hours_night_shift = fields.Selection([(str(y), str(y)) for y in range(1, 25)],
                                                 string='Average hours for Night Shift')

    average_hours_categ_one = fields.Selection([(str(y), str(y)) for y in range(1, 25)],
                                                 string='Average hours for especial category one')
    average_hours_categ_two = fields.Selection([(str(y), str(y)) for y in range(1, 25)],
                                                 string='Average hours for especial category two')

    late_checkin_threshold = fields.Integer(string="Late Check-in Tolerance", default=0)
    early_checkin_threshold = fields.Integer(string="Early Check-in Tolerance", default=0)

    @api.model
    def get_values(self):
        res = super(AttendanceSettingInherited, self).get_values()

        params = self.env['ir.config_parameter'].sudo()
        over_time_shift_type = params.get_param(
            'taerp_records_rrhh.over_time_shift_type')
        over_time_start_from = params.get_param(
            'taerp_records_rrhh.over_time_start_from')
        average_hours_day_shift = params.get_param(
            'taerp_records_rrhh.average_hours_day_shift')
        average_hours_mixed_shift = params.get_param(
            'taerp_records_rrhh.average_hours_mixed_shift')
        average_hours_night_shift = params.get_param(
            'taerp_records_rrhh.average_hours_night_shift')

        average_hours_categ_one = params.get_param(
            'taerp_records_rrhh.average_hours_categ_one')
        average_hours_categ_two = params.get_param(
            'taerp_records_rrhh.average_hours_categ_two')

        late_checkin_threshold = params.get_param(
            'taerp_records_rrhh.late_checkin_threshold')
        early_checkin_threshold = params.get_param(
            'taerp_records_rrhh.early_checkin_threshold')

        res.update(
            over_time_shift_type=over_time_shift_type,
            over_time_start_from=over_time_start_from,
            average_hours_day_shift=average_hours_day_shift,
            average_hours_mixed_shift=average_hours_mixed_shift,
            average_hours_night_shift=average_hours_night_shift,
            average_hours_categ_one=average_hours_categ_one,
            average_hours_categ_two=average_hours_categ_two,
            late_checkin_threshold=late_checkin_threshold,
            early_checkin_threshold=early_checkin_threshold

        )
        return res

    @api.model
    def set_values(self):
        super(AttendanceSettingInherited, self).set_values()

        params = self.env['ir.config_parameter'].sudo()
        self.env['ir.config_parameter'].sudo().set_param(
            "taerp_records_rrhh.over_time_shift_type", self.over_time_shift_type)
        self.env['ir.config_parameter'].sudo().set_param(
            "taerp_records_rrhh.over_time_start_from", self.over_time_start_from)
        self.env['ir.config_parameter'].sudo().set_param(
            "taerp_records_rrhh.average_hours_day_shift",
            self.average_hours_day_shift)
        self.env['ir.config_parameter'].sudo().set_param(
            "taerp_records_rrhh.average_hours_mixed_shift",
            self.average_hours_mixed_shift)
        self.env['ir.config_parameter'].sudo().set_param(
            "taerp_records_rrhh.average_hours_night_shift",
            self.average_hours_night_shift)

        self.env['ir.config_parameter'].sudo().set_param(
            "taerp_records_rrhh.average_hours_categ_one",
            self.average_hours_categ_one)
        self.env['ir.config_parameter'].sudo().set_param(
            "taerp_records_rrhh.average_hours_categ_two",
            self.average_hours_categ_two)

        self.env['ir.config_parameter'].sudo().set_param(
            "taerp_records_rrhh.late_checkin_threshold",
            self.late_checkin_threshold)
        self.env['ir.config_parameter'].sudo().set_param(
            "taerp_records_rrhh.early_checkin_threshold",
            self.early_checkin_threshold)

        shift_value = 0
        if self.over_time_shift_type:
            shift_value = 1
        table=self.env['bodhi.attendance.report']
        user_id =self.env["res.users"].search([('id', '=', 1)])

        self.env.cr.execute("""
                DROP VIEW %s;
               CREATE OR REPLACE VIEW %s AS (
                   (
                       SELECT
                              aten.id,
                              aten.department_id,
                              aten.employee_id,
                              aten.resource_id,
                              aten.check_in,
                              rest.as_of_date ,
                              rest.shift_value,
                              rest.id as res_id,
                              aten.worked_hours AS raw_work_hours,
                              COALESCE(is_holiday, 0) AS is_holiday,
                              COALESCE(is_no_compuholiday, 0) AS is_no_compuholiday,
                              COALESCE(is_free, 0) AS is_free,
                              COALESCE(((aten.worked_hours +(LEAST(EXTRACT(epoch FROM aten.check_in_time-COALESCE(rest.start_datetime, aten.check_in_time))/ 3600, 0))-aten.break)* GREATEST(0,(1-COALESCE(is_holiday, 0)-COALESCE(is_no_compuholiday, 0)-COALESCE(is_free, 0)))),0.0)::double PRECISION AS worked_hours,
                              COALESCE(((aten.worked_hours +(LEAST(EXTRACT(epoch FROM aten.check_in_time-COALESCE(rest.start_datetime, aten.check_in_time))/ 3600, 0))
                              -(COALESCE((((
                                    CASE WHEN
                                    ((aten.worked_hours +(LEAST(EXTRACT(epoch FROM aten.check_in_time-COALESCE(rest.start_datetime, aten.check_in_time))/ 3600, 0))-aten.break)-COALESCE(rest.shift_value, 8))>= 0
                                    THEN
                                        ((aten.worked_hours +(LEAST(EXTRACT(epoch FROM aten.check_in_time-COALESCE(rest.start_datetime, aten.check_in_time))/ 3600, 0))-aten.break)-COALESCE(rest.shift_value, 8))
                                    ELSE
                                        0
                                    END
                                    )* %s)* GREATEST(COALESCE(is_holiday, 0),COALESCE(is_no_compuholiday, 0))), 0)::double PRECISION)
                              -aten.break)*(is_no_compuholiday)), 0.0)::double PRECISION AS no_compuholiday,
                              COALESCE(((aten.worked_hours +(LEAST(EXTRACT(epoch FROM aten.check_in_time-COALESCE(rest.start_datetime, aten.check_in_time))/ 3600, 0))
                              -(COALESCE((((
                                    CASE WHEN
                                    ((aten.worked_hours +(LEAST(EXTRACT(epoch FROM aten.check_in_time-COALESCE(rest.start_datetime, aten.check_in_time))/ 3600, 0))-aten.break)-COALESCE(rest.shift_value, 8))>= 0
                                    THEN
                                        ((aten.worked_hours +(LEAST(EXTRACT(epoch FROM aten.check_in_time-COALESCE(rest.start_datetime, aten.check_in_time))/ 3600, 0))-aten.break)-COALESCE(rest.shift_value, 8))
                                    ELSE
                                        0
                                    END
                                    )* %s)* GREATEST(COALESCE(is_holiday, 0),COALESCE(is_no_compuholiday, 0))), 0)::double PRECISION)
                              -aten.break)*(is_holiday)), 0.0)::double PRECISION AS holiday,
                              COALESCE(((
                                CASE WHEN
                                ((aten.worked_hours +(LEAST(EXTRACT(epoch FROM aten.check_in_time-COALESCE(rest.start_datetime, aten.check_in_time))/ 3600, 0))-aten.break)-COALESCE(rest.shift_value, 8))>= 0
                                THEN
                                8
                                ELSE
                                COALESCE(((aten.worked_hours +(LEAST(EXTRACT(epoch FROM aten.check_in_time-COALESCE(rest.start_datetime, aten.check_in_time))/ 3600, 0))-aten.break)), 0.0)
                                END
                                )* COALESCE(is_free, 0)), 0.0)::double PRECISION AS free_time,
                              aten.break::double PRECISION AS break_hours,
                              COALESCE(rest.expected_break, 0.0)::double PRECISION AS break_expected_hours,
                              COALESCE(rest.expected_break-aten.break, 0.0)::double PRECISION AS break_hours_difference,
                              COALESCE((((
                                    CASE WHEN
                                    ((aten.worked_hours +(LEAST(EXTRACT(epoch FROM aten.check_in_time-COALESCE(rest.start_datetime, aten.check_in_time))/ 3600, 0))-aten.break)-COALESCE(rest.shift_value, 8))>= divider
                                    THEN
                                    ((aten.worked_hours +(LEAST(EXTRACT(epoch FROM aten.check_in_time-COALESCE(rest.start_datetime, aten.check_in_time))/ 3600, 0))-aten.break)-COALESCE(rest.shift_value, 8))
                                    ELSE
                                    0
                                    END
                                    )* %s)* GREATEST(0,(1-COALESCE(is_holiday, 0)-COALESCE(is_no_compuholiday, 0)-COALESCE(is_free, 0)))), 0)::double PRECISION AS overtime_hours,
                                    
                              COALESCE((((
                                    CASE WHEN
                                    ((aten.worked_hours +(LEAST(EXTRACT(epoch FROM aten.check_in_time-COALESCE(rest.start_datetime, aten.check_in_time))/ 3600, 0))-aten.break)-COALESCE(rest.shift_value, 8))>= divider
                                    THEN
                                    ((aten.worked_hours +(LEAST(EXTRACT(epoch FROM aten.check_in_time-COALESCE(rest.start_datetime, aten.check_in_time))/ 3600, 0))-aten.break)-COALESCE(rest.shift_value, 8))
                                    ELSE
                                    0
                                    END
                                    )* %s)* COALESCE(is_holiday, 0)), 0)::double PRECISION AS holiday_overtime_hours,
                                    
                            COALESCE((((
                                    CASE WHEN
                                    ((aten.worked_hours +(LEAST(EXTRACT(epoch FROM aten.check_in_time-COALESCE(rest.start_datetime, aten.check_in_time))/ 3600, 0))-aten.break)-COALESCE(rest.shift_value, 8))>= divider
                                    THEN
                                    ((aten.worked_hours +(LEAST(EXTRACT(epoch FROM aten.check_in_time-COALESCE(rest.start_datetime, aten.check_in_time))/ 3600, 0))-aten.break)-COALESCE(rest.shift_value, 8))
                                    ELSE
                                    0
                                    END
                                    )* %s)* COALESCE(is_no_compuholiday, 0)), 0)::double PRECISION AS holiday_no_overtime_hours,
                                    
                               COALESCE(
                                      CASE
                                        WHEN ((aten.worked_hours + (LEAST(EXTRACT(epoch FROM aten.check_in_time - COALESCE(rest.start_datetime, aten.check_in_time)) / 3600, 0)) - aten.break) - COALESCE(rest.shift_value, 8)) >= 0
                                        THEN ((aten.worked_hours + (LEAST(EXTRACT(epoch FROM aten.check_in_time - COALESCE(rest.start_datetime, aten.check_in_time)) / 3600, 0)) - aten.break) - COALESCE(rest.shift_value, 8))
                                        ELSE 0
                                      END * COALESCE(is_free, 0), 0.0
                                    )::DOUBLE PRECISION AS free_overtime_hours,
                            
                              COALESCE((((
                                    CASE WHEN
                                    ((aten.worked_hours +(LEAST(EXTRACT(epoch FROM aten.check_in_time-COALESCE(rest.start_datetime, aten.check_in_time))/ 3600, 0))-aten.break)-COALESCE(rest.shift_value, 8))>= 0
                                    THEN
                                    COALESCE(rest.shift_value, 8)
                                    ELSE
                                    0
                                    END
                                    )* %s)* GREATEST(0,(1-COALESCE(is_holiday, 0)-COALESCE(is_no_compuholiday, 0)-COALESCE(is_free, 0)))), 0)::double PRECISION AS worked_hours_rounded,
                              COALESCE((((
                                    CASE WHEN
                                    ((aten.worked_hours +(LEAST(EXTRACT(epoch FROM aten.check_in_time-COALESCE(rest.start_datetime, aten.check_in_time))/ 3600, 0))-aten.break)-COALESCE(rest.shift_value, 8))>= 0
                                    THEN
                                    1
                                    ELSE
                                    0
                                    END
                                    )* %s)* GREATEST(0,(1-COALESCE(is_holiday, 0)-COALESCE(is_no_compuholiday, 0)-COALESCE(is_free, 0)))), 0)::double PRECISION AS worked_days,
                              COALESCE((((
                                    CASE WHEN
                                    ((aten.worked_hours +(LEAST(EXTRACT(epoch FROM aten.check_in_time-COALESCE(rest.start_datetime, aten.check_in_time))/ 3600, 0))-aten.break)-COALESCE(rest.shift_value, 8))>= 0
                                    THEN
                                    0
                                    ELSE
                                    (aten.worked_hours +(LEAST(EXTRACT(epoch FROM aten.check_in_time-COALESCE(rest.start_datetime, aten.check_in_time))/ 3600, 0))-aten.break)
                                    END
                                    )* %s)* GREATEST(0,(1-COALESCE(is_holiday, 0)-COALESCE(is_no_compuholiday, 0)-COALESCE(is_free, 0)))), 0)::double PRECISION AS incomplete_hours,
                            COALESCE((((
                                 CASE WHEN
                                 ((aten.worked_hours +(LEAST(EXTRACT(epoch FROM aten.check_in_time-COALESCE(rest.start_datetime, aten.check_in_time))/ 3600, 0))-aten.break)-COALESCE(rest.shift_value, 8))>= 0
                                 THEN
                                 0
                                 ELSE
                                 1
                                 END
                                 )* %s)* GREATEST(0,(1-COALESCE(is_holiday, 0)-COALESCE(is_no_compuholiday, 0)-COALESCE(is_free, 0)))), 0)::double PRECISION AS incomplete_count,
                              COALESCE((((
                                    CASE WHEN
                                    ((aten.worked_hours +(LEAST(EXTRACT(epoch FROM aten.check_in_time-COALESCE(rest.start_datetime, aten.check_in_time))/ 3600, 0))-aten.break)-COALESCE(rest.shift_value, 8))>= 0
                                    THEN
                                    0
                                    ELSE
                                    (aten.worked_hours +(LEAST(EXTRACT(epoch FROM aten.check_in_time-COALESCE(rest.start_datetime, aten.check_in_time))/ 3600, 0))-aten.break)/ COALESCE(rest.shift_value, 8)
                                    END
                                    )* %s)* GREATEST(0,(1-COALESCE(is_holiday, 0)-COALESCE(is_no_compuholiday, 0)-COALESCE(is_free, 0)))), 0)::double PRECISION AS incomplete_days
                        FROM
                              (
                                    SELECT
                                          max(hra.id) AS id,
                                          max(hr_employee.department_id) AS department_id,
                                          max(hr_employee.resource_id) AS resource_id,
                                          hra.employee_id,
                                          hra.check_in,
                                          min(hra.check_in_time) AS check_in_time,
                                          (
                                                CAST(%s AS decimal)/ CAST(60 AS decimal)
                                          ) AS divider,
                                          sum(COALESCE(hra.worked_hours, 0)) AS worked_hours,
                                          sum(COALESCE(hra.break, 0)) AS break
                                    FROM
                                          (
                                                SELECT
                                                      id,
                                                      ROW_NUMBER() OVER (
                                                            PARTITION BY employee_id,
                                                            CAST(check_in AT time ZONE 'utc' AT time ZONE '%s' AS DATE)
                                                      ) AS ot_check,
                                                      employee_id,
                                                      CASE
                                                            WHEN TYPE = 'normal' THEN 
                                                                CAST(check_in AT time ZONE 'utc' AT time ZONE '%s' AS DATE) 
                                                            ELSE 
                                                                CAST(planing_check_in AT time ZONE 'utc' AT time ZONE '%s' AS DATE)
                                                      END AS check_in,
                                                      CASE
                                                            WHEN TYPE = 'normal' THEN 
                                                                (check_in AT time ZONE 'utc' AT time ZONE '%s')
                                                            ELSE 
                                                                planing_check_in AT time ZONE 'utc' AT time ZONE '%s'
                                                      END AS check_in_time,
                                                      CASE
                                                            WHEN TYPE = 'normal' THEN worked_hours
                                                            ELSE 0
                                                      END AS worked_hours,
                                                      CASE
                                                            WHEN TYPE = 'break' THEN worked_hours
                                                            ELSE 0
                                                      END AS break
                                                FROM
                                                      hr_attendance
                                          ) AS hra
                                    LEFT JOIN
                        hr_employee
                        ON
                                          hr_employee.id = hra.employee_id
                                    GROUP BY
                                          employee_id,
                                          check_in
                              ) aten
                        LEFT OUTER JOIN
                        (
                                    SELECT
                                          daylight.id,
                                          daylight.resource_id,
                                          daylight.as_of_date,
                                          daylight.start_datetime,
                                          daylight.is_holiday,
                                          daylight.is_free,
                                          CASE
                                                WHEN daylight.id = night.id THEN daylight.expected_break
                                                ELSE daylight.expected_break + COALESCE (night.expected_break,0)
                                          END AS expected_break,
                                          daylight.is_no_compuholiday,
                                          daylight.shift_value
                                    FROM
                                          (
                                                SELECT
                                                      id,
                                                      resource_id,
                                                      date_compare AS as_of_date,
                                                      start_datetime,
                                                      date_compare,
                                                      (
                                                            COALESCE(ps.minutes_for_breaks, 0.0)
                                                      )/ 60.0 AS expected_break,
                                                      CASE
                                                            WHEN is_holiday = TRUE THEN 1
                                                            ELSE 0
                                                      END AS is_holiday,
                                                      CASE
                                                            WHEN is_free = TRUE THEN 1
                                                            ELSE 0
                                                      END AS is_free,
                                                      CASE
                                                            WHEN is_no_compuholiday = TRUE THEN 1
                                                            ELSE 0
                                                      END AS is_no_compuholiday,
                                                      CASE
                                                            WHEN ps.shift_type = 'day' THEN %s
                                                            WHEN ps.shift_type = 'mixed' THEN %s
                                                            WHEN ps.shift_type = 'night' THEN %s
                                                            WHEN ps.shift_type = 'categ_one' THEN %s
                                                            WHEN ps.shift_type = 'categ_two' THEN %s
                                                            ELSE 8
                                                      END AS shift_value
                                                FROM
                                                      (
                                                            SELECT
                                                                  min(id) AS id,
                                                                  resource_id,
                                                                  shift_type,
                                                                  CAST(start_datetime AT time ZONE 'utc' AT time ZONE '%s' AS DATE) AS date_compare,
                                                                  min(start_datetime AT time ZONE 'utc' AT time ZONE '%s') AS start_datetime,
                                                                  max(end_datetime) AS end_datetime,
                                                                  sum(COALESCE(minutes_for_breaks, 0)) AS minutes_for_breaks,
                                                                  COALESCE(is_holiday, FALSE) AS is_holiday,
                                                                  COALESCE(is_free, FALSE) AS is_free,
                                                                  COALESCE(is_no_compuholiday, FALSE) AS is_no_compuholiday
                                                            FROM
                                                                  planning_slot
                                                            WHERE
                                                                  state = 'published'
                                                            GROUP BY
                                                                  date_compare,
                                                                  shift_type,
                                                                  resource_id,
                                                                  is_holiday,
                                                                  is_free,
                                                                  is_no_compuholiday
                                                      ) ps
                                          ) daylight
                                          LEFT JOIN
                                          (
                                                SELECT
                                                      id,
                                                      resource_id,
                                                      end_date AS end_date,
                                                      expected_break
                                                FROM
                                                      (
                                                            SELECT
                                                                  min(id) AS id,
                                                                  resource_id,
                                                                  min(end_datetime AT time ZONE 'utc' AT time ZONE '%s') AS end_datetime,
                                                                  CAST(end_datetime AT time ZONE 'utc' AT time ZONE '%s' AS DATE) AS end_date,
                                                                  sum(COALESCE(minutes_for_breaks, 0)/60) AS expected_break
                                                            FROM
                                                                  planning_slot
                                                            WHERE
                                                                  state = 'published'
                                                            GROUP BY
                                                                  end_date,
                                                                  shift_type,
                                                                  resource_id
                                                      ) ps
                                          ) AS night  ON daylight.date_compare = night.end_date
                                                    AND daylight.resource_id = night.resource_id
                                    ORDER BY
                                          end_date
                              ) rest
                        ON
                              rest.resource_id = aten.resource_id
                              AND rest.as_of_date = aten.check_in
                        ORDER BY
                              check_in
                                    
                   )
               );
           """  % (table._table,
                       table._table,
                        shift_value,
                        shift_value,
                        shift_value,
                        shift_value,
                        shift_value,
                       shift_value,
                        shift_value,
                       shift_value,
                        shift_value,
                       shift_value,
                        self.overtime_company_threshold or 0,
                        user_id.tz,
                        user_id.tz,
                        user_id.tz,
                        user_id.tz,
                     user_id.tz,
                        self.average_hours_day_shift or 0,
                       self.average_hours_mixed_shift or 0,
                       self.average_hours_night_shift or 0,
                       self.average_hours_categ_one or 0,
                       self.average_hours_categ_two or 0,
                   user_id.tz,
                        user_id.tz,
                       user_id.tz,
                       user_id.tz
                       ))





