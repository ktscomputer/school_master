# -*- coding: utf-8 -*-
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

    name = fields.Char(string='Admission Number',readonly=True, default='New')
    student_name = fields.Char(string='Student Name ', required=True, tracking=True)
    student_gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string='Gender ')
    dob = fields.Date(string='D O B ')
    age = fields.Integer(string='Age ', compute='_compute_age', readonly=True, store=False)
    student_class = fields.Many2one('student.class.no', string='Year ', tracking=True)
    student_class_name = fields.Many2one('student.class.name', string='Course ', tracking=True)
    student_division = fields.Many2one('student.division', string='Batch ')
    teacher_id = fields.Many2one('teacher.master', string='Teacher ')
    student_roll_number = fields.Integer(string='Roll Number ')
    student_guardian = fields.Char(string='Daughter/Son Of ')
    student_add = fields.Text('Address ')
    pincode = fields.Char('Pin Code ')
    student_add1 = fields.Char(string='House Name ', )
    student_add2 = fields.Char(string='Location ')
    student_add3 = fields.Char(string='City ')
    student_contact1 = fields.Char(string='Student Mobile Number ', size=10)
    student_contact2 = fields.Char(string=' Guardian Mobile Number ', size=10)
    student_img = fields.Image(string='Photo ', max_width=128, max_height=128)
    student_trans = fields.Selection([('school_bus', 'School Bus'), ('auto', 'Auto'), ('self', 'Self')],
                                     string='Transportation ')
    transport_mode = fields.Selection([('one_way', 'One Way'), ('two_way', 'Two Way')], string='Transportation Mode ')
    is_locked = fields.Boolean(string='Locked', default=False)
    aadhaar_card = fields.Char(string='Aadhaar Card No ')
    has_aadhaar = fields.Boolean(compute='_compute_has_aadhaar', store=True)
    active = fields.Boolean(string='Active', default=True)

    # Add a related field to get the company logo
    company_logo = fields.Binary(string='Company Logo', related='company_id.logo', readonly=True)
    # Ensure company_id exists in the model
    company_id = fields.Many2one(
        'res.company', string='Company', default=lambda self: self.env.company, readonly=True)

    # student_result_ids = fields.One2many('exam.result', 'student_id', string="Exam Results")
    total_fees_accumulated = fields.Float(string='Total Fees Accumulated', default=0.0, readonly=True)
    total_fees_receipted = fields.Float(string='Total Receipted Amount', default=0.0, readonly=True)
    academic_id = fields.Many2one('student.academic', string='Academic Record')
    #current_balance = fields.Float(string='Current Balance :', related='academic_id.current_balance', readonly=True)
    current_balance = fields.Float(
        string="Current Balance :",
        compute="_compute_current_balance",
        store=True
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
    ], string="Status", default='draft', tracking=True)
    last_fee_addition = fields.Datetime(string='Last Fee Addition', readonly=True)
    exam_ids = fields.One2many('exam.result', 'student_id', string='Exam Details')
    transport_ids = fields.One2many('student.transportation', 'student_id', string="Transport Details")
    monthly_fee_ids = fields.One2many('transport.monthly.fee', 'transport_id', string='Monthly Fees')
    fee_invoice_ids = fields.One2many('student.fee.invoice', 'student_id', string="Invoices")
    fee_receipt_ids = fields.One2many('student.fee.receipt', 'student_id', string="Receipts")
    receipt_type = fields.Selection([
        ('charge', 'Charge'),
        ('payment', 'Payment')
    ], default='payment', string="Type", tracking=True)

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

        # Locking / Unlocking

    def action_save(self):
        self.write({'is_locked': True})
        for rec in self:
            rec.state = 'confirmed'

            # Create Admission Fee Invoice
            if rec.student_class_name and rec.student_class_name.admission_fee > 0:
                self.env['student.fee.invoice'].create({
                    'student_id': rec.id,
                    'course_id': rec.student_class_name.id,
                    'year_id': rec.student_class.id if rec.student_class else False,
                    'amount': rec.student_class_name.admission_fee,
                    'description': 'Admission Fee',
                })

            # Create Quarter Fee Invoice
            if rec.student_class_name and rec.student_class_name.quarter_fee > 0:
                self.env['student.fee.invoice'].create({
                    'student_id': rec.id,
                    'course_id': rec.student_class_name.id,
                    'year_id': rec.student_class.id if rec.student_class else False,
                    'amount': rec.student_class_name.quarter_fee,
                    'description': 'Quarter Fee',
                })

        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def action_edit(self):
        self.write({'is_locked': False})
        for rec in self:
            rec.state = 'draft'
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def action_new_receipt(self):
        """Open a blank new form for another receipt"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'New Student',
            'res_model': 'student.master',
            'view_mode': 'form',
            'target': 'current',
            'context': {'default_state': 'draft'}
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
        for vals in vals_list:
            if not vals.get('name') or vals['name'] == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('student.sequence.master') or 'New'
        records = super().create(vals_list)
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
                'default_course_id': self.student_class_name.id if self.student_class_name else False,
                'default_year_id': self.student_class.id if self.student_class else False,
                'reload_parent_form': True,
            },
        }

    @api.depends('fee_invoice_ids.amount', 'fee_invoice_ids.state',
                 'fee_receipt_ids.amount', 'fee_receipt_ids.state')
    def _compute_current_balance(self):
        for rec in self:
            charges = sum(inv.amount for inv in rec.fee_invoice_ids if inv.state == 'confirmed')
            payments = sum(rc.amount for rc in rec.fee_receipt_ids if rc.state == 'confirmed')
            rec.current_balance = charges - payments

    # def action_new_student(self):
    #     """Open a new form for a student from Kanban view"""
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'New Student',
    #         'res_model': 'student.master',
    #         'view_mode': 'kanban',
    #         'view_type': 'kanban',
    #         'target': 'current',
    #         'context': {
    #             'default_state': 'draft',
    #             'default_active': True,
    #             'default_is_locked': False,
    #             'default_company_id': self.env.company.id,
    #         },
    #     }
    #
