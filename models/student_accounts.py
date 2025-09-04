from odoo import models, fields, api
from datetime import datetime


class StudentMasterOne(models.Model):
    _inherit = 'student.master'




class StudentFeeInvoice(models.Model):
    _name = 'student.fee.invoice'
    _description = 'Student Fee Invoice'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'description'

    student_id = fields.Many2one('student.master', string="Student", required=True, ondelete='cascade')
    course_id = fields.Many2one('student.class.name', string="Course", readonly=True)
    year_id = fields.Many2one('student.class.no', string="Year", readonly=True)

    amount = fields.Float(string="Invoice Amount", required=True, tracking=True)
    description = fields.Char(string="Description", required=True)
    invoice_date = fields.Date(string="Invoice Date", default=fields.Date.today, required=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ], string="Status", default='confirmed', tracking=True)

    # Add a related field to get the company logo
    company_logo = fields.Binary(string='Company Logo', related='company_id.logo', readonly=True)
    # Ensure company_id exists in the model
    company_id = fields.Many2one(
        'res.company', string='Company', default=lambda self: self.env.company, readonly=True)


    @api.onchange('student_id')
    def _onchange_student_id(self):
        for rec in self:
            if rec.student_id:
                rec.course_id = rec.student_id.student_class_name.id
                rec.year_id = rec.student_id.student_class.id
            else:
                rec.course_id = False
                rec.year_id = False

