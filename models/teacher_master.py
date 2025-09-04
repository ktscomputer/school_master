from datetime import date
from email.policy import default

from dateutil.relativedelta import relativedelta

from odoo import models,fields,api

class TeacherMaster(models.Model):
    _name = 'teacher.master'
    _description = 'Student Class Teacher'
    _inherit = ['mail.thread', 'mail.activity.mixin']



    name = fields.Char(string='Teacher Name', required=True)
    gender= fields.Selection([('male','Male'),('female','Female')],string='Gender',default='male')
    doj= fields.Date('Date of Joining')
    year_of_service = fields.Char(string='Servicing Years',compute='_compute_year_of_service',
        store=True
    )
    active=fields.Boolean('Active',default=True)


    contact_no = fields.Char(string='Contact No')
    emergency_contact = fields.Char(string='Emergency Contact')
    address = fields.Text('Address')
    designation_id = fields.Many2one('teacher.designation',string='Designation')
    std = fields.Many2many('student.class.no',string='Class')
    is_locked = fields.Boolean(string='Locked', default=False)

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

    # display_std = fields.Char(string="Std Display", compute="_compute_display_std")

    # def _compute_display_std(self):
    #     for record in self:
    #         record.display_std = ", ".join(record.std.mapped('name')) if record.std else ""

    @api.depends('doj')
    def _compute_year_of_service(self):
        today = date.today()
        for record in self:
            if record.doj:
                delta = relativedelta(today, record.doj)
                record.year_of_service = f"{delta.years}y {delta.months}m {delta.days}d"
            else:
                record.year_of_service = "0y 0m 0d"

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

    def action_new_teacher(self):
        """Open a blank new form for another receipt"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'New Year',
            'res_model': 'student.teacher',
            'view_mode': 'form',
            'target': 'current',
            'context': {'default_state': 'draft'}
        }