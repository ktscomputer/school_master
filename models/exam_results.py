 #-*- coding: utf-8 -*-

from odoo import models, fields, api


class ExamResult(models.Model):
    _name = 'exam.result'
    _description = 'Exam Result'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'student_id'



    student_id = fields.Many2one('student.master','Student Name ',tracking=True,required=True)
    exam_name_id = fields.Many2one('exam.name', string='Exam Name ',tracking=True,required=True)
    exam_subject_id = fields.Many2one('exam.subject', string='Subject ',tracking=True,required=True)
    exam_total_mark = fields.Float(string='Total Marks ',tracking=True,required=True)
    obtained_mark = fields.Float(string='Mark Obtained ',tracking=True,required=True)

    # Grade fields (computed)
    grade = fields.Char(string='Grade ', compute='_compute_grade', store=True)
    grade_point = fields.Float(string='Grade Point ', compute='_compute_grade', store=True)
    is_locked = fields.Boolean(string='Locked', default=False)

    # Add a related field to get the company logo
    company_logo = fields.Binary(string='Company Logo', related='company_id.logo', readonly=True)
    # Ensure company_id exists in the model
    company_id = fields.Many2one(
        'res.company', string='Company', default=lambda self: self.env.company, readonly=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
    ], string="Status", default='draft', tracking=True)

    def action_save(self):
        self.write({'is_locked': True})
        for rec in self:
            rec.state = 'confirmed'
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def action_edit(self):
        self.write({'is_locked': False})
        for rec in self:
            rec.state = 'draft'
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def action_new_result(self):
        """Open a blank new form for another receipt"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'New Year',
            'res_model': 'student.class.no',
            'view_mode': 'form',
            'target': 'current',
            'context': {'default_state': 'draft'}
        }


    @api.depends('obtained_mark', 'exam_total_mark')
    def _compute_grade(self):
        for record in self:
            # Avoid division by zero
            if record.exam_total_mark > 0:
                percentage = (record.obtained_mark / record.exam_total_mark) * 100
            else:
                percentage = 0

            # Define your grading system (percentage to grades)
            if percentage >= 90:
                record.grade = 'A+'
                record.grade_point = 4.0
            elif percentage >= 80:
                record.grade = 'A'
                record.grade_point = 3.75
            elif percentage >= 75:
                record.grade = 'B+'
                record.grade_point = 3.5
            elif percentage >= 70:
                record.grade = 'B'
                record.grade_point = 3.0
            elif percentage >= 65:
                record.grade = 'C+'
                record.grade_point = 2.5
            elif percentage >= 60:
                record.grade = 'C'
                record.grade_point = 2.0
            elif percentage >= 50:
                record.grade = 'D'
                record.grade_point = 1.0
            else:
                record.grade = 'F'
                record.grade_point = 0.0



