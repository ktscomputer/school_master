from odoo import models, fields, api


# view created sequence 20
class StudentClassNo(models.Model):
    _name = 'student.class.no'
    _description = 'Student Class'

    name = fields.Char(string='Year', required=True)
    active = fields.Boolean(string='Active', default=True)
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

    def action_new_year(self):
        """Open a blank new form for another receipt"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'New Year',
            'res_model': 'student.class.no',
            'view_mode': 'form',
            'target': 'current',
            'context': {'default_state': 'draft'}
        }

    def action_cancel(self):

        return {
            'type': 'ir.actions.act_window',
            'name': 'Student Classes',
            'res_model': 'student.class.no',
            'view_mode': 'list',
            'view_type': 'list',
            'target': 'current',
        }


class StudentClassName(models.Model):
    _name = 'student.class.name'
    _description = 'Available Courses and its fees'

    name = fields.Char(string='Class Name', required=True)
    duration = fields.Char('Course Duration')
    admission_fee = fields.Float('Admission Fee')
    quarter_fee = fields.Float(string='Quarter Fee', )
    is_locked = fields.Boolean(string='Locked', default=False)
    active = fields.Boolean(string='Active', default=True)
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

    def action_new_course(self):
        """Open a blank new form for another receipt"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'New Year',
            'res_model': 'student.class.no',
            'view_mode': 'form',
            'target': 'current',
            'context': {'default_state': 'draft'}
        }

    # VIEW CREATED IN SETTINGS 10 SEQUENCE


class StudentDivision(models.Model):
    _name = 'student.division'
    _description = 'Student Division'

    name = fields.Char(string='Batch Name', required=True)
    is_locked = fields.Boolean(string='Locked', default=False)

    active = fields.Boolean(string='Active', default=True)
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

    def action_new_batch(self):
        """Open a blank new form for another receipt"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'New Batch',
            'res_model': 'student.division',
            'view_mode': 'form',
            'target': 'current',
            'context': {'default_state': 'draft'}
        }

    def action_cancel(self):
        self.write({'is_locked': False})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'student.division',
            'view_mode': 'tree',
            'target': 'main',
        }


class TeacherDesignation(models.Model):
    _name = 'teacher.designation'
    _description = 'Teachers Designation'

    name = fields.Char(string='Teachers Designations')
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


class ExamName(models.Model):
    _name = 'exam.name'
    _description = 'Exam Subject Name'

    name = fields.Char(string='Exam Name')
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


class ExamSubject(models.Model):
    _name = 'exam.subject'
    _description = 'Exam Subject'

    name = fields.Char(string='Subject Name')
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

#
# class TeacherClass(models.Model):
#     _name = 'teacher.class'
#     _description = 'Teachers Class Room'
#
#     name = fields.Char(string='Teachers Class Room')
