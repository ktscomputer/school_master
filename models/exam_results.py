 #-*- coding: utf-8 -*-

from odoo import models, fields, api


class ExamResult(models.Model):
    _name = 'exam.result'
    _description = 'Exam Result'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'student_id'



    student_id = fields.Many2one('student.master','Student Name ',tracking=True)
    exam_name_id = fields.Many2one('exam.name', string='Exam Name ',tracking=True)
    exam_subject_id = fields.Many2one('exam.subject', string='Subject ',tracking=True)
    exam_total_mark = fields.Float(string='Total Marks ',tracking=True)
    obtained_mark = fields.Float(string='Mark Obtained ',tracking=True)

    # Grade fields (computed)
    grade = fields.Char(string='Grade ', compute='_compute_grade', store=True)
    grade_point = fields.Float(string='Grade Point ', compute='_compute_grade', store=True)
    is_locked = fields.Boolean(string='Locked', default=False)

    # Add a related field to get the company logo
    company_logo = fields.Binary(string='Company Logo', related='company_id.logo', readonly=True)
    # Ensure company_id exists in the model
    company_id = fields.Many2one(
        'res.company', string='Company', default=lambda self: self.env.company, readonly=True)


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

    @api.depends('obtained_mark')
    def _compute_grade(self):
        for record in self:
            mark = record.obtained_mark

            # Define your grading system (mark ranges to grades)
            if mark >= 90:
                record.grade = 'A+'
                record.grade_point = 4.0
            elif mark >= 80:
                record.grade = 'A'
                record.grade_point = 3.75
            elif mark >= 75:
                record.grade = 'B+'
                record.grade_point = 3.5
            elif mark >= 70:
                record.grade = 'B'
                record.grade_point = 3.0
            elif mark >= 65:
                record.grade = 'C+'
                record.grade_point = 2.5
            elif mark >= 60:
                record.grade = 'C'
                record.grade_point = 2.0
            elif mark >= 50:
                record.grade = 'D'
                record.grade_point = 1.0
            else:
                record.grade = 'F'
                record.grade_point = 0.0


