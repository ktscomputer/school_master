#-*- coding: utf-8 -*-
import re
from datetime import date

import dateutil

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class StudentMaster(models.Model):
    _name = 'student.master'
    _description = 'Student Master'
    _rec_name = 'student_name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    student_name = fields.Char(string='Student Name', required=True,tracking=True)
    student_gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string='Gender')
    dob= fields.Date(string='D O B')
    age = fields.Integer(string='Age', compute='_compute_age', readonly=True, store=False)
    student_class = fields.Many2one('student.class.no', string='Year',tracking=True)
    student_class_name = fields.Many2one('student.class.name', string='Course',tracking=True)
    student_division = fields.Many2one('student.division', string='Batch')
    #class_teacher_id = fields.Many2one('student.teacher',string='Class Teacher',required=True)
    teacher_id = fields.Many2one('teacher.master',string='Teacher')
    student_roll_number = fields.Integer(string='Roll Number')
    student_guardian = fields.Char(string='Daughter/Son Of')
    student_add1 = fields.Char(string='House Name',)
    student_add2 = fields.Char(string='Location')
    student_add3 = fields.Char(string='City')
    student_contact1 = fields.Char(string='Mobile Number', size=15)
    student_img = fields.Image(string='Image', max_width=128, max_height=128)
    student_trans = fields.Selection([('school_bus','School Bus'),('auto','Auto'),('self','Self')],string='Transportation')
    transport_mode = fields.Selection([('one_way','One Way'),('two_way','Two Way')],string='Transportation Mode')
    is_locked = fields.Boolean(string='Locked', default=False)
    aadhaar_card = fields.Char(string='Aadhaar Card No')
    has_aadhaar = fields.Boolean(compute='_compute_has_aadhaar', store=True)
    active = fields.Boolean(string='Active', default=True)

    # Add a related field to get the company logo
    company_logo = fields.Binary(
        string='Company Logo',
        related='company_id.logo',
        readonly=True
    )
    # Ensure company_id exists in the model
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        readonly=True
    )

    # student_result_ids = fields.One2many('exam.result', 'student_id', string="Exam Results")
    exam_ids = fields.One2many('exam.result','student_id',string='Exam Details')
    transport_ids = fields.One2many('student.transportation','student_id',string="Transport Details")
    monthly_fee_ids = fields.One2many('transport.monthly.fee', 'transport_id', string='Monthly Fees')
    _sql_constraints = [
        ('roll_number_unique', 'UNIQUE(student_roll_number, student_class, student_division)',
         'Roll number must be unique per class and division.')
    ]

    @api.depends('dob')
    def _compute_age(self):
        today = date.today()
        for record in self:
            if record.dob:
                dob = fields.Date.from_string(record.dob)
                record.age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            else:
                record.age = 0

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

    @api.depends('aadhaar_card')
    def _compute_has_aadhaar(self):
        for record in self:
            record.has_aadhaar = bool(record.aadhaar_card and record.aadhaar_card.strip())

    @api.constrains('aadhaar_card')
    def _check_aadhaar_number(self):
        for record in self:
            if record.aadhaar_card and record.aadhaar_card.strip():
                # Remove spaces or hyphens if any
                aadhaar_clean = re.sub(r'[\s-]', '', record.aadhaar_card)
                if not aadhaar_clean.isdigit() or len(aadhaar_clean) != 12:
                    raise ValidationError("Aadhaar number must be 12 digits (numbers only)")

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        other_vals_list = []
        for record in records:
            other_vals_list.append({
                'name': record.student_name,
                'student_id': record.id,
                'course': record.student_class_no.name,
                'year': record.student_class_name.name,
            })
        if other_vals_list:
            self.env['student.academic'].create(other_vals_list)
        return records

    def action_pay_now(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Record Payment',
            'res_model': 'student.fee.receipt',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_student_id': self.id,
                'default_amount': self.current_balance,
                'default_course': self.student_class_name.name if self.student_class_name else False,
                'reload_parent_form': True,
            },
        }


