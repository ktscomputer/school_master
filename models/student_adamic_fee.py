import logging
_logger = logging.getLogger(__name__)

import dateutil.utils

from odoo import models, fields, api


class StudentFee(models.Model):
    _name = 'student.academic'
    _description = 'Student Academic Fee Details'

    name = fields.Char(string='Student Name')
    receipt_date = fields.Date(string='Date', default=dateutil.utils.today())

    course = fields.Char(string='Course',)
    year = fields.Char(string='Year',)
    student_id = fields.Many2one('student.master')
    #course_id = fields.Many2one('student.class.name', string='Course',
                                #related='name.student_class_name', readonly=True, store=True)
    #year_id = fields.Many2one('student.class.no', string='Year',
                              #related='name.student_class', readonly=True, store=True)
    academic_fee = fields.Float('Quarterly Fee Amount')
    admission_fee = fields.Float('Admission Fee')
    active = fields.Boolean(string='Active', default=True)

    total_fees_accumulated = fields.Float(string='Total Fees Accumulated', default=0.00, readonly=True)
    fee_receipt = fields.Float(string='Receipt')
    current_balance = fields.Float(string='Current Balance', compute='_compute_current_balance')
    last_fee_addition = fields.Datetime(string='Last Fee Addition', readonly=True)

    is_locked = fields.Boolean(string='Locked', default=False)

    def action_save(self):
        self.write({'is_locked': True})
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def action_edit(self):
        self.write({'is_locked': False})
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }


    @api.depends('total_fees_accumulated', 'fee_receipt')
    def _compute_current_balance(self):
        for student in self:
            student.current_balance = student.total_fees_accumulated - student.fee_receipt

    @api.onchange('name')
    def _onchange_name_course(self):
        self.course = None
        self.year = None

        if self.name:
            # Auto-set fields based on the selected student's data
            self.course = self.name.course
            self.year = self.name.year
